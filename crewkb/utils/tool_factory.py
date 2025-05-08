"""
Tool factory for CrewKB.

This module provides a factory for creating tool instances based on tool name
and configuration parameters.
"""

from typing import Any, List

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


class ToolFactory:
    """
    Factory for creating tool instances.
    
    This factory centralizes the creation of tool instances, making it easier
    to manage tool dependencies and configuration.
    """
    
    @staticmethod
    def create_tool(tool_name: str, **kwargs) -> Any:
        """
        Create a tool instance based on the tool name.
        
        Args:
            tool_name: The name of the tool to create
            **kwargs: Additional configuration parameters for the tool
            
        Returns:
            A tool instance
            
        Raises:
            ValueError: If the tool name is not recognized
        """
        # Search tools
        if tool_name == "serper_dev":
            return SerperDevTool()
        elif tool_name == "pubmed_search":
            return PubMedSearchTool()
        elif tool_name == "serper_google_scholar":
            return SerperGoogleScholarTool()
        elif tool_name == "direct_google_scholar":
            return DirectGoogleScholarTool()
        elif tool_name == "webpage_scraper":
            return WebpageScraperTool()
        elif tool_name == "semantic_scholar":
            return SemanticScholarTool()
        elif tool_name == "crawl4ai_scraper":
            return Crawl4AIScraperTool()
        
        # Content tools
        elif tool_name == "outline_generator":
            return OutlineGeneratorTool()
        elif tool_name == "content_structure":
            return ContentStructureTool()
        elif tool_name == "citation_formatter":
            return CitationFormatterTool()
        
        # Unknown tool
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    @staticmethod
    def create_tools_for_agent(agent_name: str) -> List[Any]:
        """
        Create a list of tools for a specific agent.
        
        Args:
            agent_name: The name of the agent
            
        Returns:
            A list of tool instances appropriate for the agent
        """
        tools = []
        
        # Research agents
        if agent_name == "medical_literature_researcher":
            tools = [
                SerperGoogleScholarTool(),
                DirectGoogleScholarTool(),
                PubMedSearchTool(), 
                SemanticScholarTool(),
                WebpageScraperTool(),
                Crawl4AIScraperTool()
            ]
        elif agent_name == "clinical_guidelines_analyst":
            tools = [
                SerperDevTool(), 
                SerperGoogleScholarTool(),
                WebpageScraperTool(),
                Crawl4AIScraperTool()
            ]
        elif agent_name == "medical_data_synthesizer":
            tools = [WebpageScraperTool(), Crawl4AIScraperTool()]  # For data extraction
        
        # Content agents
        elif agent_name == "medical_content_architect":
            tools = [OutlineGeneratorTool()]
        elif agent_name == "medical_content_writer":
            tools = [ContentStructureTool()]
        elif agent_name == "medical_citation_specialist":
            tools = [
                CitationFormatterTool(), 
                SerperGoogleScholarTool(),
                SemanticScholarTool()  # Added for academic citation lookup
            ]
        
        # Review agents
        elif agent_name == "medical_accuracy_reviewer":
            tools = [
                SerperGoogleScholarTool(),
                PubMedSearchTool(), 
                SemanticScholarTool(),  # Added for academic fact checking
                WebpageScraperTool(),
                Crawl4AIScraperTool()
            ]
        elif agent_name == "medical_content_editor":
            tools = []  # LLM will handle readability analysis
        elif agent_name == "patient_perspective_reviewer":
            tools = []  # No specific tools needed
        elif agent_name == "review_manager":
            tools = []  # No specific tools needed
        
        return tools
