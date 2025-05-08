#!/usr/bin/env python
"""
Test script for MLflow integration in CrewKB.

This script tests the MLflow integration by logging some test metrics
and verifying that they appear in the MLflow UI.
"""

import os
import sys
import time
import mlflow
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from crewkb.utils.mlflow_utils import initialize_mlflow, start_run, log_article_metrics


def test_mlflow_integration():
    """Test MLflow integration by logging test metrics."""
    print("Testing MLflow integration...")
    
    # Initialize MLflow
    initialize_mlflow()
    
    # Create test metrics
    test_metrics = {
        "topic": "Test Topic",
        "article_type": "test",
        "quality_metrics": {
            "accuracy_score": 0.85,
            "readability_score": 0.92,
            "patient_relevance_score": 0.78,
            "overall_quality_score": 0.87
        },
        "risk_assessment": {
            "confidence_level": "medium",
            "risk_areas": [
                {
                    "type": "accuracy",
                    "severity": "medium",
                    "description": "Test risk area"
                }
            ]
        }
    }
    
    # Log metrics to MLflow
    with start_run(run_name=f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        log_article_metrics(test_metrics)
        
        # Log some additional metrics directly with MLflow
        mlflow.log_metric("test_metric", 1.0)
        mlflow.log_param("test_param", "test_value")
        mlflow.set_tag("test_tag", "test_value")
        
        # Log a series of metrics
        for i in range(10):
            mlflow.log_metric("test_series", i * 0.1, step=i)
            time.sleep(0.1)  # Small delay to see the metrics in the UI
    
    print("Test metrics logged to MLflow.")
    print("You can view them in the MLflow UI at http://localhost:5000")


if __name__ == "__main__":
    test_mlflow_integration()
