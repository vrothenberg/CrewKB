"""
Test script for knowledge models.

This module provides tests for the knowledge models used in the knowledge
synthesis workflow.
"""

import os
import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from crewkb.models.knowledge.paper import PaperSource
from crewkb.models.knowledge.search import SearchTerm
from crewkb.models.knowledge.topic import KnowledgeTopic


class TestPaperSource:
    """Tests for the PaperSource model."""
    
    def test_initialization(self):
        """Test that a PaperSource can be initialized with required fields."""
        paper = PaperSource(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            source_tool="test_tool",
            search_term="test query"
        )
        
        assert paper.title == "Test Paper"
        assert paper.authors == ["Author 1", "Author 2"]
        assert paper.source_tool == "test_tool"
        assert paper.search_term == "test query"
        assert paper.downloaded is False
        assert paper.parsed is False
        assert paper.distilled is False
    
    def test_get_citation(self):
        """Test that a citation can be generated."""
        paper = PaperSource(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            year=2023,
            journal="Test Journal",
            doi="10.1234/test",
            source_tool="test_tool",
            search_term="test query"
        )
        
        citation = paper.get_citation()
        assert "Author 1 and Author 2" in citation
        assert "Test Paper" in citation
        assert "(2023)" in citation
        assert "Test Journal" in citation
        assert "DOI: 10.1234/test" in citation
    
    def test_to_dict_and_from_dict(self):
        """Test that a PaperSource can be converted to and from a dictionary."""
        paper = PaperSource(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            year=2023,
            journal="Test Journal",
            doi="10.1234/test",
            url="https://example.com",
            pdf_url="https://example.com/paper.pdf",
            citation_count=10,
            source_tool="test_tool",
            search_term="test query",
            abstract="This is a test abstract."
        )
        
        paper_dict = paper.to_dict()
        assert paper_dict["title"] == "Test Paper"
        assert paper_dict["authors"] == ["Author 1", "Author 2"]
        assert paper_dict["year"] == 2023
        assert paper_dict["journal"] == "Test Journal"
        assert paper_dict["doi"] == "10.1234/test"
        assert paper_dict["url"] == "https://example.com"
        assert paper_dict["pdf_url"] == "https://example.com/paper.pdf"
        assert paper_dict["citation_count"] == 10
        assert paper_dict["source_tool"] == "test_tool"
        assert paper_dict["search_term"] == "test query"
        assert paper_dict["abstract"] == "This is a test abstract."
        
        paper2 = PaperSource.from_dict(paper_dict)
        assert paper2.title == paper.title
        assert paper2.authors == paper.authors
        assert paper2.year == paper.year
        assert paper2.journal == paper.journal
        assert paper2.doi == paper.doi
        assert paper2.url == paper.url
        assert paper2.pdf_url == paper.pdf_url
        assert paper2.citation_count == paper.citation_count
        assert paper2.source_tool == paper.source_tool
        assert paper2.search_term == paper.search_term
        assert paper2.abstract == paper.abstract
    
    def test_from_semantic_scholar(self):
        """Test that a PaperSource can be created from Semantic Scholar data."""
        semantic_scholar_data = {
            "title": "Test Paper",
            "authors": [{"name": "Author 1"}, {"name": "Author 2"}],
            "year": 2023,
            "venue": "Test Journal",
            "externalIds": {"DOI": "10.1234/test"},
            "url": "https://example.com",
            "openAccessPdf": {"url": "https://example.com/paper.pdf"},
            "citationCount": 10,
            "abstract": "This is a test abstract."
        }
        
        paper = PaperSource.from_semantic_scholar(
            semantic_scholar_data, "test query"
        )
        
        assert paper.title == "Test Paper"
        assert paper.authors == ["Author 1", "Author 2"]
        assert paper.year == 2023
        assert paper.journal == "Test Journal"
        assert paper.doi == "10.1234/test"
        assert paper.url == "https://example.com"
        assert paper.pdf_url == "https://example.com/paper.pdf"
        assert paper.citation_count == 10
        assert paper.source_tool == "semantic_scholar"
        assert paper.search_term == "test query"
        assert paper.abstract == "This is a test abstract."
    
    def test_from_google_scholar(self):
        """Test that a PaperSource can be created from Google Scholar data."""
        google_scholar_data = {
            "title": "Test Paper",
            "publicationInfo": "Author 1, Author 2 - Test Journal, 2023",
            "year": 2023,
            "link": "https://example.com",
            "pdfUrl": "https://example.com/paper.pdf",
            "citedBy": 10,
            "snippet": "This is a test abstract."
        }
        
        paper = PaperSource.from_google_scholar(
            google_scholar_data, "test query"
        )
        
        assert paper.title == "Test Paper"
        assert "Author 1" in paper.authors
        assert "Author 2" in paper.authors
        assert paper.year == 2023
        assert paper.url == "https://example.com"
        assert paper.pdf_url == "https://example.com/paper.pdf"
        assert paper.citation_count == 10
        assert paper.source_tool == "google_scholar"
        assert paper.search_term == "test query"
        assert paper.abstract == "This is a test abstract."


