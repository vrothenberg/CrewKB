"""
OutlineGeneratorTool for creating structured article outlines.

This module provides a tool for generating structured outlines for
medical articles based on research data and article type.
"""

from typing import Dict, Any, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class OutlineGeneratorToolInput(BaseModel):
    """Input schema for OutlineGeneratorTool."""
    article_type: str = Field(
        ..., 
        description="The type of article (disease, biomarker, or lab test)"
    )
    topic: str = Field(
        ..., 
        description="The topic of the article."
    )
    research_data: str = Field(
        ..., 
        description="The research data to use for generating the outline."
    )


class OutlineGeneratorTool(BaseTool):
    """
    Tool for generating structured outlines for knowledge base articles.
    
    This tool helps create well-organized outlines for different types of
    medical articles based on research data and article type.
    """
    
    name: str = "OutlineGeneratorTool"
    description: str = "Generate a structured outline for an article"
    args_schema: type[BaseModel] = OutlineGeneratorToolInput
    
    def _run(
        self,
        article_type: str,
        topic: str,
        research_data: str
    ) -> str:
        """
        Generate a structured outline for a knowledge base article.
        
        Args:
            article_type: The type of article (disease, biomarker, or lab test)
            topic: The topic of the article.
            research_data: The research data to use for generating the outline.
            
        Returns:
            A string containing the structured outline.
        """
        # Get the appropriate template based on article type
        template = self._get_template(article_type)
        
        # Generate the outline using the template and research data
        outline = self._generate_outline(template, topic, research_data)
        
        return outline
    
    def _get_template(self, article_type: str) -> Dict[str, Any]:
        """
        Get the appropriate template based on article type.
        
        Args:
            article_type: The type of article (disease, biomarker, or lab test)
            
        Returns:
            A dictionary containing the template structure.
        """
        templates = {
            "disease": self._disease_template(),
            "biomarker": self._biomarker_template(),
            "labtest": self._lab_test_template()
        }
        
        # Default to disease template if article type is not recognized
        return templates.get(article_type.lower(), self._disease_template())
    
    def _disease_template(self) -> Dict[str, List[str]]:
        """
        Get the template for disease articles.
        
        Returns:
            A dictionary containing the template structure for disease articles.
        """
        return {
            "Overview": [
                "Brief description of the disease",
                "Importance and prevalence",
                "General impact on health"
            ],
            "Key Facts": [
                "Essential information about the disease",
                "Quick statistics",
                "Important points for patients"
            ],
            "Symptoms": [
                "Common symptoms",
                "Early warning signs",
                "Severe symptoms requiring medical attention",
                "Symptom progression"
            ],
            "Types": [
                "Different forms or classifications",
                "Distinguishing characteristics of each type",
                "Prevalence of different types"
            ],
            "Causes": [
                "Known causes and risk factors",
                "Genetic factors",
                "Environmental factors",
                "Lifestyle factors"
            ],
            "Risk Factors": [
                "Factors that increase risk",
                "Modifiable vs. non-modifiable risk factors",
                "Risk assessment"
            ],
            "Diagnosis": [
                "Diagnostic process",
                "Tests and procedures",
                "Diagnostic criteria",
                "Differential diagnosis"
            ],
            "Prevention": [
                "Preventive measures",
                "Lifestyle modifications",
                "Screening recommendations",
                "Vaccination (if applicable)"
            ],
            "Specialist to Visit": [
                "Types of healthcare providers involved",
                "When to see a specialist",
                "What to expect during specialist visits"
            ],
            "Treatment": [
                "Treatment approaches",
                "Medications",
                "Surgical options",
                "Other interventions",
                "Treatment effectiveness and considerations"
            ],
            "Home Care": [
                "Self-management strategies",
                "Lifestyle adjustments",
                "Home monitoring",
                "Supportive care"
            ],
            "Living With": [
                "Long-term management",
                "Quality of life considerations",
                "Coping strategies",
                "Support resources"
            ],
            "Complications": [
                "Potential complications",
                "Warning signs of complications",
                "Managing complications",
                "Long-term outlook"
            ],
            "Alternative Therapies": [
                "Complementary approaches",
                "Evidence for alternative therapies",
                "Integrating with conventional treatment"
            ],
            "FAQs": [
                "Common questions about the disease",
                "Misconceptions",
                "Patient concerns"
            ],
            "References": [
                "Scientific literature",
                "Clinical guidelines",
                "Authoritative sources"
            ]
        }
    
    def _biomarker_template(self) -> Dict[str, List[str]]:
        """
        Get the template for biomarker articles.
        
        Returns:
            A dictionary containing the template structure for biomarker articles.
        """
        return {
            "Overview": [
                "Definition of the biomarker",
                "Biological significance",
                "Clinical relevance"
            ],
            "Key Facts": [
                "Essential information about the biomarker",
                "Quick reference points",
                "Importance in healthcare"
            ],
            "Biological Role": [
                "Function in the body",
                "Biological pathways involved",
                "Normal physiological role"
            ],
            "Clinical Significance": [
                "Role in disease processes",
                "Diagnostic value",
                "Prognostic value",
                "Treatment monitoring value"
            ],
            "Testing": [
                "When the biomarker is tested",
                "Testing methods",
                "Sample requirements",
                "Testing procedure"
            ],
            "Normal Ranges": [
                "Reference ranges",
                "Factors affecting normal ranges",
                "Variations by population"
            ],
            "Interpretation": [
                "Meaning of elevated levels",
                "Meaning of decreased levels",
                "Factors affecting interpretation",
                "Interpretation limitations"
            ],
            "Associated Conditions": [
                "Diseases associated with abnormal levels",
                "Strength of association",
                "Specificity and sensitivity"
            ],
            "Clinical Use": [
                "Clinical practice applications",
                "Screening applications",
                "Diagnostic applications",
                "Monitoring applications"
            ],
            "Limitations": [
                "Limitations of the biomarker",
                "False positives and negatives",
                "Confounding factors"
            ],
            "Future Directions": [
                "Emerging research",
                "Potential new applications",
                "Technological developments"
            ],
            "Patient Information": [
                "What patients should know",
                "Preparing for testing",
                "Understanding results"
            ],
            "FAQs": [
                "Common questions about the biomarker",
                "Misconceptions",
                "Patient concerns"
            ],
            "References": [
                "Scientific literature",
                "Clinical guidelines",
                "Authoritative sources"
            ]
        }
    
    def _lab_test_template(self) -> Dict[str, List[str]]:
        """
        Get the template for lab test articles.
        
        Returns:
            A dictionary containing the template structure for lab test articles.
        """
        return {
            "Overview": [
                "Purpose of the test",
                "What the test measures",
                "Clinical significance"
            ],
            "Key Facts": [
                "Essential information about the test",
                "Quick reference points",
                "When the test is typically ordered"
            ],
            "Test Purpose": [
                "Detailed explanation of test purpose",
                "Clinical questions the test helps answer",
                "Conditions associated with the test"
            ],
            "Preparation": [
                "How to prepare for the test",
                "Fasting requirements",
                "Medication considerations",
                "Timing considerations"
            ],
            "Procedure": [
                "How the test is performed",
                "Sample collection method",
                "Duration and what to expect",
                "Potential discomfort or risks"
            ],
            "Normal Ranges": [
                "Reference ranges",
                "Factors affecting normal ranges",
                "Variations by population"
            ],
            "Interpretation": [
                "What high results mean",
                "What low results mean",
                "Factors affecting results",
                "Follow-up testing"
            ],
            "Clinical Use": [
                "Diagnostic applications",
                "Screening applications",
                "Monitoring applications"
            ],
            "Limitations": [
                "Limitations of the test",
                "False positives and negatives",
                "Interfering factors"
            ],
            "Alternative Tests": [
                "Other tests that may be used",
                "Comparative advantages and disadvantages",
                "When alternatives might be preferred"
            ],
            "Cost and Availability": [
                "Typical cost considerations",
                "Insurance coverage",
                "Where the test is available"
            ],
            "After the Test": [
                "Recovery information",
                "When to expect results",
                "Follow-up considerations"
            ],
            "FAQs": [
                "Common questions about the test",
                "Misconceptions",
                "Patient concerns"
            ],
            "References": [
                "Scientific literature",
                "Clinical guidelines",
                "Authoritative sources"
            ]
        }
    
    def _generate_outline(
        self, 
        template: Dict[str, List[str]], 
        topic: str, 
        research_data: str
    ) -> str:
        """
        Generate an outline based on the template and research data.
        
        Args:
            template: The template structure to use.
            topic: The topic of the article.
            research_data: The research data to use for generating the outline.
            
        Returns:
            A string containing the structured outline.
        """
        outline = f"# Outline for {topic}\n\n"
        
        # Add each section from the template
        for section, subsections in template.items():
            outline += f"## {section}\n\n"
            
            # Add each subsection
            for subsection in subsections:
                outline += f"- {subsection}\n"
            
            outline += "\n"
        
        # Add notes about the outline
        outline += "## Notes\n\n"
        outline += "- Based on the template for this article type.\n"
        outline += "- Modify sections as needed for this specific topic.\n"
        outline += "- Use research data to fill in details for each section.\n"
        outline += "- Omit sections not relevant to this topic.\n"
        
        return outline
