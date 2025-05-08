"""
MLflow utilities for CrewKB.

This module provides utilities for integrating MLflow with CrewKB.
"""

import os
import mlflow
from typing import Optional, Dict, Any, List

from crewkb.config import MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME, MLFLOW_ENABLED


def initialize_mlflow():
    """
    Initialize MLflow tracking.
    
    This function sets up MLflow tracking with the configured tracking URI
    and experiment name, and enables CrewAI autologging.
    """
    if not MLFLOW_ENABLED:
        return
    
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    
    # Enable CrewAI autologging
    mlflow.crewai.autolog()


def start_run(run_name: Optional[str] = None, tags: Optional[Dict[str, Any]] = None):
    """
    Start an MLflow run.
    
    Args:
        run_name: Optional name for the run
        tags: Optional tags for the run
    
    Returns:
        The MLflow run object
    """
    if not MLFLOW_ENABLED:
        return None
    
    return mlflow.start_run(run_name=run_name, tags=tags)


def log_article_metrics(metrics: Dict[str, Any]):
    """
    Log article metrics to MLflow.
    
    Args:
        metrics: Dictionary containing article metrics
    """
    if not MLFLOW_ENABLED:
        return
    
    # Log quality metrics
    quality_metrics = metrics.get("quality_metrics", {})
    for name, value in quality_metrics.items():
        if isinstance(value, (int, float)):
            mlflow.log_metric(name, value)
    
    # Log risk assessment
    risk_assessment = metrics.get("risk_assessment", {})
    mlflow.log_param("confidence_level", risk_assessment.get("confidence_level", "unknown"))
    
    # Log article metadata
    mlflow.log_param("topic", metrics.get("topic", "unknown"))
    mlflow.log_param("article_type", metrics.get("article_type", "unknown"))
    
    # Log risk areas as tags
    risk_areas = risk_assessment.get("risk_areas", [])
    for i, risk_area in enumerate(risk_areas):
        area_type = risk_area.get("type", "unknown")
        severity = risk_area.get("severity", "unknown")
        description = risk_area.get("description", "")
        
        mlflow.set_tag(f"risk_area_{i+1}_type", area_type)
        mlflow.set_tag(f"risk_area_{i+1}_severity", severity)
        mlflow.set_tag(f"risk_area_{i+1}_description", description)


def log_agent_metrics(agent_name: str, metrics: Dict[str, Any]):
    """
    Log agent-specific metrics to MLflow.
    
    Args:
        agent_name: Name of the agent
        metrics: Dictionary containing agent metrics
    """
    if not MLFLOW_ENABLED:
        return
    
    # Log agent metrics with agent name prefix
    for name, value in metrics.items():
        if isinstance(value, (int, float)):
            mlflow.log_metric(f"{agent_name}_{name}", value)


def log_workflow_metrics(workflow_name: str, metrics: Dict[str, Any]):
    """
    Log workflow-specific metrics to MLflow.
    
    Args:
        workflow_name: Name of the workflow
        metrics: Dictionary containing workflow metrics
    """
    if not MLFLOW_ENABLED:
        return
    
    # Log workflow metrics with workflow name prefix
    for name, value in metrics.items():
        if isinstance(value, (int, float)):
            mlflow.log_metric(f"{workflow_name}_{name}", value)


def log_article_artifacts(artifacts: Dict[str, str]):
    """
    Log article artifacts to MLflow.
    
    Args:
        artifacts: Dictionary mapping artifact names to file paths
    """
    if not MLFLOW_ENABLED:
        return
    
    # Log each artifact
    for name, path in artifacts.items():
        if os.path.exists(path):
            mlflow.log_artifact(path, name)