class TestSearchTerm:
    """Tests for the SearchTerm model."""
    
    def test_initialization(self):
        """Test that a SearchTerm can be initialized with required fields."""
        term = SearchTerm(
            term="test query",
            source="initial"
        )
        
        assert term.term == "test query"
        assert term.source == "initial"
        assert term.used is False
        assert term.used_date is None
        assert term.results_count is None
        assert term.google_scholar_results is None
        assert term.semantic_scholar_results is None
    
    def test_mark_as_used(self):
        """Test that a SearchTerm can be marked as used."""
        term = SearchTerm(
            term="test query",
            source="initial"
        )
        
        assert term.used is False
        assert term.used_date is None
        
        term.mark_as_used()
        
        assert term.used is True
        assert term.used_date is not None
        assert isinstance(term.used_date, datetime)
    
    def test_update_results_count(self):
        """Test that results count can be updated."""
        term = SearchTerm(
            term="test query",
            source="initial"
        )
        
        assert term.results_count is None
        assert term.google_scholar_results is None
        assert term.semantic_scholar_results is None
        
        term.update_results_count(
            google_scholar_count=100,
            semantic_scholar_count=50
        )
        
        assert term.google_scholar_results == 100
        assert term.semantic_scholar_results == 50
        assert term.results_count == 150
    
    def test_to_dict_and_from_dict(self):
        """Test that a SearchTerm can be converted to and from a dictionary."""
        term = SearchTerm(
            term="test query",
            source="initial",
            parent_term="parent query",
            relevance=0.8,
            priority="high",
            notes="This is a test note."
        )
        
        term_dict = term.to_dict()
        assert term_dict["term"] == "test query"
        assert term_dict["source"] == "initial"
        assert term_dict["parent_term"] == "parent query"
        assert term_dict["relevance"] == 0.8
        assert term_dict["priority"] == "high"
        assert term_dict["notes"] == "This is a test note."
        
        term2 = SearchTerm.from_dict(term_dict)
        assert term2.term == term.term
        assert term2.source == term.source
        assert term2.parent_term == term.parent_term
        assert term2.relevance == term.relevance
        assert term2.priority == term.priority
        assert term2.notes == term.notes
    
    def test_from_agent_output(self):
        """Test that SearchTerms can be created from agent output."""
        agent_output = [
            {
                "term": "test query 1",
                "relevance_score": 0.8,
                "priority": "high",
                "relevance": "This is relevant because...",
                "alternatives": ["alt 1", "alt 2"]
            },
            {
                "term": "test query 2",
                "relevance_score": 0.6,
                "priority": "medium",
                "relevance": "This is somewhat relevant because...",
                "alternatives": []
            }
        ]
        
        terms = SearchTerm.from_agent_output(agent_output)
        
        assert len(terms) == 4  # 2 main terms + 2 alternatives
        
        # Check main terms
        main_terms = [t for t in terms if t.parent_term is None]
        assert len(main_terms) == 2
        assert main_terms[0].term == "test query 1"
        assert main_terms[0].relevance == 0.8
        assert main_terms[0].priority == "high"
        assert main_terms[0].notes == "This is relevant because..."
        
        assert main_terms[1].term == "test query 2"
        assert main_terms[1].relevance == 0.6
        assert main_terms[1].priority == "medium"
        assert main_terms[1].notes == "This is somewhat relevant because..."
        
        # Check alternatives
        alt_terms = [t for t in terms if t.parent_term is not None]
        assert len(alt_terms) == 2
        assert alt_terms[0].term == "alt 1"
        assert alt_terms[0].parent_term == "test query 1"
        assert alt_terms[0].priority == "low"
        
        assert alt_terms[1].term == "alt 2"
        assert alt_terms[1].parent_term == "test query 1"
        assert alt_terms[1].priority == "low"
    
    def test_from_related_terms(self):
        """Test that SearchTerms can be created from related terms analysis."""
        related_terms = [
            {
                "term": "related query 1",
                "should_use": True,
                "priority": "high",
                "rationale": "This is related because..."
            },
            {
                "term": "related query 2",
                "should_use": False,
                "priority": "medium",
                "rationale": "This is somewhat related because..."
            },
            {
                "term": "related query 3",
                "should_use": True,
                "priority": "low",
                "rationale": "This is slightly related because..."
            }
        ]
        
        terms = SearchTerm.from_related_terms(related_terms, "parent query")
        
        assert len(terms) == 2  # Only the ones with should_use=True
        
        assert terms[0].term == "related query 1"
        assert terms[0].source == "related"
        assert terms[0].parent_term == "parent query"
        assert terms[0].priority == "high"
        assert terms[0].notes == "This is related because..."
        
        assert terms[1].term == "related query 3"
        assert terms[1].source == "related"
        assert terms[1].parent_term == "parent query"
        assert terms[1].priority == "low"
        assert terms[1].notes == "This is slightly related because..."


