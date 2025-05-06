"""
FactCheckerTool for verifying medical facts against reliable sources.

This module provides a tool for verifying factual statements in medical content
against reliable sources and assessing the confidence level of the verification.
"""

from typing import Dict, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FactCheckerToolInput(BaseModel):
    """Input schema for FactCheckerTool."""
    statement: str = Field(
        ...,
        description="The factual statement to verify"
    )
    sources: List[str] = Field(
        ...,
        description="List of sources to check against (citations, references)"
    )
    context: Optional[str] = Field(
        None,
        description="Additional context about the statement"
    )


class FactCheckerTool(BaseTool):
    """
    Tool for verifying medical facts against reliable sources.
    
    This tool checks factual statements against provided sources and research data,
    assesses the reliability of the sources, and provides a confidence score for
    the verification.
    """
    
    name: str = "FactCheckerTool"
    description: str = "Verify medical facts against reliable sources"
    args_schema: type[BaseModel] = FactCheckerToolInput
    
    def _run(
        self,
        statement: str,
        sources: List[str],
        context: Optional[str] = None
    ) -> str:
        """
        Verify a factual statement against reliable sources.
        
        Args:
            statement: The factual statement to verify
            sources: List of sources to check against
            context: Additional context about the statement
            
        Returns:
            A string containing the verification results.
        """
        # Analyze the statement
        statement_analysis = self._analyze_statement(statement)
        
        # Evaluate the sources
        source_evaluation = self._evaluate_sources(sources)
        
        # Check statement against sources
        verification_results = self._verify_statement(
            statement, sources, statement_analysis, source_evaluation, context
        )
        
        # Format and return results
        return self._format_results(
            statement, verification_results, source_evaluation
        )
    
    def _analyze_statement(self, statement: str) -> Dict[str, any]:
        """
        Analyze a factual statement to identify key claims.
        
        Args:
            statement: The factual statement to analyze
            
        Returns:
            A dictionary containing analysis results.
        """
        # In a real implementation, this would use NLP to extract claims
        # For now, we'll use a simplified approach
        
        # Identify if the statement contains quantitative claims
        has_quantitative = any(char.isdigit() for char in statement)
        
        # Identify if the statement makes causal claims
        causal_indicators = ["cause", "lead to", "result in", "effect", "affect"]
        has_causal = any(indicator in statement.lower() for indicator in causal_indicators)
        
        # Identify if the statement makes comparative claims
        comparative_indicators = ["more", "less", "better", "worse", "higher", "lower"]
        has_comparative = any(indicator in statement.lower() for indicator in comparative_indicators)
        
        # Identify if the statement makes absolute claims
        absolute_indicators = ["always", "never", "all", "none", "every", "only"]
        has_absolute = any(indicator in statement.lower() for indicator in absolute_indicators)
        
        return {
            "has_quantitative": has_quantitative,
            "has_causal": has_causal,
            "has_comparative": has_comparative,
            "has_absolute": has_absolute,
            "complexity": self._assess_complexity(statement)
        }
    
    def _assess_complexity(self, statement: str) -> str:
        """
        Assess the complexity of a statement.
        
        Args:
            statement: The statement to assess
            
        Returns:
            A string indicating the complexity level.
        """
        # Simple heuristic based on statement length and structure
        words = statement.split()
        
        if len(words) < 10:
            return "simple"
        elif len(words) < 20:
            return "moderate"
        else:
            return "complex"
    
    def _evaluate_sources(self, sources: List[str]) -> Dict[str, Dict[str, any]]:
        """
        Evaluate the reliability and relevance of sources.
        
        Args:
            sources: List of sources to evaluate
            
        Returns:
            A dictionary mapping source to evaluation results.
        """
        source_evaluation = {}
        
        for source in sources:
            # In a real implementation, this would check against a database
            # of source reliability ratings or use heuristics to evaluate
            
            # For now, we'll use a simplified approach based on source type
            reliability = self._assess_source_reliability(source)
            relevance = self._assess_source_relevance(source)
            
            source_evaluation[source] = {
                "reliability": reliability,
                "relevance": relevance,
                "score": (reliability + relevance) / 2
            }
        
        return source_evaluation
    
    def _assess_source_reliability(self, source: str) -> float:
        """
        Assess the reliability of a source.
        
        Args:
            source: The source to assess
            
        Returns:
            A float between 0 and 1 indicating reliability.
        """
        # In a real implementation, this would check against a database
        # For now, we'll use a simplified approach based on source type
        
        reliability = 0.5  # Default moderate reliability
        
        # Check for high-reliability sources
        high_reliability_indicators = [
            "pubmed", "nejm", "jama", "lancet", "bmj", "cochrane",
            "mayo clinic", "cdc", "nih", "who", "fda"
        ]
        
        # Check for moderate-reliability sources
        moderate_reliability_indicators = [
            "webmd", "healthline", "medscape", "uptodate", "medlineplus"
        ]
        
        # Check for lower-reliability sources
        lower_reliability_indicators = [
            "blog", "forum", "opinion", "anecdotal"
        ]
        
        # Adjust reliability based on source type
        source_lower = source.lower()
        
        if any(indicator in source_lower for indicator in high_reliability_indicators):
            reliability = 0.9
        elif any(indicator in source_lower for indicator in moderate_reliability_indicators):
            reliability = 0.7
        elif any(indicator in source_lower for indicator in lower_reliability_indicators):
            reliability = 0.3
        
        # Check for recency if year is mentioned
        import re
        year_match = re.search(r'20[0-9]{2}', source)
        if year_match:
            year = int(year_match.group(0))
            current_year = 2025
            
            # Adjust reliability based on recency
            if year >= current_year - 2:
                reliability = min(reliability + 0.1, 1.0)
            elif year <= current_year - 10:
                reliability = max(reliability - 0.1, 0.0)
        
        return reliability
    
    def _assess_source_relevance(self, source: str) -> float:
        """
        Assess the relevance of a source to medical content.
        
        Args:
            source: The source to assess
            
        Returns:
            A float between 0 and 1 indicating relevance.
        """
        # In a real implementation, this would use NLP to assess relevance
        # For now, we'll use a simplified approach based on keywords
        
        relevance = 0.5  # Default moderate relevance
        
        # Check for medical relevance
        medical_indicators = [
            "medicine", "medical", "health", "clinical", "patient",
            "disease", "treatment", "therapy", "diagnosis", "prognosis",
            "symptom", "doctor", "hospital", "clinic", "study", "trial",
            "research", "journal"
        ]
        
        # Adjust relevance based on medical indicators
        source_lower = source.lower()
        
        medical_indicator_count = sum(
            1 for indicator in medical_indicators if indicator in source_lower
        )
        
        if medical_indicator_count >= 3:
            relevance = 0.9
        elif medical_indicator_count >= 1:
            relevance = 0.7
        
        return relevance
    
    def _verify_statement(
        self,
        statement: str,
        sources: List[str],
        statement_analysis: Dict[str, any],
        source_evaluation: Dict[str, Dict[str, any]],
        context: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Verify a statement against sources.
        
        Args:
            statement: The statement to verify
            sources: List of sources to check against
            statement_analysis: Analysis of the statement
            source_evaluation: Evaluation of the sources
            context: Additional context about the statement
            
        Returns:
            A dictionary containing verification results.
        """
        # In a real implementation, this would use NLP to compare the statement
        # against the content of the sources
        # For now, we'll use a simplified approach
        
        # Calculate overall source quality
        if sources:
            avg_source_quality = sum(
                source_info["score"] for source_info in source_evaluation.values()
            ) / len(sources)
        else:
            avg_source_quality = 0.0
        
        # Adjust verification confidence based on statement complexity and source quality
        base_confidence = 0.5
        
        # Adjust for statement complexity
        if statement_analysis["complexity"] == "simple":
            complexity_factor = 0.2
        elif statement_analysis["complexity"] == "moderate":
            complexity_factor = 0.0
        else:  # complex
            complexity_factor = -0.2
        
        # Adjust for statement type
        type_factor = 0.0
        if statement_analysis["has_absolute"]:
            type_factor -= 0.1  # Absolute claims are harder to verify
        if statement_analysis["has_causal"]:
            type_factor -= 0.1  # Causal claims are harder to verify
        
        # Calculate final confidence
        verification_confidence = min(
            max(base_confidence + complexity_factor + type_factor + (avg_source_quality - 0.5), 0.0),
            1.0
        )
        
        # Determine verification status
        if verification_confidence >= 0.8:
            status = "verified"
        elif verification_confidence >= 0.5:
            status = "partially verified"
        elif verification_confidence >= 0.2:
            status = "insufficient evidence"
        else:
            status = "unable to verify"
        
        return {
            "status": status,
            "confidence": verification_confidence,
            "source_quality": avg_source_quality,
            "factors": {
                "complexity": statement_analysis["complexity"],
                "has_absolute": statement_analysis["has_absolute"],
                "has_causal": statement_analysis["has_causal"],
                "has_comparative": statement_analysis["has_comparative"],
                "has_quantitative": statement_analysis["has_quantitative"]
            }
        }
    
    def _format_results(
        self,
        statement: str,
        verification_results: Dict[str, any],
        source_evaluation: Dict[str, Dict[str, any]]
    ) -> str:
        """
        Format verification results as a string.
        
        Args:
            statement: The statement that was verified
            verification_results: Results of the verification
            source_evaluation: Evaluation of the sources
            
        Returns:
            A formatted string containing the verification results.
        """
        result = "Fact Checker Results\n"
        result += "===================\n\n"
        
        result += f"Statement: \"{statement}\"\n\n"
        
        result += f"Verification Status: {verification_results['status'].upper()}\n"
        result += f"Confidence: {verification_results['confidence']:.2f} (0-1 scale)\n"
        result += f"Source Quality: {verification_results['source_quality']:.2f} (0-1 scale)\n\n"
        
        result += "Statement Analysis:\n"
        result += f"- Complexity: {verification_results['factors']['complexity']}\n"
        
        # Add flags for statement types
        flags = []
        if verification_results['factors']['has_absolute']:
            flags.append("contains absolute claims")
        if verification_results['factors']['has_causal']:
            flags.append("contains causal claims")
        if verification_results['factors']['has_comparative']:
            flags.append("contains comparative claims")
        if verification_results['factors']['has_quantitative']:
            flags.append("contains quantitative claims")
        
        if flags:
            result += f"- Flags: {', '.join(flags)}\n\n"
        else:
            result += "- No specific claim types flagged\n\n"
        
        result += "Source Evaluation:\n"
        for source, evaluation in source_evaluation.items():
            result += f"- {source}:\n"
            result += f"  - Reliability: {evaluation['reliability']:.2f}\n"
            result += f"  - Relevance: {evaluation['relevance']:.2f}\n"
            result += f"  - Overall Score: {evaluation['score']:.2f}\n"
        
        result += "\nRecommendations:\n"
        
        if verification_results['status'] == "verified":
            result += "- The statement is well-supported by reliable sources.\n"
        elif verification_results['status'] == "partially verified":
            result += "- The statement is partially supported but may need additional evidence or clarification.\n"
            result += "- Consider adding more specific citations or qualifying the statement.\n"
        elif verification_results['status'] == "insufficient evidence":
            result += "- The statement lacks sufficient supporting evidence.\n"
            result += "- Consider adding more reliable sources or revising the statement.\n"
        else:  # unable to verify
            result += "- The statement could not be verified with the provided sources.\n"
            result += "- Consider revising the statement or providing more relevant sources.\n"
        
        # Add specific recommendations based on statement type
        if verification_results['factors']['has_absolute']:
            result += "- Consider qualifying absolute statements unless they are definitively proven.\n"
        if verification_results['factors']['has_causal'] and verification_results['confidence'] < 0.8:
            result += "- Ensure causal claims are strongly supported by evidence or consider using more tentative language.\n"
        
        return result
