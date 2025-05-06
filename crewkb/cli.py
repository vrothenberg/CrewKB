#!/usr/bin/env python
"""
CrewKB CLI - Command-line interface for the CrewKB knowledge base
creation system.
"""

import os
import typer
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

from crewkb.crews import ResearchCrew, ContentCreationCrew, ReviewCrew
from crewkb.flows import KnowledgeBaseFlow
from crewkb.utils.metrics_collector import MetricsCollector

# Load environment variables from .env file
load_dotenv()

app = typer.Typer(
    name="crewkb",
    help="CrewKB - A knowledge base creation system for biomedical topics.",
    add_completion=False,
)


@app.command()
def create(
    topic: str = typer.Argument(
        ..., help="The topic for the knowledge base article."
    ),
    article_type: str = typer.Option(
        "disease",
        "--type", "-t",
        help="Type of article (disease, biomarker, labtest)."
    ),
    output_dir: Optional[Path] = typer.Option(
        None, 
        "--output", "-o", 
        help="Directory to save the output files."
    ),
    research_file: Optional[Path] = typer.Option(
        None,
        "--research", "-r",
        help="Path to a file containing research data."
    ),
    verbose: bool = typer.Option(
        True, 
        "--verbose", "-v", 
        help="Enable verbose output."
    ),
):
    """
    Create a new knowledge base article on the specified topic.
    
    This command uses specialized AI agents to create a knowledge base article
    based on research data. If no research data is provided, it will first
    research the topic and then create the article.
    """
    typer.echo(f"Creating {article_type} knowledge base article on: {topic}")
    
    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        typer.echo(
            "Error: GEMINI_API_KEY environment variable not set. "
            "Please set it to your Google Gemini API key."
        )
        raise typer.Exit(1)
    
    # Set default output directory if not specified
    if not output_dir:
        output_dir = Path("output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get research data
    research_data = ""
    if research_file:
        # Read research data from file
        typer.echo(f"Reading research data from: {research_file}")
        try:
            with open(research_file, 'r') as f:
                research_data = f.read()
        except Exception as e:
            typer.echo(f"Error reading research file: {str(e)}")
            raise typer.Exit(1)
    else:
        # Perform research
        typer.echo(f"Researching topic: {topic}")
        try:
            crew = ResearchCrew(topic=topic)
            result = crew.crew.kickoff(inputs={"topic": topic})
            research_data = result.raw
            
            # Save research data
            research_output = output_dir / f"{topic.replace(' ', '_')}_research.md"
            with open(research_output, 'w') as f:
                f.write(research_data)
            typer.echo(f"Research saved to: {research_output}")
        except Exception as e:
            typer.echo(f"Error during research: {str(e)}")
            raise typer.Exit(1)
    
    # Create content
    typer.echo("Creating content...")
    try:
        crew = ContentCreationCrew(
            article_type=article_type,
            topic=topic,
            research_data=research_data
        )
        results = crew.run()
        
        # Save content
        content_output = output_dir / f"{topic.replace(' ', '_')}.md"
        with open(content_output, 'w') as f:
            f.write(results.get("content_writing_task", ""))
        typer.echo(f"Content saved to: {content_output}")
        
        # Save citations
        citations_output = output_dir / f"{topic.replace(' ', '_')}_citations.md"
        with open(citations_output, 'w') as f:
            f.write(results.get("citation_management_task", ""))
        typer.echo(f"Citations saved to: {citations_output}")
        
    except Exception as e:
        typer.echo(f"Error during content creation: {str(e)}")
        raise typer.Exit(1)


@app.command()
def research(
    topic: str = typer.Argument(
        ..., help="The biomedical topic to research."
    ),
    output_file: Optional[Path] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output file path for the research results."
    ),
    verbose: bool = typer.Option(
        True, 
        "--verbose", "-v", 
        help="Enable verbose output."
    ),
):
    """
    Research a biomedical topic using AI agents.
    
    This command uses specialized AI agents to research a biomedical topic
    and synthesize the findings into a comprehensive report.
    """
    typer.echo(f"Researching: {topic}")
    
    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        typer.echo(
            "Error: GEMINI_API_KEY environment variable not set. "
            "Please set it to your Google Gemini API key."
        )
        raise typer.Exit(1)
    
    if not os.getenv("SERPER_API_KEY"):
        typer.echo(
            "Warning: SERPER_API_KEY environment variable not set. "
            "Web search functionality will be limited."
        )
    
    if not os.getenv("ENTREZ_EMAIL"):
        typer.echo(
            "Warning: ENTREZ_EMAIL environment variable not set. "
            "PubMed search functionality will be limited."
        )
    
    # Create and run the research crew
    try:
        crew = ResearchCrew(topic=topic)
        result = crew.crew.kickoff(inputs={"topic": topic})
        
        # Save the result if output_file is specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(result.raw)
            typer.echo(f"Research saved to: {output_file}")
        else:
            typer.echo("\nResearch Results:\n")
            typer.echo(result.raw)
    
    except Exception as e:
        typer.echo(f"Error during research: {str(e)}")
        raise typer.Exit(1)


