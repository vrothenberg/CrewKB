# MLflow Integration for CrewKB

This document provides information on how to use MLflow with CrewKB for tracking experiments, logging metrics, and visualizing agent performance.

## Overview

MLflow is an open-source platform for managing the end-to-end machine learning lifecycle. In CrewKB, MLflow is used to:

1. Track experiments and runs
2. Log metrics about article quality and agent performance
3. Visualize the knowledge base article creation process
4. Monitor the behavior of CrewAI agents

## Setup

### Prerequisites

- MLflow is installed as part of the CrewKB dependencies
- A running MLflow server (started with `mlflow server`)

### Configuration

MLflow integration is configured through environment variables in the `.env` file:

```
# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=CrewKB
MLFLOW_ENABLED=True
```

- `MLFLOW_TRACKING_URI`: The URI of the MLflow tracking server (default: http://localhost:5000)
- `MLFLOW_EXPERIMENT_NAME`: The name of the MLflow experiment (default: CrewKB)
- `MLFLOW_ENABLED`: Whether MLflow integration is enabled (default: True)

## Starting the MLflow Server

To start the MLflow server, run the following command:

```bash
mlflow server
```

This will start the MLflow server on http://localhost:5000 by default.

## Testing the MLflow Integration

A test script is provided to verify the MLflow integration:

```bash
./test_mlflow_integration.py
```

This script logs test metrics to MLflow and verifies that they appear in the MLflow UI.

## Viewing MLflow Experiments

To view the MLflow experiments, open the MLflow UI in your browser:

```
http://localhost:5000
```

## MLflow Integration Components

### MLflow Utility Module

The `crewkb/utils/mlflow_utils.py` module provides utilities for integrating MLflow with CrewKB:

- `initialize_mlflow()`: Initialize MLflow tracking
- `start_run()`: Start an MLflow run
- `log_article_metrics()`: Log article metrics to MLflow
- `log_agent_metrics()`: Log agent-specific metrics to MLflow
- `log_workflow_metrics()`: Log workflow-specific metrics to MLflow
- `log_article_artifacts()`: Log article artifacts to MLflow

### CrewAI Autologging

CrewKB uses MLflow's CrewAI autologging feature to automatically log agent activities:

```python
mlflow.crewai.autolog()
```

This captures agent interactions, tool usage, and other relevant information.

### Metrics Logging

The `MetricsCollector` class is integrated with MLflow to log article metrics:

```python
from crewkb.utils.mlflow_utils import log_article_metrics

# In the add_article_metrics method
log_article_metrics(metrics_data)
```

### Workflow Integration

The `KnowledgeBaseFlow` class is integrated with MLflow to log workflow metrics:

```python
from crewkb.utils.mlflow_utils import start_run, log_article_metrics, log_workflow_metrics

# In the _save_metrics method
with start_run(run_name=f"article_{self.state.topic}"):
    log_article_metrics(metrics_data)
    log_workflow_metrics("knowledge_base_flow", workflow_metrics)
```

## Logged Metrics

The following metrics are logged to MLflow:

### Article Metrics

- **Quality Metrics**:
  - `accuracy_score`: Accuracy of the article content
  - `readability_score`: Readability of the article content
  - `patient_relevance_score`: Relevance of the article to patients
  - `overall_quality_score`: Overall quality score of the article

- **Risk Assessment**:
  - `confidence_level`: Confidence level in the article content
  - `risk_areas`: Areas of risk identified in the article

- **Metadata**:
  - `topic`: Topic of the article
  - `article_type`: Type of article (disease, biomarker, labtest)

### Agent Metrics

- **Performance Metrics**:
  - `execution_time`: Time taken to execute agent tasks
  - `token_usage`: Number of tokens used by the agent
  - `success_rate`: Success rate of agent tasks

### Workflow Metrics

- **Process Metrics**:
  - `workflow_completion_time`: Time taken to complete the workflow
  - `phase_execution_times`: Time taken to execute each phase of the workflow

## Best Practices

1. **Run the MLflow Server**: Always ensure the MLflow server is running before starting CrewKB.
2. **Check the MLflow UI**: Regularly check the MLflow UI to monitor the performance of your agents and workflows.
3. **Use Meaningful Run Names**: When starting a run, use a meaningful name that describes the purpose of the run.
4. **Log Relevant Metrics**: Log metrics that are relevant to the task at hand and that will help you understand the performance of your agents and workflows.
5. **Use Tags**: Use tags to categorize runs and make them easier to find in the MLflow UI.

## Troubleshooting

### MLflow Server Not Running

If the MLflow server is not running, you will see an error message when trying to log metrics. Start the MLflow server with:

```bash
mlflow server
```

### MLflow Integration Not Working

If the MLflow integration is not working, check the following:

1. Ensure the MLflow server is running
2. Check the `MLFLOW_TRACKING_URI` environment variable is set correctly
3. Verify that `MLFLOW_ENABLED` is set to `True`
4. Check the MLflow logs for any error messages

### No Metrics Showing in MLflow UI

If no metrics are showing in the MLflow UI, check the following:

1. Ensure the MLflow server is running
2. Check that the metrics are being logged correctly
3. Verify that the MLflow experiment name is set correctly
4. Check the MLflow logs for any error messages

## References

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [CrewAI Documentation](https://docs.crewai.com/)
- [MLflow Python API](https://mlflow.org/docs/latest/python_api/index.html)
