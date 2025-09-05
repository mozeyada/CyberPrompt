import logging

logger = logging.getLogger(__name__)

RUBRIC_DIMENSIONS = [
    "technical_accuracy",
    "actionability",
    "completeness",
    "compliance_alignment",
    "risk_awareness",
    "relevance",
    "clarity",
]


def composite_from(scores: dict[str, float]) -> float:
    """Calculate composite score as mean of 7 dimensions"""
    try:
        total = sum(scores[dim] for dim in RUBRIC_DIMENSIONS if dim in scores)
        return round(total / len(RUBRIC_DIMENSIONS), 3)
    except Exception as e:
        logger.error(f"Error calculating composite score: {e}")
        return 0.0


def validate_rubric_scores(scores: dict[str, float]) -> bool:
    """Validate that all scores are in valid range [0, 5]"""
    try:
        for dim in RUBRIC_DIMENSIONS:
            if dim not in scores:
                return False
            score = scores[dim]
            if not isinstance(score, int | float) or score < 0 or score > 5:
                return False
        return True
    except Exception:
        return False


def normalize_rubric_scores(scores: dict[str, float]) -> dict[str, float]:
    """Normalize scores to ensure they're within [0, 5] range"""
    normalized = {}
    for dim in RUBRIC_DIMENSIONS:
        if dim in scores:
            score = max(0, min(5, float(scores[dim])))
            normalized[dim] = round(score, 3)
        else:
            normalized[dim] = 0.0

    # Calculate composite
    normalized["composite"] = composite_from(normalized)
    return normalized
