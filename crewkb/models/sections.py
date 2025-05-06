"""
Section models for knowledge base articles.

This module defines the Pydantic models for the various sections of a
knowledge base article.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class OverviewSection(BaseModel):
    """Overview section of a knowledge base article."""

    content: str = Field(
        ...,
        description="General overview of the topic"
    )


class KeyFactsSection(BaseModel):
    """Key facts section of a knowledge base article."""

    facts: List[str] = Field(
        ...,
        description="List of key facts about the topic"
    )


class SymptomsSection(BaseModel):
    """Symptoms section of a knowledge base article."""

    common_symptoms: List[str] = Field(
        ...,
        description="Common symptoms"
    )
    rare_symptoms: Optional[List[str]] = Field(
        None,
        description="Rare symptoms"
    )
    emergency_symptoms: Optional[List[str]] = Field(
        None,
        description="Symptoms requiring immediate medical attention"
    )


class TypesSection(BaseModel):
    """Types section of a knowledge base article."""

    types: List[dict] = Field(
        ...,
        description="Different types or classifications"
    )
    classification_criteria: Optional[str] = Field(
        None,
        description="Criteria used for classification"
    )


class CausesSection(BaseModel):
    """Causes section of a knowledge base article."""

    primary_causes: List[str] = Field(
        ...,
        description="Primary causes"
    )
    secondary_causes: Optional[List[str]] = Field(
        None,
        description="Secondary or contributing causes"
    )
    mechanism: Optional[str] = Field(
        None,
        description="Mechanism of action or pathophysiology"
    )


class RiskFactorsSection(BaseModel):
    """Risk factors section of a knowledge base article."""

    risk_factors: List[dict] = Field(
        ...,
        description="Risk factors with descriptions"
    )
    preventable_factors: Optional[List[str]] = Field(
        None,
        description="Risk factors that can be modified or prevented"
    )
    non_preventable_factors: Optional[List[str]] = Field(
        None,
        description="Risk factors that cannot be modified"
    )


class LifestyleSection(BaseModel):
    """Lifestyle section of a knowledge base article."""

    recommendations: List[dict] = Field(
        ...,
        description="Lifestyle recommendations"
    )
    diet: Optional[str] = Field(
        None,
        description="Dietary recommendations"
    )
    exercise: Optional[str] = Field(
        None,
        description="Exercise recommendations"
    )
    habits_to_avoid: Optional[List[str]] = Field(
        None,
        description="Habits or activities to avoid"
    )


class DiagnosisSection(BaseModel):
    """Diagnosis section of a knowledge base article."""

    diagnostic_methods: List[dict] = Field(
        ...,
        description="Methods used for diagnosis"
    )
    common_tests: Optional[List[str]] = Field(
        None,
        description="Common tests used in diagnosis"
    )
    differential_diagnosis: Optional[List[str]] = Field(
        None,
        description="Conditions with similar symptoms"
    )


class PreventionSection(BaseModel):
    """Prevention section of a knowledge base article."""

    prevention_methods: List[dict] = Field(
        ...,
        description="Methods for prevention"
    )
    screening: Optional[str] = Field(
        None,
        description="Screening recommendations"
    )
    vaccines: Optional[str] = Field(
        None,
        description="Vaccine information if applicable"
    )


class SpecialistToVisitSection(BaseModel):
    """Specialist to visit section of a knowledge base article."""

    primary_specialists: List[str] = Field(
        ...,
        description="Primary specialists to consult"
    )
    when_to_see_doctor: str = Field(
        ...,
        description="When to seek medical attention"
    )
    questions_to_ask: Optional[List[str]] = Field(
        None,
        description="Questions to ask the healthcare provider"
    )


class TreatmentSection(BaseModel):
    """Treatment section of a knowledge base article."""

    treatment_approaches: List[dict] = Field(
        ...,
        description="Different treatment approaches"
    )
    medications: Optional[List[dict]] = Field(
        None,
        description="Medications used in treatment"
    )
    procedures: Optional[List[dict]] = Field(
        None,
        description="Medical procedures used in treatment"
    )
    effectiveness: Optional[str] = Field(
        None,
        description="Information about treatment effectiveness"
    )


class HomeCareSection(BaseModel):
    """Home care section of a knowledge base article."""

    home_care_tips: List[dict] = Field(
        ...,
        description="Tips for managing at home"
    )
    self_care: Optional[str] = Field(
        None,
        description="Self-care recommendations"
    )
    caregiver_tips: Optional[str] = Field(
        None,
        description="Tips for caregivers"
    )


class LivingWithSection(BaseModel):
    """Living with section of a knowledge base article."""

    daily_management: str = Field(
        ...,
        description="Daily management strategies"
    )
    long_term_outlook: str = Field(
        ...,
        description="Long-term outlook and prognosis"
    )
    coping_strategies: Optional[List[str]] = Field(
        None,
        description="Strategies for coping"
    )
    support_resources: Optional[List[dict]] = Field(
        None,
        description="Support groups and resources"
    )


class ComplicationsSection(BaseModel):
    """Complications section of a knowledge base article."""

    potential_complications: List[dict] = Field(
        ...,
        description="Potential complications"
    )
    warning_signs: Optional[List[str]] = Field(
        None,
        description="Warning signs of complications"
    )
    long_term_effects: Optional[str] = Field(
        None,
        description="Long-term effects"
    )


class AlternativeTherapiesSection(BaseModel):
    """Alternative therapies section of a knowledge base article."""

    therapies: List[dict] = Field(
        ...,
        description="Alternative therapies"
    )
    evidence_level: Optional[str] = Field(
        None,
        description="Level of scientific evidence"
    )
    precautions: Optional[List[str]] = Field(
        None,
        description="Precautions and warnings"
    )


class FAQsSection(BaseModel):
    """FAQs section of a knowledge base article."""

    questions: List[dict] = Field(
        ...,
        description="Frequently asked questions and answers"
    )


class ReferencesSection(BaseModel):
    """References section of a knowledge base article."""

    citations: List[str] = Field(
        ...,
        description="List of citations and references"
    )
    further_reading: Optional[List[dict]] = Field(
        None,
        description="Suggested further reading"
    )
