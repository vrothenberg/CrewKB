"""
Metrics Collector for CrewKB.

This module provides a metrics collector for tracking and analyzing the quality
of generated knowledge base articles.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from crewkb.utils.mlflow_utils import log_article_metrics


class MetricsCollector:
    """
    Collect and store metrics for knowledge base article creation.
    
    This class provides functionality for tracking and analyzing the quality
    of generated knowledge base articles. It stores metrics in a JSON file
    and can generate dashboards for visualizing the metrics.
    """
    
    def __init__(self, output_dir: str = "metrics"):
        """
        Initialize the metrics collector.
        
        Args:
            output_dir: Directory to store metrics data
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize metrics file if it doesn't exist
        self.metrics_file = os.path.join(output_dir, "article_metrics.json")
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, "w") as f:
                json.dump([], f)
    
    def add_article_metrics(self, metrics: Dict[str, Any]):
        """
        Add metrics for a new article.
        
        Args:
            metrics: Dictionary containing article metrics
        """
        # Load existing metrics
        with open(self.metrics_file, "r") as f:
            all_metrics = json.load(f)
        
        # Add timestamp
        metrics["timestamp"] = datetime.datetime.now().isoformat()
        
        # Add new metrics
        all_metrics.append(metrics)
        
        # Save updated metrics
        with open(self.metrics_file, "w") as f:
            json.dump(all_metrics, f, indent=2)
        
        # Log metrics to MLflow
        log_article_metrics(metrics)
    
    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """
        Get all article metrics.
        
        Returns:
            List of dictionaries containing article metrics
        """
        with open(self.metrics_file, "r") as f:
            return json.load(f)
    
    def get_article_metrics(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific article.
        
        Args:
            topic: Topic of the article
            
        Returns:
            Dictionary containing article metrics, or None if not found
        """
        all_metrics = self.get_all_metrics()
        
        # Find metrics for the specified topic
        for metrics in all_metrics:
            if metrics.get("topic", "").lower() == topic.lower():
                return metrics
        
        return None
    
    def get_average_quality_score(self) -> float:
        """
        Get the average overall quality score across all articles.
        
        Returns:
            Average overall quality score
        """
        all_metrics = self.get_all_metrics()
        
        if not all_metrics:
            return 0.0
        
        # Calculate average quality score
        total_score = 0.0
        count = 0
        
        for metrics in all_metrics:
            quality_metrics = metrics.get("quality_metrics", {})
            overall_score = quality_metrics.get("overall_quality_score")
            
            if overall_score is not None:
                total_score += overall_score
                count += 1
        
        return total_score / count if count > 0 else 0.0
    
    def get_quality_score_by_article_type(self) -> Dict[str, float]:
        """
        Get the average quality score by article type.
        
        Returns:
            Dictionary mapping article types to average quality scores
        """
        all_metrics = self.get_all_metrics()
        
        # Calculate average quality score by article type
        scores_by_type = {}
        counts_by_type = {}
        
        for metrics in all_metrics:
            article_type = metrics.get("article_type", "unknown")
            quality_metrics = metrics.get("quality_metrics", {})
            overall_score = quality_metrics.get("overall_quality_score")
            
            if overall_score is not None:
                scores_by_type[article_type] = scores_by_type.get(article_type, 0.0) + overall_score
                counts_by_type[article_type] = counts_by_type.get(article_type, 0) + 1
        
        # Calculate averages
        avg_scores_by_type = {}
        for article_type, total_score in scores_by_type.items():
            count = counts_by_type.get(article_type, 0)
            avg_scores_by_type[article_type] = total_score / count if count > 0 else 0.0
        
        return avg_scores_by_type
    
    def get_risk_area_counts(self) -> Dict[str, int]:
        """
        Get counts of different risk areas across all articles.
        
        Returns:
            Dictionary mapping risk area types to counts
        """
        all_metrics = self.get_all_metrics()
        
        # Count risk areas by type
        risk_area_counts = {}
        
        for metrics in all_metrics:
            risk_assessment = metrics.get("risk_assessment", {})
            risk_areas = risk_assessment.get("risk_areas", [])
            
            for risk_area in risk_areas:
                risk_type = risk_area.get("type", "unknown")
                risk_area_counts[risk_type] = risk_area_counts.get(risk_type, 0) + 1
        
        return risk_area_counts
    
    def generate_dashboard(self) -> str:
        """
        Generate a dashboard of article metrics.
        
        Returns:
            Path to the generated dashboard HTML file
        """
        # Load metrics
        all_metrics = self.get_all_metrics()
        
        # Get summary statistics
        avg_quality_score = self.get_average_quality_score()
        scores_by_type = self.get_quality_score_by_article_type()
        risk_area_counts = self.get_risk_area_counts()
        
        # Generate dashboard HTML
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CrewKB Metrics Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { color: #333; }
                .summary { display: flex; justify-content: space-between; margin-bottom: 20px; }
                .summary-card { background-color: #f5f5f5; border-radius: 5px; padding: 15px; width: 30%; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .chart { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>CrewKB Metrics Dashboard</h1>
            
            <div class="summary">
                <div class="summary-card">
                    <h3>Total Articles</h3>
                    <p>{total_articles}</p>
                </div>
                <div class="summary-card">
                    <h3>Average Quality Score</h3>
                    <p>{avg_quality_score:.2f}</p>
                </div>
                <div class="summary-card">
                    <h3>Most Common Risk</h3>
                    <p>{most_common_risk}</p>
                </div>
            </div>
            
            <h2>Quality Scores by Article Type</h2>
            <table>
                <tr>
                    <th>Article Type</th>
                    <th>Average Quality Score</th>
                </tr>
        """.format(
            total_articles=len(all_metrics),
            avg_quality_score=avg_quality_score,
            most_common_risk=max(risk_area_counts.items(), key=lambda x: x[1])[0] if risk_area_counts else "None"
        )
        
        # Add rows for each article type
        for article_type, score in scores_by_type.items():
            dashboard_html += f"""
                <tr>
                    <td>{article_type}</td>
                    <td>{score:.2f}</td>
                </tr>
            """
        
        dashboard_html += """
            </table>
            
            <h2>Risk Area Counts</h2>
            <table>
                <tr>
                    <th>Risk Area</th>
                    <th>Count</th>
                </tr>
        """
        
        # Add rows for each risk area
        for risk_type, count in risk_area_counts.items():
            dashboard_html += f"""
                <tr>
                    <td>{risk_type}</td>
                    <td>{count}</td>
                </tr>
            """
        
        dashboard_html += """
            </table>
            
            <h2>Article Quality Metrics</h2>
            <table>
                <tr>
                    <th>Topic</th>
                    <th>Type</th>
                    <th>Accuracy</th>
                    <th>Readability</th>
                    <th>Patient Relevance</th>
                    <th>Overall Quality</th>
                    <th>Confidence</th>
                    <th>Date</th>
                </tr>
        """
        
        # Add rows for each article
        for metrics in all_metrics:
            quality_metrics = metrics.get("quality_metrics", {})
            risk_assessment = metrics.get("risk_assessment", {})
            
            dashboard_html += f"""
                <tr>
                    <td>{metrics.get('topic', '')}</td>
                    <td>{metrics.get('article_type', '')}</td>
                    <td>{quality_metrics.get('accuracy_score', 0):.2f}</td>
                    <td>{quality_metrics.get('readability_score', 0):.2f}</td>
                    <td>{quality_metrics.get('patient_relevance_score', 0):.2f}</td>
                    <td>{quality_metrics.get('overall_quality_score', 0):.2f}</td>
                    <td>{risk_assessment.get('confidence_level', '')}</td>
                    <td>{metrics.get('timestamp', '')}</td>
                </tr>
            """
        
        dashboard_html += """
            </table>
        </body>
        </html>
        """
        
        # Save dashboard
        dashboard_file = os.path.join(self.output_dir, "dashboard.html")
        with open(dashboard_file, "w") as f:
            f.write(dashboard_html)
        
        return dashboard_file
