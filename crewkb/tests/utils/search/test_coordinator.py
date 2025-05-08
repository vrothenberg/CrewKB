"""
Tests for the AsyncSearchCoordinator.
"""

import os
import json
import asyncio
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pytest

from crewkb.utils.search.coordinator import AsyncSearchCoordinator
from crewkb.utils.search.cache import SearchCache
from crewkb.models.knowledge.paper import PaperSource


class TestAsyncSearchCoordinator(unittest.TestCase):
    """Tests for the AsyncSearchCoordinator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for cache
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = self.temp_dir.name
        
        # Create the coordinator with the temporary cache directory
        self.coordinator = AsyncSearchCoordinator(cache_dir=self.cache_dir)
        
        # Sample search results
        self.google_scholar_results = [
            {
                "title": "Test Paper 1",
                "authors": ["Author 1", "Author 2"],
                "year": 2022,
                "journal": "Test Journal",
                "url": "https://example.com/paper1",
                "pdf_url": "https://example.com/paper1.pdf",
                "citation_count": 50,
                "abstract": "This is a test abstract."
            },
            {
                "title": "Test Paper 2",
                "authors": ["Author 3", "Author 4"],
                "year": 2021,
                "journal": "Another Journal",
                "url": "https://example.com/paper2",
                "pdf_url": "https://example.com/paper2.pdf",
                "citation_count": 30,
                "abstract": "This is another test abstract."
            }
        ]
        
        self.semantic_scholar_results = [
            {
                "title": "Semantic Paper 1",
                "authors": [{"name": "Author 5"}, {"name": "Author 6"}],
                "year": 2023,
                "journal": "Semantic Journal",
                "url": "https://example.com/semantic1",
                "pdf_url": "https://example.com/semantic1.pdf",
                "citation_count": 100,
                "abstract": "This is a semantic abstract."
            },
            {
                "title": "Semantic Paper 2",
                "authors": [{"name": "Author 7"}, {"name": "Author 8"}],
                "year": 2022,
                "journal": "Another Semantic Journal",
                "url": "https://example.com/semantic2",
                "pdf_url": "https://example.com/semantic2.pdf",
                "citation_count": 80,
                "abstract": "This is another semantic abstract."
            }
        ]
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    @patch('crewkb.utils.search.coordinator.DirectGoogleScholarTool')
    @patch('crewkb.utils.search.coordinator.SemanticScholarTool')
    def test_init(self, mock_semantic_scholar, mock_google_scholar):
        """Test initialization of the coordinator."""
        coordinator = AsyncSearchCoordinator(cache_dir=self.cache_dir)
        
        # Check that the cache and retry strategy are initialized
        self.assertIsInstance(coordinator.cache, SearchCache)
        self.assertEqual(coordinator.cache.cache_dir, self.cache_dir)
        
        # Check that the search tools are initialized
        self.assertIsNotNone(coordinator.google_scholar_tool)
        self.assertIsNotNone(coordinator.semantic_scholar_tool)
    
    @patch('crewkb.utils.search.coordinator.DirectGoogleScholarTool')
    @patch('crewkb.utils.search.coordinator.SemanticScholarTool')
    def test_search_with_cache(self, mock_semantic_scholar, mock_google_scholar):
        """Test search with cache."""
        # Set up the mocks
        mock_google_scholar_instance = mock_google_scholar.return_value
        mock_google_scholar_instance.run.return_value = self.google_scholar_results
        
        mock_semantic_scholar_instance = mock_semantic_scholar.return_value
        mock_semantic_scholar_instance.run.return_value = self.semantic_scholar_results
        
        # Create a coordinator with the mocks
        coordinator = AsyncSearchCoordinator(cache_dir=self.cache_dir)
        
        # Run the search
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(coordinator.search("test", use_cache=True))
        
        # Check that the results are as expected
        self.assertEqual(results["google_scholar"], self.google_scholar_results)
        self.assertEqual(results["semantic_scholar"], self.semantic_scholar_results)
        
        # Check that the results are cached
        cache_key = "test_10_None_None"
        cached_results = coordinator.cache.get(cache_key)
        self.assertIsNotNone(cached_results)
        self.assertEqual(cached_results["google_scholar"], self.google_scholar_results)
        self.assertEqual(cached_results["semantic_scholar"], self.semantic_scholar_results)
        
        # Run the search again to use the cache
        mock_google_scholar_instance.run.reset_mock()
        mock_semantic_scholar_instance.run.reset_mock()
        
        results = loop.run_until_complete(coordinator.search("test", use_cache=True))
        
        # Check that the search tools were not called again
        mock_google_scholar_instance.run.assert_not_called()
        mock_semantic_scholar_instance.run.assert_not_called()
        
        # Check that the results are still as expected
        self.assertEqual(results["google_scholar"], self.google_scholar_results)
        self.assertEqual(results["semantic_scholar"], self.semantic_scholar_results)
    
    @patch('crewkb.utils.search.coordinator.DirectGoogleScholarTool')
    @patch('crewkb.utils.search.coordinator.SemanticScholarTool')
    def test_search_without_cache(self, mock_semantic_scholar, mock_google_scholar):
        """Test search without cache."""
        # Set up the mocks
        mock_google_scholar_instance = mock_google_scholar.return_value
        mock_google_scholar_instance.run.return_value = self.google_scholar_results
        
        mock_semantic_scholar_instance = mock_semantic_scholar.return_value
        mock_semantic_scholar_instance.run.return_value = self.semantic_scholar_results
        
        # Create a coordinator with the mocks
        coordinator = AsyncSearchCoordinator(cache_dir=self.cache_dir)
        
        # Run the search without cache
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(coordinator.search("test", use_cache=False))
        
        # Check that the results are as expected
        self.assertEqual(results["google_scholar"], self.google_scholar_results)
        self.assertEqual(results["semantic_scholar"], self.semantic_scholar_results)
        
        # Check that the search tools were called
        mock_google_scholar_instance.run.assert_called_once()
        mock_semantic_scholar_instance.run.assert_called_once()
        
        # Run the search again without cache
        mock_google_scholar_instance.run.reset_mock()
        mock_semantic_scholar_instance.run.reset_mock()
        
        results = loop.run_until_complete(coordinator.search("test", use_cache=False))
        
        # Check that the search tools were called again
        mock_google_scholar_instance.run.assert_called_once()
        mock_semantic_scholar_instance.run.assert_called_once()
    
    @patch('crewkb.utils.search.coordinator.DirectGoogleScholarTool')
    @patch('crewkb.utils.search.coordinator.SemanticScholarTool')
    def test_search_and_create_papers(self, mock_semantic_scholar, mock_google_scholar):
        """Test search and create papers."""
        # Set up the mocks
        mock_google_scholar_instance = mock_google_scholar.return_value
        mock_google_scholar_instance.run.return_value = self.google_scholar_results
        
        mock_semantic_scholar_instance = mock_semantic_scholar.return_value
        mock_semantic_scholar_instance.run.return_value = self.semantic_scholar_results
        
        # Create a coordinator with the mocks
        coordinator = AsyncSearchCoordinator(cache_dir=self.cache_dir)
        
        # Run the search and create papers
        loop = asyncio.get_event_loop()
        papers = loop.run_until_complete(coordinator.search_and_create_papers("test"))
        
        # Check that the papers are created correctly
        self.assertEqual(len(papers["google_scholar"]), 2)
        self.assertEqual(len(papers["semantic_scholar"]), 2)
        
        # Check that the papers are PaperSource objects
        for paper in papers["google_scholar"]:
            self.assertIsInstance(paper, PaperSource)
            self.assertEqual(paper.search_term, "test")
            self.assertEqual(paper.source_tool, "google_scholar")
        
        for paper in papers["semantic_scholar"]:
            self.assertIsInstance(paper, PaperSource)
            self.assertEqual(paper.search_term, "test")
            self.assertEqual(paper.source_tool, "semantic_scholar")
    
    @patch('crewkb.utils.search.coordinator.DirectGoogleScholarTool')
    @patch('crewkb.utils.search.coordinator.SemanticScholarTool')
    def test_clear_cache(self, mock_semantic_scholar, mock_google_scholar):
        """Test clear cache."""
        # Set up the mocks
        mock_google_scholar_instance = mock_google_scholar.return_value
        mock_google_scholar_instance.run.return_value = self.google_scholar_results
        
        mock_semantic_scholar_instance = mock_semantic_scholar.return_value
        mock_semantic_scholar_instance.run.return_value = self.semantic_scholar_results
        
        # Create a coordinator with the mocks
        coordinator = AsyncSearchCoordinator(cache_dir=self.cache_dir)
        
        # Run the search to populate the cache
        loop = asyncio.get_event_loop()
        loop.run_until_complete(coordinator.search("test", use_cache=True))
        
        # Check that the cache is populated
        cache_key = "test_10_None_None"
        cached_results = coordinator.cache.get(cache_key)
        self.assertIsNotNone(cached_results)
        
        # Clear the cache for a specific term
        coordinator.clear_cache("test")
        
        # Check that the cache is cleared
        cached_results = coordinator.cache.get(cache_key)
        self.assertIsNone(cached_results)
        
        # Run the search again to populate the cache
        loop.run_until_complete(coordinator.search("test", use_cache=True))
        
        # Check that the cache is populated again
        cached_results = coordinator.cache.get(cache_key)
        self.assertIsNotNone(cached_results)
        
        # Clear all cache
        coordinator.clear_cache()
        
        # Check that the cache is cleared
        cached_results = coordinator.cache.get(cache_key)
        self.assertIsNone(cached_results)
    
    @patch('crewkb.utils.search.coordinator.DirectGoogleScholarTool')
    @patch('crewkb.utils.search.coordinator.SemanticScholarTool')
    def test_search_with_error(self, mock_semantic_scholar, mock_google_scholar):
        """Test search with error."""
        # Set up the mocks
        mock_google_scholar_instance = mock_google_scholar.return_value
        mock_google_scholar_instance.run.side_effect = Exception("Google Scholar error")
        
        mock_semantic_scholar_instance = mock_semantic_scholar.return_value
        mock_semantic_scholar_instance.run.return_value = self.semantic_scholar_results
        
        # Create a coordinator with the mocks
        coordinator = AsyncSearchCoordinator(cache_dir=self.cache_dir)
        
        # Run the search
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(coordinator.search("test", use_cache=False))
        
        # Check that the results include the semantic scholar results but not google scholar
        self.assertEqual(len(results["google_scholar"]), 0)
        self.assertEqual(results["semantic_scholar"], self.semantic_scholar_results)
