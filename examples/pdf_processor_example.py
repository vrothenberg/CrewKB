"""
Example script demonstrating how to use the PDF Management utilities.

This script shows how to use the PDFDownloadManager, MarkerWrapper, and PDFProcessor
to download, parse, and process PDFs.
"""

import os
import asyncio
import logging
from pathlib import Path

from crewkb.utils.pdf import PDFDownloadManager, MarkerWrapper, PDFProcessor
from crewkb.models.knowledge.paper import PaperSource

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_pdf_download_manager():
    """Test the PDFDownloadManager."""
    # Create the cache directory if it doesn't exist
    os.makedirs("examples/pdf_cache", exist_ok=True)
    
    # Create a download manager
    download_manager = PDFDownloadManager(cache_dir="examples/pdf_cache/downloads")
    
    # Define a PDF URL to download
    pdf_url = "https://arxiv.org/pdf/2303.08774.pdf"  # "GPT-4 Technical Report"
    
    # Download the PDF
    logger.info(f"Downloading PDF from {pdf_url}...")
    pdf_path = await download_manager.download(pdf_url)
    
    if pdf_path:
        logger.info(f"Downloaded PDF to {pdf_path}")
    else:
        logger.error(f"Failed to download PDF from {pdf_url}")
    
    return pdf_path


async def test_marker_wrapper(pdf_path):
    """Test the MarkerWrapper."""
    # Create a marker wrapper
    marker_wrapper = MarkerWrapper(
        use_llm=True,  # Use Gemini for improved accuracy
        cache_dir="examples/pdf_cache/marker"
    )
    
    # Parse the PDF
    logger.info(f"Parsing PDF: {pdf_path}...")
    markdown, metadata, images = marker_wrapper.parse_pdf(
        pdf_path,
        output_path="examples/pdf_cache/gpt4_technical_report.md"
    )
    
    if markdown:
        logger.info(f"Parsed PDF to markdown ({len(markdown)} characters)")
        
        # Extract sections from the markdown
        sections = marker_wrapper.extract_sections(markdown)
        
        # Print the sections
        logger.info(f"Extracted {len(sections)} sections:")
        for section, content in sections.items():
            logger.info(f"  - {section}: {len(content)} characters")
    else:
        logger.error(f"Failed to parse PDF: {pdf_path}")
    
    return markdown, sections


async def test_pdf_processor():
    """Test the PDFProcessor."""
    # Create a PDF processor
    processor = PDFProcessor(
        cache_dir="examples/pdf_cache/processor",
        use_llm=True  # Use Gemini for improved accuracy
    )
    
    # Create a PaperSource object
    paper = PaperSource(
        id="gpt4_technical_report",
        title="GPT-4 Technical Report",
        authors=["OpenAI"],
        year=2023,
        journal="arXiv",
        url="https://arxiv.org/abs/2303.08774",
        pdf_url="https://arxiv.org/pdf/2303.08774.pdf",
        citation_count=1000,
        abstract="We report the development of GPT-4, a large-scale, multimodal model..."
    )
    
    # Process the paper
    logger.info(f"Processing paper: {paper.title}...")
    markdown_path, sections = await processor.process_paper(
        paper,
        output_dir="examples/pdf_cache/papers"
    )
    
    if markdown_path:
        logger.info(f"Processed paper to {markdown_path}")
        logger.info(f"Extracted {len(sections)} sections")
    else:
        logger.error(f"Failed to process paper: {paper.title}")
    
    return markdown_path, sections


async def test_batch_processing():
    """Test batch processing of papers."""
    # Create a PDF processor
    processor = PDFProcessor(
        cache_dir="examples/pdf_cache/processor",
        use_llm=True  # Use Gemini for improved accuracy
    )
    
    # Create a list of PaperSource objects
    papers = [
        PaperSource(
            id="gpt4_technical_report",
            title="GPT-4 Technical Report",
            authors=["OpenAI"],
            year=2023,
            journal="arXiv",
            url="https://arxiv.org/abs/2303.08774",
            pdf_url="https://arxiv.org/pdf/2303.08774.pdf",
            citation_count=1000,
            abstract="We report the development of GPT-4, a large-scale, multimodal model..."
        ),
        PaperSource(
            id="attention_is_all_you_need",
            title="Attention Is All You Need",
            authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            year=2017,
            journal="arXiv",
            url="https://arxiv.org/abs/1706.03762",
            pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
            citation_count=5000,
            abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks..."
        )
    ]
    
    # Process the papers
    logger.info(f"Processing {len(papers)} papers...")
    results = await processor.process_papers(
        papers,
        output_dir="examples/pdf_cache/papers",
        max_concurrent=2
    )
    
    # Print the results
    for paper_id, (markdown_path, sections) in results.items():
        if markdown_path:
            logger.info(f"Processed paper {paper_id} to {markdown_path}")
            logger.info(f"Extracted {len(sections)} sections")
        else:
            logger.error(f"Failed to process paper: {paper_id}")
    
    return results


async def main():
    """Main function."""
    # Create the cache directory if it doesn't exist
    os.makedirs("examples/pdf_cache", exist_ok=True)
    
    # Test the PDFDownloadManager
    pdf_path = await test_pdf_download_manager()
    
    if pdf_path:
        # Test the MarkerWrapper
        await test_marker_wrapper(pdf_path)
    
    # Test the PDFProcessor
    await test_pdf_processor()
    
    # Test batch processing
    await test_batch_processing()


if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
