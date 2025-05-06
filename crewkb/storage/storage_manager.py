"""
Storage manager module for knowledge base articles.

This module provides a unified interface for saving and loading knowledge base
articles in both JSON and Markdown formats.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from crewkb.models.article import Article
from crewkb.storage.json_storage import JSONStorage
from crewkb.storage.markdown_storage import MarkdownStorage
from crewkb.config import OUTPUT_DIR


class StorageManager:
    """
    Storage manager for saving and loading articles in multiple formats.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the storage manager.

        Args:
            output_dir: Directory to save the files. Defaults to the
                        configured OUTPUT_DIR.
        """
        self.output_dir = output_dir or OUTPUT_DIR
        self.json_storage = JSONStorage(self.output_dir)
        self.markdown_storage = MarkdownStorage(self.output_dir)

    def save(self, article: Article) -> Dict[str, Path]:
        """
        Save an article in both JSON and Markdown formats.

        Args:
            article: The article to save.

        Returns:
            A dictionary containing the paths to the saved files.
        """
        json_path = self.json_storage.save(article)
        markdown_path = self.markdown_storage.save(article)
        
        return {
            "json": json_path,
            "markdown": markdown_path,
        }

    def load(self, file_path: Union[str, Path]) -> Article:
        """
        Load an article from a JSON file.

        Args:
            file_path: Path to the JSON file.

        Returns:
            The loaded article.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not a valid JSON file or does not
                        contain a valid article.
        """
        return self.json_storage.load(file_path)

    def list_articles(
        self, article_type: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        List all articles in the output directory.

        Args:
            article_type: Optional filter for article type.

        Returns:
            A list of dictionaries containing article metadata.
        """
        return self.json_storage.list_articles(article_type)
