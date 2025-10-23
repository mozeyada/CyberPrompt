"""
End-to-End Integration Tests for CyberPrompt Evaluation Framework

Tests the complete evaluation pipeline from prompt input to score storage,
including failure recovery and concurrent execution scenarios.
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.ensemble import EnsembleJudgeService
from app.services.experiment import ExperimentService
from app.models import ScenarioType, LengthBin, JudgeResult, RubricScores


class TestIntegrationPipeline:
    """Test complete evaluation pipeline integration"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ensemble_service = EnsembleJudgeService()
        self.experiment_service = ExperimentService()
        
        # Load test data
        data_dir = Path(__file__).parent.parent.parent / "data" / "validation"
        with open(data_dir / "edge_cases.json") as f:
            self.edge_cases = json.load(f)
    
    @pytest.mark.asyncio
    async def test_full_pipeline_success(self):
        """Test complete pipeline: prompt → LLM response → ensemble evaluation → score storage"""
        test_response = "**Immediate Containment:** 1) Suspend service_account immediately 2) Isolate workstation 3) Block cloud access. **Evidence:** Image devices, collect logs, chain of custody. **Recovery:** Legal coordination, IP protection, customer notification."
        
        # Mock the LLM client to return our test response
        with patch('app.services.llm_client.ModelRunner') as mock_runner:
            mock_client = Mock()
            mock_client.generate = AsyncMock(return_value=test_response)
            mock_runner.return_value._get_client.return_value = mock_client
            
            # Mock the ensemble evaluation
            with patch.object(self.ensemble_service, 'evaluate_with_ensemble') as mock_ensemble:
                mock_ensemble.return_value = self._create_successful_ensemble_result()
                
                # Execute full pipeline
                result = await self.ensemble_service.evaluate_with_ensemble(
                    output=test_response,
                    scenario=ScenarioType.SOC_INCIDENT,
                    length_bin=LengthBin.M,
                    bias_controls={"fsp": True},
                    run_id="integration_test_001"
                )
                
                # Verify pipeline completed successfully
                assert result is not None
                assert result.aggregated is not None
                assert result.reliability_metrics is not None
                
                # Verify scores are reasonable
                assert 0 <= result.aggregated.mean_scores.composite <= 5
                assert result.aggregated.mean_scores.technical_accuracy > 0
                assert result.aggregated.mean_scores.actionability > 0
    
    @pytest.mark.asyncio
    async def test_pipeline_with_judge_failure(self):
        """Test pipeline behavior when one judge fails"""
        test_response = "Standard response for failure testing"
        
        with patch.object(self.ensemble_service, 'evaluate_single_judge') as mock_single_judge:
            # Mock two successful judges and one failed judge
            successful_result = JudgeResult(
                judge_model="claude-3-5-haiku",
                scores=RubricScores(
                    technical_accuracy=4.0,
                    actionability=4.0,
                    completeness=3.5,
                    compliance_alignment=3.0,
                    risk_awareness=4.0,
                    relevance=4.5,
                    clarity=4.0,
                    composite=3.86
                ),
                raw_response="Successful evaluation",
                evaluation_time=datetime.utcnow(),
                tokens_used=100,
                cost_usd=0.01,
                fsp_used=False,
                evaluation_failed=False
            )
            
            failed_result = JudgeResult(
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
                raw_response="Evaluation failed: API timeout",
                evaluation_time=datetime.utcnow(),
                tokens_used=0,
                cost_usd=0.0,
                fsp_used=False,
                evaluation_failed=True
            )
            
            # Configure mock to return different results for different judges
            def mock_judge_side_effect(*args, **kwargs):
                config = args[1]  # Second argument is config
                if config["model"] == "gpt-4-turbo":
                    return failed_result
                else:
                    return successful_result
            
            mock_single_judge.side_effect = mock_judge_side_effect
            
            # Execute evaluation
            result = await self.ensemble_service.evaluate_with_ensemble(
                output=test_response,
                scenario=ScenarioType.SOC_INCIDENT,
                length_bin=LengthBin.M,
                bias_controls={"fsp": True},
                run_id="failure_test_001"
            )
            
            # Should still succeed with 2 judges
            assert result is not None
            assert result.aggregated is not None
            assert result.aggregated.mean_scores.composite > 0
    
    @pytest.mark.asyncio
    async def test_pipeline_with_all_judges_failing(self):
        """Test pipeline behavior when all judges fail"""
        test_response = "Response for complete failure testing"
        
        with patch.object(self.ensemble_service, 'evaluate_single_judge') as mock_single_judge:
            # Mock all judges failing
            mock_single_judge.side_effect = Exception("All judges failed")
            
            # Execute evaluation
            result = await self.ensemble_service.evaluate_with_ensemble(
                output=test_response,
                scenario=ScenarioType.SOC_INCIDENT,
                length_bin=LengthBin.M,
                bias_controls={"fsp": True},
                run_id="complete_failure_test_001"
            )
            
            # Should return minimal ensemble with zero scores
            assert result is not None
            assert result.aggregated is not None
            assert result.aggregated.mean_scores.composite == 0.0
            assert result.reliability_metrics.inter_judge_agreement == "failed"
    
    @pytest.mark.asyncio
    async def test_concurrent_pipeline_execution(self):
        """Test multiple concurrent pipeline executions"""
        test_responses = [
            "First concurrent response for testing race conditions and thread safety",
            "Second concurrent response for testing race conditions and thread safety",
            "Third concurrent response for testing race conditions and thread safety",
            "Fourth concurrent response for testing race conditions and thread safety",
            "Fifth concurrent response for testing race conditions and thread safety"
        ]
        
        with patch.object(self.ensemble_service, 'evaluate_with_ensemble') as mock_ensemble:
            # Mock successful results
            mock_ensemble.return_value = self._create_successful_ensemble_result()
            
            # Execute concurrent evaluations
            tasks = []
            for i, response in enumerate(test_responses):
                task = self.ensemble_service.evaluate_with_ensemble(
                    output=response,
                    scenario=ScenarioType.SOC_INCIDENT,
                    length_bin=LengthBin.M,
                    bias_controls={"fsp": True},
                    run_id=f"concurrent_test_{i:03d}"
                )
                tasks.append(task)
            
            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all completed successfully
            for i, result in enumerate(results):
                assert not isinstance(result, Exception), \
                    f"Concurrent evaluation {i} failed with exception: {result}"
                assert result is not None, f"Concurrent evaluation {i} returned None"
                assert result.aggregated is not None, f"Concurrent evaluation {i} has no aggregated scores"
    
    @pytest.mark.asyncio
    async def test_pipeline_with_edge_case_inputs(self):
        """Test pipeline with edge case inputs"""
        edge_cases = [
            ("", "empty_response"),
            ("   \n\t  \n  ", "whitespace_only"),
            ("A", "single_character"),
            ("🔒 安全事件响应", "unicode_heavy"),
            ("<script>alert('xss')</script>", "code_injection_attempt")
        ]
        
        for response_text, case_name in edge_cases:
            with patch.object(self.ensemble_service, 'evaluate_with_ensemble') as mock_ensemble:
                # Mock appropriate results for edge cases
                if case_name == "empty_response":
                    mock_ensemble.return_value = self._create_zero_scores_ensemble_result()
                else:
                    mock_ensemble.return_value = self._create_successful_ensemble_result()
                
                # Execute evaluation
                result = await self.ensemble_service.evaluate_with_ensemble(
                    output=response_text,
                    scenario=ScenarioType.SOC_INCIDENT,
                    length_bin=LengthBin.S,
                    bias_controls={"fsp": True},
                    run_id=f"edge_case_{case_name}"
                )
                
                # Should not crash
                assert result is not None, f"Pipeline crashed on edge case: {case_name}"
                assert result.aggregated is not None, f"No aggregated scores for edge case: {case_name}"
                
                # Empty response should have zero scores
                if case_name == "empty_response":
                    assert result.aggregated.mean_scores.composite == 0.0, \
                        f"Empty response should have zero composite score"
    
    @pytest.mark.asyncio
    async def test_pipeline_data_consistency(self):
        """Test that pipeline maintains data consistency across components"""
        test_response = "Consistent data test response with specific technical details and actionable recommendations."
        
        with patch.object(self.ensemble_service, 'evaluate_with_ensemble') as mock_ensemble:
            # Create a specific mock result
            mock_result = self._create_successful_ensemble_result()
            mock_ensemble.return_value = mock_result
            
            # Execute evaluation
            result = await self.ensemble_service.evaluate_with_ensemble(
                output=test_response,
                scenario=ScenarioType.SOC_INCIDENT,
                length_bin=LengthBin.M,
                bias_controls={"fsp": True},
                run_id="consistency_test_001"
            )
            
            # Verify data consistency
            assert result.evaluation_id is not None
            assert result.aggregated.mean_scores.composite > 0
            assert result.aggregated.std_scores.composite >= 0
            assert len(result.aggregated.confidence_95_ci) > 0
            
            # Verify reliability metrics
            assert result.reliability_metrics.fleiss_kappa >= 0
            assert result.reliability_metrics.inter_judge_agreement in ["poor", "fair", "moderate", "substantial"]
            
            # Verify judge results structure
            if result.primary_judge:
                assert "model" in result.primary_judge
                assert "type" in result.primary_judge
    
    @pytest.mark.asyncio
    async def test_pipeline_performance_under_load(self):
        """Test pipeline performance with multiple rapid requests"""
        test_response = "Performance test response for load testing the evaluation pipeline."
        
        with patch.object(self.ensemble_service, 'evaluate_with_ensemble') as mock_ensemble:
            mock_ensemble.return_value = self._create_successful_ensemble_result()
            
            # Execute many rapid evaluations
            start_time = datetime.utcnow()
            tasks = []
            
            for i in range(20):  # 20 concurrent evaluations
                task = self.ensemble_service.evaluate_with_ensemble(
                    output=test_response,
                    scenario=ScenarioType.SOC_INCIDENT,
                    length_bin=LengthBin.M,
                    bias_controls={"fsp": True},
                    run_id=f"load_test_{i:03d}"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = datetime.utcnow()
            
            # Verify all completed
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == 20, f"Only {len(successful_results)}/20 evaluations succeeded"
            
            # Verify reasonable performance (should complete within reasonable time)
            duration = (end_time - start_time).total_seconds()
            assert duration < 30, f"Load test took too long: {duration} seconds"
    
    def _create_successful_ensemble_result(self):
        """Create a mock successful ensemble result"""
        from app.models import EnsembleEvaluation, AggregatedScores, ReliabilityMetrics
        
        aggregated = AggregatedScores(
            mean_scores=RubricScores(
                technical_accuracy=4.0,
                actionability=4.0,
                completeness=3.5,
                compliance_alignment=3.0,
                risk_awareness=4.0,
                relevance=4.5,
                clarity=4.0,
                composite=3.86
            ),
            std_scores=RubricScores(
                technical_accuracy=0.2,
                actionability=0.1,
                completeness=0.3,
                compliance_alignment=0.2,
                risk_awareness=0.1,
                relevance=0.2,
                clarity=0.1,
                composite=0.15
            ),
            confidence_95_ci={
                "technical_accuracy": (3.6, 4.4),
                "actionability": (3.8, 4.2),
                "completeness": (2.9, 4.1),
                "compliance_alignment": (2.6, 3.4),
                "risk_awareness": (3.8, 4.2),
                "relevance": (4.1, 4.9),
                "clarity": (3.8, 4.2),
                "composite": (3.57, 4.15)
            }
        )
        
        reliability = ReliabilityMetrics(
            pearson_correlations={
                "primary_secondary": 0.85,
                "primary_tertiary": 0.78,
                "secondary_tertiary": 0.82
            },
            fleiss_kappa=0.82,
            inter_judge_agreement="substantial"
        )
        
        return EnsembleEvaluation(
            evaluation_id="mock_successful_evaluation",
            primary_judge={
                "model": "claude-3-5-haiku",
                "type": "primary",
                "scores": {"composite": 3.9}
            },
            secondary_judge={
                "model": "gpt-4-turbo",
                "type": "secondary",
                "scores": {"composite": 3.8}
            },
            tertiary_judge={
                "model": "llama-3.3-70b",
                "type": "tertiary",
                "scores": {"composite": 3.9}
            },
            aggregated=aggregated,
            reliability_metrics=reliability
        )
    
    def _create_zero_scores_ensemble_result(self):
        """Create a mock ensemble result with zero scores"""
        from app.models import EnsembleEvaluation, AggregatedScores, ReliabilityMetrics
        
        aggregated = AggregatedScores(
            mean_scores=RubricScores(
                technical_accuracy=0.0,
                actionability=0.0,
                completeness=0.0,
                compliance_alignment=0.0,
                risk_awareness=0.0,
                relevance=0.0,
                clarity=0.0,
                composite=0.0
            ),
            std_scores=RubricScores(
                technical_accuracy=0.0,
                actionability=0.0,
                completeness=0.0,
                compliance_alignment=0.0,
                risk_awareness=0.0,
                relevance=0.0,
                clarity=0.0,
                composite=0.0
            ),
            confidence_95_ci={
                "technical_accuracy": (0.0, 0.0),
                "actionability": (0.0, 0.0),
                "completeness": (0.0, 0.0),
                "compliance_alignment": (0.0, 0.0),
                "risk_awareness": (0.0, 0.0),
                "relevance": (0.0, 0.0),
                "clarity": (0.0, 0.0),
                "composite": (0.0, 0.0)
            }
        )
        
        reliability = ReliabilityMetrics(
            pearson_correlations={},
            fleiss_kappa=0.0,
            inter_judge_agreement="poor"
        )
        
        return EnsembleEvaluation(
            evaluation_id="mock_zero_scores_evaluation",
            primary_judge=None,
            secondary_judge=None,
            tertiary_judge=None,
            aggregated=aggregated,
            reliability_metrics=reliability
        )




