"""
Tests for the PDF management utilities.

This module contains tests for the PDFDownloadManager, MarkerWrapper, and PDFProcessor
classes.
"""

import os
import asyncio
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest

from crewkb.utils.pdf import PDFDownloadManager, MarkerWrapper, PDFProcessor
from crewkb.models.knowledge.paper import PaperSource


class TestPDFDownloadManager(unittest.TestCase):
    """Tests for the PDFDownloadManager class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.test_cache_dir = "test_cache/pdf_downloads"
        self.download_manager = PDFDownloadManager(cache_dir=self.test_cache_dir)
        
        # Create the test cache directory
        os.makedirs(self.test_cache_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the test cache directory
        import shutil
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
    
    @patch("aiohttp.ClientSession")
    async def test_download(self, mock_session):
        """Test downloading a PDF."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.read.return_value = b"PDF content"
        
        # Mock the context manager
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_response
        mock_session.return_value.__aenter__.return_value.get.return_value = mock_context
        
        # Download the PDF
        pdf_url = "https://example.com/test.pdf"
        pdf_path = await self.download_manager.download(pdf_url)
        
        # Check that the PDF was downloaded
        self.assertIsNotNone(pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        
        # Check that the PDF content was saved
        with open(pdf_path, "rb") as f:
            content = f.read()
        self.assertEqual(content, b"PDF content")
    
    @patch("aiohttp.ClientSession")
    async def test_download_batch(self, mock_session):
        """Test downloading multiple PDFs."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.read.return_value = b"PDF content"
        
        # Mock the context manager
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_response
        mock_session.return_value.__aenter__.return_value.get.return_value = mock_context
        
        # Download the PDFs
        pdf_urls = [
            "https://example.com/test1.pdf",
            "https://example.com/test2.pdf"
        ]
        results = await self.download_manager.download_batch(pdf_urls)
        
        # Check that the PDFs were downloaded
        self.assertEqual(len(results), 2)
        for url, path in results.items():
            self.assertIsNotNone(path)
            self.assertTrue(os.path.exists(path))
            
            # Check that the PDF content was saved
            with open(path, "rb") as f:
                content = f.read()
            self.assertEqual(content, b"PDF content")


class TestMarkerWrapper(unittest.TestCase):
    """Tests for the MarkerWrapper class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.test_cache_dir = "test_cache/marker"
        self.marker_wrapper = MarkerWrapper(
            use_llm=False,  # Disable LLM for testing
            cache_dir=self.test_cache_dir
        )
        
        # Create the test cache directory
        os.makedirs(self.test_cache_dir, exist_ok=True)
        
        # Create a test PDF file
        self.test_pdf_path = os.path.join(self.test_cache_dir, "test.pdf")
        with open(self.test_pdf_path, "wb") as f:
            f.write(b"PDF content")
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the test cache directory
        import shutil
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
    
    @patch("marker.converters.pdf.PdfConverter")
    def test_parse_pdf(self, mock_converter):
        """Test parsing a PDF."""
        # Mock the converter
        mock_instance = mock_converter.return_value
        mock_instance.return_value = "rendered"
        
        # Mock the text_from_rendered function
        with patch("crewkb.utils.pdf.marker_wrapper.text_from_rendered") as mock_text_from_rendered:
            mock_text_from_rendered.return_value = ("Markdown content", {}, [])
            
            # Create a mock ConfigParser
            with patch("crewkb.utils.pdf.marker_wrapper.ConfigParser") as mock_config_parser:
                mock_config_instance = mock_config_parser.return_value
                mock_config_instance.generate_config_dict.return_value = {}
                mock_config_instance.get_processors.return_value = []
                mock_config_instance.get_renderer.return_value = None
                mock_config_instance.get_llm_service.return_value = None
                
                # Parse the PDF
                markdown, metadata, images = self.marker_wrapper.parse_pdf(self.test_pdf_path)
                
                # Check that the PDF was parsed
                self.assertEqual(markdown, "Markdown content")
                self.assertEqual(metadata, {})
                self.assertEqual(images, [])
    
    def test_extract_sections(self):
        """Test extracting sections from markdown."""
        # Create a test markdown file
        markdown = """
# Abstract

This is the abstract.

# Introduction

This is the introduction.

# Methods

This is the methods section.

# Results

This is the results section.

# Discussion

This is the discussion section.

# Conclusion

This is the conclusion.

# References

This is the references section.
"""
        
        # Extract the sections
        sections = self.marker_wrapper.extract_sections(markdown)
        
        # Check that the sections were extracted
        self.assertEqual(len(sections), 7)
        self.assertIn("abstract", sections)
        self.assertIn("introduction", sections)
        self.assertIn("methods", sections)
        self.assertIn("results", sections)
        self.assertIn("discussion", sections)
        self.assertIn("conclusion", sections)
        self.assertIn("references", sections)


class TestPDFProcessor(unittest.TestCase):
    """Tests for the PDFProcessor class."""
    
    def setUp(self):
        """Set up the test environment."""
        self.test_cache_dir = "test_cache/pdf_processor"
        
        # Mock the download manager
        self.mock_download_manager = MagicMock()
        self.mock_download_manager.download.return_value = asyncio.Future()
        self.mock_download_manager.download.return_value.set_result("test.pdf")
        
        # Mock the marker wrapper
        self.mock_marker_wrapper = MagicMock()
        self.mock_marker_wrapper.parse_pdf.return_value = (
            "Markdown content",
            {},
            []
        )
        self.mock_marker_wrapper.extract_sections.return_value = {
            "abstract": "Abstract content",
            "introduction": "Introduction content"
        }
        
        # Create the PDF processor
        self.pdf_processor = PDFProcessor(
            download_manager=self.mock_download_manager,
            marker_wrapper=self.mock_marker_wrapper,
            cache_dir=self.test_cache_dir
        )
        
        # Create the test cache directory
        os.makedirs(self.test_cache_dir, exist_ok=True)
        
        # Create a test paper
        self.test_paper = PaperSource(
            title="Test Paper",
            authors=["Test Author"],
            year=2023,
            journal="Test Journal",
            url="https://example.com/test",
            pdf_url="https://example.com/test.pdf",
            citation_count=100,
            abstract="This is a test paper.",
            source_tool="test_tool",
            search_term="test search"
        )
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the test cache directory
        import shutil
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
    
    async def test_process_paper(self):
        """Test processing a paper."""
        # Process the paper
        markdown_path, sections = await self.pdf_processor.process_paper(self.test_paper)
        
        # Check that the paper was processed
        self.assertIsNotNone(markdown_path)
        self.assertEqual(len(sections), 2)
        self.assertIn("abstract", sections)
        self.assertIn("introduction", sections)
        
        # Check that the download manager was called
        self.mock_download_manager.download.assert_called_once_with(
            "https://example.com/test.pdf"
        )
        
        # Check that the marker wrapper was called
        self.mock_marker_wrapper.parse_pdf.assert_called_once_with(
            "test.pdf",
            use_llm=None
        )
        self.mock_marker_wrapper.extract_sections.assert_called_once_with(
            "Markdown content"
        )
    
    async def test_process_papers(self):
        """Test processing multiple papers."""
        # Create another test paper
        test_paper2 = PaperSource(
            title="Test Paper 2",
            authors=["Test Author 2"],
            year=2023,
            journal="Test Journal",
            url="https://example.com/test2",
            pdf_url="https://example.com/test2.pdf",
            citation_count=200,
            abstract="This is another test paper.",
            source_tool="test_tool",
            search_term="test search"
        )
        
        # Process the papers
        results = await self.pdf_processor.process_papers([self.test_paper, test_paper2])
        
        # Check that the papers were processed
        self.assertEqual(len(results), 2)
        self.assertIn("test_paper", results)
        self.assertIn("test_paper2", results)
        
        # Check the results
        for paper_id, (markdown_path, sections) in results.items():
            self.assertIsNotNone(markdown_path)
            self.assertEqual(len(sections), 2)
            self.assertIn("abstract", sections)
            self.assertIn("introduction", sections)


# Run the tests
if __name__ == "__main__":
    unittest.main()
