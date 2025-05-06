"""
LLM Factory for CrewKB.

This module provides a factory function for creating LLM instances
with the appropriate configuration for Gemini models.
"""

from crewai import LLM
from typing import Optional

from crewkb.config import DEFAULT_LLM_MODEL, DEFAULT_LLM_TEMPERATURE


def create_llm(model: Optional[str] = None, temperature: Optional[float] = None) -> LLM:
    """
    Create an LLM instance based on configuration.
    
    Args:
        model: Optional model name override
        temperature: Optional temperature override
        
    Returns:
        Configured LLM instance
    """
    # Use provided values or defaults from config
    model = model or DEFAULT_LLM_MODEL
    temperature = temperature if temperature is not None else DEFAULT_LLM_TEMPERATURE
    
    # Create LLM with appropriate configuration
    return LLM(
        model=model,
        temperature=temperature
    )
