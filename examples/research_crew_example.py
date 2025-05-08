"""
Example script demonstrating how to use the research crew with PDF processing.

This script shows how to run the research crew with a topic like "Diabetes mellitus"
and demonstrates how the search tools and PDF utilities work together.
"""

import os
import logging
import json
from pathlib import Path

from crewkb.crews.research_crew import ResearchCrew

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def save_results(results, output_dir):
    """
    Save the results to files.
    
    Args:
        results: The results from the research crew
        output_dir: The directory to save the results to
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each task result to a separate file
    for task_name, result in results.items():
        # Sanitize the task name for use as a filename
        sanitized_name = task_name.split("\n")[0].lower().replace(" ", "_")
        sanitized_name = "".join(c for c in sanitized_name if c.isalnum() or c == "_")
        
        # Save the result to a file
        output_path = os.path.join(output_dir, f"{sanitized_name}.md")
        with open(output_path, "w") as f:
            f.write(result)
        
        logger.info(f"Saved result for task '{task_name}' to {output_path}")
    
    # Save the combined results to a single file
    combined_path = os.path.join(output_dir, "combined_results.md")
    with open(combined_path, "w") as f:
        for task_name, result in results.items():
            f.write(f"# {task_name.split('\n')[0]}\n\n")
            f.write(result)
            f.write("\n\n---\n\n")
    
    logger.info(f"Saved combined results to {combined_path}")


def main():
    """Main function."""
    # Define the topic to research
    topic = "Diabetes mellitus"
    
    # Define the output directory
    output_dir = f"output/{topic.lower().replace(' ', '_')}"
    
    # Create the research crew
    logger.info(f"Creating research crew for topic: {topic}")
    crew = ResearchCrew(topic=topic)
    
    # Run the crew
    logger.info("Running research crew...")
    results = crew.run()
    
    # Save the results
    logger.info("Saving results...")
    save_results(results, output_dir)
    
    logger.info(f"Research completed for topic: {topic}")
    logger.info(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
