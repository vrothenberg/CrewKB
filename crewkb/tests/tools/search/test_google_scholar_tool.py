"""
Tests for GoogleScholarTool.

This module contains tests for the GoogleScholarTool, which searches
academic literature using Serper's Google Scholar API endpoint.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os

from crewkb.tools.search.google_scholar_tool import GoogleScholarTool


class TestGoogleScholarTool(unittest.TestCase):
    """Tests for GoogleScholarTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = GoogleScholarTool()
        
        # Sample response data
        self.sample_response = {
            "organic": [
                {
                    "title": "Role of ChatGPT in public health",
                    "link": "https://link.springer.com/article/10.1007/s10439-023-03172-7",
                    "publication": "Journal of Medical Systems",
                    "authors": "A Smith, B Jones, C Wilson",
                    "year": "2023",
                    "cited_by": {"value": "42"},
                    "snippet": "ChatGPT in public health. In this overview, we will examine the potential uses of ChatGPT in"
                },
                {
                    "title": "Potential use of ChatGPT in global warming",
                    "link": "https://link.springer.com/article/10.1007/s10439-023-03171-8",
                    "publication": "Environmental Science",
                    "authors": "D Brown, E Green",
                    "year": "2024",
                    "cited_by": {"value": "15"},
                    "snippet": "as ChatGPT, have the potential to play a critical role in advancing our understanding of climate"
                }
            ]
        }
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_valid_response(self, mock_request):
        """Test _run method with a valid API response."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_response
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.tool._run("ChatGPT", 2)
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "https://google.serper.dev/scholar")
        self.assertEqual(kwargs["headers"]["X-API-KEY"], "test_api_key")
        
        # Verify payload
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["q"], "ChatGPT")
        self.assertEqual(payload["num"], 2)
        
        # Check result contains expected information
        self.assertIn("Google Scholar Results:", result)
        self.assertIn("Role of ChatGPT in public health", result)
        self.assertIn("Potential use of ChatGPT in global warming", result)
        self.assertIn("Journal of Medical Systems", result)
        self.assertIn("2023", result)
        self.assertIn("Cited by: 42", result)
    
    def test_run_without_api_key(self):
        """Test _run method without an API key."""
        # Temporarily remove API key from environment
        with patch.dict(os.environ, {}, clear=True):
            result = self.tool._run("ChatGPT", 2)
            self.assertIn("Error: SERPER_API_KEY environment variable not set", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_api_error(self, mock_request):
        """Test _run method with an API error."""
        # Configure the mock to raise an exception
        mock_request.side_effect = Exception("API Error")
        
        # Call the method
        result = self.tool._run("ChatGPT", 2)
        
        # Check result contains error message
        self.assertIn("Error performing Google Scholar search", result)
        self.assertIn("API Error", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_empty_response(self, mock_request):
        """Test _run method with an empty response."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.tool._run("ChatGPT", 2)
        
        # Check result contains no results message
        self.assertIn("No results found", result)


if __name__ == "__main__":
    unittest.main()
