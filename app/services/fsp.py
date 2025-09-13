import logging
from typing import Any

from app.models import LengthBin

logger = logging.getLogger(__name__)


class FSPProcessor:
    """Focus Sentence Prompting - evaluate one sentence at a time with full document context"""

    def __init__(self):
        pass

    def should_use_fsp(self, text: str, length_bin: LengthBin) -> bool:
        """Determine if FSP should be used based on length"""
        # FSP is designed for longer texts to maintain length invariance
        return length_bin in [LengthBin.L] or len(text.split()) > 200

    def split_into_sentences(self, text: str) -> list[dict[str, Any]]:
        """
        Split text into sentences for FSP evaluation
        
        Returns:
            List of sentences with metadata
        """
        # Simple sentence splitting - could be improved with proper NLP tools
        import re
        
        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+\s+', text.strip())
        
        # Clean up and create sentence objects
        sentence_list = []
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if sentence:  # Skip empty sentences
                sentence_list.append({
                    "text": sentence,
                    "sentence_id": i,
                    "position": i
                })
        
        return sentence_list

    def create_fsp_prompt(
        self,
        scenario: str,
        full_document: str,
        target_sentence: str,
        source_context: str = ""
    ) -> str:
        """Create FSP prompt as per the research paper methodology"""
        return f"""
Evaluate this {scenario} response using Focus Sentence Prompting.

FULL DOCUMENT CONTEXT:
{full_document}

TARGET SENTENCE TO EVALUATE:
{target_sentence}

Instructions: Evaluate ONLY the target sentence above, but use the full document context to understand its quality. Focus your evaluation on the specific sentence while considering how it fits within the complete response.
"""

    def aggregate_scores(self, segment_scores: list[dict[str, float]]) -> dict[str, float]:
        """
        Aggregate scores from multiple segments into document-level scores

        Uses weighted average based on segment length
        """
        if not segment_scores:
            return {}

        if len(segment_scores) == 1:
            return segment_scores[0]

        # Calculate weights based on segment contribution
        total_weight = sum(len(score.get("segment_text", "").split()) for score in segment_scores)

        aggregated = {}
        dimensions = ["technical_accuracy", "actionability", "completeness",
                     "compliance_alignment", "risk_awareness", "relevance", "clarity"]

        for dim in dimensions:
            weighted_sum = 0
            for score_dict in segment_scores:
                segment_weight = len(score_dict.get("segment_text", "").split())
                weighted_sum += score_dict.get(dim, 0) * segment_weight

            if total_weight > 0:
                aggregated[dim] = weighted_sum / total_weight
            else:
                aggregated[dim] = 0

        # Calculate composite
        aggregated["composite"] = sum(aggregated[dim] for dim in dimensions) / len(dimensions)

        return aggregated

    def aggregate_sentence_scores(self, sentence_scores: list[dict[str, float]]) -> dict[str, float]:
        """
        Aggregate sentence-level scores to document level using standard averaging
        
        FSP achieves length invariance through focused evaluation, not score manipulation
        """
        if not sentence_scores:
            return {}

        if len(sentence_scores) == 1:
            return sentence_scores[0]

        dimensions = ["technical_accuracy", "actionability", "completeness",
                     "compliance_alignment", "risk_awareness", "relevance", "clarity"]
        
        aggregated = {}
        
        # Simple average across all sentences
        for dim in dimensions:
            scores = [score_dict.get(dim, 0) for score_dict in sentence_scores]
            aggregated[dim] = sum(scores) / len(scores) if scores else 0
        
        # Calculate composite
        aggregated["composite"] = sum(aggregated[dim] for dim in dimensions) / len(dimensions)
        
        return aggregated


class GranularityMatcher:
    """Provide granularity-matched examples for different length bins"""

    def __init__(self):
        self.demos = {
            LengthBin.S: {
                "description": "Short analysis (≤300 tokens)",
                "example": """
Example for short response:
- Direct, concise answer
- Key point with minimal explanation
- Essential action only
""",
            },
            LengthBin.M: {
                "description": "Medium analysis (301-800 tokens)",
                "example": """
Example for medium response:
- 2-3 key points with brief explanations
- Specific actionable recommendations
- Main compliance considerations
""",
            },
            LengthBin.L: {
                "description": "Long analysis (>800 tokens)",
                "example": """
Example for long response:
- Comprehensive coverage of multiple aspects
- Detailed explanations with supporting evidence
- Structured recommendations with implementation steps
- Thorough compliance and regulatory considerations
- Risk assessment with mitigation strategies
""",
            },
        }

    def get_granularity_demo(self, length_bin: LengthBin) -> str:
        """Get granularity demonstration for given length bin"""
        demo = self.demos.get(length_bin)
        if demo:
            return f"{demo['description']}\n\n{demo['example']}"
        return ""

    def should_include_demo(self, length_bin: LengthBin, bias_controls: dict[str, bool]) -> bool:
        """Determine if granularity demo should be included"""
        return bias_controls.get("granularity_demo", False) and length_bin in self.demos


# Global instances
fsp_processor = FSPProcessor()
granularity_matcher = GranularityMatcher()
