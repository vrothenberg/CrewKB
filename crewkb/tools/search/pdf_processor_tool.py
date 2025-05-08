"""
PDF Processor Tool for CrewKB.

This module provides a tool for downloading and processing PDFs from URLs.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool

from crewkb.utils.pdf import PDFProcessor
from crewkb.models.knowledge.paper import PaperSource

# Set up logging
logger = logging.getLogger(__name__)


class PDFProcessorTool(BaseTool):
    """
    Tool for downloading and processing PDFs from URLs.
    
    This tool uses the PDFProcessor to download PDFs, parse them to markdown,
    and extract sections from the markdown.
    """
    
    name = "pdf_processor"
    description = """
    Use this tool to download and process PDFs from URLs. The tool will:
    1. Download the PDF from the provided URL
    2. Parse the PDF to markdown format
    3. Extract sections from the markdown
    4. Return the extracted content
    
    Input should be a JSON object with the following fields:
    - paper: A dictionary containing paper metadata (title, authors, year, etc.)
    - output_dir: (Optional) Directory to save the processed PDF
    
    Example input:
    {
        "paper": {
            "title": "Advances in Diabetes Treatment",
            "authors": ["Smith, J.", "Johnson, A."],
            "year": 2023,
            "journal": "Journal of Diabetes Research",
            "url": "https://example.com/paper",
            "pdf_url": "https://example.com/paper.pdf",
            "abstract": "This paper discusses recent advances in diabetes treatment."
        },
        "output_dir": "output/diabetes"
    }
    """
    
    def __init__(self, **kwargs):
        """Initialize the PDFProcessorTool."""
        super().__init__(**kwargs)
        self.pdf_processor = PDFProcessor(
            cache_dir="cache/pdf_processor",
            use_llm=True  # Use Gemini for improved accuracy
        )
    
    def _run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the tool synchronously.
        
        Args:
            input_data: A dictionary containing the input data
            
        Returns:
            A dictionary containing the processed PDF data
        """
        # Run the async method in a new event loop
        return asyncio.run(self._arun(input_data))
    
    async def _arun(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the tool asynchronously.
        
        Args:
            input_data: A dictionary containing the input data
            
        Returns:
            A dictionary containing the processed PDF data
        """
        # Extract input data
        paper_data = input_data.get("paper", {})
        output_dir = input_data.get("output_dir")
        
        # Create a PaperSource object
        try:
            # Add required fields if not present
            if "source_tool" not in paper_data:
                paper_data["source_tool"] = "pdf_processor_tool"
            if "search_term" not in paper_data:
                paper_data["search_term"] = paper_data.get("title", "")
            
            paper = PaperSource(**paper_data)
        except Exception as e:
            return {
                "error": f"Failed to create PaperSource: {str(e)}",
                "success": False
            }
        
        # Process the paper
        try:
            markdown_path, sections = await self.pdf_processor.process_paper(
                paper,
                output_dir=output_dir
            )
            
            if not markdown_path or not sections:
                return {
                    "error": "Failed to process PDF",
                    "success": False
                }
            
            # Read the markdown content
            with open(markdown_path, "r") as f:
                markdown_content = f.read()
            
            # Return the results
            return {
                "success": True,
                "paper_id": paper.paper_id,
                "title": paper.title,
                "markdown_path": markdown_path,
                "markdown_content": markdown_content,
                "sections": sections
            }
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            return {
                "error": f"Failed to process PDF: {str(e)}",
                "success": False
            }
    
    async def process_papers(
        self,
        papers: List[Dict[str, Any]],
        output_dir: Optional[str] = None,
        max_concurrent: int = 3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Process multiple papers in parallel.
        
        Args:
            papers: A list of dictionaries containing paper metadata
            output_dir: Directory to save the processed PDFs
            max_concurrent: Maximum number of papers to process concurrently
            
        Returns:
            A dictionary mapping paper IDs to processing results
        """
        # Create PaperSource objects
        paper_sources = []
        for paper_data in papers:
            try:
                # Add required fields if not present
                if "source_tool" not in paper_data:
                    paper_data["source_tool"] = "pdf_processor_tool"
                if "search_term" not in paper_data:
                    paper_data["search_term"] = paper_data.get("title", "")
                
                paper = PaperSource(**paper_data)
                paper_sources.append(paper)
            except Exception as e:
                logger.error(f"Failed to create PaperSource: {str(e)}")
        
        # Process the papers
        results = await self.pdf_processor.process_papers(
            paper_sources,
            output_dir=output_dir,
            max_concurrent=max_concurrent
        )
        
        # Format the results
        formatted_results = {}
        for paper_id, (markdown_path, sections) in results.items():
            if not markdown_path or not sections:
                formatted_results[paper_id] = {
                    "error": "Failed to process PDF",
                    "success": False
                }
                continue
            
            # Read the markdown content
            try:
                with open(markdown_path, "r") as f:
                    markdown_content = f.read()
                
                # Find the corresponding paper
                paper = next((p for p in paper_sources if p.paper_id == paper_id), None)
                
                # Return the results
                formatted_results[paper_id] = {
                    "success": True,
                    "paper_id": paper_id,
                    "title": paper.title if paper else "",
                    "markdown_path": markdown_path,
                    "markdown_content": markdown_content,
                    "sections": sections
                }
            except Exception as e:
                logger.error(f"Error reading markdown: {str(e)}")
                formatted_results[paper_id] = {
                    "error": f"Failed to read markdown: {str(e)}",
                    "success": False
                }
        
        return formatted_results
