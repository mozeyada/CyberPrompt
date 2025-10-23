"""
Statistical Consistency Validation Tests for CyberPrompt Ensemble Evaluation

Tests the mathematical correctness of ensemble aggregation, reliability metrics,
and score normalization in the evaluation framework.
"""

import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.services.ensemble import EnsembleJudgeService
from app.services.composite import composite_from, normalize_rubric_scores
from app.models import JudgeResult, RubricScores, AggregatedScores, ReliabilityMetrics


class TestEnsembleStatistics:
    """Test statistical calculations in ensemble evaluation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ensemble_service = EnsembleJudgeService()
    
    def test_composite_score_calculation(self):
        """Test composite score calculation from dimension scores"""
        # Test case 1: All dimensions present
        scores = {
            "technical_accuracy": 4.0,
            "actionability": 3.5,
            "completeness": 4.5,
            "compliance_alignment": 3.0,
            "risk_awareness": 4.0,
            "relevance": 4.5,
            "clarity": 3.5
        }
        expected_composite = (4.0 + 3.5 + 4.5 + 3.0 + 4.0 + 4.5 + 3.5) / 7
        assert abs(composite_from(scores) - expected_composite) < 0.001
        
        # Test case 2: Missing dimensions (should use only present ones)
        partial_scores = {
            "technical_accuracy": 5.0,
            "actionability": 4.0,
            "completeness": 3.0
        }
        expected_partial = (5.0 + 4.0 + 3.0) / 3
        assert abs(composite_from(partial_scores) - expected_partial) < 0.001
        
        # Test case 3: Empty scores
        assert composite_from({}) == 0.0
    
    def test_score_normalization(self):
        """Test score normalization to [0, 5] range"""
        # Test case 1: Scores already in range
        normal_scores = {
            "technical_accuracy": 4.0,
            "actionability": 3.5,
            "completeness": 2.0
        }
        normalized = normalize_rubric_scores(normal_scores)
        assert normalized["technical_accuracy"] == 4.0
        assert normalized["actionability"] == 3.5
        assert normalized["completeness"] == 2.0
        
        # Test case 2: Out-of-range scores
        out_of_range = {
            "technical_accuracy": 6.0,  # Above 5
            "actionability": -1.0,      # Below 0
            "completeness": 3.0
        }
        normalized = normalize_rubric_scores(out_of_range)
        assert normalized["technical_accuracy"] == 5.0  # Clamped to 5
        assert normalized["actionability"] == 0.0       # Clamped to 0
        assert normalized["completeness"] == 3.0
        
        # Test case 3: Missing dimensions filled with zeros
        incomplete = {"technical_accuracy": 4.0}
        normalized = normalize_rubric_scores(incomplete)
        assert normalized["technical_accuracy"] == 4.0
        assert normalized["actionability"] == 0.0
        assert normalized["completeness"] == 0.0
        assert normalized["compliance_alignment"] == 0.0
        assert normalized["risk_awareness"] == 0.0
        assert normalized["relevance"] == 0.0
        assert normalized["clarity"] == 0.0
    
    def test_ensemble_metrics_perfect_agreement(self):
        """Test ensemble aggregation with perfect judge agreement"""
        # Create mock judge results with identical scores
        judge_results = {
            "primary": JudgeResult(
                judge_model="claude-3-5-haiku",
                scores=RubricScores(
                    technical_accuracy=5.0,
                    actionability=5.0,
                    completeness=5.0,
                    compliance_alignment=5.0,
                    risk_awareness=5.0,
                    relevance=5.0,
                    clarity=5.0,
                    composite=5.0
                ),
                raw_response="Perfect response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "secondary": JudgeResult(
                judge_model="gpt-4-turbo",
                scores=RubricScores(
                    technical_accuracy=5.0,
                    actionability=5.0,
                    completeness=5.0,
                    compliance_alignment=5.0,
                    risk_awareness=5.0,
                    relevance=5.0,
                    clarity=5.0,
                    composite=5.0
                ),
                raw_response="Perfect response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "tertiary": JudgeResult(
                judge_model="llama-3.3-70b",
                scores=RubricScores(
                    technical_accuracy=5.0,
                    actionability=5.0,
                    completeness=5.0,
                    compliance_alignment=5.0,
                    risk_awareness=5.0,
                    relevance=5.0,
                    clarity=5.0,
                    composite=5.0
                ),
                raw_response="Perfect response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            )
        }
        
        aggregated = self.ensemble_service.calculate_ensemble_metrics(judge_results)
        
        # Perfect agreement should yield mean=5.0, std=0.0
        assert abs(aggregated.mean_scores.technical_accuracy - 5.0) < 0.001
        assert abs(aggregated.mean_scores.composite - 5.0) < 0.001
        assert abs(aggregated.std_scores.technical_accuracy - 0.0) < 0.001
        assert abs(aggregated.std_scores.composite - 0.0) < 0.001
        
        # Confidence intervals should be tight
        ci = aggregated.confidence_95_ci["technical_accuracy"]
        assert abs(ci[0] - 5.0) < 0.001
        assert abs(ci[1] - 5.0) < 0.001
    
    def test_ensemble_metrics_maximum_disagreement(self):
        """Test ensemble aggregation with maximum judge disagreement"""
        judge_results = {
            "primary": JudgeResult(
                judge_model="claude-3-5-haiku",
                scores=RubricScores(
                    technical_accuracy=1.0,
                    actionability=1.0,
                    completeness=1.0,
                    compliance_alignment=1.0,
                    risk_awareness=1.0,
                    relevance=1.0,
                    clarity=1.0,
                    composite=1.0
                ),
                raw_response="Poor response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "secondary": JudgeResult(
                judge_model="gpt-4-turbo",
                scores=RubricScores(
                    technical_accuracy=3.0,
                    actionability=3.0,
                    completeness=3.0,
                    compliance_alignment=3.0,
                    risk_awareness=3.0,
                    relevance=3.0,
                    clarity=3.0,
                    composite=3.0
                ),
                raw_response="Average response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "tertiary": JudgeResult(
                judge_model="llama-3.3-70b",
                scores=RubricScores(
                    technical_accuracy=5.0,
                    actionability=5.0,
                    completeness=5.0,
                    compliance_alignment=5.0,
                    risk_awareness=5.0,
                    relevance=5.0,
                    clarity=5.0,
                    composite=5.0
                ),
                raw_response="Excellent response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            )
        }
        
        aggregated = self.ensemble_service.calculate_ensemble_metrics(judge_results)
        
        # Mean should be 3.0 (average of 1, 3, 5)
        assert abs(aggregated.mean_scores.technical_accuracy - 3.0) < 0.001
        assert abs(aggregated.mean_scores.composite - 3.0) < 0.001
        
        # Standard deviation should be calculated correctly
        expected_std = np.std([1.0, 3.0, 5.0], ddof=1)  # Sample std
        assert abs(aggregated.std_scores.technical_accuracy - expected_std) < 0.001
        
        # Confidence interval should be wide due to disagreement
        ci = aggregated.confidence_95_ci["technical_accuracy"]
        assert ci[0] < 3.0 < ci[1]  # Mean should be within CI
    
    def test_ensemble_metrics_missing_judge(self):
        """Test ensemble aggregation with missing judge (only 2 judges)"""
        judge_results = {
            "primary": JudgeResult(
                judge_model="claude-3-5-haiku",
                scores=RubricScores(
                    technical_accuracy=4.0,
                    actionability=4.0,
                    completeness=4.0,
                    compliance_alignment=4.0,
                    risk_awareness=4.0,
                    relevance=4.0,
                    clarity=4.0,
                    composite=4.0
                ),
                raw_response="Good response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "secondary": JudgeResult(
                judge_model="gpt-4-turbo",
                scores=RubricScores(
                    technical_accuracy=3.0,
                    actionability=3.0,
                    completeness=3.0,
                    compliance_alignment=3.0,
                    risk_awareness=3.0,
                    relevance=3.0,
                    clarity=3.0,
                    composite=3.0
                ),
                raw_response="Average response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            )
            # tertiary judge missing
        }
        
        aggregated = self.ensemble_service.calculate_ensemble_metrics(judge_results)
        
        # Should work with 2 judges
        assert abs(aggregated.mean_scores.technical_accuracy - 3.5) < 0.001  # (4.0 + 3.0) / 2
        assert abs(aggregated.mean_scores.composite - 3.5) < 0.001
    
    def test_ensemble_metrics_failed_judge(self):
        """Test ensemble aggregation with failed judge"""
        judge_results = {
            "primary": JudgeResult(
                judge_model="claude-3-5-haiku",
                scores=RubricScores(
                    technical_accuracy=4.0,
                    actionability=4.0,
                    completeness=4.0,
                    compliance_alignment=4.0,
                    risk_awareness=4.0,
                    relevance=4.0,
                    clarity=4.0,
                    composite=4.0
                ),
                raw_response="Good response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "secondary": JudgeResult(
                judge_model="gpt-4-turbo",
                scores=RubricScores(
                    technical_accuracy=3.0,
                    actionability=3.0,
                    completeness=3.0,
                    compliance_alignment=3.0,
                    risk_awareness=3.0,
                    relevance=3.0,
                    clarity=3.0,
                    composite=3.0
                ),
                raw_response="Average response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "tertiary": JudgeResult(
                judge_model="llama-3.3-70b",
                scores=RubricScores(
                    technical_accuracy=0.0,
                    actionability=0.0,
                    completeness=0.0,
                    compliance_alignment=0.0,
                    risk_awareness=0.0,
                    relevance=0.0,
                    clarity=0.0,
                    composite=0.0
                ),
                raw_response="Evaluation failed: API error",
                evaluation_time=datetime.utcnow(),
                tokens_used=0,
                cost_usd=0.0,
                fsp_used=False,
                evaluation_failed=True  # This judge failed
            )
        }
        
        aggregated = self.ensemble_service.calculate_ensemble_metrics(judge_results)
        
        # Should only use successful judges (primary and secondary)
        assert abs(aggregated.mean_scores.technical_accuracy - 3.5) < 0.001  # (4.0 + 3.0) / 2
        assert abs(aggregated.mean_scores.composite - 3.5) < 0.001
    
    def test_insufficient_judges_raises_exception(self):
        """Test that insufficient successful judges raises exception"""
        judge_results = {
            "primary": JudgeResult(
                judge_model="claude-3-5-haiku",
                scores=RubricScores(
                    technical_accuracy=4.0,
                    actionability=4.0,
                    completeness=4.0,
                    compliance_alignment=4.0,
                    risk_awareness=4.0,
                    relevance=4.0,
                    clarity=4.0,
                    composite=4.0
                ),
                raw_response="Good response",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "secondary": JudgeResult(
                judge_model="gpt-4-turbo",
                scores=RubricScores(
                    technical_accuracy=0.0,
                    actionability=0.0,
                    completeness=0.0,
                    compliance_alignment=0.0,
                    risk_awareness=0.0,
                    relevance=0.0,
                    clarity=0.0,
                    composite=0.0
                ),
                raw_response="Evaluation failed",
                evaluation_time=datetime.utcnow(),
                tokens_used=0,
                cost_usd=0.0,
                fsp_used=False,
                evaluation_failed=True
            ),
            "tertiary": JudgeResult(
                judge_model="llama-3.3-70b",
                scores=RubricScores(
                    technical_accuracy=0.0,
                    actionability=0.0,
                    completeness=0.0,
                    compliance_alignment=0.0,
                    risk_awareness=0.0,
                    relevance=0.0,
                    clarity=0.0,
                    composite=0.0
                ),
                raw_response="Evaluation failed",
                evaluation_time=datetime.utcnow(),
                tokens_used=0,
                cost_usd=0.0,
                fsp_used=False,
                evaluation_failed=True
            )
        }
        
        # Should raise exception with < 2 successful judges
        with pytest.raises(Exception, match="Less than 2 judges succeeded"):
            self.ensemble_service.calculate_ensemble_metrics(judge_results)
    
    def test_reliability_metrics_calculation(self):
        """Test reliability metrics calculation (Pearson correlations)"""
        judge_results = {
            "primary": JudgeResult(
                judge_model="claude-3-5-haiku",
                scores=RubricScores(
                    technical_accuracy=4.0,
                    actionability=3.0,
                    completeness=5.0,
                    compliance_alignment=2.0,
                    risk_awareness=4.0,
                    relevance=3.0,
                    clarity=4.0,
                    composite=3.57
                ),
                raw_response="Response 1",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "secondary": JudgeResult(
                judge_model="gpt-4-turbo",
                scores=RubricScores(
                    technical_accuracy=3.0,
                    actionability=4.0,
                    completeness=4.0,
                    compliance_alignment=3.0,
                    risk_awareness=3.0,
                    relevance=4.0,
                    clarity=3.0,
                    composite=3.43
                ),
                raw_response="Response 2",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            ),
            "tertiary": JudgeResult(
                judge_model="llama-3.3-70b",
                scores=RubricScores(
                    technical_accuracy=5.0,
                    actionability=2.0,
                    completeness=3.0,
                    compliance_alignment=4.0,
                    risk_awareness=5.0,
                    relevance=2.0,
                    clarity=5.0,
                    composite=3.71
                ),
                raw_response="Response 3",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            )
        }
        
        reliability = self.ensemble_service.calculate_reliability_metrics(judge_results)
        
        # Should have correlations for all pairs
        assert "primary_secondary" in reliability.pearson_correlations
        assert "primary_tertiary" in reliability.pearson_correlations
        assert "secondary_tertiary" in reliability.pearson_correlations
        
        # Correlations should be finite numbers
        for corr in reliability.pearson_correlations.values():
            assert np.isfinite(corr)
            assert -1.0 <= corr <= 1.0
        
        # Fleiss kappa should be finite
        assert np.isfinite(reliability.fleiss_kappa)
        
        # Agreement level should be one of the expected values
        assert reliability.inter_judge_agreement in ["poor", "fair", "moderate", "substantial"]
    
    def test_cost_estimation_accuracy(self):
        """Test cost estimation for different models"""
        # Test known pricing
        assert abs(self.ensemble_service.estimate_cost("claude-3-5-haiku-20241022", 1000) - 0.0001) < 0.00001
        assert abs(self.ensemble_service.estimate_cost("gpt-4-turbo", 1000) - 0.0003) < 0.00001
        assert abs(self.ensemble_service.estimate_cost("llama-3.3-70b-versatile", 1000) - 0.00005) < 0.00001
        
        # Test unknown model fallback
        fallback_cost = self.ensemble_service.estimate_cost("unknown-model", 1000)
        assert fallback_cost > 0
        assert abs(fallback_cost - 0.0002) < 0.00001  # Default pricing
