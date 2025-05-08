"""
Knowledge Base Flow for CrewKB.

This module provides a flow that orchestrates the entire knowledge base article
creation process, including research, content creation, review, and quality assessment.
"""

import os
import json
import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field

import mlflow
from crewai.flow.flow import Flow, listen, start
from crewkb.utils.mlflow_utils import start_run, log_article_metrics, log_workflow_metrics

from crewkb.crews.research_crew import ResearchCrew
from crewkb.crews.content_creation_crew import ContentCreationCrew
from crewkb.crews.review_crew import ReviewCrew
from crewkb.models.article import Article
from crewkb.storage.storage_manager import StorageManager
from crewkb.utils.metrics_collector import MetricsCollector


class ArticleState(BaseModel):
    """State model for the knowledge base article creation flow."""
    
    # Input parameters
    topic: str
    article_type: str = "disease"  # disease, biomarker, or lab test
    
    # Phase outputs
    research_data: Optional[str] = None
    content: Optional[str] = None
    review_results: Optional[Dict[str, str]] = None
    
    # Quality metrics
    accuracy_score: Optional[float] = None
    readability_score: Optional[float] = None
    patient_relevance_score: Optional[float] = None
    overall_quality_score: Optional[float] = None
    
    # Risk assessment
    risk_areas: Optional[List[Dict[str, Any]]] = None
    confidence_level: Optional[str] = None
    
    # Output paths
    output_directory: str = "output"
    json_path: Optional[str] = None
    markdown_path: Optional[str] = None