@app.command()
def list(
    article_type: Optional[str] = typer.Option(
        None, 
        "--type", "-t", 
        help="Filter by article type (disease, biomarker, labtest)."
    ),
    output_format: str = typer.Option(
        "table", 
        "--format", "-f", 
        help="Output format (table, json, markdown)."
    ),
):
    """
    List existing knowledge base articles.
    """
    typer.echo("Listing knowledge base articles")
    typer.echo("This functionality is not yet implemented.")
    # TODO: Implement article listing logic


@app.command()
def review(
    article_file: Path = typer.Argument(
        ..., help="The file containing the article to review."
    ),
    article_type: str = typer.Option(
        "disease",
        "--type", "-t",
        help="Type of article (disease, biomarker, labtest)."
    ),
    topic: Optional[str] = typer.Option(
        None, 
        "--topic", 
        help="The topic of the article. If not provided, will be extracted from the filename."
    ),
    output_dir: Optional[Path] = typer.Option(
        None, 
        "--output", "-o", 
        help="Directory to save the review results."
    ),
    verbose: bool = typer.Option(
        True, 
        "--verbose", "-v", 
        help="Enable verbose output."
    ),
):
    """
    Review a knowledge base article for accuracy, readability, and patient relevance.
    
    This command uses specialized AI agents to review a knowledge base article
    and provide feedback on its accuracy, readability, and patient relevance.
    It can also detect and resolve conflicts between different review perspectives.
    """
    # Check if article file exists
    if not article_file.exists():
        typer.echo(f"Error: Article file not found: {article_file}")
        raise typer.Exit(1)
    
    # Extract topic from filename if not provided
    if not topic:
        topic = article_file.stem.replace('_', ' ')
    
    typer.echo(f"Reviewing {article_type} knowledge base article on: {topic}")
    
    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        typer.echo(
            "Error: GEMINI_API_KEY environment variable not set. "
            "Please set it to your Google Gemini API key."
        )
        raise typer.Exit(1)
    
    # Set default output directory if not specified
    if not output_dir:
        output_dir = Path("output/reviews")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read article content
    try:
        with open(article_file, 'r') as f:
            article_content = f.read()
    except Exception as e:
        typer.echo(f"Error reading article file: {str(e)}")
        raise typer.Exit(1)
    
    # Create and run the review crew
    try:
        crew = ReviewCrew(
            article_type=article_type,
            topic=topic,
            content=article_content
        )
        results = crew.run()
        
        # Save review results
        for task_name, result in results.items():
            # Clean up task name for filename
            clean_name = task_name.split("\n")[0].lower()
            clean_name = clean_name.replace(" ", "_").replace(":", "")
            
            # Save to file
            output_file = output_dir / f"{topic.replace(' ', '_')}_{clean_name}.md"
            with open(output_file, 'w') as f:
                f.write(result)
            typer.echo(f"Review saved to: {output_file}")
        
        # Check if conflicts were detected and resolved
        if "conflict_resolution" in results:
            typer.echo("\nConflicts were detected and resolved.")
        
    except Exception as e:
        typer.echo(f"Error during review: {str(e)}")
        raise typer.Exit(1)


@app.command()
def export(
    topic: str = typer.Argument(
        ..., help="The topic of the article to export."
    ),
    format: str = typer.Option(
        "markdown",
        "--format", "-f",
        help="Export format (markdown, json, html)."
    ),
    output_file: Optional[Path] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output file path."
    ),
):
    """
    Export a knowledge base article to a specific format.
    """
    typer.echo(f"Exporting article on {topic} to {format}")
    typer.echo("This functionality is not yet implemented.")
    # TODO: Implement article export logic


