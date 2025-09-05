"""Enhanced FSP (Focus Sentence Prompting) implementation for research-grade bias mitigation"""

import logging
import re
from typing import Any

from app.models import LengthBin

logger = logging.getLogger(__name__)

class EnhancedFSPProcessor:
    """Research-grade FSP implementation with statistical validation"""

    def __init__(self):
        self.length_thresholds = {
            LengthBin.XS: 200,   # ≤200 tokens
            LengthBin.S: 500,    # 201-500 tokens
            LengthBin.M: 1000,   # 501-1000 tokens
            LengthBin.L: 2000,   # 1001-2000 tokens
            LengthBin.XL: 9999,   # >2000 tokens
        }

    def should_apply_fsp(self, response: str, length_bin: LengthBin) -> bool:
        """Determine if FSP should be applied based on response characteristics"""
        word_count = len(response.split())

        # Apply FSP for Medium+ responses to mitigate verbosity bias
        return length_bin in [LengthBin.M, LengthBin.L, LengthBin.XL] and word_count > 150

    def segment_response(self, response: str, target_segments: int = 3) -> list[dict[str, Any]]:
        """Segment response into focus areas for FSP evaluation"""

        # Split by natural boundaries (paragraphs, numbered lists, etc.)
        segments = []

        # Method 1: Split by paragraphs
        paragraphs = [p.strip() for p in response.split("\n\n") if p.strip()]

        if len(paragraphs) >= target_segments:
            # Use paragraph boundaries
            segment_size = len(paragraphs) // target_segments
            for i in range(0, len(paragraphs), segment_size):
                segment_text = "\n\n".join(paragraphs[i:i+segment_size])
                segments.append({
                    "text": segment_text,
                    "type": "paragraph_group",
                    "position": i // segment_size,
                    "word_count": len(segment_text.split()),
                })
        else:
            # Method 2: Split by sentences for shorter responses
            sentences = re.split(r"[.!?]+", response)
            sentences = [s.strip() for s in sentences if s.strip()]

            if len(sentences) >= target_segments:
                segment_size = len(sentences) // target_segments
                for i in range(0, len(sentences), segment_size):
                    segment_text = ". ".join(sentences[i:i+segment_size]) + "."
                    segments.append({
                        "text": segment_text,
                        "type": "sentence_group",
                        "position": i // segment_size,
                        "word_count": len(segment_text.split()),
                    })

        # Ensure we have at least one segment
        if not segments:
            segments = [{
                "text": response,
                "type": "full_response",
                "position": 0,
                "word_count": len(response.split()),
            }]

        return segments[:target_segments]  # Limit to target number

    def create_focused_prompt(self, original_prompt: str, full_response: str,
                            segment: dict[str, Any], context: str = "") -> str:
        """Create FSP-enhanced prompt for segment evaluation"""

        fsp_template = """
FOCUS SENTENCE PROMPTING (FSP) EVALUATION

ORIGINAL TASK: {original_prompt}

FULL RESPONSE CONTEXT:
{context_preview}

FOCUS SEGMENT TO EVALUATE:
{segment_text}

EVALUATION INSTRUCTIONS:
- Evaluate ONLY the focus segment above
- Consider the segment within the context of the full response
- Score based on the segment's contribution to the overall task
- Use the same 7-dimension rubric: Technical Accuracy, Actionability, Completeness, Compliance Alignment, Risk Awareness, Relevance, Clarity

Return JSON scores for the focus segment:
"""

        # Create context preview (first and last 100 words of full response)
        words = full_response.split()
        if len(words) > 200:
            context_preview = " ".join(words[:100]) + "\n[...middle content...]\n" + " ".join(words[-100:])
        else:
            context_preview = full_response

        return fsp_template.format(
            original_prompt=original_prompt,
            context_preview=context_preview,
            segment_text=segment["text"],
        )

    def aggregate_fsp_scores(self, segment_scores: list[dict[str, Any]]) -> dict[str, float]:
        """Aggregate FSP segment scores using weighted averaging"""

        if not segment_scores:
            return {}

        # Weight segments by word count (longer segments have more influence)
        total_weight = sum(score.get("word_count", 1) for score in segment_scores)

        aggregated = {}
        rubric_dimensions = ["technical_accuracy", "actionability", "completeness",
                           "compliance_alignment", "risk_awareness", "relevance", "clarity"]

        for dimension in rubric_dimensions:
            weighted_sum = 0
            for score in segment_scores:
                if dimension in score:
                    weight = score.get("word_count", 1) / total_weight
                    weighted_sum += score[dimension] * weight

            aggregated[dimension] = round(weighted_sum, 2)

        # Calculate composite score
        if aggregated:
            aggregated["composite"] = round(sum(aggregated.values()) / len(aggregated), 2)

        return aggregated

    def calculate_bias_metrics(self, standard_scores: dict[str, float],
                             fsp_scores: dict[str, float]) -> dict[str, Any]:
        """Calculate bias mitigation metrics for research analysis"""

        if not standard_scores or not fsp_scores:
            return {}

        bias_metrics = {}

        for dimension in standard_scores:
            if dimension in fsp_scores:
                standard_score = standard_scores[dimension]
                fsp_score = fsp_scores[dimension]

                # Calculate bias adjustment
                bias_adjustment = standard_score - fsp_score
                bias_percentage = (bias_adjustment / standard_score * 100) if standard_score > 0 else 0

                bias_metrics[f"{dimension}_bias"] = {
                    "standard_score": standard_score,
                    "fsp_score": fsp_score,
                    "bias_adjustment": round(bias_adjustment, 3),
                    "bias_percentage": round(bias_percentage, 1),
                }

        # Overall bias summary
        bias_adjustments = [m["bias_adjustment"] for m in bias_metrics.values()]
        bias_metrics["summary"] = {
            "avg_bias_adjustment": round(sum(bias_adjustments) / len(bias_adjustments), 3),
            "max_bias_adjustment": max(bias_adjustments),
            "bias_direction": "positive" if sum(bias_adjustments) > 0 else "negative",
        }

        return bias_metrics

# Global enhanced FSP processor
enhanced_fsp = EnhancedFSPProcessor()
