"""
CitationFormatterTool for formatting and validating citations.

This module provides a tool for formatting citations in standard medical
citation styles and validating citation completeness.
"""

from typing import List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Model for a citation."""
    authors: str = Field(
        ...,
        description="Author names in format 'Last FM, Last FM, ...'"
    )
    title: str = Field(
        ...,
        description="Title of the article or resource"
    )
    journal: Optional[str] = Field(
        None,
        description="Journal name if applicable"
    )
    year: str = Field(
        ...,
        description="Publication year"
    )
    volume: Optional[str] = Field(
        None,
        description="Volume number if applicable"
    )
    issue: Optional[str] = Field(
        None,
        description="Issue number if applicable"
    )
    pages: Optional[str] = Field(
        None,
        description="Page range if applicable"
    )
    doi: Optional[str] = Field(
        None,
        description="DOI if available"
    )
    url: Optional[str] = Field(
        None,
        description="URL if available"
    )
    publisher: Optional[str] = Field(
        None,
        description="Publisher name for books"
    )
    accessed_date: Optional[str] = Field(
        None,
        description="Date accessed for online resources"
    )


class CitationFormatterToolInput(BaseModel):
    """Input schema for CitationFormatterTool."""
    citations: List[Citation] = Field(
        ...,
        description="List of citations to format"
    )
    style: str = Field(
        ...,
        description="Citation style (ama, apa, or vancouver)"
    )


class CitationFormatterTool(BaseTool):
    """
    Tool for formatting citations in standard medical citation styles.
    
    This tool formats citations according to standard medical citation
    styles and validates citation completeness.
    """
    
    name: str = "CitationFormatterTool"
    description: str = "Format citations in standard medical styles"
    args_schema: type[BaseModel] = CitationFormatterToolInput
    
    def _run(
        self,
        citations: List[Citation],
        style: str
    ) -> str:
        """
        Format citations in the specified style.
        
        Args:
            citations: List of citations to format
            style: Citation style (ama, apa, or vancouver)
            
        Returns:
            A string containing the formatted citations and validation results.
        """
        # Validate citations
        validation_results = self._validate_citations(citations)
        
        # Format citations
        formatted_citations = self._format_citations(citations, style)
        
        # Combine results
        result = "Citation Formatting Results:\n\n"
        result += validation_results + "\n\n"
        result += "Formatted Citations:\n\n"
        result += formatted_citations
        
        return result
    
    def _validate_citations(self, citations: List[Citation]) -> str:
        """
        Validate citations for completeness.
        
        Args:
            citations: List of citations to validate
            
        Returns:
            A string containing the validation results.
        """
        results = "Citation Validation:\n\n"
        
        if not citations:
            return results + "❌ No citations provided."
        
        incomplete_citations = []
        
        for i, citation in enumerate(citations):
            missing_fields = []
            
            # Check for required fields
            if not citation.authors:
                missing_fields.append("authors")
            if not citation.title:
                missing_fields.append("title")
            if not citation.year:
                missing_fields.append("year")
            
            # Check for journal article specific fields
            if citation.journal and not (citation.volume or citation.pages):
                missing_fields.append("volume/pages")
            
            # Check for online resource specific fields
            if citation.url and not citation.accessed_date:
                missing_fields.append("accessed_date")
            
            if missing_fields:
                incomplete_citations.append((i, missing_fields))
        
        if not incomplete_citations:
            results += "✅ All citations are complete.\n"
        else:
            results += "❌ Incomplete citations found:\n\n"
            for i, missing_fields in incomplete_citations:
                results += f"Citation {i+1} ({citations[i].title}):\n"
                results += f"  Missing: {', '.join(missing_fields)}\n\n"
        
        return results
    
    def _format_citations(
        self,
        citations: List[Citation],
        style: str
    ) -> str:
        """
        Format citations in the specified style.
        
        Args:
            citations: List of citations to format
            style: Citation style (ama, apa, or vancouver)
            
        Returns:
            A string containing the formatted citations.
        """
        style = style.lower()
        
        if style not in ["ama", "apa", "vancouver"]:
            return f"Unsupported citation style: {style}"
        
        formatter = getattr(self, f"_format_{style}")
        
        formatted_citations = []
        for i, citation in enumerate(citations):
            formatted = formatter(citation)
            formatted_citations.append(f"{i+1}. {formatted}")
        
        return "\n\n".join(formatted_citations)
    
    def _format_ama(self, citation: Citation) -> str:
        """
        Format a citation in AMA style.
        
        Args:
            citation: Citation to format
            
        Returns:
            A string containing the formatted citation.
        """
        # Authors
        result = citation.authors + "."
        
        # Title
        result += f" {citation.title}."
        
        # Journal info
        if citation.journal:
            result += f" {citation.journal}."
            
            # Year, volume, issue, pages
            if citation.year:
                result += f" {citation.year}"
                
                if citation.volume:
                    result += f";{citation.volume}"
                    
                    if citation.issue:
                        result += f"({citation.issue})"
                    
                    if citation.pages:
                        result += f":{citation.pages}"
                
                result += "."
        # Book or website
        elif citation.publisher:
            result += f" {citation.publisher}; {citation.year}."
        else:
            # Add year if not already added
            if citation.year:
                result += f" {citation.year}."
        
        # DOI or URL
        if citation.doi:
            result += f" doi:{citation.doi}"
        elif citation.url:
            result += f" {citation.url}"
            if citation.accessed_date:
                result += f". Accessed {citation.accessed_date}"
        
        return result
    
    def _format_apa(self, citation: Citation) -> str:
        """
        Format a citation in APA style.
        
        Args:
            citation: Citation to format
            
        Returns:
            A string containing the formatted citation.
        """
        # Authors
        result = citation.authors + " "
        
        # Year
        result += f"({citation.year}). "
        
        # Title
        result += f"{citation.title}. "
        
        # Journal info
        if citation.journal:
            result += f"{citation.journal}"
            
            if citation.volume:
                result += f", {citation.volume}"
                
                if citation.issue:
                    result += f"({citation.issue})"
            
            if citation.pages:
                result += f", {citation.pages}"
            
            result += "."
        # Book or website
        elif citation.publisher:
            result += f"{citation.publisher}."
        
        # DOI or URL
        if citation.doi:
            result += f" https://doi.org/{citation.doi}"
        elif citation.url:
            result += f" Retrieved from {citation.url}"
            if citation.accessed_date:
                result += f" on {citation.accessed_date}"
        
        return result
    
    def _format_vancouver(self, citation: Citation) -> str:
        """
        Format a citation in Vancouver style.
        
        Args:
            citation: Citation to format
            
        Returns:
            A string containing the formatted citation.
        """
        # Authors
        result = citation.authors + ". "
        
        # Title
        result += f"{citation.title}. "
        
        # Journal info
        if citation.journal:
            result += f"{citation.journal} "
            
            # Year, volume, issue, pages
            if citation.year:
                result += f"{citation.year}"
                
                if citation.volume:
                    result += f";{citation.volume}"
                    
                    if citation.issue:
                        result += f"({citation.issue})"
                    
                    if citation.pages:
                        result += f":{citation.pages}"
                
                result += "."
        # Book or website
        elif citation.publisher:
            result += f"{citation.publisher}; {citation.year}."
        else:
            # Add year if not already added
            if citation.year:
                result += f"{citation.year}."
        
        # DOI or URL
        if citation.doi:
            result += f" doi: {citation.doi}"
        elif citation.url:
            result += f" Available from: {citation.url}"
            if citation.accessed_date:
                result += f" [cited {citation.accessed_date}]"
        
        return result
