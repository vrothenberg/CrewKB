"""
JSON storage module for knowledge base articles.

This module provides functionality for saving and loading knowledge base
articles in JSON format.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

from crewkb.models.article import Article
from crewkb.config import OUTPUT_DIR


class JSONStorage:
    """
    Storage class for saving and loading articles in JSON format.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the JSON storage.

        Args:
            output_dir: Directory to save the JSON files. Defaults to the
                        configured OUTPUT_DIR.
        """
        self.output_dir = output_dir or OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def save(self, article: Article) -> Path:
        """
        Save an article to a JSON file.

        Args:
            article: The article to save.

        Returns:
            The path to the saved file.
        """
        # Create a sanitized filename from the title
        filename = self._sanitize_filename(article.title)
        
        # Add article type and version to the filename
        filename = f"{filename}_{article.article_type}_v{article.version}.json"
        
        # Create the full path
        file_path = self.output_dir / filename
        
        # Convert the article to a dictionary
        article_dict = article.dict()
        
        # Convert datetime objects to ISO format strings
        article_dict["created_at"] = article_dict["created_at"].isoformat()
        article_dict["updated_at"] = article_dict["updated_at"].isoformat()
        
        # Write the article to the file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(article_dict, f, indent=2, ensure_ascii=False)
        
        return file_path

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
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                article_dict = json.load(f)
            
            # Convert ISO format strings to datetime objects
            article_dict["created_at"] = datetime.fromisoformat(
                article_dict["created_at"]
            )
            article_dict["updated_at"] = datetime.fromisoformat(
                article_dict["updated_at"]
            )
            
            # Create an Article object from the dictionary
            return Article(**article_dict)
        
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON file: {file_path}")
        
        except Exception as e:
            raise ValueError(f"Error loading article: {e}")

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
        articles = []
        
        for file_path in self.output_dir.glob("*.json"):
            try:
                article = self.load(file_path)
                
                # Filter by article type if specified
                if article_type and article.article_type != article_type:
                    continue
                
                articles.append({
                    "title": article.title,
                    "article_type": article.article_type,
                    "version": article.version,
                    "updated_at": article.updated_at.isoformat(),
                    "file_path": str(file_path),
                })
            
            except Exception:
                # Skip invalid files
                continue
        
        return articles

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename by removing invalid characters.

        Args:
            filename: The filename to sanitize.

        Returns:
            The sanitized filename.
        """
        # Replace spaces with underscores
        filename = filename.replace(" ", "_")
        
        # Remove invalid characters
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "")
        
        # Convert to lowercase
        filename = filename.lower()
        
        return filename