class KnowledgeBaseFlow(Flow[ArticleState]):
    """Flow for creating a comprehensive knowledge base article."""

    @start()
    def get_user_input(self):
        """Get input from the user about the article topic and type."""
        print("\n=== Create Knowledge Base Article ===\n")

        # Get user input
        self.state.topic = input("What biomedical topic would you like to create an article for? ")

        # Get article type with validation
        while True:
            article_type = input("What type of article? (disease/biomarker/labtest) ").lower()
            if article_type in ["disease", "biomarker", "labtest"]:
                self.state.article_type = article_type
                break
            print("Please enter 'disease', 'biomarker', or 'labtest'")

        # Get output directory
        output_dir = input("Output directory (default: output): ")
        if output_dir:
            self.state.output_directory = output_dir

        print(f"\nCreating a {self.state.article_type} article on {self.state.topic}...\n")
        return self.state

    @listen(get_user_input)
    def research_phase(self, state):
        """Research the topic using the ResearchCrew."""
        print("Starting research phase...")
        
        # Create and run the research crew
        crew = ResearchCrew()
        result = crew.crew().kickoff(inputs={"topic": state.topic})
        
        # Store research data
        self.state.research_data = result.raw
        
        # Save research data to file
        os.makedirs(self.state.output_directory, exist_ok=True)
        research_file = os.path.join(
            self.state.output_directory, 
            f"{self.state.topic.replace(' ', '_')}_research.md"
        )
        with open(research_file, "w") as f:
            f.write(self.state.research_data)
        
        print(f"Research completed and saved to {research_file}")
        return self.state.research_data

    @listen(research_phase)
    def content_creation_phase(self, research_data):
        """Create content based on research data."""
        print("Starting content creation phase...")
        
        # Create and run the content creation crew
        crew = ContentCreationCrew(
            article_type=self.state.article_type,
            topic=self.state.topic,
            research_data=research_data
        )
        results = crew.run()
        
        # Extract content from results
        content = results.get("Content Writing Task", "")
        self.state.content = content
        
        # Save content to file
        content_file = os.path.join(
            self.state.output_directory, 
            f"{self.state.topic.replace(' ', '_')}.md"
        )
        with open(content_file, "w") as f:
            f.write(content)
        
        # Save citations to file
        citations = results.get("Citation Management Task", "")
        citations_file = os.path.join(
            self.state.output_directory, 
            f"{self.state.topic.replace(' ', '_')}_citations.md"
        )
        with open(citations_file, "w") as f:
            f.write(citations)
        
        print(f"Content created and saved to {content_file}")
        print(f"Citations saved to {citations_file}")
        return self.state.content

    @listen(content_creation_phase)
    def review_phase(self, content):
        """Review the content for accuracy, readability, and patient relevance."""
        print("Starting review phase...")
        
        # Create and run the review crew
        crew = ReviewCrew(
            article_type=self.state.article_type,
            topic=self.state.topic,
            content=content
        )
        results = crew.run()
        
        # Store review results
        self.state.review_results = results
        
        # Save review results to files
        review_dir = os.path.join(self.state.output_directory, "reviews")
        os.makedirs(review_dir, exist_ok=True)
        
        for task_name, result in results.items():
            # Clean up task name for filename
            clean_name = task_name.split("\n")[0].lower()
            clean_name = clean_name.replace(" ", "_").replace(":", "")
            
            # Save to file
            review_file = os.path.join(
                review_dir,
                f"{self.state.topic.replace(' ', '_')}_{clean_name}.md"
            )
            with open(review_file, "w") as f:
                f.write(result)
        
        print(f"Review completed and saved to {review_dir}")
        return results

    @listen(review_phase)
    def quality_assessment_phase(self, review_results):
        """Assess the quality of the article based on review results."""
        print("Starting quality assessment phase...")
        
        # Calculate quality metrics
        self.state.accuracy_score = self._calculate_accuracy_score(review_results)
        self.state.readability_score = self._calculate_readability_score(review_results)
        self.state.patient_relevance_score = self._calculate_patient_relevance_score(review_results)
        
        # Calculate overall quality score
        self.state.overall_quality_score = (
            self.state.accuracy_score * 0.5 +
            self.state.readability_score * 0.3 +
            self.state.patient_relevance_score * 0.2
        )
        
        # Perform risk assessment
        self.state.risk_areas = self._identify_risk_areas(review_results)
        
        # Determine confidence level
        self.state.confidence_level = self._determine_confidence_level(
            self.state.overall_quality_score,
            self.state.risk_areas
        )
        
        # Save quality assessment to file
        assessment_file = os.path.join(
            self.state.output_directory,
            f"{self.state.topic.replace(' ', '_')}_quality_assessment.json"
        )
        
        assessment_data = {
            "topic": self.state.topic,
            "article_type": self.state.article_type,
            "quality_metrics": {
                "accuracy_score": self.state.accuracy_score,
                "readability_score": self.state.readability_score,
                "patient_relevance_score": self.state.patient_relevance_score,
                "overall_quality_score": self.state.overall_quality_score
            },
            "risk_assessment": {
                "risk_areas": self.state.risk_areas,
                "confidence_level": self.state.confidence_level
            }
        }
        
        with open(assessment_file, "w") as f:
            json.dump(assessment_data, f, indent=2)
        
        print(f"Quality assessment completed and saved to {assessment_file}")
        return assessment_data

    @listen(quality_assessment_phase)
    def generate_final_output(self, assessment_data):
        """Generate the final knowledge base article."""
        print("Generating final output...")
        
        # Parse content into article sections
        article = self._parse_content_to_article(
            self.state.content,
            self.state.topic,
            self.state.article_type
        )
        
        # Add quality assessment metadata
        article.metadata.quality_score = self.state.overall_quality_score
        article.metadata.confidence_level = self.state.confidence_level
        article.metadata.risk_areas = self.state.risk_areas
        
        # Save article using storage manager
        storage_manager = StorageManager()
        
        # Save as JSON
        json_path = os.path.join(
            self.state.output_directory,
            f"{self.state.topic.replace(' ', '_')}.json"
        )
        storage_manager.save_json(article, json_path)
        self.state.json_path = json_path
        
        # Save as Markdown
        markdown_path = os.path.join(
            self.state.output_directory,
            f"{self.state.topic.replace(' ', '_')}_final.md"
        )
        storage_manager.save_markdown(article, markdown_path)
        self.state.markdown_path = markdown_path
        
        # Save metrics
        self._save_metrics()
        
        print(f"Final article saved as JSON: {json_path}")
        print(f"Final article saved as Markdown: {markdown_path}")
        
        return {
            "topic": self.state.topic,
            "article_type": self.state.article_type,
            "json_path": self.state.json_path,
            "markdown_path": self.state.markdown_path,
            "quality_score": self.state.overall_quality_score,
            "confidence_level": self.state.confidence_level
        }
    
    def _save_metrics(self):
        """Save metrics for the generated article."""
        # Create metrics collector
        metrics_dir = os.path.join(self.state.output_directory, "../metrics")
        metrics_collector = MetricsCollector(metrics_dir)
        
        # Prepare metrics data
        metrics_data = {
            "topic": self.state.topic,
            "article_type": self.state.article_type,
            "quality_metrics": {
                "accuracy_score": self.state.accuracy_score,
                "readability_score": self.state.readability_score,
                "patient_relevance_score": self.state.patient_relevance_score,
                "overall_quality_score": self.state.overall_quality_score
            },
            "risk_assessment": {
                "risk_areas": self.state.risk_areas,
                "confidence_level": self.state.confidence_level
            },
            "output_paths": {
                "json_path": self.state.json_path,
                "markdown_path": self.state.markdown_path
            }
        }
        
        # Add metrics to local storage
        metrics_collector.add_article_metrics(metrics_data)
        
        # Log metrics to MLflow
        with start_run(run_name=f"article_{self.state.topic}"):
            log_article_metrics(metrics_data)
            
            # Log workflow metrics
            workflow_metrics = {
                "workflow_completion_time": datetime.datetime.now().isoformat()
            }
            log_workflow_metrics("knowledge_base_flow", workflow_metrics)
        
        print(f"Article metrics saved to {metrics_dir}")

    def _calculate_accuracy_score(self, review_results: Dict[str, str]) -> float:
        """Calculate accuracy score based on review results."""
        # Implementation uses NLP to analyze the accuracy review
        # and extract a numerical score
        # For now, we'll use a simplified implementation
        accuracy_review = review_results.get("Review the knowledge base article", "")
        
        # Count issues by severity
        critical_issues = accuracy_review.lower().count("critical")
        major_issues = accuracy_review.lower().count("major")
        minor_issues = accuracy_review.lower().count("minor")
        
        # Calculate score (0-1 scale)
        base_score = 0.9  # Start with high score
        score = base_score - (critical_issues * 0.2) - (major_issues * 0.1) - (minor_issues * 0.02)
        return max(0.0, min(1.0, score))  # Clamp to 0-1 range
    
    def _calculate_readability_score(self, review_results: Dict[str, str]) -> float:
        """Calculate readability score based on review results."""
        # Similar implementation as accuracy score
        # but focused on readability metrics
        content_review = review_results.get("Review and edit the knowledge base article", "")
        
        # Count issues by severity
        major_issues = content_review.lower().count("major")
        moderate_issues = content_review.lower().count("moderate")
        minor_issues = content_review.lower().count("minor")
        
        # Calculate score (0-1 scale)
        base_score = 0.9  # Start with high score
        score = base_score - (major_issues * 0.15) - (moderate_issues * 0.08) - (minor_issues * 0.02)
        return max(0.0, min(1.0, score))  # Clamp to 0-1 range
    
    def _calculate_patient_relevance_score(self, review_results: Dict[str, str]) -> float:
        """Calculate patient relevance score based on review results."""
        # Similar implementation as other scores
        # but focused on patient relevance metrics
        patient_review = review_results.get("Review the knowledge base article from a patient's perspective", "")
        
        # Count issues by severity
        high_issues = patient_review.lower().count("high")
        medium_issues = patient_review.lower().count("medium")
        low_issues = patient_review.lower().count("low")
        
        # Calculate score (0-1 scale)
        base_score = 0.9  # Start with high score
        score = base_score - (high_issues * 0.15) - (medium_issues * 0.08) - (low_issues * 0.02)
        return max(0.0, min(1.0, score))  # Clamp to 0-1 range
    
    def _identify_risk_areas(self, review_results: Dict[str, str]) -> List[Dict[str, Any]]:
        """Identify risk areas based on review results."""
        risk_areas = []
        
        # Extract risk areas from accuracy review
        accuracy_review = review_results.get("Review the knowledge base article", "")
        if "critical" in accuracy_review.lower():
            # Extract critical issues
            # This would use more sophisticated NLP in a real implementation
            risk_areas.append({
                "type": "accuracy",
                "severity": "high",
                "description": "Critical accuracy issues identified"
            })
        
        # Extract risk areas from content review
        content_review = review_results.get("Review and edit the knowledge base article", "")
        if "major" in content_review.lower():
            risk_areas.append({
                "type": "readability",
                "severity": "medium",
                "description": "Major readability issues identified"
            })
        
        # Extract risk areas from patient perspective review
        patient_review = review_results.get("Review the knowledge base article from a patient's perspective", "")
        if "high" in patient_review.lower():
            risk_areas.append({
                "type": "patient_relevance",
                "severity": "high",
                "description": "High patient relevance issues identified"
            })
        
        return risk_areas
    
    def _determine_confidence_level(self, overall_score: float, risk_areas: List[Dict[str, Any]]) -> str:
        """Determine confidence level based on overall score and risk areas."""
        # Count high severity risk areas
        high_risk_count = sum(1 for area in risk_areas if area["severity"] == "high")
        
        # Determine confidence level
        if overall_score >= 0.9 and high_risk_count == 0:
            return "high"
        elif overall_score >= 0.7 and high_risk_count <= 1:
            return "medium"
        else:
            return "low"
    
    def _parse_content_to_article(self, content: str, topic: str, article_type: str) -> Article:
        """Parse content into article sections."""
        from crewkb.models.article import Article, ArticleMetadata
        from crewkb.models.sections import (
            Overview, Causes, Symptoms, Diagnosis, Treatment, Prevention, Prognosis
        )
        
        # This would use more sophisticated parsing in a real implementation
        # For now, we'll use a simplified approach based on section headers
        
        # Initialize sections with empty content
        overview = Overview(content="")
        causes = Causes(content="")
        symptoms = Symptoms(content="")
        diagnosis = Diagnosis(content="")
        treatment = Treatment(content="")
        prevention = Prevention(content="")
        prognosis = Prognosis(content="")
        
        # Parse content by looking for section headers
        lines = content.split("\n")
        current_section = None
        section_content = []
        
        for line in lines:
            # Check for section headers
            lower_line = line.lower()
            if "overview" in lower_line or "introduction" in lower_line:
                if current_section:
                    self._set_section_content(current_section, section_content)
                current_section = "overview"
                section_content = []
            elif "causes" in lower_line or "etiology" in lower_line:
                if current_section:
                    self._set_section_content(current_section, section_content)
                current_section = "causes"
                section_content = []
            elif "symptoms" in lower_line or "signs" in lower_line:
                if current_section:
                    self._set_section_content(current_section, section_content)
                current_section = "symptoms"
                section_content = []
            elif "diagnosis" in lower_line or "testing" in lower_line:
                if current_section:
                    self._set_section_content(current_section, section_content)
                current_section = "diagnosis"
                section_content = []
            elif "treatment" in lower_line or "management" in lower_line:
                if current_section:
                    self._set_section_content(current_section, section_content)
                current_section = "treatment"
                section_content = []
            elif "prevention" in lower_line:
                if current_section:
                    self._set_section_content(current_section, section_content)
                current_section = "prevention"
                section_content = []
            elif "prognosis" in lower_line or "outlook" in lower_line:
                if current_section:
                    self._set_section_content(current_section, section_content)
                current_section = "prognosis"
                section_content = []
            else:
                # Add line to current section
                if current_section:
                    section_content.append(line)
        
        # Set content for the last section
        if current_section:
            self._set_section_content(current_section, section_content)
        
        # Create article with parsed sections
        article = Article(
            title=topic,
            article_type=article_type,
            metadata=ArticleMetadata(
                created_at=datetime.datetime.now().isoformat(),
                updated_at=datetime.datetime.now().isoformat(),
                version="1.0.0",
                status="draft"
            ),
            overview=overview,
            causes=causes,
            symptoms=symptoms,
            diagnosis=diagnosis,
            treatment=treatment,
            prevention=prevention,
            prognosis=prognosis
        )
        
        return article
    
    def _set_section_content(self, section_name: str, lines: List[str]):
        """Set content for a specific section."""
        if section_name == "overview":
            self.overview = "\n".join(lines)
        elif section_name == "causes":
            self.causes = "\n".join(lines)
        elif section_name == "symptoms":
            self.symptoms = "\n".join(lines)
        elif section_name == "diagnosis":
            self.diagnosis = "\n".join(lines)
        elif section_name == "treatment":
            self.treatment = "\n".join(lines)
        elif section_name == "prevention":
            self.prevention = "\n".join(lines)
        elif section_name == "prognosis":
            self.prognosis = "\n".join(lines)


def kickoff():
    """Run the knowledge base flow."""
    # Start MLflow run
    with start_run(run_name="knowledge_base_flow"):
        flow = KnowledgeBaseFlow()
        result = flow.kickoff()
        
        # Log metrics to MLflow
        metrics_data = {
            "topic": result["topic"],
            "article_type": result["article_type"],
            "quality_metrics": {
                "quality_score": result["quality_score"],
            },
            "risk_assessment": {
                "confidence_level": result["confidence_level"]
            }
        }
        log_article_metrics(metrics_data)
        
        print("\n=== Knowledge Base Article Creation Complete ===")
        print(f"Topic: {result['topic']}")
        print(f"Article Type: {result['article_type']}")
        print(f"Quality Score: {result['quality_score']:.2f}")
        print(f"Confidence Level: {result['confidence_level']}")
        print(f"JSON Output: {result['json_path']}")
        print(f"Markdown Output: {result['markdown_path']}")


def plot():
    """Generate a visualization of the flow."""
    flow = KnowledgeBaseFlow()
    flow.plot("knowledge_base_flow")
    print("Flow visualization saved to knowledge_base_flow.html")


if __name__ == "__main__":
    kickoff()
