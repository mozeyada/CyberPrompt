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
    """Calculate composite score as mean of present dimensions"""
    try:
        present_dims = [dim for dim in RUBRIC_DIMENSIONS if dim in scores]
        if not present_dims:
            return 0.0
        
        total = sum(scores[dim] for dim in present_dims)
        return round(total / len(present_dims), 3)
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
    # VERIFICATION: Log input scores
    logger.debug(f"[VARIANT-CHECK] Normalizing scores: input={scores}")
    
    normalized = {}
    for dim in RUBRIC_DIMENSIONS:
        if dim in scores:
            score = max(0, min(5, float(scores[dim])))
            normalized[dim] = round(score, 3)
        else:
            normalized[dim] = 0.0

    # Calculate composite
    normalized["composite"] = composite_from(normalized)
    
    # VERIFICATION: Log normalized scores
    logger.debug(f"[VARIANT-CHECK] Normalized scores: composite={normalized['composite']:.3f}, dimensions={sum(1 for v in normalized.values() if v > 0)}/7 non-zero")
    
    return normalized
