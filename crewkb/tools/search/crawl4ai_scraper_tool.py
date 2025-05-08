"""
Crawl4AIScraperTool for scraping web pages using Crawl4AI.

This module provides a tool for scraping web pages and extracting their content
using the Crawl4AI library, which is designed to be LLM-friendly.
"""

import asyncio
import hashlib
import json
import time
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode


class Crawl4AIScraperToolInput(BaseModel):
    """Input schema for Crawl4AIScraperTool."""
    url: str = Field(
        ...,
        description="The URL of the webpage to scrape."
    )
    word_count_threshold: int = Field(
        default=10,
        description="Minimum words per content block to include."
    )
    exclude_external_links: bool = Field(
        default=True,
        description="Whether to exclude external links from the output."
    )
    rate_limit_delay: float = Field(
        default=1.0,
        description="Delay in seconds between requests to the same domain."
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests."
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached results if available."
    )


class Crawl4AIScraperTool(BaseTool):
    """
    Tool for scraping web pages using Crawl4AI.
    
    This tool allows agents to scrape web pages and extract their content as markdown,
    which is particularly useful for retrieving full text of articles and other
    research materials.
    """
    
    name: str = "Crawl4AIScraperTool"
    description: str = "Scrape a webpage to extract its full content as markdown"
    args_schema: type[BaseModel] = Crawl4AIScraperToolInput
    
    # Class-level cache for rate limiting
    _domain_last_access = {}
    
    def _run(
        self,
        url: str,
        word_count_threshold: int = 10,
        exclude_external_links: bool = True,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        use_cache: bool = True
    ) -> str:
        """
        Scrape a webpage and extract its content as markdown.
        
        Args:
            url: The URL of the webpage to scrape.
            word_count_threshold: Minimum words per content block to include.
            exclude_external_links: Whether to exclude external links from the output.
            rate_limit_delay: Delay in seconds between requests to the same domain.
            max_retries: Maximum number of retries for failed requests.
            use_cache: Whether to use cached results if available.
            
        Returns:
            A string containing the scraped content in markdown format.
        """
        # Run the async crawl in a synchronous wrapper
        return asyncio.run(
            self._async_run(
                url, 
                word_count_threshold, 
                exclude_external_links,
                rate_limit_delay,
                max_retries,
                use_cache
            )
        )
    
    async def _async_run(
        self, 
        url: str, 
        word_count_threshold: int,
        exclude_external_links: bool,
        rate_limit_delay: float,
        max_retries: int,
        use_cache: bool
    ) -> str:
        """
        Asynchronous implementation of the webpage scraping.
        """
        # Check cache first if enabled
        if use_cache:
            cached_result = self._check_cache(url)
            if cached_result:
                return cached_result
        
        # Apply rate limiting
        domain = urlparse(url).netloc
        self._apply_rate_limiting(domain, rate_limit_delay)
        
        # Configure the crawler
        browser_config = BrowserConfig()
        run_config = CrawlerRunConfig(
            word_count_threshold=word_count_threshold,
            exclude_external_links=exclude_external_links,
            remove_overlay_elements=True,
            process_iframes=True,
            cache_mode=CacheMode.ENABLED if use_cache else CacheMode.DISABLED
        )
        
        # Implement retry logic with exponential backoff
        retry_count = 0
        base_delay = 1.0
        
        while retry_count <= max_retries:
            try:
                # Create and run the crawler
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    result = await crawler.arun(url=url, config=run_config)
                    
                    if not result.success:
                        if retry_count < max_retries:
                            retry_count += 1
                            delay = base_delay * (2 ** (retry_count - 1))
                            print(
                                f"Retry {retry_count}/{max_retries} "
                                f"after {delay}s delay..."
                            )
                            await asyncio.sleep(delay)
                            continue
                        else:
                            return (
                                f"Error scraping webpage after {max_retries} "
                                f"retries: {result.error_message}"
                            )
                    
                    # Save the markdown to a file
                    filename = self._get_filename_from_url(url)
                    file_path = Path("data/crawl4ai") / filename
                    file_path.parent.mkdir(exist_ok=True, parents=True)
                    
                    # Extract the markdown content
                    if hasattr(result.markdown, 'raw_markdown'):
                        markdown_content = result.markdown.raw_markdown
                    else:
                        markdown_content = str(result.markdown)
                    
                    # Save to file
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    
                    # Cache the result
                    if use_cache:
                        self._cache_result(url, markdown_content, file_path)
                    
                    # Format and return the result
                    return self._format_result(result, url, str(file_path))
                    
            except Exception as e:
                if retry_count < max_retries:
                    retry_count += 1
                    delay = base_delay * (2 ** (retry_count - 1))
                    print(
                        f"Error: {str(e)}. Retry {retry_count}/{max_retries} "
                        f"after {delay}s delay..."
                    )
                    await asyncio.sleep(delay)
                else:
                    return (
                        f"Error scraping webpage after {max_retries} "
                        f"retries: {str(e)}"
                    )
        
        return f"Failed to scrape webpage after {max_retries} retries."
    
    def _apply_rate_limiting(self, domain: str, delay: float) -> None:
        """
        Apply rate limiting for a specific domain.
        
        Args:
            domain: The domain to rate limit.
            delay: The minimum delay between requests to the same domain.
        """
        current_time = time.time()
        if domain in self._domain_last_access:
            last_access = self._domain_last_access[domain]
            elapsed = current_time - last_access
            if elapsed < delay:
                time.sleep(delay - elapsed)
        
        # Update the last access time
        self._domain_last_access[domain] = time.time()
    
    def _get_filename_from_url(self, url: str) -> str:
        """
        Generate a filename from a URL.
        
        Args:
            url: The URL to generate a filename from.
            
        Returns:
            A sanitized filename.
        """
        # Extract domain and path
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        
        # Create a sanitized filename
        if path and path != "/":
            # Use the last part of the path
            filename = path.strip("/").split("/")[-1]
            if not filename:
                filename = path.strip("/").replace("/", "_")
        else:
            filename = domain
        
        # Remove invalid characters and add extension
        filename = "".join(
            c if c.isalnum() or c in "-_" else "_" for c in filename
        )
        if not filename.endswith(".md"):
            filename += ".md"
        
        return filename
    
    def _get_cache_path(self, url: str) -> Path:
        """
        Get the cache file path for a URL.
        
        Args:
            url: The URL to get the cache path for.
            
        Returns:
            The path to the cache file.
        """
        # Create a hash of the URL to use as the cache key
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_dir = Path("data/crawl4ai/cache")
        cache_dir.mkdir(exist_ok=True, parents=True)
        return cache_dir / f"{url_hash}.json"
    
    def _check_cache(self, url: str) -> Optional[str]:
        """
        Check if a URL is cached and return the cached result if it exists.
        
        Args:
            url: The URL to check the cache for.
            
        Returns:
            The cached result if it exists, None otherwise.
        """
        cache_path = self._get_cache_path(url)
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                
                # Check if the cache is still valid (for now, we consider it always valid)
                return cache_data["formatted_result"]
            except Exception as e:
                print(f"Error reading cache: {str(e)}")
        
        return None
    
    def _cache_result(self, url: str, markdown_content: str, file_path: Path) -> None:
        """
        Cache the result of a scrape.
        
        Args:
            url: The URL that was scraped.
            markdown_content: The markdown content that was extracted.
            file_path: The path to the saved markdown file.
        """
        cache_path = self._get_cache_path(url)
        try:
            cache_data = {
                "url": url,
                "markdown_content": markdown_content,
                "file_path": str(file_path),
                "timestamp": time.time(),
                "formatted_result": self._format_result_from_cache(
                    url, markdown_content, file_path
                )
            }
            
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error caching result: {str(e)}")
    
    def _format_result(self, result, url: str, file_path: str) -> str:
        """
        Format the scrape result.
        
        Args:
            result: The CrawlResult object.
            url: The URL that was scraped.
            file_path: The path to the saved markdown file.
            
        Returns:
            A formatted string with the scraped content.
        """
        formatted = f"Scraped Content from {url}\n"
        formatted += "=" * 80 + "\n\n"
        
        # Add title if available
        if hasattr(result, 'metadata') and result.metadata and "title" in result.metadata:
            formatted += f"Title: {result.metadata['title']}\n\n"
        
        # Add the content
        if hasattr(result.markdown, 'raw_markdown'):
            formatted += result.markdown.raw_markdown
        else:
            formatted += str(result.markdown)
        
        # Add file path information
        formatted += f"\n\nContent saved to: {file_path}\n"
        
        return formatted
    
    def _format_result_from_cache(self, url: str, markdown_content: str, file_path: Path) -> str:
        """
        Format the result from cache data.
        
        Args:
            url: The URL that was scraped.
            markdown_content: The markdown content that was extracted.
            file_path: The path to the saved markdown file.
            
        Returns:
            A formatted string with the scraped content.
        """
        formatted = f"Scraped Content from {url} (cached)\n"
        formatted += "=" * 80 + "\n\n"
        
        # Add the content
        formatted += markdown_content
        
        # Add file path information
        formatted += f"\n\nContent saved to: {file_path}\n"
        
        return formatted
