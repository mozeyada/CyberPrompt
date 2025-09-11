import logging
from typing import Any

from app.models import LengthBin

logger = logging.getLogger(__name__)


class FSPProcessor:
    """Focus Sentence Prompting - evaluate segments with full context preserved"""

    def __init__(self, segment_size: int = 200):
        self.segment_size = segment_size

    def should_use_fsp(self, text: str, length_bin: LengthBin) -> bool:
        """Determine if FSP should be used based on length"""
        return length_bin in [LengthBin.L]  # Only use FSP for long prompts

    def split_into_segments(self, text: str) -> list[dict[str, Any]]:
        """
        Split text into focused segments for evaluation

        Returns:
            List of segments with metadata
        """
        words = text.split()
        segments = []

        if len(words) <= self.segment_size:
            return [{"text": text, "start": 0, "end": len(words), "segment_id": 0}]

        # Create overlapping segments
        overlap = self.segment_size // 4  # 25% overlap
        step = self.segment_size - overlap

        for i in range(0, len(words), step):
            end = min(i + self.segment_size, len(words))
            segment_text = " ".join(words[i:end])

            segments.append({
                "text": segment_text,
                "start": i,
                "end": end,
                "segment_id": len(segments),
            })

            if end >= len(words):
                break

        return segments

    def create_focused_prompt(
        self,
        original_prompt: str,
        full_context: str,
        focus_segment: str,
        segment_info: dict[str, Any],
    ) -> str:
        """Create a focused evaluation prompt for a specific segment"""
        return f"""
{original_prompt}

FULL CONTEXT:
{full_context}

FOCUS SEGMENT (words {segment_info['start']}-{segment_info['end']}):
{focus_segment}

Please evaluate specifically the focused segment while considering the full context.
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


class GranularityMatcher:
    """Provide granularity-matched examples for different length bins"""

    def __init__(self):
        self.demos = {
            LengthBin.S: {
                "description": "Short analysis (≤16 tokens)",
                "example": """
Example for short response:
- Direct, concise answer
- Key point with minimal explanation
- Essential action only
""",
            },
            LengthBin.M: {
                "description": "Medium analysis (17-20 tokens)",
                "example": """
Example for medium response:
- 2-3 key points with brief explanations
- Specific actionable recommendations
- Main compliance considerations
""",
            },
            LengthBin.L: {
                "description": "Long analysis (>20 tokens)",
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
