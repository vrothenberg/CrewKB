"""
Search coordinator for CrewKB.

This module provides a coordinator for managing searches across multiple tools
with caching and error handling.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple

from crewkb.models.knowledge.paper import PaperSource
from crewkb.tools.search.direct_google_scholar_tool import DirectGoogleScholarTool
from crewkb.tools.search.semantic_scholar_tool import SemanticScholarTool
from crewkb.utils.search.cache import SearchCache
from crewkb.utils.search.retry import RetryStrategy

# Set up logging
logger = logging.getLogger(__name__)


class AsyncSearchCoordinator:
    """
    Coordinator for managing searches across multiple tools.
    
    This class coordinates searches across multiple tools with caching and
    error handling. It provides a unified interface for searching across
    different sources and combines the results.
    """
    
    def __init__(
        self,
        cache_dir: str = "cache/search",
        max_retries: int = 3,
        backoff_factor: float = 1.5
    ):
        """
        Initialize the search coordinator.
        
        Args:
            cache_dir: The directory to store cache files.
            max_retries: The maximum number of retries for failed API calls.
            backoff_factor: The factor to multiply the delay by after each retry.
        """
        self.cache = SearchCache(cache_dir)
        self.retry_strategy = RetryStrategy(
            max_retries=max_retries,
            backoff_factor=backoff_factor
        )
        
        # Initialize search tools
        self.google_scholar_tool = DirectGoogleScholarTool()
        self.semantic_scholar_tool = SemanticScholarTool()
    
    async def search(
        self,
        term: str,
        max_results: int = 10,
        use_cache: bool = True,
        min_citation_count: Optional[int] = None,
        year_range: Optional[Tuple[int, int]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across multiple tools and combine results.
        
        Args:
            term: The search term.
            max_results: Maximum number of results per tool.
            use_cache: Whether to use cached results.
            min_citation_count: Minimum citation count for filtering results.
            year_range: Year range for filtering results (min_year, max_year).
            
        Returns:
            Combined search results from all tools.
        """
        # Check cache first if enabled
        if use_cache:
            cache_key = f"{term}_{max_results}_{min_citation_count}_{year_range}"
            cached_results = self.cache.get(cache_key)
            if cached_results:
                logger.info(f"Using cached results for '{term}'")
                return cached_results
        
        # Run searches in parallel
        tasks = [
            self._search_google_scholar(term, max_results),
            self._search_semantic_scholar(term, max_results, min_citation_count, year_range)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        combined_results: Dict[str, List[Dict[str, Any]]] = {
            "google_scholar": [],
            "semantic_scholar": []
        }
        
        # Handle Google Scholar results
        if isinstance(results[0], list):
            combined_results["google_scholar"] = results[0]
        else:
            logger.error(f"Google Scholar search failed: {str(results[0])}")
        
        # Handle Semantic Scholar results
        if isinstance(results[1], list):
            combined_results["semantic_scholar"] = results[1]
        else:
            logger.error(f"Semantic Scholar search failed: {str(results[1])}")
        
        # Cache results if enabled
        if use_cache:
            cache_key = f"{term}_{max_results}_{min_citation_count}_{year_range}"
            self.cache.set(cache_key, combined_results)
        
        return combined_results
    
    async def _search_google_scholar(
        self,
        term: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search Google Scholar with caching and error handling.
        
        Args:
            term: The search term.
            max_results: Maximum number of results.
            
        Returns:
            Search results from Google Scholar.
        """
        async def _search():
            try:
                # The DirectGoogleScholarTool.run method is synchronous but time-consuming
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None,
                    lambda: self.google_scholar_tool.run(term, max_results)
                )
                return results
            except Exception as e:
                logger.error(f"Error searching Google Scholar: {str(e)}")
                raise
        
        return await self.retry_strategy.execute(_search)
    
    async def _search_semantic_scholar(
        self,
        term: str,
        max_results: int,
        min_citation_count: Optional[int] = None,
        year_range: Optional[Tuple[int, int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search Semantic Scholar with caching and error handling.
        
        Args:
            term: The search term.
            max_results: Maximum number of results.
            min_citation_count: Minimum citation count for filtering results.
            year_range: Year range for filtering results (min_year, max_year).
            
        Returns:
            Search results from Semantic Scholar.
        """
        async def _search():
            try:
                # The SemanticScholarTool.run method is synchronous
                loop = asyncio.get_event_loop()
                
                # Prepare arguments
                kwargs = {
                    "query": term,
                    "limit": max_results
                }
                
                if min_citation_count is not None:
                    kwargs["min_citation_count"] = min_citation_count
                
                if year_range is not None:
                    kwargs["year"] = f"{year_range[0]}-{year_range[1]}"
                
                results = await loop.run_in_executor(
                    None,
                    lambda: self.semantic_scholar_tool.run(**kwargs)
                )
                return results
            except Exception as e:
                logger.error(f"Error searching Semantic Scholar: {str(e)}")
                raise
        
        return await self.retry_strategy.execute(_search)
    
    async def search_and_create_papers(
        self,
        term: str,
        max_results: int = 10,
        use_cache: bool = True,
        min_citation_count: Optional[int] = None,
        year_range: Optional[Tuple[int, int]] = None
    ) -> Dict[str, List[PaperSource]]:
        """
        Search and create PaperSource objects from the results.
        
        Args:
            term: The search term.
            max_results: Maximum number of results per tool.
            use_cache: Whether to use cached results.
            min_citation_count: Minimum citation count for filtering results.
            year_range: Year range for filtering results (min_year, max_year).
            
        Returns:
            Dictionary of PaperSource objects by source.
        """
        results = await self.search(
            term, max_results, use_cache, min_citation_count, year_range
        )
        
        papers: Dict[str, List[PaperSource]] = {
            "google_scholar": [],
            "semantic_scholar": []
        }
        
        # Convert Google Scholar results to PaperSource objects
        for result in results["google_scholar"]:
            try:
                paper = PaperSource.from_google_scholar(result, term)
                papers["google_scholar"].append(paper)
            except Exception as e:
                logger.error(f"Error creating PaperSource from Google Scholar result: {str(e)}")
        
        # Convert Semantic Scholar results to PaperSource objects
        for result in results["semantic_scholar"]:
            try:
                paper = PaperSource.from_semantic_scholar(result, term)
                papers["semantic_scholar"].append(paper)
            except Exception as e:
                logger.error(f"Error creating PaperSource from Semantic Scholar result: {str(e)}")
        
        return papers
    
    def clear_cache(self, term: Optional[str] = None) -> None:
        """
        Clear the search cache.
        
        Args:
            term: The search term to clear, or None to clear all.
        """
        if term is not None:
            # Clear specific term
            for max_results in [10, 20, 50]:  # Common max_results values
                for min_citation_count in [None, 10, 50, 100]:  # Common min_citation_count values
                    for year_range in [None, (2010, 2023), (2015, 2023), (2020, 2023)]:  # Common year_range values
                        cache_key = f"{term}_{max_results}_{min_citation_count}_{year_range}"
                        self.cache.clear(cache_key)
        else:
            # Clear all
            self.cache.clear()