@app.command()
def generate(
    topic: str = typer.Argument(
        ..., help="The biomedical topic to create a knowledge base article for."
    ),
    article_type: str = typer.Option(
        "disease",
        "--type", "-t",
        help="Type of article (disease, biomarker, labtest)."
    ),
    output_dir: Optional[Path] = typer.Option(
        None, 
        "--output", "-o", 
        help="Directory to save the output files."
    ),
    verbose: bool = typer.Option(
        True, 
        "--verbose", "-v", 
        help="Enable verbose output."
    ),
):
    """
    Generate a complete knowledge base article using the end-to-end workflow.
    
    This command uses the full CrewKB workflow to research, create, review,
    and assess the quality of a knowledge base article on the specified topic.
    It combines all phases of the article creation process into a single,
    seamless workflow.
    """
    typer.echo(f"Generating complete {article_type} knowledge base article on: {topic}")
    
    # Check for required environment variables
    if not os.getenv("GEMINI_API_KEY"):
        typer.echo(
            "Error: GEMINI_API_KEY environment variable not set. "
            "Please set it to your Google Gemini API key."
        )
        raise typer.Exit(1)
    
    # Set default output directory if not specified
    if not output_dir:
        output_dir = Path("output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize the flow state
        from crewkb.flows.knowledge_base_flow import ArticleState
        
        state = ArticleState(
            topic=topic,
            article_type=article_type,
            output_directory=str(output_dir)
        )
        
        # Create and run the flow
        flow = KnowledgeBaseFlow(state=state)
        result = flow.kickoff()
        
        # Display summary
        typer.echo("\n=== Knowledge Base Article Creation Complete ===")
        typer.echo(f"Topic: {result['topic']}")
        typer.echo(f"Article Type: {result['article_type']}")
        typer.echo(f"Quality Score: {result['quality_score']:.2f}")
        typer.echo(f"Confidence Level: {result['confidence_level']}")
        typer.echo(f"JSON Output: {result['json_path']}")
        typer.echo(f"Markdown Output: {result['markdown_path']}")
        
    except Exception as e:
        typer.echo(f"Error during article generation: {str(e)}")
        raise typer.Exit(1)


@app.command()
def visualize_flow():
    """
    Generate a visualization of the knowledge base article creation flow.
    
    This command creates an HTML file that visualizes the structure of the
    knowledge base article creation flow, showing the relationships between
    different steps and the data that flows between them.
    """
    typer.echo("Generating flow visualization...")
    
    try:
        from crewkb.flows import plot
        
        # Generate the visualization
        plot()
        
        typer.echo("Flow visualization saved to knowledge_base_flow.html")
        
    except Exception as e:
        typer.echo(f"Error generating flow visualization: {str(e)}")
        raise typer.Exit(1)


@app.command()
def metrics(
    output_dir: Optional[Path] = typer.Option(
        None, 
        "--output", "-o", 
        help="Directory to save the metrics dashboard."
    ),
    topic: Optional[str] = typer.Option(
        None,
        "--topic", "-t",
        help="Show metrics for a specific topic."
    ),
):
    """
    Generate a metrics dashboard for knowledge base articles.
    
    This command generates a dashboard that visualizes the quality metrics
    of generated knowledge base articles. It can show metrics for all articles
    or for a specific topic.
    """
    # Set default output directory if not specified
    if not output_dir:
        output_dir = Path("metrics")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create metrics collector
        metrics_collector = MetricsCollector(str(output_dir))
        
        if topic:
            # Show metrics for a specific topic
            article_metrics = metrics_collector.get_article_metrics(topic)
            
            if article_metrics:
                typer.echo(f"\nMetrics for article on {topic}:")
                
                quality_metrics = article_metrics.get("quality_metrics", {})
                risk_assessment = article_metrics.get("risk_assessment", {})
                
                typer.echo(f"Article Type: {article_metrics.get('article_type', '')}")
                typer.echo(f"Accuracy Score: {quality_metrics.get('accuracy_score', 0):.2f}")
                typer.echo(f"Readability Score: {quality_metrics.get('readability_score', 0):.2f}")
                typer.echo(f"Patient Relevance Score: {quality_metrics.get('patient_relevance_score', 0):.2f}")
                typer.echo(f"Overall Quality Score: {quality_metrics.get('overall_quality_score', 0):.2f}")
                typer.echo(f"Confidence Level: {risk_assessment.get('confidence_level', '')}")
                
                # Show risk areas
                risk_areas = risk_assessment.get("risk_areas", [])
                if risk_areas:
                    typer.echo("\nRisk Areas:")
                    for risk_area in risk_areas:
                        typer.echo(f"- {risk_area.get('type', '')}: {risk_area.get('description', '')}")
            else:
                typer.echo(f"No metrics found for article on {topic}")
        else:
            # Generate dashboard for all articles
            dashboard_file = metrics_collector.generate_dashboard()
            
            # Show summary statistics
            all_metrics = metrics_collector.get_all_metrics()
            avg_quality_score = metrics_collector.get_average_quality_score()
            scores_by_type = metrics_collector.get_quality_score_by_article_type()
            
            typer.echo(f"\nMetrics Dashboard Summary:")
            typer.echo(f"Total Articles: {len(all_metrics)}")
            typer.echo(f"Average Quality Score: {avg_quality_score:.2f}")
            
            if scores_by_type:
                typer.echo("\nQuality Scores by Article Type:")
                for article_type, score in scores_by_type.items():
                    typer.echo(f"- {article_type}: {score:.2f}")
            
            typer.echo(f"\nMetrics dashboard saved to: {dashboard_file}")
        
    except Exception as e:
        typer.echo(f"Error generating metrics dashboard: {str(e)}")
        raise typer.Exit(1)


@app.command()
def version():
    """
    Show the version of CrewKB.
    """
    typer.echo("CrewKB v0.1.0")


def main():
    """
    Main entry point for the CLI.
    """
    app()


if __name__ == "__main__":
    main()
