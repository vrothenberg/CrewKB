"""
Tests for SemanticScholarTool.

This module contains tests for the SemanticScholarTool, which searches
academic papers using the Semantic Scholar API.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import json

from crewkb.tools.search.semantic_scholar_tool import SemanticScholarTool


class TestSemanticScholarTool(unittest.TestCase):
    """Tests for SemanticScholarTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = SemanticScholarTool()
        self.test_query = "diabetes treatment"
        
        # Sample search results
        self.sample_search_results = {
            "data": [
                {"paperId": "paper1"},
                {"paperId": "paper2"},
                {"paperId": "paper3"}
            ],
            "next": None
        }
        
        # Sample paper details
        self.sample_paper_details = [
            {
                "paperId": "paper1",
                "title": "Advances in Diabetes Treatment",
                "abstract": "This paper reviews recent advances in diabetes treatment.",
                "authors": [
                    {"name": "Smith, John"},
                    {"name": "Jones, Sarah"},
                    {"name": "Brown, David"}
                ],
                "year": 2023,
                "citationCount": 120,
                "publicationVenue": {
                    "name": "Journal of Diabetes Research",
                    "issn": "1234-5678"
                },
                "url": "https://example.com/paper1",
                "externalIds": {
                    "DOI": "10.1234/jdr.2023.001"
                }
            },
            {
                "paperId": "paper2",
                "title": "Novel Insulin Delivery Methods",
                "abstract": "This study examines new methods for insulin delivery.",
                "authors": [
                    {"name": "Johnson, Emily"},
                    {"name": "Williams, Robert"}
                ],
                "year": 2022,
                "citationCount": 85,
                "publicationVenue": {
                    "name": "Diabetes Care",
                    "issn": "5678-1234"
                },
                "url": "https://example.com/paper2",
                "externalIds": {
                    "DOI": "10.5678/dc.2022.002"
                }
            }
        ]
    
    @patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "test_api_key"})
    @patch.object(SemanticScholarTool, "_search_papers")
    @patch.object(SemanticScholarTool, "_get_paper_details")
    def test_run_with_valid_response(self, mock_get_details, mock_search):
        """Test _run method with a valid API response."""
        # Configure the mocks
        mock_search.return_value = self.sample_search_results
        mock_get_details.return_value = self.sample_paper_details
        
        # Call the method
        result = self.tool._run(
            self.test_query, 
            max_results=2, 
            min_citation_count=50, 
            sjr_threshold=1.0
        )
        
        # Verify the search was performed correctly
        mock_search.assert_called_once_with(
            self.test_query, "test_api_key", 2
        )
        
        # Verify paper details were retrieved
        mock_get_details.assert_called_once_with(
            ["paper1", "paper2", "paper3"], "test_api_key", self.test_query
        )
        
        # Check result contains expected information
        self.assertIn(f"Semantic Scholar Results for '{self.test_query}'", result)
        self.assertIn("Advances in Diabetes Treatment", result)
        self.assertIn("Smith, John", result)
        self.assertIn("Journal of Diabetes Research", result)
        self.assertIn("Novel Insulin Delivery Methods", result)
        self.assertIn("Citations: 85", result)
    
    def test_run_without_api_key(self):
        """Test _run method without an API key."""
        # Temporarily remove API key from environment
        with patch.dict(os.environ, {}, clear=True):
            result = self.tool._run(self.test_query)
            self.assertIn(
                "Error: SEMANTIC_SCHOLAR_API_KEY environment variable not set", 
                result
            )
    
    @patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "test_api_key"})
    @patch.object(SemanticScholarTool, "_search_papers")
    def test_run_with_no_search_results(self, mock_search):
        """Test _run method with no search results."""
        # Configure the mock
        mock_search.return_value = {"data": []}
        
        # Call the method
        result = self.tool._run(self.test_query)
        
        # Check result contains no results message
        self.assertIn(f"No paper IDs found for query: {self.test_query}", result)
    
    @patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "test_api_key"})
    @patch.object(SemanticScholarTool, "_search_papers")
    @patch.object(SemanticScholarTool, "_get_paper_details")
    def test_run_with_no_paper_details(self, mock_get_details, mock_search):
        """Test _run method with no paper details."""
        # Configure the mocks
        mock_search.return_value = self.sample_search_results
        mock_get_details.return_value = []
        
        # Call the method
        result = self.tool._run(self.test_query)
        
        # Check result contains no paper details message
        self.assertIn(
            f"No detailed paper information found for query: {self.test_query}", 
            result
        )
    
    @patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "test_api_key"})
    @patch.object(SemanticScholarTool, "_search_papers")
    @patch.object(SemanticScholarTool, "_get_paper_details")
    def test_run_with_no_filtered_papers(self, mock_get_details, mock_search):
        """Test _run method with no papers after filtering."""
        # Configure the mocks
        mock_search.return_value = self.sample_search_results
        
        # Create papers with low citation counts
        low_citation_papers = [
            {
                "paperId": "paper1",
                "title": "Low Citation Paper",
                "abstract": "This is a test paper.",
                "citationCount": 10,  # Below the threshold
                "authors": [{"name": "Test Author"}],
                "year": 2023
            }
        ]
        mock_get_details.return_value = low_citation_papers
        
        # Call the method with high citation threshold
        result = self.tool._run(
            self.test_query, min_citation_count=100
        )
        
        # Check result contains no filtered papers message
        self.assertIn(
            f"No papers found that meet the criteria (min citations: 100", 
            result
        )
    
    @patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_request_with_backoff_success(self, mock_request):
        """Test _request_with_backoff method with successful response."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.tool._request_with_backoff(
            "GET", "https://api.semanticscholar.org/test"
        )
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "https://api.semanticscholar.org/test")
        
        # Check result
        self.assertEqual(result, {"test": "data"})
    
    @patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "test_api_key"})
    @patch("requests.request")
    @patch("time.sleep")
    def test_request_with_backoff_retry(self, mock_sleep, mock_request):
        """Test _request_with_backoff method with retry."""
        # Configure the mock to fail once then succeed
        from requests.exceptions import RequestException
        
        # Create a success response
        mock_success_response = MagicMock()
        mock_success_response.json.return_value = {"test": "data"}
        
        # Set up the side effect sequence
        mock_request.side_effect = [
            RequestException("Rate limit exceeded"),
            mock_success_response
        ]
        
        # Call the method
        result = self.tool._request_with_backoff(
            "GET", "https://api.semanticscholar.org/test"
        )
        
        # Verify the request was made twice
        self.assertEqual(mock_request.call_count, 2)
        
        # Verify sleep was called
        mock_sleep.assert_called()
        
        # Check result
        self.assertEqual(result, {"test": "data"})
    
    def test_format_citation(self):
        """Test _format_citation method."""
        paper = {
            "title": "Test Paper",
            "authors": [
                {"name": "Smith, John"},
                {"name": "Jones, Sarah"}
            ],
            "year": 2023,
            "publicationVenue": {
                "name": "Test Journal"
            },
            "externalIds": {
                "DOI": "10.1234/test.2023"
            },
            "url": "https://example.com/test"
        }
        
        citation = self.tool._format_citation(paper)
        
        self.assertIn("Smith, John, Jones, Sarah", citation)
        self.assertIn('"Test Paper"', citation)
        self.assertIn("(2023)", citation)
        self.assertIn("Test Journal", citation)
        self.assertIn("DOI: 10.1234/test.2023", citation)
        self.assertIn("Available at: https://example.com/test", citation)


if __name__ == "__main__":
    unittest.main()
