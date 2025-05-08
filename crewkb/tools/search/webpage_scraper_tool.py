"""
WebpageScraperTool for scraping web pages using Serper's scrape API.

This module provides a tool for scraping web pages and extracting their content
using the Serper.dev scrape API.
"""

import os
import json
import requests
from typing import Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WebpageScraperToolInput(BaseModel):
    """Input schema for WebpageScraperTool."""
    url: str = Field(
        ...,
        description="The URL of the webpage to scrape."
    )
    include_markdown: bool = Field(
        default=True,
        description="Whether to include markdown in the response."
    )


class WebpageScraperTool(BaseTool):
    """
    Tool for scraping web pages using Serper's scrape API.
    
    This tool allows agents to scrape web pages and extract their content,
    which is particularly useful for retrieving full text of academic papers
    and other research materials.
    """
    
    name: str = "WebpageScraperTool"
    description: str = "Scrape a webpage to extract its full content"
    args_schema: type[BaseModel] = WebpageScraperToolInput
    
    def _run(
        self,
        url: str,
        include_markdown: bool = True
    ) -> str:
        """
        Scrape a webpage and extract its content.
        
        Args:
            url: The URL of the webpage to scrape.
            include_markdown: Whether to include markdown in the response.
            
        Returns:
            A string containing the scraped content.
            
        Raises:
            Exception: If the API request fails.
        """
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY environment variable not set"
        
        scrape_url = "https://scrape.serper.dev"
        payload = json.dumps({
            "url": url,
            "includeMarkdown": include_markdown
        })
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request(
                "POST", scrape_url, headers=headers, data=payload
            )
            response.raise_for_status()
            scrape_result = response.json()
            
            # Format and return the result
            return self._format_result(scrape_result, url)
        except Exception as e:
            return f"Error scraping webpage: {str(e)}"
    
    def _format_result(self, result: Dict[str, Any], url: str) -> str:
        """
        Format the scrape result.
        
        Args:
            result: The raw scrape result from the API.
            url: The URL that was scraped.
            
        Returns:
            A formatted string with the scraped content.
        """
        formatted = f"Scraped Content from {url}\n"
        formatted += "=" * 80 + "\n\n"
        
        # Check if the scrape was successful
        if "error" in result:
            return formatted + f"Error: {result['error']}"
        
        # Extract title if available
        if "title" in result:
            formatted += f"Title: {result['title']}\n\n"
        
        # Use markdown content if available, otherwise use text content
        if "markdown" in result and result["markdown"]:
            content = result["markdown"]
        elif "text" in result and result["text"]:
            content = result["text"]
        else:
            return formatted + "No content found in the scraped page."
        
        # Add the content
        formatted += content
        
        # Add metadata if available
        if "metadata" in result and result["metadata"]:
            formatted += "\n\nMetadata:\n"
            for key, value in result["metadata"].items():
                formatted += f"{key}: {value}\n"
        
        return formatted
