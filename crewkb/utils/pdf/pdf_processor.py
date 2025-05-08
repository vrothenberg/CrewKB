"""
PDF Processor for CrewKB.

This module provides utilities for processing PDFs, including downloading, parsing,
and extracting content.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Set, Tuple

from crewkb.utils.pdf.pdf_download_manager import PDFDownloadManager
from crewkb.utils.pdf.marker_wrapper import MarkerWrapper
from crewkb.models.knowledge.paper import PaperSource

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Processes PDFs for knowledge synthesis.
    
    This class orchestrates the download and parsing of PDFs, with support for:
    - Downloading PDFs from URLs
    - Parsing PDFs to markdown format
    - Extracting sections from parsed PDFs
    - Tracking failed downloads and parsing attempts
    - Providing fallback options for failed processing
    """
    
    def __init__(
        self,
        download_manager: Optional[PDFDownloadManager] = None,
        marker_wrapper: Optional[MarkerWrapper] = None,
        cache_dir: str = "cache/pdf_processor",
        use_llm: bool = True,
        google_api_key: Optional[str] = None
    ):
        """
        Initialize the PDFProcessor.
        
        Args:
            download_manager: The PDFDownloadManager to use. If None, a new one will be created.
            marker_wrapper: The MarkerWrapper to use. If None, a new one will be created.
            cache_dir: Directory to cache processed PDFs.
            use_llm: Whether to use Gemini for improved accuracy.
            google_api_key: Google API key for Gemini. If None, will use the
                            GOOGLE_API_KEY environment variable.
        """
        self.download_manager = download_manager or PDFDownloadManager(
            cache_dir=os.path.join(cache_dir, "downloads")
        )
        
        self.marker_wrapper = marker_wrapper or MarkerWrapper(
            use_llm=use_llm,
            cache_dir=os.path.join(cache_dir, "marker"),
            google_api_key=google_api_key
        )
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.failed_processing: Set[str] = set()
    
    async def process_paper(
        self,
        paper: PaperSource,
        output_dir: Optional[str] = None,
        force: bool = False,
        use_llm: Optional[bool] = None
    ) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
        """
        Process a paper and extract its content.
        
        Args:
            paper: The PaperSource object representing the paper.
            output_dir: The directory to save the processed paper to. If None,
                        the paper will be saved to the cache directory.
            force: Whether to force processing even if the paper is already cached.
            use_llm: Whether to use Gemini for improved accuracy. If None, will use
                     the value provided in the constructor.
            
        Returns:
            A tuple containing:
            - The path to the processed markdown file (or None if processing failed)
            - A dictionary mapping section names to section content (or None if processing failed)
        """
        # Get the PDF URL from the paper
        pdf_url = paper.pdf_url
        
        # If the paper doesn't have a PDF URL, try to use the regular URL
        if not pdf_url:
            pdf_url = paper.url
        
        # If we still don't have a URL, we can't process the paper
        if not pdf_url:
            logger.error(f"Paper {paper.title} has no URL to download from")
            self.failed_processing.add(paper.id)
            return None, None
        
        # Create the output directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Create the output path
        output_path = None
        if output_dir:
            # Create a sanitized filename from the paper title
            sanitized_title = paper.title.lower().replace(" ", "_").replace("/", "_")
            sanitized_title = "".join(c for c in sanitized_title if c.isalnum() or c == "_")
            
            # Truncate the filename if it's too long
            if len(sanitized_title) > 100:
                sanitized_title = sanitized_title[:100]
            
            # Create the output path
            output_path = os.path.join(output_dir, f"{sanitized_title}.md")
        
        # Create the cache key
        cache_key = f"{paper.id}.md"
        cache_path = self.cache_dir / cache_key
        
        # If the file already exists and force is False, return the cached result
        if not force and cache_path.exists():
            logger.info(f"Paper {paper.title} already processed at {cache_path}")
            
            # Load the cached result
            with open(cache_path, "r") as f:
                markdown = f.read()
            
            # Extract sections from the markdown
            sections = self.marker_wrapper.extract_sections(markdown)
            
            # If output_path is provided and different from cache_path, copy the file
            if output_path and str(cache_path) != output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(cache_path, "r") as src:
                    with open(output_path, "w") as dst:
                        dst.write(src.read())
            
            return str(cache_path), sections
        
        try:
            # Download the PDF
            pdf_path = await self.download_manager.download(pdf_url)
            
            # If the download failed, we can't process the paper
            if not pdf_path:
                logger.error(f"Failed to download PDF for paper {paper.title}")
                self.failed_processing.add(paper.id)
                return None, None
            
            # Parse the PDF
            markdown, metadata, _ = self.marker_wrapper.parse_pdf(
                pdf_path,
                use_llm=use_llm
            )
            
            # If the parsing failed, we can't process the paper
            if not markdown:
                logger.error(f"Failed to parse PDF for paper {paper.title}")
                self.failed_processing.add(paper.id)
                return None, None
            
            # Extract sections from the markdown
            sections = self.marker_wrapper.extract_sections(markdown)
            
            # Save the markdown to the cache path
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "w") as f:
                f.write(markdown)
            
            # Save the sections to a separate file
            sections_path = cache_path.with_suffix(".sections.json")
            import json
            with open(sections_path, "w") as f:
                json.dump(sections, f)
            
            # If output_path is provided, save the markdown to the output path
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(markdown)
            
            logger.info(f"Processed paper {paper.title} to {cache_path}")
            
            return str(cache_path), sections
            
        except Exception as e:
            logger.error(f"Failed to process paper {paper.title}: {str(e)}")
            self.failed_processing.add(paper.id)
            return None, None
    
    async def process_papers(
        self,
        papers: List[PaperSource],
        output_dir: Optional[str] = None,
        force: bool = False,
        use_llm: Optional[bool] = None,
        max_concurrent: int = 5
    ) -> Dict[str, Tuple[Optional[str], Optional[Dict[str, str]]]]:
        """
        Process multiple papers in parallel.
        
        Args:
            papers: The list of PaperSource objects to process.
            output_dir: The directory to save the processed papers to. If None,
                        the papers will be saved to the cache directory.
            force: Whether to force processing even if the papers are already cached.
            use_llm: Whether to use Gemini for improved accuracy. If None, will use
                     the value provided in the constructor.
            max_concurrent: Maximum number of papers to process concurrently.
            
        Returns:
            A dictionary mapping paper IDs to tuples containing:
            - The path to the processed markdown file (or None if processing failed)
            - A dictionary mapping section names to section content (or None if processing failed)
        """
        # Create a semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # Create tasks for processing each paper
        async def process_with_semaphore(paper):
            async with semaphore:
                return paper.id, await self.process_paper(
                    paper,
                    output_dir=output_dir,
                    force=force,
                    use_llm=use_llm
                )
        
        # Create tasks for processing each paper
        tasks = [process_with_semaphore(paper) for paper in papers]
        
        # Wait for all tasks to complete
        results = {}
        for task in asyncio.as_completed(tasks):
            paper_id, result = await task
            results[paper_id] = result
        
        return results
    
    def get_failed_processing(self) -> Set[str]:
        """
        Get the set of paper IDs that failed to process.
        
        Returns:
            The set of paper IDs that failed to process.
        """
        return self.failed_processing
    
    def clear_cache(self) -> None:
        """
        Clear the cache directory.
        """
        # Clear the download manager cache
        self.download_manager.clear_cache()
        
        # Clear the marker wrapper cache
        self.marker_wrapper.clear_cache()
        
        # Clear the processor cache
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                file.unlink()
        
        logger.info(f"Cleared PDF processor cache directory: {self.cache_dir}")
