"""
Knowledge directory utilities for CrewKB.

This module provides utilities for managing the knowledge directory structure,
which is used to store knowledge base articles and research materials.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from crewkb.models.knowledge.topic import KnowledgeTopic


def initialize_knowledge_directory(base_dir: str = "knowledge") -> str:
    """
    Initialize the knowledge directory structure.
    
    Args:
        base_dir: The base directory for the knowledge directory.
        
    Returns:
        The path to the knowledge directory.
    """
    # Create the knowledge directory if it doesn't exist
    knowledge_dir = Path(base_dir)
    knowledge_dir.mkdir(exist_ok=True, parents=True)
    
    return str(knowledge_dir)


def create_topic_directory(
    topic: str,
    article_type: str = "disease",
    base_dir: str = "knowledge"
) -> KnowledgeTopic:
    """
    Create a directory for a knowledge topic.
    
    Args:
        topic: The topic name.
        article_type: The article type (disease, biomarker, or lab test).
        base_dir: The base directory for the knowledge directory.
        
    Returns:
        A KnowledgeTopic instance.
    """
    # Initialize the knowledge directory
    knowledge_dir = initialize_knowledge_directory(base_dir)
    
    # Create a KnowledgeTopic instance
    topic_model = KnowledgeTopic(
        topic=topic,
        article_type=article_type
    )
    
    # Initialize the directory structure
    topic_model.initialize_directory_structure(knowledge_dir)
    
    # Save the metadata
    topic_model.save_metadata()
    
    return topic_model


def list_topics(base_dir: str = "knowledge") -> List[Dict[str, Any]]:
    """
    List all topics in the knowledge directory.
    
    Args:
        base_dir: The base directory for the knowledge directory.
        
    Returns:
        A list of topic metadata.
    """
    # Initialize the knowledge directory
    knowledge_dir = initialize_knowledge_directory(base_dir)
    
    # List all subdirectories
    topics = []
    for item in os.listdir(knowledge_dir):
        item_path = os.path.join(knowledge_dir, item)
        if os.path.isdir(item_path):
            # Check if it's a topic directory
            metadata_path = os.path.join(item_path, "metadata.json")
            if os.path.exists(metadata_path):
                # Load the metadata
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                
                # Add to the list
                topics.append(metadata)
    
    return topics


def load_topic(
    topic_name: str,
    base_dir: str = "knowledge"
) -> Optional[KnowledgeTopic]:
    """
    Load a knowledge topic.
    
    Args:
        topic_name: The topic name.
        base_dir: The base directory for the knowledge directory.
        
    Returns:
        A KnowledgeTopic instance, or None if the topic doesn't exist.
    """
    # Initialize the knowledge directory
    knowledge_dir = initialize_knowledge_directory(base_dir)
    
    # Create a sanitized topic name for the directory
    sanitized_topic = topic_name.lower().replace(" ", "_").replace("/", "_")
    
    # Check if the topic directory exists
    topic_dir = os.path.join(knowledge_dir, sanitized_topic)
    if not os.path.exists(topic_dir):
        return None
    
    # Load the topic
    try:
        return KnowledgeTopic.load(topic_dir)
    except Exception as e:
        print(f"Error loading topic: {str(e)}")
        return None


def delete_topic(
    topic_name: str,
    base_dir: str = "knowledge"
) -> bool:
    """
    Delete a knowledge topic.
    
    Args:
        topic_name: The topic name.
        base_dir: The base directory for the knowledge directory.
        
    Returns:
        True if the topic was deleted, False otherwise.
    """
    # Initialize the knowledge directory
    knowledge_dir = initialize_knowledge_directory(base_dir)
    
    # Create a sanitized topic name for the directory
    sanitized_topic = topic_name.lower().replace(" ", "_").replace("/", "_")
    
    # Check if the topic directory exists
    topic_dir = os.path.join(knowledge_dir, sanitized_topic)
    if not os.path.exists(topic_dir):
        return False
    
    # Delete the topic directory
    import shutil
    shutil.rmtree(topic_dir)
    
    return True
