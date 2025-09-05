import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.environ["PYTHONPATH"] = str(project_root)

from app.evaluation.composite import composite_from, normalize_rubric_scores, validate_rubric_scores


def test_composite_calculation():
    """Test composite score calculation"""
    scores = {
        "technical_accuracy": 4.0,
        "actionability": 3.5,
        "completeness": 4.2,
        "compliance_alignment": 3.8,
        "risk_awareness": 4.1,
        "relevance": 4.0,
        "clarity": 3.9,
    }

    composite = composite_from(scores)
    expected = (4.0 + 3.5 + 4.2 + 3.8 + 4.1 + 4.0 + 3.9) / 7
    assert abs(composite - expected) < 0.001

def test_score_validation():
    """Test rubric score validation"""
    valid_scores = {
        "technical_accuracy": 3.0,
        "actionability": 4.0,
        "completeness": 2.0,
        "compliance_alignment": 5.0,
        "risk_awareness": 1.0,
        "relevance": 3.5,
        "clarity": 4.2,
    }

    assert validate_rubric_scores(valid_scores) is True

    # Test invalid scores
    invalid_scores = valid_scores.copy()
    invalid_scores["technical_accuracy"] = 6.0  # Too high
    assert validate_rubric_scores(invalid_scores) is False

    # Test missing dimension
    incomplete_scores = valid_scores.copy()
    del incomplete_scores["clarity"]
    assert validate_rubric_scores(incomplete_scores) is False

def test_score_normalization():
    """Test score normalization"""
    scores = {
        "technical_accuracy": 6.0,  # Too high
        "actionability": -1.0,       # Too low
        "completeness": 3.5,
        "compliance_alignment": 4.0,
        "risk_awareness": 2.8,
        "relevance": 4.2,
        "clarity": 3.1,
    }

    normalized = normalize_rubric_scores(scores)

    assert normalized["technical_accuracy"] == 5.0  # Capped at 5
    assert normalized["actionability"] == 0.0       # Floored at 0
    assert normalized["completeness"] == 3.5        # Unchanged
    assert "composite" in normalized                # Composite added
