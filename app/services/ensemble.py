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
            google_key=settings.google_api_key,  # Enable Google for Gemini judge
            groq_key=settings.groq_api_key
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
        
        # VERIFICATION: Log ensemble evaluation inputs
        logger.info(f"[VARIANT-CHECK] Ensemble evaluation start for {run_id}: length_bin={length_bin}, output_len={len(output)}, context_len={len(context) if context else 0}, scenario={scenario}")
        logger.info(f"Starting ensemble evaluation for run {run_id}")
        
        # Define judge configurations  
        judge_configs = [
            {"model": "claude-3-5-haiku-20241022", "type": "primary"},
            {"model": "gpt-4-turbo", "type": "secondary"},
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
                    # Don't add failed judges to results - let ensemble fail if any judge fails
                    continue
                else:
                    judge_results[config['type']] = result
                    # VERIFICATION: Log individual judge scores
                    logger.info(f"[DEBUG] Judge {config['model']} result type: {type(result)}, has scores: {hasattr(result, 'scores')}")
                    scores = result.scores  # ✅ Access as object attribute
                    logger.info(f"[VARIANT-CHECK] Judge {config['model']} ({config['type']}) scores for {run_id}: composite={scores.composite:.3f}, technical_accuracy={scores.technical_accuracy:.3f}, completeness={scores.completeness:.3f}")
            
            # DEBUG: Check what we have in judge_results
            logger.info(f"[DEBUG] judge_results keys: {list(judge_results.keys())}")
            for judge_type, judge_result in judge_results.items():
                logger.info(f"[DEBUG] {judge_type}: type={type(judge_result)}, has scores: {hasattr(judge_result, 'scores')}")
            
            # Calculate aggregated scores
            aggregated = self.calculate_ensemble_metrics(judge_results)
            
            # Calculate reliability metrics
            reliability = self.calculate_reliability_metrics(judge_results)
            
            # Convert JudgeResult objects to dicts with model and type fields for database storage
            def convert_judge_result(judge_result, judge_type):
                if not judge_result:
                    return None
                result_dict = judge_result.model_dump()
                result_dict["model"] = judge_result.judge_model
                result_dict["type"] = judge_type
                return result_dict
            
            return EnsembleEvaluation(
                evaluation_id=f"ensemble_{run_id}_{int(datetime.utcnow().timestamp())}",
                primary_judge=convert_judge_result(judge_results.get("primary"), "primary"),
                secondary_judge=convert_judge_result(judge_results.get("secondary"), "secondary"),
                tertiary_judge=convert_judge_result(judge_results.get("tertiary"), "tertiary"),
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
        
        # VERIFICATION: Log judge evaluation start
        logger.info(f"[VARIANT-CHECK] Judge {config['model']} evaluating {run_id}: output_len={len(output)}, length_bin={length_bin}")
        
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
            
            # result is a dictionary from base judge service
            return JudgeResult(
                judge_model=config["model"],
                scores=RubricScores(**result["scores"]),
                raw_response=result.get("raw_response", ""),
                evaluation_time=datetime.utcnow(),
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                fsp_used=result.get("fsp_used", False),
                evaluation_failed=result.get("evaluation_failed", False)
            )
            
        except Exception as e:
            logger.error(f"Judge {config['model']} evaluation failed: {e}")
            raise e
    
    def calculate_ensemble_metrics(self, judge_results: Dict[str, JudgeResult]) -> AggregatedScores:
        """Calculate mean, median, std, and confidence intervals"""
        
        # VERIFICATION: Log before aggregation
        logger.info(f"[VARIANT-CHECK] Calculating ensemble metrics from {len(judge_results)} judges")
        
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
        
        # Collect only successful judge scores
        successful_judges = [j for j in judge_results.values() 
                           if j and not j.evaluation_failed]
        
        if len(successful_judges) < 2:
            # Not enough judges - mark run as failed
            logger.error(f"Insufficient successful judges ({len(successful_judges)}), marking run as failed")
            raise Exception("Less than 2 judges succeeded")
        else:
            logger.info(f"Calculating from {len(successful_judges)} successful judges")
        
        for dim in dimensions:
            scores = []
            for judge_type in ["primary", "secondary", "tertiary"]:
                if judge_type in judge_results and judge_results[judge_type]:
                    # Only include successful judges
                    if not judge_results[judge_type].evaluation_failed:
                        score_value = getattr(judge_results[judge_type].scores, dim, 0)
                        scores.append(score_value)
            
            if len(scores) >= 2:  # Need at least 2 scores for meaningful aggregation
                mean_scores[dim] = safe_float(np.mean(scores))
                # Use sample std (ddof=1) for small sample size (n=3 judges)
                std_scores[dim] = safe_float(np.std(scores, ddof=1))
                
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
        
        # Composite score aggregation - calculate from individual judge composite scores
        composite_scores = []
        for judge_type in ["primary", "secondary", "tertiary"]:
            if judge_type in judge_results and judge_results[judge_type]:
                # Only include successful judges
                if not judge_results[judge_type].evaluation_failed:
                    composite_score = getattr(judge_results[judge_type].scores, "composite", 0)
                    composite_scores.append(composite_score)
        
        if len(composite_scores) >= 2:
            mean_scores["composite"] = safe_float(np.mean(composite_scores))
            # Use sample std (ddof=1) for small sample size
            std_scores["composite"] = safe_float(np.std(composite_scores, ddof=1))
            
            # VERIFICATION: Log composite std calculation details
            logger.info(f"[STD-CHECK] Composite scores: {composite_scores}, std={std_scores['composite']:.3f}")
            
            # Sanity check: std should not exceed score range
            score_range = max(composite_scores) - min(composite_scores)
            if std_scores["composite"] > score_range:
                logger.warning(f"[STD-CHECK] Composite std ({std_scores['composite']:.3f}) exceeds range ({score_range:.3f})")
        else:
            # Fallback if insufficient scores
            mean_scores["composite"] = safe_float(composite_scores[0] if composite_scores else 0)
            std_scores["composite"] = 0.0
        
        ci_95["composite"] = (
            safe_float(mean_scores["composite"] - 1.96 * std_scores["composite"]),
            safe_float(mean_scores["composite"] + 1.96 * std_scores["composite"])
        )
        
        # VERIFICATION: Log aggregated scores
        logger.info(f"[VARIANT-CHECK] Ensemble aggregation complete: mean_composite={mean_scores['composite']:.3f}, std_composite={std_scores['composite']:.3f}, mean_tech_acc={mean_scores.get('technical_accuracy', 0):.3f}")
        
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
                    
                    # Include all valid scores in 0-5 range (zero is valid)
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
            "claude-3-5-haiku-20241022": 0.0001 * (tokens_used / 1000),  # $0.10 AUD per 1k tokens
            "gpt-4-turbo": 0.0003 * (tokens_used / 1000),                # $0.30 AUD per 1k tokens  
            "llama-3.3-70b-versatile": 0.00005 * (tokens_used / 1000),   # $0.05 AUD per 1k tokens
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
