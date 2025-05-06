"""
Article model for knowledge base articles.

This module defines the Pydantic model for a complete knowledge base article,
incorporating all the section models.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from crewkb.models.sections import (
    OverviewSection,
    KeyFactsSection,
    SymptomsSection,
    TypesSection,
    CausesSection,
    RiskFactorsSection,
    LifestyleSection,
    DiagnosisSection,
    PreventionSection,
    SpecialistToVisitSection,
    TreatmentSection,
    HomeCareSection,
    LivingWithSection,
    ComplicationsSection,
    AlternativeTherapiesSection,
    FAQsSection,
    ReferencesSection,
)


class Article(BaseModel):
    """
    Knowledge base article model.

    This model represents a complete knowledge base article with all sections.
    """

    # Metadata
    title: str = Field(
        ...,
        description="The main heading of the article."
    )
    subtitle: str = Field(
        ...,
        description="A concise introductory phrase summarizing the condition."
    )
    keywords: List[str] = Field(
        ...,
        description="Keywords associated with the article for searchability."
    )
    article_type: str = Field(
        ...,
        description="Type of article (disease, biomarker, labtest)"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Date and time when the article was created."
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Date and time when the article was last updated."
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the article."
    )

    # Content sections
    overview: OverviewSection = Field(
        ...,
        description="Overview section of the article."
    )
    key_facts: KeyFactsSection = Field(
        ...,
        description="Key Facts section of the article."
    )
    symptoms: Optional[SymptomsSection] = Field(
        None,
        description="Symptoms section of the article."
    )
    types: Optional[TypesSection] = Field(
        None,
        description="Types section of the article."
    )
    causes: Optional[CausesSection] = Field(
        None,
        description="Causes section of the article."
    )
    risk_factors: Optional[RiskFactorsSection] = Field(
        None,
        description="Risk Factors section of the article."
    )
    lifestyle: Optional[LifestyleSection] = Field(
        None,
        description="Lifestyle section of the article."
    )
    diagnosis: Optional[DiagnosisSection] = Field(
        None,
        description="Diagnosis section of the article."
    )
    prevention: Optional[PreventionSection] = Field(
        None,
        description="Prevention section of the article."
    )
    specialist_to_visit: Optional[SpecialistToVisitSection] = Field(
        None,
        description="Specialist to Visit section of the article."
    )
    treatment: Optional[TreatmentSection] = Field(
        None,
        description="Treatment section of the article."
    )
    home_care: Optional[HomeCareSection] = Field(
        None,
        description="Home-Care section of the article."
    )
    living_with: Optional[LivingWithSection] = Field(
        None,
        description="Living With section of the article."
    )
    complications: Optional[ComplicationsSection] = Field(
        None,
        description="Complications section of the article."
    )
    alternative_therapies: Optional[AlternativeTherapiesSection] = Field(
        None,
        description="Alternative Therapies section of the article."
    )
    faqs: Optional[FAQsSection] = Field(
        None,
        description="FAQs section of the article."
    )
    references: ReferencesSection = Field(
        ...,
        description="References section of the article."
    )

    @validator("article_type")
    def validate_article_type(cls, v):
        """Validate that the article type is one of the allowed values."""
        allowed_types = ["disease", "biomarker", "labtest"]
        if v not in allowed_types:
            raise ValueError(
                f"Article type must be one of {allowed_types}, got {v}"
            )
        return v

    def to_markdown(self) -> str:
        """
        Convert the article to Markdown format.

        Returns:
            A string containing the article in Markdown format.
        """
        md = []

        # Title and subtitle
        md.append(f"# {self.title}")
        md.append(f"*{self.subtitle}*")
        md.append("")

        # Overview
        md.append("## Overview")
        md.append(self.overview.content)
        md.append("")

        # Key Facts
        md.append("## Key Facts")
        for fact in self.key_facts.facts:
            md.append(f"- {fact}")
        md.append("")

        # Symptoms (if available)
        if self.symptoms:
            md.append("## Symptoms")
            md.append("### Common Symptoms")
            for symptom in self.symptoms.common_symptoms:
                md.append(f"- {symptom}")
            md.append("")

            if self.symptoms.rare_symptoms:
                md.append("### Rare Symptoms")
                for symptom in self.symptoms.rare_symptoms:
                    md.append(f"- {symptom}")
                md.append("")

            if self.symptoms.emergency_symptoms:
                md.append("### Emergency Symptoms")
                md.append(
                    "*Seek immediate medical attention if you experience any "
                    "of the following:*"
                )
                for symptom in self.symptoms.emergency_symptoms:
                    md.append(f"- {symptom}")
                md.append("")

        # Add other sections similarly...
        # This is a simplified implementation; a complete implementation would
        # include all sections.

        # References
        md.append("## References")
        for i, citation in enumerate(self.references.citations, 1):
            md.append(f"{i}. {citation}")
        md.append("")

        if self.references.further_reading:
            md.append("### Further Reading")
            for reading in self.references.further_reading:
                md.append(f"- [{reading.get('title', 'Untitled')}]"
                          f"({reading.get('url', '#')})")
            md.append("")

        # Metadata
        md.append("---")
        md.append(f"*Last updated: {self.updated_at.strftime('%Y-%m-%d')}*")
        md.append(f"*Version: {self.version}*")

        return "\n".join(md)

    class Config:
        """Pydantic model configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
