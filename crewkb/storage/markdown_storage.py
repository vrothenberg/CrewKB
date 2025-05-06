"""
Markdown storage module for knowledge base articles.

This module provides functionality for saving knowledge base articles in
Markdown format.
"""

from pathlib import Path
from typing import Optional

from crewkb.models.article import Article
from crewkb.config import OUTPUT_DIR


class MarkdownStorage:
    """
    Storage class for saving articles in Markdown format.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the Markdown storage.

        Args:
            output_dir: Directory to save the Markdown files. Defaults to the
                        configured OUTPUT_DIR.
        """
        self.output_dir = output_dir or OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def save(self, article: Article) -> Path:
        """
        Save an article to a Markdown file.

        Args:
            article: The article to save.

        Returns:
            The path to the saved file.
        """
        # Create a sanitized filename from the title
        filename = self._sanitize_filename(article.title)
        
        # Add article type and version to the filename
        filename = f"{filename}_{article.article_type}_v{article.version}.md"
        
        # Create the full path
        file_path = self.output_dir / filename
        
        # Convert the article to Markdown
        markdown_content = article.to_markdown()
        
        # Write the article to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return file_path

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
