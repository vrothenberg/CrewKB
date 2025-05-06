"""
SerperDevTool for performing web searches using the SerperDev API.

This module provides a tool for searching the web using the SerperDev API,
which provides Google search results in a structured format.
"""

import os
import json
import requests
from typing import Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class SerperDevToolInput(BaseModel):
    """Input schema for SerperDevTool."""
    query: str = Field(..., description="The search query to perform.")
    num_results: int = Field(
        default=10,
        description="The number of search results to return."
    )
    search_type: str = Field(
        default="search",
        description="The type of search to perform (search, news, etc.)"
    )


class SerperDevTool(BaseTool):
    """
    Tool for performing web searches using the SerperDev API.
    
    This tool allows agents to search the web for information on a given topic.
    It uses the SerperDev API, which provides Google search results in a
    structured format.
    """
    
    name: str = "SerperDevTool"
    description: str = "Search the web for information on a given topic"
    args_schema: type[BaseModel] = SerperDevToolInput
    
    def _run(
        self,
        query: str,
        num_results: int = 10,
        search_type: str = "search"
    ) -> str:
        """
        Run the SerperDev search.
        
        Args:
            query: The search query to perform.
            num_results: The number of search results to return.
            search_type: The type of search to perform (search, news, etc.)
            
        Returns:
            A string containing the search results.
            
        Raises:
            Exception: If the API request fails.
        """
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY environment variable not set"
        
        url = "https://google.serper.dev/search"
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
            return f"Error performing search: {str(e)}"
    
    def _format_results(self, results: Dict[str, Any], num_results: int) -> str:
        """
        Format the search results.
        
        Args:
            results: The raw search results from the API.
            num_results: The number of results to include.
            
        Returns:
            A formatted string with results.
        """
        formatted = "Search Results:\n\n"
        
        # Add organic results
        if "organic" in results:
            for i, result in enumerate(results["organic"][:num_results], 1):
                title = result.get("title", "No Title")
                link = result.get("link", "No Link")
                snippet = result.get("snippet", "No Snippet")
                
                formatted += f"{i}. {title}\n"
                formatted += f"   URL: {link}\n"
                formatted += f"   Snippet: {snippet}\n\n"
        
        # Add knowledge graph if available
        if "knowledgeGraph" in results:
            kg = results["knowledgeGraph"]
            formatted += "Knowledge Graph:\n"
            formatted += f"Title: {kg.get('title', 'N/A')}\n"
            formatted += f"Type: {kg.get('type', 'N/A')}\n"
            if "description" in kg:
                formatted += f"Description: {kg['description']}\n"
            formatted += "\n"
        
        # Add related searches if available
        if "relatedSearches" in results:
            formatted += "Related Searches:\n"
            for i, search in enumerate(results["relatedSearches"][:5], 1):
                formatted += f"{i}. {search.get('query', 'N/A')}\n"
        
        return formatted
