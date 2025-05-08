"""
PDF Download Manager for CrewKB.

This module provides utilities for downloading PDFs from URLs with caching and retry logic.
"""

import os
import asyncio
import logging
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Set
import aiohttp
import aiofiles
from urllib.parse import urlparse

from crewkb.utils.search.retry import RetryStrategy

logger = logging.getLogger(__name__)


class PDFDownloadManager:
    """
    Manages downloading PDFs from URLs with caching and retry logic.
    
    This class provides utilities for downloading PDFs from URLs, with support for:
    - Caching downloaded PDFs to avoid redundant downloads
    - Retry logic with exponential backoff for failed downloads
    - Parallel downloads with rate limiting
    - Tracking of failed downloads for potential fallback processing
    """
    
    def __init__(
        self,
        cache_dir: str = "cache/pdf",
        max_concurrent_downloads: int = 5,
        retry_strategy: Optional[RetryStrategy] = None
    ):
        """
        Initialize the PDFDownloadManager.
        
        Args:
            cache_dir: Directory to cache downloaded PDFs.
            max_concurrent_downloads: Maximum number of concurrent downloads.
            retry_strategy: Retry strategy for failed downloads.
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_concurrent_downloads = max_concurrent_downloads
        self.semaphore = asyncio.Semaphore(max_concurrent_downloads)
        
        self.retry_strategy = retry_strategy or RetryStrategy(
            max_retries=3,
            backoff_factor=1.5,
            max_backoff=10.0
        )
        
        self.failed_downloads: Set[str] = set()
    
    def _get_cache_path(self, url: str) -> Path:
        """
        Get the cache path for a URL.
        
        Args:
            url: The URL to get the cache path for.
            
        Returns:
            The cache path for the URL.
        """
        # Create a hash of the URL to use as the filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Parse the URL to get the filename
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Get the filename from the path
        filename = os.path.basename(path)
        
        # If the filename doesn't end with .pdf, use the hash as the filename
        if not filename.lower().endswith('.pdf'):
            filename = f"{url_hash}.pdf"
        else:
            # Add the hash to the filename to ensure uniqueness
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{url_hash}{ext}"
        
        return self.cache_dir / filename
    
    async def download(
        self,
        url: str,
        output_path: Optional[str] = None,
        force: bool = False
    ) -> Optional[str]:
        """
        Download a PDF from a URL with retry logic.
        
        Args:
            url: The URL to download the PDF from.
            output_path: The path to save the PDF to. If None, the PDF will be saved to the cache directory.
            force: Whether to force download even if the PDF is already cached.
            
        Returns:
            The path to the downloaded PDF, or None if the download failed.
        """
        # Get the cache path
        cache_path = self._get_cache_path(url)
        
        # If output_path is provided, use that instead
        output_path = Path(output_path) if output_path else cache_path
        
        # If the file already exists and force is False, return the path
        if not force and cache_path.exists():
            logger.info(f"PDF already cached at {cache_path}")
            
            # If output_path is different from cache_path, copy the file
            if output_path != cache_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                await self._copy_file(cache_path, output_path)
            
            return str(output_path)
        
        # Acquire the semaphore to limit concurrent downloads
        async with self.semaphore:
            try:
                # Download the PDF with retry logic
                return await self.retry_strategy.execute(
                    self._download_pdf,
                    url=url,
                    output_path=output_path,
                    cache_path=cache_path
                )
            except Exception as e:
                logger.error(f"Failed to download PDF from {url}: {str(e)}")
                self.failed_downloads.add(url)
                return None
    
    async def _download_pdf(
        self,
        url: str,
        output_path: Path,
        cache_path: Path
    ) -> str:
        """
        Download a PDF from a URL.
        
        Args:
            url: The URL to download the PDF from.
            output_path: The path to save the PDF to.
            cache_path: The cache path for the PDF.
            
        Returns:
            The path to the downloaded PDF.
            
        Raises:
            Exception: If the download fails.
        """
        logger.info(f"Downloading PDF from {url}")
        
        # Create the parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download the PDF
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download PDF from {url}: {response.status}")
                
                # Check if the content type is PDF
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type.lower() and not url.lower().endswith('.pdf'):
                    raise Exception(f"URL {url} does not point to a PDF: {content_type}")
                
                # Save the PDF to the cache path
                async with aiofiles.open(cache_path, 'wb') as f:
                    await f.write(await response.read())
                
                # If output_path is different from cache_path, copy the file
                if output_path != cache_path:
                    await self._copy_file(cache_path, output_path)
                
                logger.info(f"Downloaded PDF from {url} to {output_path}")
                
                return str(output_path)
    
    async def _copy_file(self, source: Path, destination: Path) -> None:
        """
        Copy a file from source to destination.
        
        Args:
            source: The source path.
            destination: The destination path.
        """
        async with aiofiles.open(source, 'rb') as src:
            async with aiofiles.open(destination, 'wb') as dst:
                await dst.write(await src.read())
    
    async def download_batch(
        self,
        urls: List[str],
        output_dir: Optional[str] = None,
        force: bool = False
    ) -> Dict[str, Optional[str]]:
        """
        Download multiple PDFs in parallel with rate limiting.
        
        Args:
            urls: The URLs to download PDFs from.
            output_dir: The directory to save the PDFs to. If None, the PDFs will be saved to the cache directory.
            force: Whether to force download even if the PDFs are already cached.
            
        Returns:
            A dictionary mapping URLs to the paths of the downloaded PDFs, or None if the download failed.
        """
        # Create tasks for downloading each PDF
        tasks = []
        for url in urls:
            # If output_dir is provided, create the output path
            output_path = None
            if output_dir:
                # Get the filename from the URL
                filename = os.path.basename(urlparse(url).path)
                
                # If the filename doesn't end with .pdf, use a hash of the URL as the filename
                if not filename.lower().endswith('.pdf'):
                    url_hash = hashlib.md5(url.encode()).hexdigest()
                    filename = f"{url_hash}.pdf"
                
                output_path = os.path.join(output_dir, filename)
            
            # Create a task for downloading the PDF
            task = asyncio.create_task(self.download(url, output_path, force))
            tasks.append((url, task))
        
        # Wait for all tasks to complete
        results = {}
        for url, task in tasks:
            try:
                results[url] = await task
            except Exception as e:
                logger.error(f"Failed to download PDF from {url}: {str(e)}")
                results[url] = None
                self.failed_downloads.add(url)
        
        return results
    
    def get_failed_downloads(self) -> Set[str]:
        """
        Get the set of URLs that failed to download.
        
        Returns:
            The set of URLs that failed to download.
        """
        return self.failed_downloads
    
    def clear_cache(self) -> None:
        """
        Clear the cache directory.
        """
        for file in self.cache_dir.glob('*.pdf'):
            file.unlink()
        
        logger.info(f"Cleared PDF cache directory: {self.cache_dir}")
