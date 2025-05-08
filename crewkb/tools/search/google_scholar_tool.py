"""
GoogleScholarTool for searching academic literature using Serper's Google Scholar API.

This module provides a tool for searching academic literature using the Serper.dev
Google Scholar API endpoint, which returns structured results from Google Scholar.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GoogleScholarToolInput(BaseModel):
    """Input schema for GoogleScholarTool."""
    query: str = Field(..., description="The search query to perform.")
    num_results: int = Field(
        default=5,
        description="The number of search results to return."
    )


class GoogleScholarTool(BaseTool):
    """
    Tool for searching academic literature using Serper's Google Scholar API.
    
    This tool allows agents to search for academic papers and research on a given topic.
    It uses the Serper.dev Google Scholar API endpoint, which provides structured
    results from Google Scholar.
    """
    
    name: str = "GoogleScholarTool"
    description: str = "Search Google Scholar for academic papers and research"
    args_schema: type[BaseModel] = GoogleScholarToolInput
    
    def _run(
        self,
        query: str,
        num_results: int = 5
    ) -> str:
        """
        Run the Google Scholar search.
        
        Args:
            query: The search query to perform.
            num_results: The number of search results to return.
            
        Returns:
            A string containing the search results.
            
        Raises:
            Exception: If the API request fails.
        """
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY environment variable not set"
        
        url = "https://google.serper.dev/scholar"
        payload = json.dumps({
            "q": query,
            "num": num_results
        })
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload
            )
            response.raise_for_status()
            search_results = response.json()
            
            # Format results
            formatted_results = self._format_results(
                search_results, num_results
            )
            return formatted_results
        except Exception as e:
            return f"Error performing Google Scholar search: {str(e)}"
    
    def _format_results(self, results: Dict[str, Any], num_results: int) -> str:
        """
        Format the search results.
        
        Args:
            results: The raw search results from the API.
            num_results: The number of results to include.
            
        Returns:
            A formatted string with results.
        """
        formatted = "Google Scholar Results:\n\n"
        
        # Check if organic results exist
        if "organic" not in results or not results["organic"]:
            return formatted + "No results found."
        
        # Add organic results
        for i, result in enumerate(results["organic"][:num_results], 1):
            title = result.get("title", "No Title")
            link = result.get("link", "No Link")
            publication = result.get("publication", "")
            authors = result.get("authors", "")
            year = result.get("year", "")
            cited_by = result.get("cited_by", {}).get("value", "")
            snippet = result.get("snippet", "No Abstract")
            
            formatted += f"{i}. {title}\n"
            
            if authors:
                formatted += f"   Authors: {authors}\n"
            
            if publication:
                formatted += f"   Publication: {publication}"
                if year:
                    formatted += f" ({year})"
                formatted += "\n"
            elif year:
                formatted += f"   Year: {year}\n"
            
            if cited_by:
                formatted += f"   Cited by: {cited_by}\n"
            
            formatted += f"   URL: {link}\n"
            formatted += f"   Abstract: {snippet}\n\n"
        
        return formatted
