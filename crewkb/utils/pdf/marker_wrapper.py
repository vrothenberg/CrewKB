"""
Marker Wrapper for CrewKB.

This module provides a wrapper for the Marker PDF parser with Gemini integration.
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Union

# Import Marker components
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser

logger = logging.getLogger(__name__)


class MarkerWrapper:
    """
    Wrapper for the Marker PDF parser with Gemini integration.
    
    This class provides a wrapper for the Marker PDF parser, with support for:
    - Parsing PDFs to markdown format
    - Using Gemini for improved accuracy
    - Customizing parsing options
    - Tracking failed parsing attempts
    - Providing fallback options for failed parsing
    """
    
    def __init__(
        self,
        use_llm: bool = True,
        output_format: str = "markdown",
        cache_dir: str = "cache/marker",
        google_api_key: Optional[str] = None
    ):
        """
        Initialize the MarkerWrapper.
        
        Args:
            use_llm: Whether to use Gemini for improved accuracy.
            output_format: The output format (markdown, json, html).
            cache_dir: Directory to cache parsed PDFs.
            google_api_key: Google API key for Gemini. If None, will use the
                            GOOGLE_API_KEY environment variable.
        """
        self.use_llm = use_llm
        self.output_format = output_format
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Set the Google API key if provided
        if google_api_key:
            os.environ["GOOGLE_API_KEY"] = google_api_key
        
        # Initialize the failed parsing set
        self.failed_parsing = set()
    
    def parse_pdf(
        self,
        pdf_path: str,
        output_path: Optional[str] = None,
        use_llm: Optional[bool] = None,
        output_format: Optional[str] = None,
        force: bool = False,
        page_range: Optional[str] = None,
        redo_inline_math: bool = False,
        disable_image_extraction: bool = False,
        force_ocr: bool = False,
        strip_existing_ocr: bool = False,
        languages: Optional[List[str]] = None
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]]]:
        """
        Parse a PDF file using Marker.
        
        Args:
            pdf_path: Path to the PDF file.
            output_path: Path to save the parsed output. If None, the output will be
                         saved to the cache directory.
            use_llm: Whether to use Gemini for improved accuracy. If None, will use
                     the value provided in the constructor.
            output_format: The output format (markdown, json, html). If None, will use
                           the value provided in the constructor.
            force: Whether to force parsing even if the PDF is already cached.
            page_range: Specify which pages to process. Accepts comma-separated page
                        numbers and ranges. Example: "0,5-10,20".
            redo_inline_math: If True, will use Gemini for high-quality inline math conversion.
            disable_image_extraction: If True, will not extract images from the PDF.
            force_ocr: If True, will force OCR processing on the entire document.
            strip_existing_ocr: If True, will remove all existing OCR text and re-OCR.
            languages: Optionally specify which languages to use for OCR processing.
                       Accepts a list of language codes. Example: ["en", "fr", "de"].
                       
        Returns:
            A tuple containing:
            - The parsed text (or None if parsing failed)
            - The metadata dictionary (or None if parsing failed)
            - The list of images (or None if parsing failed or image extraction is disabled)
        """
        # Use the provided values or fall back to the constructor values
        use_llm = use_llm if use_llm is not None else self.use_llm
        output_format = output_format or self.output_format
        
        # Create the cache path
        pdf_filename = os.path.basename(pdf_path)
        cache_key = f"{pdf_filename}_{use_llm}_{output_format}"
        if page_range:
            cache_key += f"_{page_range}"
        if redo_inline_math:
            cache_key += "_math"
        if disable_image_extraction:
            cache_key += "_noimg"
        if force_ocr:
            cache_key += "_ocr"
        if strip_existing_ocr:
            cache_key += "_strip"
        if languages:
            cache_key += f"_{'_'.join(languages)}"
        
        cache_path = self.cache_dir / f"{cache_key}.{output_format}"
        
        # If output_path is provided, use that instead
        output_path = output_path or str(cache_path)
        
        # If the file already exists and force is False, return the cached result
        if not force and os.path.exists(cache_path):
            logger.info(f"PDF already parsed at {cache_path}")
            
            # Load the cached result
            if output_format == "markdown":
                with open(cache_path, "r") as f:
                    text = f.read()
                
                # Load the metadata and images if they exist
                metadata_path = cache_path.with_suffix(".metadata.json")
                metadata = None
                if metadata_path.exists():
                    import json
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                
                # Load the images if they exist and image extraction is not disabled
                images = None
                if not disable_image_extraction:
                    images_dir = cache_path.with_suffix(".images")
                    if images_dir.exists():
                        images = []
                        for image_path in images_dir.glob("*"):
                            with open(image_path, "rb") as f:
                                image_data = f.read()
                            images.append({
                                "path": str(image_path),
                                "data": image_data
                            })
                
                return text, metadata, images
            
            # For other formats, we need to parse the PDF again
            # This is because we don't have a good way to cache the rendered object
            
        try:
            # Create the configuration
            config = {
                "output_format": output_format,
                "use_llm": use_llm,
                "redo_inline_math": redo_inline_math,
                "disable_image_extraction": disable_image_extraction,
                "force_ocr": force_ocr,
                "strip_existing_ocr": strip_existing_ocr
            }
            
            # Add page_range if provided
            if page_range:
                config["page_range"] = page_range
            
            # Add languages if provided
            if languages:
                config["languages"] = ",".join(languages)
            
            # Create the config parser
            config_parser = ConfigParser(config)
            
            # Create the converter
            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=create_model_dict(),
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
                llm_service=config_parser.get_llm_service()
            )
            
            # Parse the PDF
            logger.info(f"Parsing PDF: {pdf_path}")
            rendered = converter(pdf_path)
            
            # Extract the text, metadata, and images
            text, metadata, images = text_from_rendered(rendered)
            
            # Save the result to the cache path
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "w") as f:
                f.write(text)
            
            # Save the metadata if available
            if metadata:
                import json
                metadata_path = cache_path.with_suffix(".metadata.json")
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f)
            
            # Save the images if available and image extraction is not disabled
            if images and not disable_image_extraction:
                images_dir = cache_path.with_suffix(".images")
                images_dir.mkdir(parents=True, exist_ok=True)
                
                for i, image in enumerate(images):
                    image_path = images_dir / f"image_{i}.png"
                    with open(image_path, "wb") as f:
                        f.write(image)
                    
                    # Update the image path in the list
                    images[i] = {
                        "path": str(image_path),
                        "data": image
                    }
            
            # If output_path is different from cache_path, copy the file
            if output_path != str(cache_path):
                output_path_obj = Path(output_path)
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)
                
                with open(cache_path, "r") as src:
                    with open(output_path_obj, "w") as dst:
                        dst.write(src.read())
            
            logger.info(f"Parsed PDF from {pdf_path} to {output_path}")
            
            return text, metadata, images
            
        except Exception as e:
            logger.error(f"Failed to parse PDF {pdf_path}: {str(e)}")
            self.failed_parsing.add(pdf_path)
            return None, None, None
    
    def parse_pdf_with_custom_config(
        self,
        pdf_path: str,
        config: Dict[str, Any],
        output_path: Optional[str] = None,
        force: bool = False
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]]]:
        """
        Parse a PDF file with custom configuration.
        
        Args:
            pdf_path: Path to the PDF file.
            config: Custom configuration for Marker.
            output_path: Path to save the parsed output. If None, the output will be
                         saved to the cache directory.
            force: Whether to force parsing even if the PDF is already cached.
            
        Returns:
            A tuple containing:
            - The parsed text (or None if parsing failed)
            - The metadata dictionary (or None if parsing failed)
            - The list of images (or None if parsing failed or image extraction is disabled)
        """
        # Extract the output format from the config
        output_format = config.get("output_format", self.output_format)
        
        # Create a cache key from the config
        import hashlib
        import json
        config_str = json.dumps(config, sort_keys=True)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()
        
        # Create the cache path
        pdf_filename = os.path.basename(pdf_path)
        cache_key = f"{pdf_filename}_{config_hash}"
        cache_path = self.cache_dir / f"{cache_key}.{output_format}"
        
        # If output_path is provided, use that instead
        output_path = output_path or str(cache_path)
        
        # If the file already exists and force is False, return the cached result
        if not force and os.path.exists(cache_path):
            logger.info(f"PDF already parsed at {cache_path}")
            
            # Load the cached result
            if output_format == "markdown":
                with open(cache_path, "r") as f:
                    text = f.read()
                
                # Load the metadata and images if they exist
                metadata_path = cache_path.with_suffix(".metadata.json")
                metadata = None
                if metadata_path.exists():
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                
                # Load the images if they exist and image extraction is not disabled
                images = None
                if not config.get("disable_image_extraction", False):
                    images_dir = cache_path.with_suffix(".images")
                    if images_dir.exists():
                        images = []
                        for image_path in images_dir.glob("*"):
                            with open(image_path, "rb") as f:
                                image_data = f.read()
                            images.append({
                                "path": str(image_path),
                                "data": image_data
                            })
                
                return text, metadata, images
        
        try:
            # Create the config parser
            config_parser = ConfigParser(config)
            
            # Create the converter
            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=create_model_dict(),
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
                llm_service=config_parser.get_llm_service()
            )
            
            # Parse the PDF
            logger.info(f"Parsing PDF with custom config: {pdf_path}")
            rendered = converter(pdf_path)
            
            # Extract the text, metadata, and images
            text, metadata, images = text_from_rendered(rendered)
            
            # Save the result to the cache path
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "w") as f:
                f.write(text)
            
            # Save the metadata if available
            if metadata:
                metadata_path = cache_path.with_suffix(".metadata.json")
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f)
            
            # Save the images if available and image extraction is not disabled
            if images and not config.get("disable_image_extraction", False):
                images_dir = cache_path.with_suffix(".images")
                images_dir.mkdir(parents=True, exist_ok=True)
                
                for i, image in enumerate(images):
                    image_path = images_dir / f"image_{i}.png"
                    with open(image_path, "wb") as f:
                        f.write(image)
                    
                    # Update the image path in the list
                    images[i] = {
                        "path": str(image_path),
                        "data": image
                    }
            
            # If output_path is different from cache_path, copy the file
            if output_path != str(cache_path):
                output_path_obj = Path(output_path)
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)
                
                with open(cache_path, "r") as src:
                    with open(output_path_obj, "w") as dst:
                        dst.write(src.read())
            
            logger.info(f"Parsed PDF with custom config from {pdf_path} to {output_path}")
            
            return text, metadata, images
            
        except Exception as e:
            logger.error(f"Failed to parse PDF with custom config {pdf_path}: {str(e)}")
            self.failed_parsing.add(pdf_path)
            return None, None, None
    
    def extract_sections(
        self,
        markdown: str,
        section_markers: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, str]:
        """
        Extract sections from markdown content.
        
        Args:
            markdown: The markdown content to extract sections from.
            section_markers: A dictionary mapping section names to lists of possible
                             section headings. If None, will use default section markers.
                             
        Returns:
            A dictionary mapping section names to section content.
        """
        # Use default section markers if none are provided
        if section_markers is None:
            section_markers = {
                "abstract": ["abstract", "summary"],
                "introduction": ["introduction", "background"],
                "methods": ["methods", "methodology", "materials and methods"],
                "results": ["results", "findings"],
                "discussion": ["discussion"],
                "conclusion": ["conclusion", "conclusions"],
                "references": ["references", "bibliography"]
            }
        
        # Split the markdown into lines
        lines = markdown.split("\n")
        
        # Initialize the sections dictionary
        sections = {}
        
        # Initialize variables for tracking the current section
        current_section = None
        current_content = []
        
        # Process each line
        for line in lines:
            # Check if the line is a heading
            if line.startswith("#"):
                # Extract the heading text
                heading_text = line.lstrip("#").strip().lower()
                
                # Check if the heading matches any section marker
                matched_section = None
                for section, markers in section_markers.items():
                    if any(marker in heading_text for marker in markers):
                        matched_section = section
                        break
                
                # If we found a matching section
                if matched_section:
                    # If we were already in a section, save it
                    if current_section:
                        sections[current_section] = "\n".join(current_content)
                    
                    # Start a new section
                    current_section = matched_section
                    current_content = [line]
                else:
                    # If we're in a section, add the line to the current content
                    if current_section:
                        current_content.append(line)
            else:
                # If we're in a section, add the line to the current content
                if current_section:
                    current_content.append(line)
        
        # Save the last section if there is one
        if current_section:
            sections[current_section] = "\n".join(current_content)
        
        return sections
    
    def get_failed_parsing(self) -> set:
        """
        Get the set of PDF paths that failed to parse.
        
        Returns:
            The set of PDF paths that failed to parse.
        """
        return self.failed_parsing
    
    def clear_cache(self) -> None:
        """
        Clear the cache directory.
        """
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                import shutil
                shutil.rmtree(file)
        
        logger.info(f"Cleared Marker cache directory: {self.cache_dir}")
