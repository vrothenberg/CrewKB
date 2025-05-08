"""
Example script for using the knowledge models and directory utilities.

This script demonstrates how to use the knowledge models and directory utilities
to create and manage knowledge topics, search terms, and papers.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from crewkb.models.knowledge.paper import PaperSource
from crewkb.models.knowledge.search import SearchTerm
from crewkb.models.knowledge.topic import KnowledgeTopic
from crewkb.utils.knowledge_directory import (
    initialize_knowledge_directory,
    create_topic_directory,
    list_topics,
    load_topic,
    delete_topic
)


def main():
    """Run the example."""
    # Initialize the knowledge directory
    knowledge_dir = initialize_knowledge_directory("examples/knowledge")
    print(f"Initialized knowledge directory: {knowledge_dir}")
    
    # Create a topic
    topic_name = "Diabetes Mellitus"
    print(f"\nCreating topic: {topic_name}")
    topic = create_topic_directory(
        topic=topic_name,
        article_type="disease",
        base_dir="examples/knowledge"
    )
    print(f"Created topic: {topic.topic}")
    print(f"Topic directory: {topic.base_dir}")
    
    # Add a search term
    print("\nAdding search terms")
    term1 = SearchTerm(
        term="diabetes mellitus pathophysiology",
        source="initial",
        priority="high",
        notes="Focus on the pathophysiology of diabetes mellitus"
    )
    topic.add_search_term(term1)
    
    term2 = SearchTerm(
        term="diabetes mellitus treatment",
        source="initial",
        priority="medium",
        notes="Focus on the treatment of diabetes mellitus"
    )
    topic.add_search_term(term2)
    
    # Save the search terms
    topic.save_search_terms()
    print(f"Added {len(topic.search_terms)} search terms")
    
    # Add a paper
    print("\nAdding papers")
    paper1 = PaperSource(
        title="Pathophysiology of Diabetes Mellitus",
        authors=["Smith, J.", "Johnson, A."],
        year=2022,
        journal="Journal of Diabetes Research",
        doi="10.1234/jdr.2022.001",
        url="https://example.com/paper1",
        pdf_url="https://example.com/paper1.pdf",
        citation_count=50,
        source_tool="semantic_scholar",
        search_term="diabetes mellitus pathophysiology",
        abstract="This paper discusses the pathophysiology of diabetes mellitus..."
    )
    topic.add_paper(paper1)
    
    paper2 = PaperSource(
        title="Treatment Options for Diabetes Mellitus",
        authors=["Brown, R.", "Davis, M."],
        year=2021,
        journal="Journal of Diabetes Treatment",
        doi="10.1234/jdt.2021.001",
        url="https://example.com/paper2",
        pdf_url="https://example.com/paper2.pdf",
        citation_count=30,
        source_tool="google_scholar",
        search_term="diabetes mellitus treatment",
        abstract="This paper discusses the treatment options for diabetes mellitus..."
    )
    topic.add_paper(paper2)
    
    # Save the metadata
    topic.save_metadata()
    print(f"Added {len(topic.papers)} papers")
    
    # Add an outline
    print("\nAdding outline")
    topic.outline = """# Diabetes Mellitus

## Overview
- Definition
- Types
- Epidemiology

## Pathophysiology
- Type 1 Diabetes
- Type 2 Diabetes
- Gestational Diabetes

## Clinical Presentation
- Symptoms
- Signs
- Complications

## Diagnosis
- Diagnostic Criteria
- Laboratory Tests
- Differential Diagnosis

## Treatment
- Lifestyle Modifications
- Medications
- Insulin Therapy
- Surgical Options

## Prognosis
- Short-term Outcomes
- Long-term Outcomes
- Quality of Life

## Prevention
- Primary Prevention
- Secondary Prevention
- Tertiary Prevention
"""
    topic.save_outline()
    print("Added outline")
    
    # Add synthesis
    print("\nAdding synthesis")
    topic.synthesis = """# Synthesis of Research on Diabetes Mellitus

## Pathophysiology
Based on the research by Smith et al. (2022), diabetes mellitus is characterized by...

## Treatment
According to Brown and Davis (2021), the treatment options for diabetes mellitus include...
"""
    topic.save_synthesis()
    print("Added synthesis")
    
    # Save all data
    topic.save_all()
    print("\nSaved all data")
    
    # List all topics
    print("\nListing all topics")
    topics = list_topics("examples/knowledge")
    for t in topics:
        print(f"- {t['topic']} ({t['article_type']})")
    
    # Load a topic
    print("\nLoading topic")
    loaded_topic = load_topic(topic_name, "examples/knowledge")
    if loaded_topic:
        print(f"Loaded topic: {loaded_topic.topic}")
        print(f"Article type: {loaded_topic.article_type}")
        print(f"Number of search terms: {len(loaded_topic.search_terms)}")
        print(f"Number of papers: {len(loaded_topic.papers)}")
    else:
        print(f"Failed to load topic: {topic_name}")
    
    # Delete the topic (uncomment to test)
    # print("\nDeleting topic")
    # deleted = delete_topic(topic_name, "examples/knowledge")
    # print(f"Topic deleted: {deleted}")


if __name__ == "__main__":
    main()
