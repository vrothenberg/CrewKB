"""
Tests for WebpageScraperTool.

This module contains tests for the WebpageScraperTool, which scrapes
web pages using Serper's scrape API.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os

from crewkb.tools.search.webpage_scraper_tool import WebpageScraperTool


class TestWebpageScraperTool(unittest.TestCase):
    """Tests for WebpageScraperTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = WebpageScraperTool()
        self.test_url = "https://example.com/article"
        
        # Sample response data
        self.sample_response = {
            "title": "Example Medical Article",
            "markdown": "# Example Medical Article\n\n## Introduction\n\nThis is a sample medical article about diabetes.\n\n## Symptoms\n\n- Increased thirst\n- Frequent urination\n- Extreme hunger\n- Unexplained weight loss\n\n## Treatment\n\nTreatment includes insulin therapy and lifestyle changes.",
            "text": "Example Medical Article\n\nIntroduction\n\nThis is a sample medical article about diabetes.\n\nSymptoms\n\n- Increased thirst\n- Frequent urination\n- Extreme hunger\n- Unexplained weight loss\n\nTreatment\n\nTreatment includes insulin therapy and lifestyle changes.",
            "metadata": {
                "author": "Dr. Jane Smith",
                "published_date": "2024-05-01",
                "word_count": 42
            }
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
        result = self.tool._run(self.test_url, True)
        
        # Verify the request was made correctly
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "https://scrape.serper.dev")
        self.assertEqual(kwargs["headers"]["X-API-KEY"], "test_api_key")
        
        # Verify payload
        payload = json.loads(kwargs["data"])
        self.assertEqual(payload["url"], self.test_url)
        self.assertEqual(payload["includeMarkdown"], True)
        
        # Check result contains expected information
        self.assertIn(f"Scraped Content from {self.test_url}", result)
        self.assertIn("Example Medical Article", result)
        self.assertIn("Introduction", result)
        self.assertIn("diabetes", result)
        self.assertIn("Symptoms", result)
        self.assertIn("Treatment", result)
        self.assertIn("Metadata", result)
        self.assertIn("Dr. Jane Smith", result)
    
    def test_run_without_api_key(self):
        """Test _run method without an API key."""
        # Temporarily remove API key from environment
        with patch.dict(os.environ, {}, clear=True):
            result = self.tool._run(self.test_url)
            self.assertIn(
                "Error: SERPER_API_KEY environment variable not set", 
                result
            )
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_api_error(self, mock_request):
        """Test _run method with an API error."""
        # Configure the mock to raise an exception
        mock_request.side_effect = Exception("API Error")
        
        # Call the method
        result = self.tool._run(self.test_url)
        
        # Check result contains error message
        self.assertIn("Error scraping webpage", result)
        self.assertIn("API Error", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_error_response(self, mock_request):
        """Test _run method with an error in the response."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": "Failed to scrape the page"
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.tool._run(self.test_url)
        
        # Check result contains error message
        self.assertIn("Error: Failed to scrape the page", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_text_only_response(self, mock_request):
        """Test _run method with a response containing only text."""
        # Configure the mock
        response_with_text_only = {
            "title": "Example Medical Article",
            "text": "This is the text content",
            "markdown": None
        }
        mock_response = MagicMock()
        mock_response.json.return_value = response_with_text_only
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.tool._run(self.test_url)
        
        # Check result contains text content
        self.assertIn("This is the text content", result)
    
    @patch.dict(os.environ, {"SERPER_API_KEY": "test_api_key"})
    @patch("requests.request")
    def test_run_with_empty_content(self, mock_request):
        """Test _run method with a response containing no content."""
        # Configure the mock
        empty_response = {
            "title": "Example Medical Article"
        }
        mock_response = MagicMock()
        mock_response.json.return_value = empty_response
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.tool._run(self.test_url)
        
        # Check result contains no content message
        self.assertIn("No content found in the scraped page", result)


if __name__ == "__main__":
    unittest.main()
