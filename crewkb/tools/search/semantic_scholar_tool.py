"""
SemanticScholarTool for searching academic papers using the Semantic Scholar API.

This module provides a tool for searching academic papers with semantic understanding,
filtering by journal quality and citation count, and retrieving detailed paper information.
"""

import os
import json
import time
import random
import logging
import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SemanticScholarToolInput(BaseModel):
    """Input schema for SemanticScholarTool."""
    query: str = Field(..., description="The search query to perform.")
    max_results: int = Field(
        default=10,
        description="The maximum number of results to return."
    )
    min_citation_count: int = Field(
        default=50,
        description="The minimum citation count for papers to include."
    )
    sjr_threshold: float = Field(
        default=1.0,
        description="The minimum SJR score for journals to include."
    )
    sort_by: str = Field(
        default="relevance",
        description="How to sort results (relevance, citation_count)."
    )


class SemanticScholarTool(BaseTool):
    """
    Tool for searching academic papers using the Semantic Scholar API.
    
    This tool allows agents to search for academic papers with semantic understanding,
    filter by journal quality and citation count, and retrieve detailed paper information.
    It can be used to find high-quality research papers on a given topic.
    """
    
    name: str = "SemanticScholarTool"
    description: str = "Search Semantic Scholar for academic papers with quality filtering"
    args_schema: type[BaseModel] = SemanticScholarToolInput
    
    def __init__(self):
        """Initialize the SemanticScholarTool."""
        super().__init__()
        self._sjr_map = {}  # ISSN -> {"sjr": float, "h_index": float}
        self._last_request_time = 0
        self._min_delay = 1.0  # Minimum time (in seconds) between requests
        self._max_retries = 5
        
        # Load SJR data if available
        journals_path = os.getenv("JOURNALS_CSV_PATH")
        if journals_path and os.path.exists(journals_path):
            self.load_journal_sjr_data(journals_path)
    
    def load_journal_sjr_data(self, csv_path: str) -> None:
        """
        Load a CSV file of journals and parse out SJR/H-Index info keyed by ISSN.
        
        Args:
            csv_path: Path to the CSV file containing journal data.
        """
        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                sjr = row.get("SJR")
                h_index = row.get("H index")
                
                # Some rows may have multiple ISSNs
                for col in ["Issn1", "Issn2"]:
                    issn_vals = row.get(col, "")
                    if isinstance(issn_vals, str):
                        for issn_raw in issn_vals.split(","):
                            issn_clean = issn_raw.replace("-", "").strip()
                            if issn_clean and pd.notnull(sjr):
                                self._sjr_map[issn_clean] = {
                                    "sjr": float(sjr),
                                    "h_index": float(h_index) if pd.notnull(h_index) else None,
                                }
            logging.info(f"Loaded SJR data for {len(self._sjr_map)} journals")
        except Exception as e:
            logging.error(f"Error loading journal SJR data: {str(e)}")
    
    def _run(
        self,
        query: str,
        max_results: int = 10,
        min_citation_count: int = 50,
        sjr_threshold: float = 1.0,
        sort_by: str = "relevance"
    ) -> str:
        """
        Run the Semantic Scholar search.
        
        Args:
            query: The search query to perform.
            max_results: The maximum number of results to return.
            min_citation_count: The minimum citation count for papers to include.
            sjr_threshold: The minimum SJR score for journals to include.
            sort_by: How to sort results (relevance, citation_count).
            
        Returns:
            A string containing the search results.
            
        Raises:
            Exception: If the API request fails.
        """
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        if not api_key:
            return "Error: SEMANTIC_SCHOLAR_API_KEY environment variable not set"
        
        try:
            # Step 1: Search for papers
            search_results = self._search_papers(query, api_key, max_results)
            if not search_results or "data" not in search_results:
                return f"No results found for query: {query}"
            
            paper_ids = [paper.get("paperId") for paper in search_results.get("data", [])]
            if not paper_ids:
                return f"No paper IDs found for query: {query}"
            
            # Step 2: Get detailed paper information
            papers = self._get_paper_details(paper_ids, api_key, query)
            if not papers:
                return f"No detailed paper information found for query: {query}"
            
            # Step 3: Filter papers by citation count and journal quality
            filtered_papers = self._filter_papers(
                papers, min_citation_count, sjr_threshold
            )
            if not filtered_papers:
                return (
                    f"No papers found that meet the criteria (min citations: {min_citation_count}, "
                    f"min SJR: {sjr_threshold}) for query: {query}"
                )
            
            # Step 4: Sort papers
            sorted_papers = self._sort_papers(filtered_papers, sort_by)
            
            # Step 5: Format and return results
            return self._format_results(sorted_papers[:max_results], query)
        
        except Exception as e:
            return f"Error performing Semantic Scholar search: {str(e)}"
    
    def _search_papers(self, query: str, api_key: str, limit: int) -> Dict[str, Any]:
        """
        Search for papers using the Semantic Scholar API.
        
        Args:
            query: The search query.
            api_key: The Semantic Scholar API key.
            limit: The maximum number of results to return.
            
        Returns:
            The search results.
        """
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": min(limit * 2, 100),  # Get more results than needed for filtering
            "fields": "paperId"
        }
        headers = {"x-api-key": api_key}
        
        return self._request_with_backoff("GET", url, headers=headers, params=params)
    
    def _get_paper_details(
        self, paper_ids: List[str], api_key: str, query: str
    ) -> List[Dict[str, Any]]:
        """
        Get detailed information for papers using the Semantic Scholar batch API.
        
        Args:
            paper_ids: List of paper IDs.
            api_key: The Semantic Scholar API key.
            query: The original search query.
            
        Returns:
            List of paper details.
        """
        url = "https://api.semanticscholar.org/graph/v1/paper/batch"
        headers = {"x-api-key": api_key}
        fields = (
            "title,abstract,authors,citationCount,referenceCount,"
            "url,venue,publicationVenue,year,openAccessPdf,externalIds"
        )
        params = {"fields": fields}
        
        # Process in batches of 20 to avoid API limits
        all_papers = []
        for i in range(0, len(paper_ids), 20):
            batch_ids = paper_ids[i:i+20]
            payload = {"ids": batch_ids}
            
            response_data = self._request_with_backoff(
                "POST", url, headers=headers, params=params, json=payload
            )
            
            if response_data:
                # Add the query to each paper for context
                for paper in response_data:
                    if paper:
                        paper["query"] = query
                all_papers.extend([p for p in response_data if p])
            
            # Sleep between batches to respect rate limits
            time.sleep(1)
        
        return all_papers
    
    def _filter_papers(
        self, papers: List[Dict[str, Any]], min_citation_count: int, sjr_threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Filter papers by citation count and journal quality.
        
        Args:
            papers: List of papers to filter.
            min_citation_count: Minimum citation count.
            sjr_threshold: Minimum SJR score.
            
        Returns:
            Filtered list of papers.
        """
        filtered_papers = []
        
        for paper in papers:
            # Skip papers without required fields
            if not paper or "title" not in paper or "abstract" not in paper:
                continue
            
            # Check citation count
            citation_count = paper.get("citationCount", 0)
            if citation_count < min_citation_count:
                continue
            
            # Check journal quality if SJR data is available
            pub_venue = paper.get("publicationVenue", {})
            if pub_venue and self._sjr_map:
                issn = pub_venue.get("issn", "")
                issn_clean = issn.replace("-", "").strip()
                
                if issn_clean in self._sjr_map:
                    sjr_info = self._sjr_map[issn_clean]
                    sjr = sjr_info.get("sjr")
                    
                    if sjr is not None and sjr > sjr_threshold:
                        # Add SJR info to the paper
                        paper["publicationVenue"]["SJR"] = sjr
                        filtered_papers.append(paper)
                else:
                    # If we don't have SJR data for this journal, include it anyway
                    # if it meets the citation count threshold
                    filtered_papers.append(paper)
            else:
                # If we don't have publication venue info or SJR data,
                # include it if it meets the citation count threshold
                filtered_papers.append(paper)
        
        return filtered_papers
    
    def _sort_papers(
        self, papers: List[Dict[str, Any]], sort_by: str
    ) -> List[Dict[str, Any]]:
        """
        Sort papers by the specified criterion.
        
        Args:
            papers: List of papers to sort.
            sort_by: Criterion to sort by (relevance, citation_count).
            
        Returns:
            Sorted list of papers.
        """
        if sort_by == "citation_count":
            return sorted(
                papers, key=lambda p: p.get("citationCount", 0), reverse=True
            )
        else:
            # Default to relevance (as returned by the API)
            return papers
    
    def _format_results(
        self, papers: List[Dict[str, Any]], query: str
    ) -> str:
        """
        Format the search results.
        
        Args:
            papers: List of papers to format.
            query: The original search query.
            
        Returns:
            Formatted string with results.
        """
        formatted = f"Semantic Scholar Results for '{query}':\n\n"
        
        if not papers:
            return formatted + "No results found."
        
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "No Title")
            authors = paper.get("authors", [])
            author_names = [a.get("name", "") for a in authors[:3]]
            if len(authors) > 3:
                author_names.append("et al.")
            author_str = ", ".join(author_names)
            
            year = paper.get("year", "Unknown Year")
            citation_count = paper.get("citationCount", 0)
            
            venue = "Unknown Venue"
            sjr = None
            pub_venue = paper.get("publicationVenue", {})
            if pub_venue:
                venue = pub_venue.get("name", venue)
                sjr = pub_venue.get("SJR")
            
            url = paper.get("url", "")
            doi = paper.get("externalIds", {}).get("DOI", "")
            
            abstract = paper.get("abstract", "No abstract available.")
            if len(abstract) > 300:
                abstract = abstract[:300] + "..."
            
            formatted += f"{i}. {title}\n"
            formatted += f"   Authors: {author_str}\n"
            formatted += f"   Year: {year}\n"
            formatted += f"   Citations: {citation_count}\n"
            formatted += f"   Venue: {venue}"
            if sjr:
                formatted += f" (SJR: {sjr:.2f})"
            formatted += "\n"
            
            if url:
                formatted += f"   URL: {url}\n"
            if doi:
                formatted += f"   DOI: {doi}\n"
            
            formatted += f"   Abstract: {abstract}\n"
            
            # Add formatted citation
            formatted += f"   Citation: {self._format_citation(paper)}\n\n"
        
        return formatted
    
    def _format_citation(self, paper: Dict[str, Any]) -> str:
        """
        Format the citation for a paper.
        
        Args:
            paper: The paper metadata.
            
        Returns:
            Formatted citation.
        """
        authors = paper.get("authors", [])
        author_names = [a.get("name", "") for a in authors[:3]]
        if len(authors) > 3:
            author_names.append("et al.")
        author_str = ", ".join(author_names)
        
        title = paper.get("title", "Unknown Title")
        year = paper.get("year", "Unknown Year")
        
        venue = "Unknown Venue"
        pub_venue = paper.get("publicationVenue", {})
        if pub_venue:
            venue = pub_venue.get("name", venue)
        
        doi = paper.get("externalIds", {}).get("DOI", "")
        url = paper.get("url", "")
        
        citation = f'{author_str}. "{title}" ({year}). {venue}.'
        
        if doi:
            citation += f" DOI: {doi}."
        if url:
            citation += f" Available at: {url}."
        
        return citation
    
    def _request_with_backoff(
        self, method: str, url: str, **kwargs
    ) -> Any:
        """
        Perform an HTTP request with exponential backoff.
        
        Args:
            method: The HTTP method (GET, POST, etc.).
            url: The URL for the request.
            **kwargs: Additional parameters for the request.
            
        Returns:
            The JSON response data or None if the request ultimately fails.
        """
        for attempt in range(self._max_retries):
            try:
                # Enforce rate limiting
                now = time.time()
                elapsed = now - self._last_request_time
                if elapsed < self._min_delay:
                    time.sleep(self._min_delay - elapsed)
                self._last_request_time = time.time()
                
                # Perform the request
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            
            except requests.RequestException as e:
                logging.warning(f"Request error: {e}")
                
                # Check for rate limiting response
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 429:  # Too Many Requests
                        logging.warning("Rate limit hit, backing off")
                    elif e.response.status_code == 403:  # Forbidden
                        logging.error("API key invalid or unauthorized")
                        break
                
                # Exponential backoff with jitter
                delay = (2 ** attempt) + random.uniform(0, 1)
                logging.warning(
                    f"Retrying in {delay:.2f} seconds... "
                    f"(Attempt {attempt + 1}/{self._max_retries})"
                )
                time.sleep(delay)
        
        logging.error(f"Max retries reached for {url}. Giving up.")
        return None
