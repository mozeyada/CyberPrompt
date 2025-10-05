"""Triple-Judge Ensemble Evaluation Service"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List
import numpy as np
from scipy.stats import pearsonr

from app.models import (
    JudgeResult, AggregatedScores, ReliabilityMetrics, EnsembleEvaluation,
    RubricScores, ScenarioType, LengthBin
)
from app.services.base import create_judge
from app.services.llm_client import ModelRunner

logger = logging.getLogger(__name__)


class EnsembleJudgeService:
    """Triple-judge ensemble evaluation service"""
    
    def __init__(self):
        from app.core.config import settings
        
        self.model_runner = ModelRunner(
            openai_key=settings.openai_api_key,
            anthropic_key=settings.anthropic_api_key,
            google_key="",  # Not used for ensemble
            groq_key=settings.groq_api_key  # For Llama 3.3 70B judge
        )
    
    async def evaluate_with_ensemble(
        self, 
        output: str, 
        scenario: ScenarioType,
        length_bin: LengthBin,
        bias_controls: Dict[str, bool],
        run_id: str,
        context: str = None
    ) -> EnsembleEvaluation:
        """Execute ensemble evaluation with all three judges"""
        
        logger.info(f"Starting ensemble evaluation for run {run_id}")
        
        # Define judge configurations  
        judge_configs = [
            {"model": "gpt-4o-mini", "type": "primary"},
            {"model": "claude-3-5-sonnet-20241022", "type": "secondary"},
            {"model": "llama-3.3-70b-versatile", "type": "tertiary"}
        ]
        
        # Execute parallel evaluations
        evaluation_tasks = [
            self.evaluate_single_judge(output, config, scenario, length_bin, bias_controls, run_id, context)
            for config in judge_configs
        ]
        
        try:
            results = await asyncio.gather(*evaluation_tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            judge_results = {}
            for i, result in enumerate(results):
                config = judge_configs[i]
                if isinstance(result, Exception):
                    logger.error(f"Judge {config['model']} failed: {result}")
                    judge_results[config['type']] = self.create_fallback_result(config['model'], str(result))
                else:
                    judge_results[config['type']] = result
            
            # Calculate aggregated scores
            aggregated = self.calculate_ensemble_metrics(judge_results)
            
            # Calculate reliability metrics
            reliability = self.calculate_reliability_metrics(judge_results)
            
            return EnsembleEvaluation(
                evaluation_id=f"ensemble_{run_id}_{int(datetime.utcnow().timestamp())}",
                primary_judge=judge_results.get("primary"),
                secondary_judge=judge_results.get("secondary"),
                tertiary_judge=judge_results.get("tertiary"),
                aggregated=aggregated,
                reliability_metrics=reliability
            )
            
        except Exception as e:
            logger.error(f"Ensemble evaluation failed: {e}")
            # Return minimal ensemble if all judges fail
            return self.create_minimal_ensemble(run_id, str(e))
    
    async def evaluate_single_judge(
        self, 
        output: str, 
        config: Dict[str, str], 
        scenario: ScenarioType, 
        length_bin: LengthBin, 
        bias_controls: Dict[str, bool], 
        run_id: str,
        context: str = None
    ) -> JudgeResult:
        """Evaluate with a single judge model"""
        
        try:
            # Handle Groq models separately
            if "llama" in config["model"].lower():
                from app.services.groq_client import GroqClient
                from app.core.config import settings
                client = GroqClient(settings.groq_api_key)
            else:        
                client = self.model_runner._get_client(config["model"])
                
            judge = create_judge({
                "type": "llm",
                "judge_model": config["model"]
            }, client)
            
            start_time = time.time()
            
            result = await judge.evaluate(
                output=output,
                scenario=scenario,
                length_bin=length_bin,
                bias_controls=bias_controls,
                context=context
            )
            
            eval_time = time.time() - start_time
            
            # Extract token counts and cost (simplified)
            tokens_used = len(output.split()) + len(str(result.get("raw_response", "")).split())
            cost_usd = self.estimate_cost(config["model"], tokens_used)
            
            return JudgeResult(
                judge_model=config["model"],
                scores=RubricScores(**result["scores"]),
                raw_response=result.get("raw_response", ""),
                evaluation_time=datetime.utcnow(),
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                fsp_used=result.get("fsp_used", False)
            )
            
        except Exception as e:
            logger.error(f"Judge {config['model']} evaluation failed: {e}")
            raise e
    
    def calculate_ensemble_metrics(self, judge_results: Dict[str, JudgeResult]) -> AggregatedScores:
        """Calculate mean, median, std, and confidence intervals"""
        
        def safe_float(value, default=0.0):
            """Convert numpy values to JSON-safe floats"""
            if np.isfinite(value):
                return float(value)
            return default
        
        dimensions = ["technical_accuracy", "actionability", "completeness",
                     "compliance_alignment", "risk_awareness", "relevance", "clarity"]
        
        mean_scores = {}
        std_scores = {}
        ci_95 = {}
        
        for dim in dimensions:
            scores = []
            for judge_type in ["primary", "secondary", "tertiary"]:
                if judge_type in judge_results and judge_results[judge_type]:
                    score_value = getattr(judge_results[judge_type].scores, dim, 0)
                    if score_value > 0:  # Only include valid scores
                        scores.append(score_value)
            
            if len(scores) >= 2:  # Need at least 2 scores for meaningful aggregation
                mean_scores[dim] = safe_float(np.mean(scores))
                std_scores[dim] = safe_float(np.std(scores))
                
                # 95% confidence interval
                ci_95[dim] = (
                    safe_float(mean_scores[dim] - 1.96 * std_scores[dim]),
                    safe_float(mean_scores[dim] + 1.96 * std_scores[dim])
                )
            else:
                # Fallback if insufficient scores
                mean_scores[dim] = safe_float(scores[0] if scores else 0)
                std_scores[dim] = 0.0
                ci_95[dim] = (mean_scores[dim], mean_scores[dim])
        
        # Composite score aggregation
        eligible_scores = [v for v in mean_scores.values() if v > 0]
        mean_scores["composite"] = safe_float(np.mean(eligible_scores)) if eligible_scores else 0.0
        std_scores["composite"] = safe_float(np.std(eligible_scores)) if len(eligible_scores) > 1 else 0.0
        
        ci_95["composite"] = (
            safe_float(mean_scores["composite"] - 1.96 * std_scores["composite"]),
            safe_float(mean_scores["composite"] + 1.96 * std_scores["composite"])
        )
        
        return AggregatedScores(
            mean_scores=RubricScores(**mean_scores),
            std_scores=RubricScores(**std_scores),
            confidence_95_ci=ci_95
        )
    
    def calculate_reliability_metrics(self, judge_results: Dict[str, JudgeResult]) -> ReliabilityMetrics:
        """Calculate Pearson correlations between judges"""
        
        correlations = {}
        
        # Extract scores for correlation analysis
        dimensions = ["technical_accuracy", "actionability", "completeness",
                     "compliance_alignment", "risk_awareness", "relevance", "clarity"]
        
        # Calculate pairwise correlations
        pairs = [("primary", "secondary"), ("primary", "tertiary"), ("secondary", "tertiary")]
        
        for (judge1_name, judge2_name) in pairs:
            judge1 = judge_results.get(judge1_name)
            judge2 = judge_results.get(judge2_name)
            
            if judge1 and judge2:
                scores1 = []
                scores2 = []
                
                for dim in dimensions:
                    score1 = getattr(judge1.scores, dim, 0)
                    score2 = getattr(judge2.scores, dim, 0)
                    
                    if score1 > 0 and score2 > 0:  # Only valid scores
                        scores1.append(score1)
                        scores2.append(score2)
                
                if len(scores1) >= 2:
                    try:
                        corr_coef, _ = pearsonr(scores1, scores2)
                        # Ensure correlation is finite
                        if np.isfinite(corr_coef):
                            correlations[f"{judge1_name}_{judge2_name}"] = float(corr_coef)
                        else:
                            correlations[f"{judge1_name}_{judge2_name}"] = 0.0
                    except Exception as e:
                        logger.warning(f"Correlation calculation failed: {e}")
                        correlations[f"{judge1_name}_{judge2_name}"] = 0.0
                else:
                    correlations[f"{judge1_name}_{judge2_name}"] = 0.0
        
        # Calculate average correlation with safe float conversion
        def safe_float(value, default=0.0):
            """Convert numpy values to JSON-safe floats"""
            if np.isfinite(value):
                return float(value)
            return default
        
        avg_correlation = safe_float(np.mean(list(correlations.values()))) if correlations else 0.0
        
        # Determine agreement level
        if avg_correlation > 0.8:
            agreement_level = "substantial"
        elif avg_correlation > 0.6:
            agreement_level = "moderate"  
        elif avg_correlation > 0.4:
            agreement_level = "fair"
        else:
            agreement_level = "poor"
        
        return ReliabilityMetrics(
            pearson_correlations=correlations,
            fleiss_kappa=avg_correlation,  # Simplified kappa approximation
            inter_judge_agreement=agreement_level
        )
    
    def estimate_cost(self, model: str, tokens_used: int) -> float:
        """Estimate cost for judge evaluation"""
        pricing = {
            "gpt-4o-mini": 0.0001 * (tokens_used / 1000),      # ~$0.10 per 1k tokens
            "claude-3-5-sonnet-20241022": 0.0003 * (tokens_used / 1000),  # ~$0.30 per 1k tokens
            "llama-3.3-70b-versatile": 0.00005 * (tokens_used / 1000),    # ~$0.05 per 1k tokens
        }
        return pricing.get(model, 0.0002 * (tokens_used / 1000))
    
    def create_fallback_result(self, judge_model: str, error: str) -> JudgeResult:
        """Create fallback result when judge fails"""
        fallback_scores = RubricScores(
            technical_accuracy=0,
            actionability=0,
            completeness=0,
            compliance_alignment=0,
            risk_awareness=0,
            relevance=0,
            clarity=0,
            composite=0
        )
        
        return JudgeResult(
            judge_model=judge_model,
            scores=fallback_scores,
            raw_response=f"Evaluation failed: {error}",
            tokens_used=0,
            cost_usd=0.0,
            fsp_used=False
        )
    
    def create_minimal_ensemble(self, run_id: str, error: str) -> EnsembleEvaluation:
        """Create minimal ensemble when all judges fail"""
        return EnsembleEvaluation(
            evaluation_id=f"ensemble_{run_id}_failed",
            primary_judge=None,
            secondary_judge=None,
            tertiary_judge=None,
            aggregated=AggregatedScores(
                mean_scores=RubricScores(
                    technical_accuracy=0,
                    actionability=0,
                    completeness=0,
                    compliance_alignment=0,
                    risk_awareness=0,
                    relevance=0,
                    clarity=0,
                    composite=0
                )
            ),
            reliability_metrics=ReliabilityMetrics(
                pearson_correlations={},
                fleiss_kappa=0,
                inter_judge_agreement="failed"
            )
        )
