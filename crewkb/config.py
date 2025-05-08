"""
Configuration module for the CrewKB project.

This module handles loading configuration from environment variables,
configuration files, and default values.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent.absolute()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "output")))
KNOWLEDGE_DIR = Path(os.getenv("KNOWLEDGE_DIR", str(BASE_DIR / "knowledge")))

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
KNOWLEDGE_DIR.mkdir(exist_ok=True, parents=True)

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY")
SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "CrewKB")
MLFLOW_ENABLED = os.getenv("MLFLOW_ENABLED", "True").lower() == "true"

# LLM configuration
DEFAULT_LLM_MODEL = os.getenv(
    "DEFAULT_LLM_MODEL", "gemini/gemini-2.0-flash-exp"
)
DEFAULT_LLM_TEMPERATURE = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.7"))

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = Path(os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "crewkb.log")))

# Ensure log directory exists
LOG_FILE.parent.mkdir(exist_ok=True, parents=True)

# Article types and their configurations
ARTICLE_TYPES = {
    "disease": {
        "workflow": "disease_workflow",
        "template": "disease_template",
        "description": "Knowledge base article about a disease or condition",
    },
    "biomarker": {
        "workflow": "biomarker_workflow",
        "template": "biomarker_template",
        "description": "Knowledge base article about a biomarker",
    },
    "labtest": {
        "workflow": "labtest_workflow",
        "template": "labtest_template",
        "description": "Knowledge base article about a laboratory test",
    },
}

# Search configuration
SEARCH_CONFIG = {
    "max_results": int(os.getenv("SEARCH_MAX_RESULTS", "10")),
    "timeout": int(os.getenv("SEARCH_TIMEOUT", "30")),
    "sources": [
        "google",
        "pubmed",
        "arxiv",
        "semantic_scholar",
    ],
}

# Agent configuration
AGENT_CONFIG = {
    "max_iterations": int(os.getenv("AGENT_MAX_ITERATIONS", "10")),
    "max_execution_time": int(os.getenv("AGENT_MAX_EXECUTION_TIME", "300")),
    "verbose": os.getenv("AGENT_VERBOSE", "False").lower() == "true",
}


def get_api_key(service: str) -> Optional[str]:
    """
    Get the API key for a specific service.

    Args:
        service: The name of the service (e.g., "gemini", "serper").

    Returns:
        The API key if available, None otherwise.
    """
    keys = {
        "gemini": GEMINI_API_KEY,
        "serper": SERPER_API_KEY,
        "pubmed": PUBMED_API_KEY,
        "semantic_scholar": SEMANTIC_SCHOLAR_API_KEY,
    }
    return keys.get(service.lower())


def get_article_config(article_type: str) -> Dict[str, Any]:
    """
    Get the configuration for a specific article type.

    Args:
        article_type: The type of article (e.g., "disease", "biomarker").

    Returns:
        A dictionary containing the configuration for the article type.
    """
    return ARTICLE_TYPES.get(article_type.lower(), ARTICLE_TYPES["disease"])


def validate_config() -> bool:
    """
    Validate the configuration.

    Returns:
        True if the configuration is valid, False otherwise.
    """
    # Check if required API keys are available
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY is not set.")
        return False

    # Check if output directory is writable
    try:
        test_file = OUTPUT_DIR / ".test_write"
        test_file.touch()
        test_file.unlink()
    except Exception as e:
        print(f"Error: Output directory is not writable: {e}")
        return False

    return True
