"""
Tests for the integration of the AsyncSearchCoordinator with the knowledge directory.
"""

import os
import asyncio
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import pytest

from crewkb.utils.search.coordinator import AsyncSearchCoordinator
from crewkb.models.knowledge.paper import PaperSource
from crewkb.models.knowledge.topic import KnowledgeTopic
from crewkb.utils.knowledge_directory import create_topic_directory, load_topic


class TestSearchIntegration(unittest.TestCase):
    """Tests for the integration of the AsyncSearchCoordinator with the knowledge directory."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for cache and knowledge
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = os.path.join(self.temp_dir.name, "cache")
        self.knowledge_dir = os.path.join(self.temp_dir.name, "knowledge")
        
        # Create the cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
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
    def test_search_and_save_to_topic(self, mock_semantic_scholar, mock_google_scholar):
        """Test searching and saving papers to a knowledge topic."""
        # Set up the mocks
        mock_google_scholar_instance = mock_google_scholar.return_value
        mock_google_scholar_instance.run.return_value = self.google_scholar_results
        
        mock_semantic_scholar_instance = mock_semantic_scholar.return_value
        mock_semantic_scholar_instance.run.return_value = self.semantic_scholar_results
        
        # Create a topic
        topic = create_topic_directory(
            topic="Test Topic",
            article_type="disease",
            base_dir=self.knowledge_dir
        )
        
        # Run the search
        loop = asyncio.get_event_loop()
        papers_by_source = loop.run_until_complete(
            self.coordinator.search_and_create_papers(
                term="test",
                max_results=5,
                use_cache=True
            )
        )
        
        # Add papers to the topic
        all_papers = []
        for source, papers in papers_by_source.items():
            all_papers.extend(papers)
        
        for paper in all_papers:
            topic.add_paper(paper)
        
        # Save the topic
        topic.save_metadata()
        
        # Load the topic again to verify it was saved correctly
        loaded_topic = load_topic("Test Topic", base_dir=self.knowledge_dir)
        
        # Check that the topic was loaded correctly
        self.assertIsNotNone(loaded_topic)
        self.assertEqual(loaded_topic.topic, "Test Topic")
        
        # Check that the papers were saved correctly
        self.assertEqual(len(loaded_topic.papers), len(all_papers))
    
    @patch('crewkb.utils.search.coordinator.DirectGoogleScholarTool')
    @patch('crewkb.utils.search.coordinator.SemanticScholarTool')
    def test_search_with_filtering(self, mock_semantic_scholar, mock_google_scholar):
        """Test searching with filtering by citation count and year range."""
        # Set up the mocks
        mock_google_scholar_instance = mock_google_scholar.return_value
        mock_google_scholar_instance.run.return_value = self.google_scholar_results
        
        mock_semantic_scholar_instance = mock_semantic_scholar.return_value
        mock_semantic_scholar_instance.run.return_value = self.semantic_scholar_results
        
        # Run the search with filtering
        loop = asyncio.get_event_loop()
        papers_by_source = loop.run_until_complete(
            self.coordinator.search_and_create_papers(
                term="test",
                max_results=5,
                use_cache=True,
                min_citation_count=50,  # Filter by citation count
                year_range=(2022, 2023)  # Filter by year range
            )
        )
        
        # Check that the filtering was applied
        all_papers = []
        for source, papers in papers_by_source.items():
            all_papers.extend(papers)
        
        # All papers should have citation count >= 50 and year between 2022 and 2023
        for paper in all_papers:
            self.assertGreaterEqual(paper.citation_count or 0, 50)
            self.assertGreaterEqual(paper.year or 0, 2022)
            self.assertLessEqual(paper.year or 0, 2023)
