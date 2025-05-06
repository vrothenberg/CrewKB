"""
PubMedSearchTool for searching medical literature on PubMed.

This module provides a tool for searching PubMed for medical literature
using the Entrez API from the Bio package.
"""

import os
from typing import List, Dict, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

try:
    from Bio import Entrez
except ImportError:
    Entrez = None


class PubMedSearchToolInput(BaseModel):
    """Input schema for PubMedSearchTool."""
    query: str = Field(..., description="The search query to perform.")
    max_results: int = Field(
        default=10,
        description="The maximum number of results to return."
    )
    sort: str = Field(
        default="relevance",
        description="How to sort results (relevance, date)."
    )


class PubMedSearchTool(BaseTool):
    """
    Tool for searching medical literature on PubMed.
    
    This tool allows agents to search for medical literature on PubMed
    using the Entrez API from the Bio package.
    """
    
    name: str = "PubMedSearchTool"
    description: str = "Search PubMed for medical literature"
    args_schema: type[BaseModel] = PubMedSearchToolInput
    
    def _run(
        self,
        query: str,
        max_results: int = 10,
        sort: str = "relevance"
    ) -> str:
        """
        Run the PubMed search.
        
        Args:
            query: The search query to perform.
            max_results: The maximum number of results to return.
            sort: How to sort results (relevance, date).
            
        Returns:
            A string containing the search results.
            
        Raises:
            Exception: If the API request fails.
        """
        if Entrez is None:
            return (
                "Error: Biopython package not installed. "
                "Please install it with 'pip install biopython'."
            )
        
        email = os.getenv("ENTREZ_EMAIL")
        if not email:
            return (
                "Error: ENTREZ_EMAIL environment variable not set. "
                "Please set it to your email address."
            )
        
        Entrez.email = email
        api_key = os.getenv("ENTREZ_API_KEY")
        if api_key:
            Entrez.api_key = api_key
        
        try:
            # Search for articles
            sort_method = "relevance" if sort == "relevance" else "pub date"
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort=sort_method
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()
            
            id_list = search_results["IdList"]
            if not id_list:
                return f"No results found for query: {query}"
            
            # Fetch article details
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                retmode="xml"
            )
            articles = Entrez.read(fetch_handle)["PubmedArticle"]
            fetch_handle.close()
            
            # Format the results
            return self._format_results(articles)
        except Exception as e:
            return f"Error performing PubMed search: {str(e)}"
    
    def _format_results(self, articles: List[Dict[str, Any]]) -> str:
        """
        Format the PubMed search results.
        
        Args:
            articles: The list of article data from PubMed.
            
        Returns:
            A formatted string with results.
        """
        formatted = "PubMed Search Results:\n\n"
        
        for i, article in enumerate(articles, 1):
            article_data = article["MedlineCitation"]
            article_info = article_data["Article"]
            
            # Extract title
            title = article_info.get("ArticleTitle", "No Title")
            
            # Extract authors
            authors = []
            if "AuthorList" in article_info:
                for author in article_info["AuthorList"]:
                    if "LastName" in author and "ForeName" in author:
                        authors.append(
                            f"{author['LastName']} {author['ForeName'][0]}"
                        )
            author_str = ", ".join(authors) if authors else "No Authors"
            
            # Extract journal and date
            journal = article_info.get("Journal", {})
            journal_title = journal.get("Title", "No Journal")
            
            pub_date = "No Date"
            if "PubDate" in journal.get("JournalIssue", {}).get("PubDate", {}):
                pub_date_info = journal["JournalIssue"]["PubDate"]
                if "Year" in pub_date_info:
                    pub_date = pub_date_info["Year"]
                    if "Month" in pub_date_info:
                        pub_date = f"{pub_date_info['Month']} {pub_date}"
            
            # Extract abstract
            abstract = "No Abstract"
            if "Abstract" in article_info:
                abstract_parts = article_info["Abstract"].get(
                    "AbstractText", []
                )
                if abstract_parts:
                    if isinstance(abstract_parts, list):
                        abstract = " ".join(
                            str(part) for part in abstract_parts
                        )
                    else:
                        abstract = str(abstract_parts)
            
            # Extract PMID
            pmid = article_data["PMID"].get("#text", "No PMID")
            
            # Format the article information
            formatted += f"{i}. {title}\n"
            formatted += f"   Authors: {author_str}\n"
            formatted += f"   Journal: {journal_title}, {pub_date}\n"
            formatted += f"   PMID: {pmid}\n"
            formatted += f"   Abstract: {abstract[:200]}...\n\n"
        
        return formatted
