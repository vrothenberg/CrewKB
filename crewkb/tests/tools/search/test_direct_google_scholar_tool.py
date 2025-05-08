"""
Tests for DirectGoogleScholarTool.

This module contains tests for the DirectGoogleScholarTool, which searches
Google Scholar directly without using an API.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import json
from pathlib import Path
import asyncio

from crewkb.tools.search.direct_google_scholar_tool import DirectGoogleScholarTool


class TestDirectGoogleScholarTool(unittest.TestCase):
    """Tests for DirectGoogleScholarTool."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = DirectGoogleScholarTool()

        # Sample extracted content
        self.sample_extracted_content = json.dumps([
            {
                "title": "Role of AI in public health",
                "link": "https://example.com/article1",
                "publicationInfo": "A Smith, B Jones - Journal of AI, 2023",
                "snippet": "AI in public health. In this overview, we will examine the potential uses of AI in",
                "citedByText": "Cited by 42",
                "citedByUrl": "https://scholar.google.com/scholar?cites=123456",
                "relatedArticlesUrl": "https://scholar.google.com/scholar?related=123456",
                "allVersionsUrl": "https://scholar.google.com/scholar?cluster=123456"
            },
            {
                "title": "Potential use of AI in global warming",
                "link": "https://example.com/article2",
                "publicationInfo": "D Brown, E Green - Environmental Science, 2024",
                "snippet": "as AI, have the potential to play a critical role in advancing our understanding of climate",
                "citedByText": "Cited by 15",
                "citedByUrl": "https://scholar.google.com/scholar?cites=789012",
                "relatedArticlesUrl": "https://scholar.google.com/scholar?related=789012",
                "allVersionsUrl": "https://scholar.google.com/scholar?cluster=789012"
            }
        ])

        # Sample PDF links
        self.sample_pdf_links = json.dumps([
            {
                "pdfUrl": "https://example.com/article1.pdf",
                "source": "[PDF] example.com"
            },
            {
                "pdfUrl": "https://example.com/article2.pdf",
                "source": "[PDF] example.com"
            }
        ])

        # Sample related searches
        self.sample_related_searches = json.dumps([
            {"search_term": "AI in healthcare"},
            {"search_term": "AI ethics"}
        ])

        # Create a mock AsyncWebCrawler result
        self.mock_result = MagicMock()
        self.mock_result.success = True
        self.mock_result.extracted_content = self.sample_extracted_content
        self.mock_result.html = "<html><body>Sample HTML</body></html>"

        # Create a mock PDF links result
        self.mock_pdf_result = MagicMock()
        self.mock_pdf_result.success = True
        self.mock_pdf_result.extracted_content = self.sample_pdf_links

        # Create a mock related searches result
        self.mock_related_searches_result = MagicMock()
        self.mock_related_searches_result.success = True
        self.mock_related_searches_result.extracted_content = self.sample_related_searches

    @patch("asyncio.run")
    def test_run_delegates_to_async_run(self, mock_asyncio_run):
        """Test that _run delegates to _async_run."""
        # Configure the mock
        mock_asyncio_run.return_value = "test result"

        # Call the method
        result = self.tool._run("AI", 2020, False, 10, 0, 1.0, 3, True, False)

        # Verify asyncio.run was called
        mock_asyncio_run.assert_called_once()
        
        # Close the coroutine passed to the mock to prevent RuntimeWarning
        # The first argument to asyncio.run is the coroutine.
        args, _ = mock_asyncio_run.call_args
        if args and hasattr(args[0], 'close'):
            args[0].close()
            
        self.assertEqual(result, "test result")

    @patch("crewkb.tools.search.direct_google_scholar_tool.AsyncWebCrawler")
    @patch("crewkb.tools.search.direct_google_scholar_tool.BeautifulSoup")
    @patch.object(DirectGoogleScholarTool, "_check_cache")
    @patch.object(DirectGoogleScholarTool, "_cache_result")
    @patch.object(DirectGoogleScholarTool, "_save_results_to_file")
    def test_async_run_with_successful_extraction(
        self, mock_save, mock_cache, mock_check_cache, mock_bs, mock_crawler_class
    ):
        """Test _async_run method with successful extraction."""
        # Configure the mocks
        mock_check_cache.return_value = None  # No cached result
        mock_crawler = AsyncMock()
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        mock_crawler.arun.return_value = self.mock_result

        # Mock the extraction methods
        self.tool._extract_pdf_links = AsyncMock(return_value=[
            {"pdfUrl": "https://example.com/article1.pdf"},
            {"pdfUrl": "https://example.com/article2.pdf"}
        ])
        self.tool._extract_related_searches = AsyncMock(return_value=[
            "AI in healthcare", "AI ethics"
        ])
        self.tool._extract_pagination_info = AsyncMock(return_value={
            "current_page": 0,
            "next_page_url": "https://scholar.google.com/scholar?start=10",
            "total_pages": 10
        })
        self.tool._extract_total_results_count = AsyncMock(return_value="About 1,000,000 results")

        # Call the method
        result = asyncio.run(self.tool._async_run("AI", None, False, 10, 0, 1.0, 3, True, False))

        # Verify the crawler was called with the correct URL
        mock_crawler.arun.assert_called()

        # Verify the extraction methods were called
        self.tool._extract_pdf_links.assert_called_once()
        self.tool._extract_related_searches.assert_called_once()
        self.tool._extract_pagination_info.assert_called_once()
        self.tool._extract_total_results_count.assert_called_once()

        # Verify the result is a JSON string
        result_obj = json.loads(result)
        self.assertEqual(result_obj["query"], "AI")
        self.assertIn("results", result_obj)
        self.assertIn("related_searches", result_obj)
        self.assertIn("pagination", result_obj)

    def test_build_google_scholar_url(self):
        """Test _build_google_scholar_url method."""
        # Test with basic query
        url = self.tool._build_google_scholar_url("AI", None, False, 0)
        self.assertEqual(url, "https://scholar.google.com/scholar?q=AI&hl=en&as_sdt=0%2C5")

        # Test with since_year
        url = self.tool._build_google_scholar_url("AI", 2020, False, 0)
        self.assertEqual(
            url,
            "https://scholar.google.com/scholar?q=AI&hl=en&as_sdt=0%2C5&as_ylo=2020"
        )

        # Test with only_reviews
        url = self.tool._build_google_scholar_url("AI", None, True, 0)
        self.assertEqual(
            url,
            "https://scholar.google.com/scholar?q=AI&hl=en&as_sdt=0%2C5&as_rr=1"
        )

        # Test with page
        url = self.tool._build_google_scholar_url("AI", None, False, 1)
        self.assertEqual(
            url,
            "https://scholar.google.com/scholar?q=AI&hl=en&as_sdt=0%2C5&start=10"
        )

        # Test with all parameters
        url = self.tool._build_google_scholar_url("AI", 2020, True, 1)
        self.assertIn("q=AI", url)
        self.assertIn("as_ylo=2020", url)
        self.assertIn("as_rr=1", url)
        self.assertIn("start=10", url)

    def test_get_cache_key(self):
        """Test _get_cache_key method."""
        # Test with different parameters
        key1 = self.tool._get_cache_key("AI", None, False, 0)
        key2 = self.tool._get_cache_key("AI", 2020, False, 0)
        key3 = self.tool._get_cache_key("AI", None, True, 0)
        key4 = self.tool._get_cache_key("AI", None, False, 1)

        # Verify the keys are different
        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key1, key3)
        self.assertNotEqual(key1, key4)

        # Verify the same parameters produce the same key
        key5 = self.tool._get_cache_key("AI", None, False, 0)
        self.assertEqual(key1, key5)

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch.object(Path, "exists")
    def test_check_cache_with_existing_cache(self, mock_exists, mock_open):
        """Test _check_cache method with existing cache."""
        # Configure the mocks
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = "cached result"

        # Call the method
        result = self.tool._check_cache("test_key")

        # Verify the result
        self.assertEqual(result, "cached result")
        mock_open.assert_called_once()

    @patch.object(Path, "exists")
    def test_check_cache_with_no_cache(self, mock_exists):
        """Test _check_cache method with no cache."""
        # Configure the mock
        mock_exists.return_value = False

        # Call the method
        result = self.tool._check_cache("test_key")

        # Verify the result
        self.assertIsNone(result)

    def test_process_search_results(self):
        """Test _process_search_results method."""
        # Sample input
        search_results = json.loads(self.sample_extracted_content)
        pdf_links = json.loads(self.sample_pdf_links)

        # Call the method
        processed_results = self.tool._process_search_results(search_results, pdf_links)

        # Verify the results
        self.assertEqual(len(processed_results), 2)

        # Check the first result
        first_result = processed_results[0]
        self.assertEqual(first_result["title"], "Role of AI in public health")
        self.assertEqual(first_result["link"], "https://example.com/article1")
        self.assertEqual(first_result["year"], 2023)
        self.assertEqual(first_result["citedBy"], 42)
        self.assertEqual(first_result["pdfUrl"], "https://example.com/article1.pdf")

        # Check the second result
        second_result = processed_results[1]
        self.assertEqual(second_result["title"], "Potential use of AI in global warming")
        self.assertEqual(second_result["link"], "https://example.com/article2")
        self.assertEqual(second_result["year"], 2024)
        self.assertEqual(second_result["citedBy"], 15)
        self.assertEqual(second_result["pdfUrl"], "https://example.com/article2.pdf")


if __name__ == "__main__":
    unittest.main()