class TestKnowledgeTopic:
    """Tests for the KnowledgeTopic model."""
    
    def setup_method(self):
        """Set up a temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test that a KnowledgeTopic can be initialized with required fields."""
        topic = KnowledgeTopic(
            topic="Test Topic",
            article_type="disease"
        )
        
        assert topic.topic == "Test Topic"
        assert topic.article_type == "disease"
        assert topic.status == "initialized"
        assert topic.search_terms == []
        assert topic.papers == []
    
    def test_update_status(self):
        """Test that the status can be updated."""
        topic = KnowledgeTopic(
            topic="Test Topic",
            article_type="disease"
        )
        
        assert topic.status == "initialized"
        
        topic.update_status("researching")
        
        assert topic.status == "researching"
    
    def test_add_search_term(self):
        """Test that a search term can be added."""
        topic = KnowledgeTopic(
            topic="Test Topic",
            article_type="disease"
        )
        
        assert len(topic.search_terms) == 0
        
        term = SearchTerm(
            term="test query",
            source="initial"
        )
        
        topic.add_search_term(term)
        
        assert len(topic.search_terms) == 1
        assert topic.search_terms[0].term == "test query"
        
        # Test that duplicate terms are not added
        topic.add_search_term(term)
        
        assert len(topic.search_terms) == 1
    
    def test_add_paper(self):
        """Test that a paper can be added."""
        topic = KnowledgeTopic(
            topic="Test Topic",
            article_type="disease"
        )
        
        assert len(topic.papers) == 0
        
        paper = PaperSource(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            source_tool="test_tool",
            search_term="test query"
        )
        
        topic.add_paper(paper)
        
        assert len(topic.papers) == 1
        assert topic.papers[0].title == "Test Paper"
        
        # Test that duplicate papers are not added
        topic.add_paper(paper)
        
        assert len(topic.papers) == 1
    
    def test_get_unused_search_terms(self):
        """Test that unused search terms can be retrieved."""
        topic = KnowledgeTopic(
            topic="Test Topic",
            article_type="disease"
        )
        
        term1 = SearchTerm(
            term="test query 1",
            source="initial"
        )
        
        term2 = SearchTerm(
            term="test query 2",
            source="initial",
            used=True
        )
        
        topic.add_search_term(term1)
        topic.add_search_term(term2)
        
        unused_terms = topic.get_unused_search_terms()
        
        assert len(unused_terms) == 1
        assert unused_terms[0].term == "test query 1"
    
    def test_to_dict_and_from_dict(self):
        """Test that a KnowledgeTopic can be converted to and from a dictionary."""
        topic = KnowledgeTopic(
            topic="Test Topic",
            article_type="disease"
        )
        
        term = SearchTerm(
            term="test query",
            source="initial"
        )
        
        paper = PaperSource(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            source_tool="test_tool",
            search_term="test query"
        )
        
        topic.add_search_term(term)
        topic.add_paper(paper)
        
        topic_dict = topic.to_dict()
        assert topic_dict["topic"] == "Test Topic"
        assert topic_dict["article_type"] == "disease"
        assert len(topic_dict["search_terms"]) == 1
        assert len(topic_dict["papers"]) == 1
        
        topic2 = KnowledgeTopic.from_dict(topic_dict)
        assert topic2.topic == topic.topic
        assert topic2.article_type == topic.article_type
        assert len(topic2.search_terms) == 1
        assert topic2.search_terms[0].term == "test query"
        assert len(topic2.papers) == 1
        assert topic2.papers[0].title == "Test Paper"
    
    def test_initialize_directory_structure(self):
        """Test that the directory structure can be initialized."""
        topic = KnowledgeTopic(
            topic="Test Topic",
            article_type="disease"
        )
        
        topic.initialize_directory_structure(self.temp_dir)
        
        assert topic.base_dir is not None
        assert os.path.exists(topic.base_dir)
        assert os.path.exists(topic.papers_dir)
        assert topic.outline_path is not None
        assert topic.search_terms_path is not None
        assert topic.synthesis_path is not None
        assert topic.draft_path is not None
        assert topic.review_path is not None
        assert topic.final_path is not None
    
    def test_save_and_load(self):
        """Test that a KnowledgeTopic can be saved and loaded."""
        topic = KnowledgeTopic(
            topic="Test Topic",
            article_type="disease"
        )
        
        term = SearchTerm(
            term="test query",
            source="initial"
        )
        
        paper = PaperSource(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            source_tool="test_tool",
            search_term="test query"
        )
        
        topic.add_search_term(term)
        topic.add_paper(paper)
        
        topic.initialize_directory_structure(self.temp_dir)
        topic.outline = "# Test Outline"
        topic.synthesis = "# Test Synthesis"
        topic.article_draft = "# Test Draft"
        topic.review_feedback = "# Test Review"
        topic.final_article = "# Test Final"
        
        topic.save_all()
        
        # Check that files were created
        assert os.path.exists(os.path.join(topic.base_dir, "metadata.json"))
        assert os.path.exists(topic.outline_path)
        assert os.path.exists(topic.search_terms_path)
        assert os.path.exists(topic.synthesis_path)
        assert os.path.exists(topic.draft_path)
        assert os.path.exists(topic.review_path)
        assert os.path.exists(topic.final_path)
        
        # Load the topic
        topic2 = KnowledgeTopic.load(topic.base_dir)
        
        assert topic2.topic == topic.topic
        assert topic2.article_type == topic.article_type
        assert len(topic2.search_terms) == 1
        assert topic2.search_terms[0].term == "test query"
        assert len(topic2.papers) == 1
        assert topic2.papers[0].title == "Test Paper"
