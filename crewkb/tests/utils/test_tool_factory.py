"""
Tests for the ToolFactory.

This module contains unit tests for the ToolFactory, which is used to create
tool instances for agents.
"""

import unittest
# No need for mocks in this test

from crewkb.utils.tool_factory import ToolFactory
from crewkb.tools.search.serper_dev_tool import SerperDevTool
from crewkb.tools.search.pubmed_search_tool import PubMedSearchTool
from crewkb.tools.search.serper_google_scholar_tool import SerperGoogleScholarTool
from crewkb.tools.search.direct_google_scholar_tool import DirectGoogleScholarTool
from crewkb.tools.search.webpage_scraper_tool import WebpageScraperTool
from crewkb.tools.search.semantic_scholar_tool import SemanticScholarTool
from crewkb.tools.search.crawl4ai_scraper_tool import Crawl4AIScraperTool
from crewkb.tools.content.outline_generator_tool import OutlineGeneratorTool
from crewkb.tools.content.content_structure_tool import ContentStructureTool
from crewkb.tools.content.citation_formatter_tool import CitationFormatterTool


class TestToolFactory(unittest.TestCase):
    """Test cases for the ToolFactory."""

    def test_create_tool(self):
        """Test creating tools by name."""
        # Test creating search tools
        serper_tool = ToolFactory.create_tool("serper_dev")
        self.assertIsInstance(serper_tool, SerperDevTool)
        
        pubmed_tool = ToolFactory.create_tool("pubmed_search")
        self.assertIsInstance(pubmed_tool, PubMedSearchTool)
        
        serper_google_scholar_tool = ToolFactory.create_tool("serper_google_scholar")
        self.assertIsInstance(serper_google_scholar_tool, SerperGoogleScholarTool)
        
        direct_google_scholar_tool = ToolFactory.create_tool("direct_google_scholar")
        self.assertIsInstance(direct_google_scholar_tool, DirectGoogleScholarTool)
        
        webpage_scraper_tool = ToolFactory.create_tool("webpage_scraper")
        self.assertIsInstance(webpage_scraper_tool, WebpageScraperTool)
        
        semantic_scholar_tool = ToolFactory.create_tool("semantic_scholar")
        self.assertIsInstance(semantic_scholar_tool, SemanticScholarTool)
        
        # Test creating content tools
        outline_tool = ToolFactory.create_tool("outline_generator")
        self.assertIsInstance(outline_tool, OutlineGeneratorTool)
        
        structure_tool = ToolFactory.create_tool("content_structure")
        self.assertIsInstance(structure_tool, ContentStructureTool)
        
        citation_tool = ToolFactory.create_tool("citation_formatter")
        self.assertIsInstance(citation_tool, CitationFormatterTool)
        
        # Test with unknown tool name
        with self.assertRaises(ValueError):
            ToolFactory.create_tool("unknown_tool")

    def test_create_tools_for_agent(self):
        """Test creating tools for specific agents."""
        # Test research agents
        lit_researcher_tools = ToolFactory.create_tools_for_agent(
            "medical_literature_researcher"
        )
        self.assertEqual(len(lit_researcher_tools), 6)
        self.assertIsInstance(lit_researcher_tools[0], SerperGoogleScholarTool)
        self.assertIsInstance(lit_researcher_tools[1], DirectGoogleScholarTool)
        self.assertIsInstance(lit_researcher_tools[2], PubMedSearchTool)
        self.assertIsInstance(lit_researcher_tools[3], SemanticScholarTool)
        self.assertIsInstance(lit_researcher_tools[4], WebpageScraperTool)
        self.assertIsInstance(lit_researcher_tools[5], Crawl4AIScraperTool)
        
        guidelines_analyst_tools = ToolFactory.create_tools_for_agent(
            "clinical_guidelines_analyst"
        )
        self.assertEqual(len(guidelines_analyst_tools), 4)
        self.assertIsInstance(guidelines_analyst_tools[0], SerperDevTool)
        self.assertIsInstance(guidelines_analyst_tools[1], SerperGoogleScholarTool)
        self.assertIsInstance(guidelines_analyst_tools[2], WebpageScraperTool)
        self.assertIsInstance(guidelines_analyst_tools[3], Crawl4AIScraperTool)
        
        data_synthesizer_tools = ToolFactory.create_tools_for_agent(
            "medical_data_synthesizer"
        )
        self.assertEqual(len(data_synthesizer_tools), 2)
        self.assertIsInstance(data_synthesizer_tools[0], WebpageScraperTool)
        self.assertIsInstance(data_synthesizer_tools[1], Crawl4AIScraperTool)
        
        # Test content agents
        content_architect_tools = ToolFactory.create_tools_for_agent(
            "medical_content_architect"
        )
        self.assertEqual(len(content_architect_tools), 1)
        self.assertIsInstance(content_architect_tools[0], OutlineGeneratorTool)
        
        content_writer_tools = ToolFactory.create_tools_for_agent(
            "medical_content_writer"
        )
        self.assertEqual(len(content_writer_tools), 1)
        self.assertIsInstance(content_writer_tools[0], ContentStructureTool)
        
        citation_specialist_tools = ToolFactory.create_tools_for_agent(
            "medical_citation_specialist"
        )
        self.assertEqual(len(citation_specialist_tools), 3)
        self.assertIsInstance(citation_specialist_tools[0], CitationFormatterTool)
        self.assertIsInstance(citation_specialist_tools[1], SerperGoogleScholarTool)
        self.assertIsInstance(citation_specialist_tools[2], SemanticScholarTool)
        
        # Test review agents
        accuracy_reviewer_tools = ToolFactory.create_tools_for_agent(
            "medical_accuracy_reviewer"
        )
        self.assertEqual(len(accuracy_reviewer_tools), 5)
        self.assertIsInstance(accuracy_reviewer_tools[0], SerperGoogleScholarTool)
        self.assertIsInstance(accuracy_reviewer_tools[1], PubMedSearchTool)
        self.assertIsInstance(accuracy_reviewer_tools[2], SemanticScholarTool)
        self.assertIsInstance(accuracy_reviewer_tools[3], WebpageScraperTool)
        self.assertIsInstance(accuracy_reviewer_tools[4], Crawl4AIScraperTool)
        
        content_editor_tools = ToolFactory.create_tools_for_agent(
            "medical_content_editor"
        )
        self.assertEqual(len(content_editor_tools), 0)
        
        patient_perspective_tools = ToolFactory.create_tools_for_agent(
            "patient_perspective_reviewer"
        )
        self.assertEqual(len(patient_perspective_tools), 0)
        
        review_manager_tools = ToolFactory.create_tools_for_agent(
            "review_manager"
        )
        self.assertEqual(len(review_manager_tools), 0)
        
        # Test with unknown agent name
        unknown_agent_tools = ToolFactory.create_tools_for_agent(
            "unknown_agent"
        )
        self.assertEqual(len(unknown_agent_tools), 0)


if __name__ == '__main__':
    unittest.main()
