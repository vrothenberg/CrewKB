"""
ReadabilityAnalyzerTool for analyzing text readability.

This module provides a tool for analyzing the readability of medical content,
including reading level assessment, sentence structure analysis, and
technical terminology detection.
"""

from typing import Dict, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import re


class ReadabilityAnalyzerToolInput(BaseModel):
    """Input schema for ReadabilityAnalyzerTool."""
    text: str = Field(
        ...,
        description="The text to analyze for readability"
    )
    target_grade_level: Optional[str] = Field(
        "8-10",
        description="Target grade level range (e.g., '8-10')"
    )


class ReadabilityAnalyzerTool(BaseTool):
    """
    Tool for analyzing the readability of medical content.
    
    This tool analyzes text for reading level, sentence complexity,
    technical terminology, and provides recommendations for improving
    readability.
    """
    
    name: str = "ReadabilityAnalyzerTool"
    description: str = "Analyze text readability and suggest improvements"
    args_schema: type[BaseModel] = ReadabilityAnalyzerToolInput
    
    # Technical medical terms that may need explanation
    MEDICAL_TERMS = [
        "acute", "chronic", "benign", "malignant", "idiopathic", "etiology",
        "pathophysiology", "prognosis", "remission", "exacerbation",
        "comorbidity", "contraindication", "differential diagnosis",
        "hypertension", "hypotension", "tachycardia", "bradycardia",
        "hyperglycemia", "hypoglycemia", "edema", "ischemia", "necrosis",
        "metastasis", "neuropathy", "myopathy", "nephropathy", "retinopathy",
        "carcinoma", "sarcoma", "lymphoma", "leukemia", "anemia", "thrombosis",
        "embolism", "infarction", "stenosis", "occlusion", "perfusion",
        "hypoxia", "anoxia", "dyspnea", "apnea", "hemoptysis", "hematemesis",
        "hematuria", "dysuria", "dysphagia", "dysphonia", "dysarthria",
        "paresthesia", "anesthesia", "hyperesthesia", "hypoesthesia",
        "ataxia", "apraxia", "aphasia", "agnosia", "amnesia", "dementia",
        "delirium", "syncope", "vertigo", "tinnitus", "nystagmus",
        "photophobia", "diplopia", "amblyopia", "scotoma", "ptosis",
        "mydriasis", "miosis", "strabismus", "hyperopia", "myopia",
        "astigmatism", "presbyopia", "cataract", "glaucoma", "retinopathy",
        "macular degeneration", "conjunctivitis", "keratitis", "uveitis",
        "blepharitis", "chalazion", "hordeolum", "xerophthalmia",
        "xerostomia", "gingivitis", "periodontitis", "stomatitis",
        "glossitis", "pharyngitis", "laryngitis", "rhinitis", "sinusitis",
        "otitis", "mastoiditis", "labyrinthitis", "bronchitis", "pneumonia",
        "pleuritis", "empyema", "pneumothorax", "hemothorax", "atelectasis",
        "emphysema", "asthma", "bronchiectasis", "fibrosis", "sarcoidosis"
    ]
    
    def _run(
        self,
        text: str,
        target_grade_level: Optional[str] = "8-10"
    ) -> str:
        """
        Analyze text readability and suggest improvements.
        
        Args:
            text: The text to analyze
            target_grade_level: Target grade level range (e.g., '8-10')
            
        Returns:
            A string containing the readability analysis and recommendations.
        """
        # Parse target grade level
        target_min, target_max = self._parse_grade_level(target_grade_level)
        
        # Calculate readability metrics
        metrics = self._calculate_metrics(text)
        
        # Analyze sentence structure
        sentence_analysis = self._analyze_sentences(text)
        
        # Identify technical terminology
        terminology_analysis = self._identify_technical_terms(text)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            metrics, sentence_analysis, terminology_analysis,
            target_min, target_max
        )
        
        # Format and return results
        return self._format_results(
            metrics, sentence_analysis, terminology_analysis,
            recommendations, target_min, target_max
        )
    
    def _parse_grade_level(self, target_grade_level: str) -> tuple:
        """
        Parse the target grade level range.
        
        Args:
            target_grade_level: Target grade level range (e.g., '8-10')
            
        Returns:
            A tuple containing the minimum and maximum grade levels.
        """
        try:
            if "-" in target_grade_level:
                min_level, max_level = target_grade_level.split("-")
                return int(min_level), int(max_level)
            else:
                level = int(target_grade_level)
                return level, level
        except (ValueError, TypeError):
            # Default to 8-10 if parsing fails
            return 8, 10
    
    def _calculate_metrics(self, text: str) -> Dict[str, float]:
        """
        Calculate readability metrics for the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary containing readability metrics.
        """
        # Prepare text for analysis
        text = text.replace("\n", " ").strip()
        
        # Count sentences, words, and syllables
        sentences = self._count_sentences(text)
        words = self._count_words(text)
        syllables = self._count_syllables(text)
        complex_words = self._count_complex_words(text)
        
        # Calculate average sentence length
        avg_sentence_length = words / max(sentences, 1)
        
        # Calculate average syllables per word
        avg_syllables_per_word = syllables / max(words, 1)
        
        # Calculate percentage of complex words
        percent_complex_words = (complex_words / max(words, 1)) * 100
        
        # Calculate Flesch-Kincaid Grade Level
        # Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        fk_grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        
        # Calculate Flesch Reading Ease
        # Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        flesch_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        
        # Calculate Gunning Fog Index
        # Formula: 0.4 * ((words/sentences) + 100 * (complex_words/words))
        gunning_fog = 0.4 * (avg_sentence_length + 100 * (complex_words / max(words, 1)))
        
        # Calculate SMOG Index
        # Formula: 1.043 * sqrt(complex_words * (30/sentences)) + 3.1291
        import math
        smog = 1.043 * math.sqrt(complex_words * (30 / max(sentences, 1))) + 3.1291
        
        return {
            "sentences": sentences,
            "words": words,
            "syllables": syllables,
            "complex_words": complex_words,
            "avg_sentence_length": avg_sentence_length,
            "avg_syllables_per_word": avg_syllables_per_word,
            "percent_complex_words": percent_complex_words,
            "flesch_kincaid_grade": fk_grade,
            "flesch_reading_ease": flesch_ease,
            "gunning_fog": gunning_fog,
            "smog": smog
        }
    
    def _count_sentences(self, text: str) -> int:
        """
        Count the number of sentences in the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            The number of sentences.
        """
        # Simple sentence counting based on punctuation
        # This is a simplification; a more robust implementation would use NLP
        sentence_endings = re.findall(r'[.!?]+', text)
        return len(sentence_endings) or 1  # Ensure at least 1 sentence
    
    def _count_words(self, text: str) -> int:
        """
        Count the number of words in the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            The number of words.
        """
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _count_syllables(self, text: str) -> int:
        """
        Count the number of syllables in the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            The estimated number of syllables.
        """
        # This is a simplified syllable counter
        # A more accurate implementation would use a dictionary or ML model
        words = re.findall(r'\b\w+\b', text.lower())
        syllable_count = 0
        
        for word in words:
            word = word.lower()
            # Count vowel groups as syllables
            count = len(re.findall(r'[aeiouy]+', word))
            
            # Adjust for common patterns
            if word.endswith('e'):
                count -= 1
            if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
                count += 1
            if count == 0:
                count = 1
                
            syllable_count += count
        
        return syllable_count
    
    def _count_complex_words(self, text: str) -> int:
        """
        Count the number of complex words (3+ syllables) in the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            The number of complex words.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        complex_word_count = 0
        
        for word in words:
            # Skip common suffixes that don't add syllables
            word = re.sub(r'(es|ed)$', '', word)
            
            # Count vowel groups as syllables
            syllables = len(re.findall(r'[aeiouy]+', word))
            
            # Adjust for common patterns
            if word.endswith('e'):
                syllables -= 1
            if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
                syllables += 1
            if syllables == 0:
                syllables = 1
            
            # Words with 3+ syllables are considered complex
            if syllables >= 3:
                complex_word_count += 1
        
        return complex_word_count
    
    def _analyze_sentences(self, text: str) -> Dict[str, any]:
        """
        Analyze sentence structure in the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary containing sentence analysis results.
        """
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Analyze sentence lengths
        sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
        
        # Identify long sentences (>20 words)
        long_sentences = [
            (i, s) for i, (s, length) in enumerate(zip(sentences, sentence_lengths))
            if length > 20
        ]
        
        # Identify sentences with passive voice
        passive_indicators = [
            r'\b(is|are|was|were|be|been|being)\s+\w+ed\b',
            r'\b(is|are|was|were|be|been|being)\s+\w+en\b'
        ]
        
        passive_sentences = []
        for i, sentence in enumerate(sentences):
            for pattern in passive_indicators:
                if re.search(pattern, sentence, re.IGNORECASE):
                    passive_sentences.append((i, sentence))
                    break
        
        # Calculate sentence variety
        if sentence_lengths:
            sentence_length_variance = self._calculate_variance(sentence_lengths)
        else:
            sentence_length_variance = 0
        
        return {
            "sentence_count": len(sentences),
            "avg_sentence_length": sum(sentence_lengths) / max(len(sentence_lengths), 1),
            "max_sentence_length": max(sentence_lengths) if sentence_lengths else 0,
            "min_sentence_length": min(sentence_lengths) if sentence_lengths else 0,
            "sentence_length_variance": sentence_length_variance,
            "long_sentences": long_sentences,
            "passive_sentences": passive_sentences
        }
    
    def _calculate_variance(self, values: List[int]) -> float:
        """
        Calculate the variance of a list of values.
        
        Args:
            values: List of values
            
        Returns:
            The variance of the values.
        """
        mean = sum(values) / len(values)
        squared_diff_sum = sum((x - mean) ** 2 for x in values)
        return squared_diff_sum / len(values)
    
    def _identify_technical_terms(self, text: str) -> Dict[str, any]:
        """
        Identify technical medical terminology in the text.
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary containing terminology analysis results.
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Identify medical terms
        medical_terms_found = []
        for term in self.MEDICAL_TERMS:
            if term.lower() in words:
                medical_terms_found.append(term)
        
        # Calculate density of medical terms
        medical_term_density = len(medical_terms_found) / max(len(words), 1) * 100
        
        return {
            "medical_terms_found": medical_terms_found,
            "medical_term_count": len(medical_terms_found),
            "medical_term_density": medical_term_density
        }
    
    def _generate_recommendations(
        self,
        metrics: Dict[str, float],
        sentence_analysis: Dict[str, any],
        terminology_analysis: Dict[str, any],
        target_min: int,
        target_max: int
    ) -> List[str]:
        """
        Generate recommendations for improving readability.
        
        Args:
            metrics: Readability metrics
            sentence_analysis: Sentence structure analysis
            terminology_analysis: Technical terminology analysis
            target_min: Minimum target grade level
            target_max: Maximum target grade level
            
        Returns:
            A list of recommendations.
        """
        recommendations = []
        
        # Check grade level
        grade_level = metrics["flesch_kincaid_grade"]
        if grade_level > target_max:
            recommendations.append(
                f"Simplify language to reduce grade level from {grade_level:.1f} "
                f"to target range ({target_min}-{target_max})."
            )
        
        # Check sentence length
        avg_sentence_length = sentence_analysis["avg_sentence_length"]
        if avg_sentence_length > 20:
            recommendations.append(
                f"Shorten sentences. Average sentence length is {avg_sentence_length:.1f} "
                f"words, aim for 15-20 words maximum."
            )
        
        # Check for long sentences
        long_sentences = sentence_analysis["long_sentences"]
        if long_sentences:
            recommendations.append(
                f"Break down {len(long_sentences)} long sentences "
                f"(>20 words) into shorter ones."
            )
        
        # Check for passive voice
        passive_sentences = sentence_analysis["passive_sentences"]
        if passive_sentences:
            recommendations.append(
                f"Convert {len(passive_sentences)} passive voice sentences "
                f"to active voice for clarity."
            )
        
        # Check for technical terminology
        medical_term_density = terminology_analysis["medical_term_density"]
        if medical_term_density > 5:
            recommendations.append(
                f"Reduce or explain medical terminology. Current density is "
                f"{medical_term_density:.1f}% of words."
            )
        
        # Check for sentence variety
        sentence_variance = sentence_analysis["sentence_length_variance"]
        if sentence_variance < 10:
            recommendations.append(
                "Increase sentence variety by mixing short and long sentences."
            )
        
        # Check for complex words
        percent_complex = metrics["percent_complex_words"]
        if percent_complex > 15:
            recommendations.append(
                f"Replace complex words (3+ syllables) with simpler alternatives. "
                f"Currently {percent_complex:.1f}% of words are complex."
            )
        
        return recommendations
    
    def _format_results(
        self,
        metrics: Dict[str, float],
        sentence_analysis: Dict[str, any],
        terminology_analysis: Dict[str, any],
        recommendations: List[str],
        target_min: int,
        target_max: int
    ) -> str:
        """
        Format analysis results as a string.
        
        Args:
            metrics: Readability metrics
            sentence_analysis: Sentence structure analysis
            terminology_analysis: Technical terminology analysis
            recommendations: List of recommendations
            target_min: Minimum target grade level
            target_max: Maximum target grade level
            
        Returns:
            A formatted string containing the analysis results.
        """
        result = "Readability Analysis Results\n"
        result += "===========================\n\n"
        
        # Format readability metrics
        result += "Readability Metrics:\n"
        result += f"- Flesch-Kincaid Grade Level: {metrics['flesch_kincaid_grade']:.1f}\n"
        result += f"- Flesch Reading Ease: {metrics['flesch_reading_ease']:.1f}\n"
        result += f"- Gunning Fog Index: {metrics['gunning_fog']:.1f}\n"
        result += f"- SMOG Index: {metrics['smog']:.1f}\n\n"
        
        # Interpret grade level
        grade_level = metrics["flesch_kincaid_grade"]
        if grade_level < target_min:
            grade_level_assessment = (
                f"Below target range ({target_min}-{target_max}). "
                f"Content may be too simple for the intended audience."
            )
        elif grade_level > target_max:
            grade_level_assessment = (
                f"Above target range ({target_min}-{target_max}). "
                f"Content may be too complex for the intended audience."
            )
        else:
            grade_level_assessment = (
                f"Within target range ({target_min}-{target_max}). "
                f"Appropriate for the intended audience."
            )
        
        result += f"Grade Level Assessment: {grade_level_assessment}\n\n"
        
        # Format sentence analysis
        result += "Sentence Structure Analysis:\n"
        result += f"- Total Sentences: {sentence_analysis['sentence_count']}\n"
        result += f"- Average Sentence Length: {sentence_analysis['avg_sentence_length']:.1f} words\n"
        result += f"- Longest Sentence: {sentence_analysis['max_sentence_length']} words\n"
        result += f"- Shortest Sentence: {sentence_analysis['min_sentence_length']} words\n"
        result += f"- Sentence Length Variety: {sentence_analysis['sentence_length_variance']:.1f}\n"
        result += f"- Long Sentences (>20 words): {len(sentence_analysis['long_sentences'])}\n"
        result += f"- Passive Voice Sentences: {len(sentence_analysis['passive_sentences'])}\n\n"
        
        # Format terminology analysis
        result += "Medical Terminology Analysis:\n"
        result += f"- Medical Terms Found: {terminology_analysis['medical_term_count']}\n"
        result += f"- Medical Term Density: {terminology_analysis['medical_term_density']:.1f}%\n"
        
        if terminology_analysis['medical_terms_found']:
            result += "- Examples of Medical Terms Found:\n"
            # Show up to 10 examples
            for term in terminology_analysis['medical_terms_found'][:10]:
                result += f"  - {term}\n"
            
            if len(terminology_analysis['medical_terms_found']) > 10:
                result += f"  - ... and {len(terminology_analysis['medical_terms_found']) - 10} more\n"
        
        result += "\n"
        
        # Format recommendations
        result += "Recommendations for Improving Readability:\n"
        if recommendations:
            for i, recommendation in enumerate(recommendations, 1):
                result += f"{i}. {recommendation}\n"
        else:
            result += "- No specific recommendations. The content appears to be readable and appropriate for the target audience.\n"
        
        return result
