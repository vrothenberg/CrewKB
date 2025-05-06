"""
ContentStructureTool for validating article structure.

This module provides a tool for validating the structure of knowledge base
articles against the article model and ensuring section completeness.
"""

from typing import Dict, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ContentStructureToolInput(BaseModel):
    """Input schema for ContentStructureTool."""
    article_type: str = Field(
        ..., 
        description="The type of article (disease, biomarker, or lab test)"
    )
    content: str = Field(
        ..., 
        description="The article content to validate"
    )


class ContentStructureTool(BaseTool):
    """
    Tool for validating article structure.
    
    This tool checks that article content follows the required structure
    and includes all necessary sections based on the article type.
    """
    
    name: str = "ContentStructureTool"
    description: str = "Validate article structure against the model"
    args_schema: type[BaseModel] = ContentStructureToolInput
    
    def _run(
        self,
        article_type: str,
        content: str
    ) -> str:
        """
        Validate article structure against the model.
        
        Args:
            article_type: The type of article (disease, biomarker, or lab test)
            content: The article content to validate
            
        Returns:
            A string containing the validation results.
        """
        # Get the required sections based on article type
        required_sections = self._get_required_sections(article_type)
        
        # Extract sections from the content
        content_sections = self._extract_sections(content)
        
        # Validate the structure
        validation_results = self._validate_structure(
            required_sections, content_sections
        )
        
        return validation_results
    
    def _get_required_sections(self, article_type: str) -> List[str]:
        """
        Get the required sections based on article type.
        
        Args:
            article_type: The type of article (disease, biomarker, or lab test)
            
        Returns:
            A list of required section names.
        """
        # Common sections for all article types
        common_sections = [
            "Overview",
            "Key Facts",
            "FAQs",
            "References"
        ]
        
        # Article type-specific sections
        type_specific_sections = {
            "disease": [
                "Symptoms",
                "Causes",
                "Diagnosis",
                "Treatment",
                "Prevention"
            ],
            "biomarker": [
                "Biological Role",
                "Clinical Significance",
                "Testing",
                "Normal Ranges",
                "Interpretation"
            ],
            "labtest": [
                "Test Purpose",
                "Preparation",
                "Procedure",
                "Normal Ranges",
                "Interpretation"
            ]
        }
        
        # Get the specific sections for this article type
        specific_sections = type_specific_sections.get(
            article_type.lower(), []
        )
        
        # Combine common and specific sections
        return common_sections + specific_sections
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """
        Extract sections from the article content.
        
        Args:
            content: The article content
            
        Returns:
            A dictionary mapping section names to section content.
        """
        sections = {}
        lines = content.split("\n")
        
        current_section = None
        current_content = []
        
        for line in lines:
            # Check if this line is a section heading
            if (line.strip().startswith("# ") or 
                line.strip().startswith("## ")):
                # If we were already processing a section, save it
                if current_section:
                    sections[current_section] = "\n".join(current_content)
                
                # Start a new section
                # Extract section name
                section_line = line.strip()
                current_section = section_line.replace("# ", "").replace("## ", "")
                current_content = []
            elif current_section:
                # Add this line to the current section
                current_content.append(line)
        
        # Save the last section
        if current_section:
            sections[current_section] = "\n".join(current_content)
        
        return sections
    
    def _validate_structure(
        self, 
        required_sections: List[str], 
        content_sections: Dict[str, str]
    ) -> str:
        """
        Validate the article structure.
        
        Args:
            required_sections: List of required section names
            content_sections: Dictionary mapping section names to content
            
        Returns:
            A string containing the validation results.
        """
        results = "Article Structure Validation Results:\n\n"
        
        # Check for missing required sections
        missing_sections = [
            section for section in required_sections 
            if section not in content_sections
        ]
        
        # Check for empty sections
        empty_sections = [
            section for section, content in content_sections.items()
            if not content.strip()
        ]
        
        # Check for extra sections
        extra_sections = [
            section for section in content_sections 
            if section not in required_sections
        ]
        
        # Add results
        if not missing_sections and not empty_sections:
            results += "✅ All required sections are present and have content.\n\n"
        else:
            if missing_sections:
                results += "❌ Missing required sections:\n"
                for section in missing_sections:
                    results += f"   - {section}\n"
                results += "\n"
            
            if empty_sections:
                results += "❌ Empty sections:\n"
                for section in empty_sections:
                    results += f"   - {section}\n"
                results += "\n"
        
        if extra_sections:
            results += "ℹ️ Additional sections (not required but may be useful):\n"
            for section in extra_sections:
                results += f"   - {section}\n"
            results += "\n"
        
        # Add section length analysis
        results += "Section Length Analysis:\n"
        for section, content in content_sections.items():
            word_count = len(content.split())
            results += f"   - {section}: {word_count} words\n"
        
        return results
