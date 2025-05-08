"""
DirectGoogleScholarTool for searching Google Scholar directly.

This module provides a tool for searching Google Scholar directly without using
an API, supporting date range filtering and review article filtering.
"""

import asyncio
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode, urlparse

from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


class DirectGoogleScholarToolInput(BaseModel):
    """Input schema for DirectGoogleScholarTool."""
    query: str = Field(
        ...,
        description="The search query to perform."
    )
    since_year: Optional[int] = Field(
        default=None,
        description=(
            "Only include papers published since this year (e.g., 2020)."
        ),
    )
    only_reviews: bool = Field(
        default=False,
        description="Only include review articles."
    )
    num_results: int = Field(
        default=10,
        description="The number of search results to return.",
    )
    page: int = Field(
        default=0,
        description="The page number to retrieve (0-indexed)."
    )
    rate_limit_delay: float = Field(
        default=1.0,
        description="Delay in seconds between requests to the same domain.",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests."
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached results if available.",
    )
    use_llm_fallback: bool = Field(
        default=False,
        description=(
            "Whether to use LLM-based extraction as a fallback if CSS-based "
            "extraction fails."
        ),
    )


class DirectGoogleScholarTool(BaseTool):
    """
    Tool for searching Google Scholar directly without using an API.

    This tool allows agents to search for academic papers and research on a
    given topic, with options to filter by publication date and article type.
    """

    name: str = "DirectGoogleScholarTool"
    description: str = (
        "Search Google Scholar for academic papers and research with "
        "filtering options"
    )
    args_schema: type[BaseModel] = DirectGoogleScholarToolInput

    # Class-level cache for rate limiting
    _domain_last_access = {}

    def _run(
        self,
        query: str,
        since_year: Optional[int] = None,
        only_reviews: bool = False,
        num_results: int = 10,
        page: int = 0,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        use_cache: bool = True,
        use_llm_fallback: bool = False,
    ) -> str:
        """
        Run the Google Scholar search.

        Args:
            query: The search query to perform.
            since_year: Only include papers published since this year.
            only_reviews: Only include review articles.
            num_results: The number of search results to return.
            page: The page number to retrieve (0-indexed).
            rate_limit_delay: Delay in seconds between requests to the same domain.
            max_retries: Maximum number of retries for failed requests.
            use_cache: Whether to use cached results if available.
            use_llm_fallback: Whether to use LLM-based extraction as a fallback.

        Returns:
            A string containing the search results in JSON format.

        Raises:
            Exception: If the search fails.
        """
        # Run the async crawl in a synchronous wrapper
        return asyncio.run(
            self._async_run(
                query,
                since_year,
                only_reviews,
                num_results,
                page,
                rate_limit_delay,
                max_retries,
                use_cache,
                use_llm_fallback,
            )
        )

    async def _async_run(
        self,
        query: str,
        since_year: Optional[int],
        only_reviews: bool,
        num_results: int,
        page: int,
        rate_limit_delay: float,
        max_retries: int,
        use_cache: bool,
        use_llm_fallback: bool,
    ) -> str:
        """
        Asynchronous implementation of the Google Scholar search.
        """
        # Generate a cache key for this search
        cache_key = self._get_cache_key(
            query, since_year, only_reviews, page
        )

        # Check cache first if enabled
        if use_cache:
            cached_result = self._check_cache(cache_key)
            if cached_result:
                return cached_result

        # Construct the Google Scholar URL
        url = self._build_google_scholar_url(
            query, since_year, only_reviews, page
        )

        # Apply rate limiting
        domain = urlparse(url).netloc
        self._apply_rate_limiting(domain, rate_limit_delay)

        # Define the extraction schema for Google Scholar results
        # Use "html" type instead of "text" to get the raw HTML
        google_scholar_schema = {
            "name": "Google Scholar Results",
            "baseSelector": ".gs_ri",  # Each search result item
            "fields": [
                {
                    "name": "title",
                    "selector": ".gs_rt",
                    "type": "html"  # Get raw HTML instead of text
                },
                {
                    "name": "link",
                    "selector": ".gs_rt a",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "publicationInfo",
                    "selector": ".gs_a",
                    "type": "html"  # Get raw HTML instead of text
                },
                {
                    "name": "snippet",
                    "selector": ".gs_rs",
                    "type": "html"  # Get raw HTML instead of text
                },
                {
                    "name": "citedByText",
                    "selector": "a:contains('Cited by')",
                    "type": "text"
                },
                {
                    "name": "citedByUrl",
                    "selector": "a:contains('Cited by')",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "relatedArticlesUrl",
                    "selector": "a:contains('Related articles')",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "allVersionsUrl",
                    "selector": "a:contains('All') span:contains('version')",
                    "type": "attribute",
                    "attribute": "href",
                    "parentSelector": "a"
                }
            ]
        }

        # Define the extraction schema for PDF links
        pdf_links_schema = {
            "name": "PDF Links",
            "baseSelector": ".gs_or_ggsm",
            "fields": [
                {
                    "name": "pdfUrl",
                    "selector": "a",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "source",
                    "selector": "a",
                    "type": "text"
                }
            ]
        }

        # Define the extraction schema for related searches
        related_searches_schema = {
            "name": "Related Searches",
            "baseSelector": ".gs_qsuggest_wrap a",
            "fields": [
                {
                    "name": "search_term",
                    "type": "text"
                }
            ]
        }

        # Configure the crawler
        browser_config = BrowserConfig(
            headless=True,
            user_agent_mode="random",  # Randomize user agent
            # TODO: Consider adding proxy_config, headers, extra_args from tool input
        )

        # Create the extraction strategy
        extraction_strategy = JsonCssExtractionStrategy(google_scholar_schema)

        # Configure the crawler run
        run_config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            cache_mode=CacheMode.ENABLED if use_cache else CacheMode.DISABLED,
            wait_for=".gs_ri",  # Wait for search results to load
            page_timeout=30000,  # 30 seconds timeout
            # TODO: Consider adding simulate_user=True if supported and beneficial
        )

        # Implement retry logic with exponential backoff
        retry_count = 0
        base_delay = 1.0

        while retry_count <= max_retries:
            try:
                # Create and run the crawler
                async with AsyncWebCrawler(config=browser_config) as crawler:
                    # Pass magic=True to arun for enhanced anti-detection
                    result = await crawler.arun(url=url, config=run_config, magic=True)

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
                            # Try LLM-based extraction as a fallback
                            if use_llm_fallback:
                                return await self._fallback_to_llm(
                                    url, query, since_year, only_reviews, page
                                )
                            else:
                                return json.dumps({
                                    "error": (
                                        f"Error searching Google Scholar after "
                                        f"{max_retries} retries: "
                                        f"{result.error_message}"
                                    ),
                                    "query": query,
                                    "filters": {
                                        "since_year": since_year,
                                        "only_reviews": only_reviews
                                    },
                                    "page": page,
                                    "results": []
                                })

                    # Parse the extracted content
                    search_results = json.loads(result.extracted_content)

                    # Extract PDF links
                    pdf_links = await self._extract_pdf_links(
                        crawler, url, pdf_links_schema
                    )

                    # Extract related searches
                    related_searches = await self._extract_related_searches(
                        crawler, url, related_searches_schema
                    )

                    # Extract pagination info
                    pagination_info = await self._extract_pagination_info(
                        crawler, url, page
                    )

                    # Extract total results count
                    total_results_count = await self._extract_total_results_count(
                        crawler, url
                    )

                    # Process the search results to extract year and citation count
                    processed_results = self._process_search_results(
                        search_results, pdf_links
                    )

                    # Format the results
                    formatted_result = self._format_results(
                        query,
                        since_year,
                        only_reviews,
                        page,
                        processed_results,
                        related_searches,
                        pagination_info,
                        total_results_count,
                    )

                    # Save the results to a file
                    # file_path = self._save_results_to_file(
                    #     query, since_year, only_reviews, page, formatted_result
                    # )

                    # Cache the result
                    if use_cache:
                        self._cache_result(cache_key, formatted_result)

                    return formatted_result

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
                    # Try LLM-based extraction as a fallback
                    if use_llm_fallback:
                        return await self._fallback_to_llm(
                            url, query, since_year, only_reviews, page
                        )
                    else:
                        return json.dumps({
                            "error": (
                                f"Error searching Google Scholar after "
                                f"{max_retries} retries: {str(e)}"
                            ),
                            "query": query,
                            "filters": {
                                "since_year": since_year,
                                "only_reviews": only_reviews
                            },
                            "page": page,
                            "results": []
                        })

        return json.dumps({
            "error": (
                f"Failed to search Google Scholar after {max_retries} "
                f"retries."
            ),
            "query": query,
            "filters": {
                "since_year": since_year,
                "only_reviews": only_reviews
            },
            "page": page,
            "results": []
        })

    def _build_google_scholar_url(
        self,
        query: str,
        since_year: Optional[int],
        only_reviews: bool,
        page: int
    ) -> str:
        """
        Build the Google Scholar URL with the appropriate parameters.

        Args:
            query: The search query to perform.
            since_year: Only include papers published since this year.
            only_reviews: Only include review articles.
            page: The page number to retrieve (0-indexed).

        Returns:
            The Google Scholar URL.
        """
        base_url = "https://scholar.google.com/scholar"
        params = {"q": query, "hl": "en", "as_sdt": "0,5"}  # type: ignore

        if since_year:
            params["as_ylo"] = str(since_year)

        if only_reviews:
            params["as_rr"] = "1"

        if page > 0:
            params["start"] = str(page * 10)  # type: ignore

        return f"{base_url}?{urlencode(params)}"

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

    def _get_cache_key(
        self,
        query: str,
        since_year: Optional[int],
        only_reviews: bool,
        page: int
    ) -> str:
        """
        Generate a cache key for a search query.

        Args:
            query: The search query to perform.
            since_year: Only include papers published since this year.
            only_reviews: Only include review articles.
            page: The page number to retrieve (0-indexed).

        Returns:
            A cache key.
        """
        # Create a string representation of the search parameters
        params_str = (
            f"{query}|{since_year}|{only_reviews}|{page}"
        )

        # Create a hash of the parameters
        return hashlib.md5(params_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get the cache file path for a cache key.

        Args:
            cache_key: The cache key.

        Returns:
            The path to the cache file.
        """
        cache_dir = Path("data/google_scholar/cache")
        cache_dir.mkdir(exist_ok=True, parents=True)
        return cache_dir / f"{cache_key}.json"

    def _check_cache(self, cache_key: str) -> Optional[str]:
        """
        Check if a cache key is cached and return the cached result if it exists.

        Args:
            cache_key: The cache key to check.

        Returns:
            The cached result if it exists, None otherwise.
        """
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading cache: {str(e)}")

        return None

    def _cache_result(self, cache_key: str, result: str) -> None:
        """
        Cache the result of a search.

        Args:
            cache_key: The cache key.
            result: The result to cache.
        """
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(result)
        except Exception as e:
            print(f"Error caching result: {str(e)}")

    def _save_results_to_file(
        self,
        query: str,
        since_year: Optional[int],
        only_reviews: bool,
        page: int,
        result: str
    ) -> Path:
        """
        Save the search results to a file.

        Args:
            query: The search query.
            since_year: The since year filter.
            only_reviews: The only reviews filter.
            page: The page number.
            result: The search result.

        Returns:
            The path to the saved file.
        """
        # Create a sanitized filename
        sanitized_query = re.sub(
            r"[^\w\-]", "_", query.lower()
        )

        # Add filters to the filename
        filename = sanitized_query
        if since_year:
            filename += f"_since_{since_year}"
        if only_reviews:
            filename += "_reviews_only"
        if page > 0:
            filename += f"_page_{page}"

        # Add extension
        filename += ".json"

        # Create the directory if it doesn't exist
        output_dir = Path("data/google_scholar")
        output_dir.mkdir(exist_ok=True, parents=True)

        # Save the file
        file_path = output_dir / filename  # type: ignore
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)

        return file_path

    async def _extract_pdf_links(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        schema: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Extract PDF links from the Google Scholar page.

        Args:
            crawler: The AsyncWebCrawler instance.
            url: The Google Scholar URL.
            schema: The extraction schema for PDF links.

        Returns:
            A list of PDF links with their sources.
        """
        try:
            # Create the extraction strategy
            extraction_strategy = JsonCssExtractionStrategy(schema)

            # Configure the crawler run
            run_config = CrawlerRunConfig(
                extraction_strategy=extraction_strategy,
                cache_mode=CacheMode.BYPASS  # Don't cache this request
            )

            # Run the crawler
            result = await crawler.arun(url=url, config=run_config)

            if not result.success:
                return []

            # Parse the extracted content
            pdf_links = json.loads(result.extracted_content)

            return pdf_links
        except Exception as e:
            print(f"Error extracting PDF links: {str(e)}")
            return []

    async def _extract_related_searches(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        schema: Dict[str, Any]
    ) -> List[str]:
        """
        Extract related searches from the Google Scholar page.

        Args:
            crawler: The AsyncWebCrawler instance.
            url: The Google Scholar URL.
            schema: The extraction schema for related searches.

        Returns:
            A list of related search terms.
        """
        try:
            # Create the extraction strategy
            extraction_strategy = JsonCssExtractionStrategy(schema)

            # Configure the crawler run
            run_config = CrawlerRunConfig(
                extraction_strategy=extraction_strategy,
                cache_mode=CacheMode.BYPASS  # Don't cache this request
            )

            # Run the crawler
            result = await crawler.arun(url=url, config=run_config)

            if not result.success:
                return []

            # Parse the extracted content
            related_searches = json.loads(result.extracted_content)

            # Extract the search terms
            return [item["search_term"] for item in related_searches]
        except Exception as e:
            print(f"Error extracting related searches: {str(e)}")
            return []

    async def _extract_pagination_info(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        current_page: int
    ) -> Dict[str, Any]:
        """
        Extract pagination information from the Google Scholar page.

        Args:
            crawler: The AsyncWebCrawler instance.
            url: The Google Scholar URL.
            current_page: The current page number.

        Returns:
            A dictionary containing pagination information.
        """
        try:
            # Get the HTML content
            html_result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
            )

            if not html_result.success:
                return {
                    "current_page": current_page,
                    "next_page_url": None,
                    "total_pages": 1
                }

            # Parse the HTML
            soup = BeautifulSoup(html_result.html, "html.parser")

            # Find the pagination links
            pagination_links = soup.select("#gs_n a")

            # Extract the next page URL
            next_page_url = None
            for link in pagination_links:
                # Google Scholar uses 1-indexed pagination
                if link.text.strip() == str(current_page + 2):
                    next_page_url = "https://scholar.google.com" + link["href"]
                    break

            # Estimate the total number of pages
            total_pages = 1
            for link in pagination_links:
                try:
                    page_num = int(link.text.strip())
                    total_pages = max(total_pages, page_num)
                except ValueError:
                    pass

            return {
                "current_page": current_page,
                "next_page_url": next_page_url,
                "total_pages": total_pages
            }
        except Exception as e:
            print(f"Error extracting pagination info: {str(e)}")
            return {
                "current_page": current_page,
                "next_page_url": None,
                "total_pages": 1
            }

    async def _extract_total_results_count(
        self,
        crawler: AsyncWebCrawler,
        url: str
    ) -> str:
        """
        Extract the total results count from the Google Scholar page.

        Args:
            crawler: The AsyncWebCrawler instance.
            url: The Google Scholar URL.

        Returns:
            The total results count as a string.
        """
        try:
            # Get the HTML content
            html_result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
            )

            if not html_result.success:
                return "Unknown"

            # Parse the HTML
            soup = BeautifulSoup(html_result.html, "html.parser")

            # Find the results count
            results_count = soup.select_one("#gs_ab_md")

            if results_count:
                return results_count.text.strip()
            else:
                return "Unknown"
        except Exception as e:
            print(f"Error extracting total results count: {str(e)}")
            return "Unknown"

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text using BeautifulSoup to properly handle HTML and spacing.
        
        Args:
            text: The text to clean, potentially containing HTML.
            
        Returns:
            The cleaned text with proper spacing.
        """
        if not text:
            return ""
        
        # Create a BeautifulSoup object from the text
        # The text might contain HTML entities or tags
        soup = BeautifulSoup(f"<div>{text}</div>", "html.parser")
        
        # Use BeautifulSoup's get_text() method with appropriate parameters
        # separator=' ' ensures spaces between elements
        # strip=True removes leading/trailing whitespace
        cleaned_text = soup.get_text(separator=' ', strip=False)
        
        # Normalize whitespace (replace multiple spaces with a single space)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()

    def _process_search_results(
        self,
        search_results: List[Dict[str, Any]],
        pdf_links: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Process the search results to extract year and citation count.

        Args:
            search_results: The raw search results.
            pdf_links: The PDF links extracted from the page.

        Returns:
            The processed search results.
        """
        processed_results = []

        for i, result in enumerate(search_results):
            # Extract the publication info
            publication_info = self._clean_text(result.get("publicationInfo", ""))

            # Extract the year using regex
            year_match = re.search(r'\b(19|20)\d{2}\b', publication_info)
            year = int(year_match.group(0)) if year_match else None

            # Extract the citation count
            cited_by_text = result.get("citedByText", "")
            cited_by_match = re.search(r'Cited by (\d+)', cited_by_text)
            cited_by = int(cited_by_match.group(1)) if cited_by_match else None

            # Find PDF URL if available
            pdf_url = None
            if i < len(pdf_links):
                pdf_url = pdf_links[i].get("pdfUrl")

            # Clean text fields
            title = self._clean_text(result.get("title", ""))
            snippet = self._clean_text(result.get("snippet", ""))

            # Create the processed result
            processed_result = {
                "title": title,
                "link": result.get("link", ""),
                "publicationInfo": publication_info,
                "snippet": snippet,
                "year": year,
                "citedBy": cited_by,
                "pdfUrl": pdf_url,
                "id": hashlib.md5(
                    result.get("link", "").encode()
                ).hexdigest()[:16]
            }

            processed_results.append(processed_result)

        return processed_results

    def _format_results(
        self,
        query: str,
        since_year: Optional[int],
        only_reviews: bool,
        page: int,
        search_results: List[Dict[str, Any]],
        related_searches: List[str],
        pagination_info: Dict[str, Any],
        total_results_count: str,
    ) -> str:
        """
        Format the search results.

        Args:
            query: The search query.
            since_year: The since year filter.
            only_reviews: The only reviews filter.
            page: The page number.
            search_results: The search results.
            related_searches: The related searches.
            pagination_info: The pagination information.
            total_results_count: The total results count.

        Returns:
            A formatted JSON string.
        """
        # Create the result object
        result = {
            "query": query,
            "filters": {
                "since_year": since_year,
                "only_reviews": only_reviews
            },
            "page": page,
            "total_results_count": total_results_count,
            "results": search_results,
            "related_searches": related_searches,
            "pagination": pagination_info
        }

        # Convert to JSON
        return json.dumps(result, indent=2)

    async def _fallback_to_llm(
        self,
        url: str,
        query: str,
        since_year: Optional[int],
        only_reviews: bool,
        page: int
    ) -> str:
        """
        Fallback to LLM-based extraction if CSS-based extraction fails.

        Args:
            url: The Google Scholar URL.
            query: The search query.
            since_year: The since year filter.
            only_reviews: The only reviews filter.
            page: The page number.

        Returns:
            A formatted JSON string.
        """
        try:
            # Create a simple error message
            return json.dumps(
                {
                    "error": "LLM fallback not implemented yet",
                    "query": query,
                    "filters": {
                        "since_year": since_year,
                        "only_reviews": only_reviews,
                    },
                    "page": page,
                    "results": [],
                }
            )
        except Exception as e:
            return json.dumps({
                "error": f"Error in LLM fallback: {str(e)}",
                "query": query,
                "filters": {
                    "since_year": since_year,
                    "only_reviews": only_reviews
                },
                "page": page,
                "results": []
            })
