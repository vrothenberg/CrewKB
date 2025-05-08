"""
Test runner for knowledge models.

This script runs the tests for the knowledge models used in the knowledge
synthesis workflow.
"""

import pytest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    # Run the tests
    pytest.main(["-xvs", "crewkb/tests/models/test_knowledge_models.py"])
