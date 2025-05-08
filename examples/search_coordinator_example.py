"""
Example script demonstrating how to use the AsyncSearchCoordinator.

This script shows how to use the AsyncSearchCoordinator to search for papers
across multiple sources and create PaperSource objects from the results.
"""

import os
import asyncio
import logging
from typing import Dict, List

from crewkb.utils.search.coordinator import AsyncSearchCoordinator
from crewkb.models.knowledge.paper import PaperSource
from crewkb.models.knowledge.topic import KnowledgeTopic
from crewkb.utils.knowledge_directory import create_topic_directory, load_topic

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def search_and_save_papers(
    topic_name: str,
    search_term: str,
    max_results: int = 10,
    min_citation_count: int = 10,
    use_cache: bool = True
) -> KnowledgeTopic:
    """
    Search for papers and save them to a knowledge topic.
    
    Args:
        topic_name: The name of the topic.
        search_term: The search term to use.
        max_results: Maximum number of results per source.
        min_citation_count: Minimum citation count for filtering results.
        use_cache: Whether to use cached results.
        
    Returns:
        The knowledge topic with the papers added.
    """
    # Create a search coordinator
    coordinator = AsyncSearchCoordinator(cache_dir="cache/search")
    
    # Search for papers
    logger.info(f"Searching for '{search_term}'...")
    papers_by_source = await coordinator.search_and_create_papers(
        term=search_term,
        max_results=max_results,
        use_cache=use_cache,
        min_citation_count=min_citation_count,
        year_range=(2015, 2025)  # Only papers from 2015-2025
    )
    
    # Combine papers from all sources
    all_papers = []
    for source, papers in papers_by_source.items():
        logger.info(f"Found {len(papers)} papers from {source}")
        all_papers.extend(papers)
    
    # Create a knowledge topic
    logger.info(f"Creating topic '{topic_name}'...")
    topic = create_topic_directory(
        topic=topic_name,
        article_type="disease",
        base_dir="examples/knowledge"
    )
    
    # Add the search term to the topic
    topic.add_search_term(
        term=search_term,
        source="initial",
        priority="high",
        notes=f"Initial search term for {topic_name}"
    )
    
    # Add the papers to the topic
    for paper in all_papers:
        topic.add_paper(paper)
    
    # Save the topic
    topic.save_metadata()
    
    return topic


async def main():
    """Main function."""
    # Create the cache directory if it doesn't exist
    os.makedirs("cache/search", exist_ok=True)
    
    # Search for papers on diabetes mellitus
    topic = await search_and_save_papers(
        topic_name="Diabetes Mellitus",
        search_term="diabetes mellitus pathophysiology",
        max_results=5,
        min_citation_count=50,
        use_cache=True
    )
    
    # Print some information about the topic
    print(f"\nTopic: {topic.topic}")
    print(f"Number of papers: {len(topic.papers)}")
    print(f"Papers by source:")
    
    # Count papers by source
    papers_by_source: Dict[str, List[PaperSource]] = {
        "google_scholar": [],
        "semantic_scholar": []
    }
    
    for paper in topic.papers:
        papers_by_source[paper.source_tool].append(paper)
    
    for source, papers in papers_by_source.items():
        print(f"  {source}: {len(papers)}")
    
    # Print some information about the papers
    print("\nTop papers by citation count:")
    sorted_papers = sorted(
        topic.papers, key=lambda p: p.citation_count or 0, reverse=True
    )
    
    for i, paper in enumerate(sorted_papers[:3], 1):
        print(f"{i}. {paper.title} ({paper.year})")
        print(f"   Authors: {', '.join(paper.authors)}")
        print(f"   Journal: {paper.journal}")
        print(f"   Citations: {paper.citation_count}")
        print(f"   URL: {paper.url}")
        print()


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
