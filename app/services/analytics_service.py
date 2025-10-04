import logging
from typing import Any
import numpy as np

from motor.motor_asyncio import AsyncIOMotorDatabase
from scipy import stats

from app.db.connection import get_database
from app.models import JudgeType, LengthBin, ScenarioType

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating analytics and insights"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def cost_quality_analysis(
        self,
        scenario: ScenarioType | None = None,
        models: list[str] | None = None,
        length_bins: list[LengthBin] | None = None,
        judge_type: JudgeType | None = None,
    ) -> list[dict[str, Any]]:
        """Generate cost vs quality frontier analysis"""
        try:
            # Use exact working pipeline from cost-quality-scatter
            pipeline = [
                {
                    "$match": {
                        "status": "succeeded",
                        "economics.aud_cost": {"$exists": True, "$gt": 0},
                        "scores.composite": {"$exists": True},
                    },
                },
                {
                    "$project": {
                        "run_id": 1,
                        "model": 1,
                        "aud_cost": "$economics.aud_cost",
                        "composite_score": "$scores.composite",
                        "prompt_length_bin": 1,
                    },
                },
            ]

            cursor = self.db.runs.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            # Group by model and calculate averages
            model_data = {}
            for result in results:
                model = result["model"]
                if model not in model_data:
                    model_data[model] = {"costs": [], "scores": [], "length_bins": []}
                model_data[model]["costs"].append(result["aud_cost"])
                model_data[model]["scores"].append(result["composite_score"])
                model_data[model]["length_bins"].append(result.get("prompt_length_bin", "unknown"))
            
            # Calculate averages with zero-division protection
            formatted_results = []
            for model, data in model_data.items():
                avg_cost = sum(data["costs"]) / len(data["costs"]) if data["costs"] else 0
                avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
                formatted_results.append({
                    "model": model,
                    "length_bin": "all",
                    "scenario": "all",
                    "x": round(avg_cost, 6),
                    "y": round(avg_score, 3),
                    "count": len(data["costs"]),
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Error in cost-quality analysis: {e}")
            return []

    async def length_bias_analysis(
        self,
        scenario: ScenarioType | None = None,
        models: list[str] | None = None,
        dimension: str = "composite",
    ) -> dict[str, Any]:
        """Analyze length bias across different dimensions"""
        try:
            # Build pipeline
            match_stage = {
                "status": "succeeded",
                f"scores.{dimension}": {"$exists": True},
            }

            pipeline = [
                {"$lookup": {
                    "from": "prompts",
                    "localField": "prompt_id",
                    "foreignField": "prompt_id",
                    "as": "prompt",
                }},
                {"$unwind": "$prompt"},
                {"$match": match_stage},
            ]

            if scenario:
                pipeline.append({"$match": {"prompt.scenario": scenario.value}})

            if models:
                pipeline.append({"$match": {"model": {"$in": models}}})

            # Group by model and length_bin
            pipeline.extend([
                {"$group": {
                    "_id": {
                        "model": "$model",
                        "length_bin": "$prompt.length_bin",
                    },
                    "avg_score": {"$avg": f"$scores.{dimension}"},
                    "count": {"$sum": 1},
                    "scores": {"$push": f"$scores.{dimension}"},
                }},
            ])

            cursor = self.db.runs.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            # Calculate slopes for each model
            length_bin_order = {"XS": 1, "S": 2, "M": 3, "L": 4, "XL": 5}

            # Group by model
            model_data = {}
            for result in results:
                model = result["_id"]["model"]
                length_bin = result["_id"]["length_bin"]

                if model not in model_data:
                    model_data[model] = {}

                model_data[model][length_bin] = {
                    "avg_score": result["avg_score"],
                    "count": result["count"],
                    "scores": result["scores"],
                }

            # Calculate slopes
            slopes_data = []
            for model, bins in model_data.items():
                if len(bins) >= 3:  # Need at least 3 points for meaningful slope
                    sorted_bins = sorted(bins.items())
                    x_vals = [length_bin_order[bin_name] for bin_name, _ in sorted_bins]
                    y_vals = [bin_data["avg_score"] for _, bin_data in sorted_bins]

                    # Linear regression
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)

                    # Confidence interval for slope
                    n = len(x_vals)
                    t_val = stats.t.ppf(0.975, n - 2)  # 95% CI
                    slope_ci = t_val * std_err

                    slopes_data.append({
                        "model": model,
                        "slope": round(slope, 4),
                        "intercept": round(intercept, 4),
                        "r_squared": round(r_value ** 2, 4),
                        "p_value": round(p_value, 6),
                        "slope_ci_lower": round(slope - slope_ci, 4),
                        "slope_ci_upper": round(slope + slope_ci, 4),
                        "bins": bins,
                    })

            return {
                "dimension": dimension,
                "scenario": scenario.value if scenario else "all",
                "slopes": slopes_data,
                "bin_data": results,
            }

        except Exception as e:
            logger.error(f"Error in length bias analysis: {e}")
            return {"error": str(e)}

    async def risk_curves_analysis(
        self,
        scenario: ScenarioType | None = None,
        models: list[str] | None = None,
    ) -> dict[str, Any]:
        """Analyze risk metrics vs length bins"""
        try:
            match_stage = {
                "status": "succeeded",
                "scores.risk_awareness": {"$exists": True},
                "risk_metrics.hallucination_flags": {"$exists": True},
            }

            pipeline = [
                {"$lookup": {
                    "from": "prompts",
                    "localField": "prompt_id",
                    "foreignField": "prompt_id",
                    "as": "prompt",
                }},
                {"$unwind": "$prompt"},
                {"$match": match_stage},
            ]

            if scenario:
                pipeline.append({"$match": {"prompt.scenario": scenario.value}})

            if models:
                pipeline.append({"$match": {"model": {"$in": models}}})

            # Group by model and length_bin
            pipeline.extend([
                {"$group": {
                    "_id": {
                        "model": "$model",
                        "length_bin": "$prompt.length_bin",
                    },
                    "avg_risk_awareness": {"$avg": "$scores.risk_awareness"},
                    "avg_hallucination_rate": {"$avg": {
                        "$divide": ["$risk_metrics.hallucination_flags", {"$ifNull": ["$tokens.output", 1]}],
                    }},
                    "count": {"$sum": 1},
                }},
            ])

            cursor = self.db.runs.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            # Format for charts
            risk_curves = {}
            for result in results:
                model = result["_id"]["model"]
                if model not in risk_curves:
                    risk_curves[model] = {
                        "risk_awareness": [],
                        "hallucination_rate": [],
                    }

                risk_curves[model]["risk_awareness"].append({
                    "length_bin": result["_id"]["length_bin"],
                    "value": round(result["avg_risk_awareness"], 3),
                })

                risk_curves[model]["hallucination_rate"].append({
                    "length_bin": result["_id"]["length_bin"],
                    "value": round(result["avg_hallucination_rate"], 6),
                })

            return {
                "scenario": scenario.value if scenario else "all",
                "risk_curves": risk_curves,
                "raw_data": results,
            }

        except Exception as e:
            logger.error(f"Error in risk curves analysis: {e}")
            return {"error": str(e)}

    async def adaptive_relevance_analysis(
        self,
        scenario: ScenarioType | None = None,
        models: list[str] | None = None,
    ) -> dict[str, Any]:
        """Calculate adaptive relevance (slope of relevance vs length)"""
        try:
            relevance_bias = await self.length_bias_analysis(scenario, models, "relevance")

            if "error" in relevance_bias:
                return relevance_bias

            # Extract relevance slopes
            adaptive_scores = []
            for slope_data in relevance_bias["slopes"]:
                adaptive_scores.append({
                    "model": slope_data["model"],
                    "adaptive_relevance": slope_data["slope"],
                    "significance": "significant" if slope_data["p_value"] < 0.05 else "not_significant",
                    "bins": [
                        {"length_bin": bin_name, "relevance_mean": round(bin_data["avg_score"], 3)}
                        for bin_name, bin_data in slope_data["bins"].items()
                    ],
                })

            return {
                "scenario": scenario.value if scenario else "all",
                "adaptive_relevance_scores": adaptive_scores,
                "note": "Derived metric: slope of relevance vs length_bin",
            }

        except Exception as e:
            logger.error(f"Error in adaptive relevance analysis: {e}")
            return {"error": str(e)}

    async def best_quality_per_aud(
        self,
        scenario: ScenarioType | None = None,
        length_bins: list[LengthBin] | None = None,
    ) -> list[dict[str, Any]]:
        """Generate best quality per AUD leaderboard"""
        try:
            cost_quality_data = await self.cost_quality_analysis(scenario, None, length_bins)

            if not cost_quality_data:
                return []

            # Calculate quality per AUD ratio and format for leaderboard
            leaderboard = []
            for entry in cost_quality_data:
                if entry["x"] > 0:  # Avoid division by zero
                    quality_per_aud = round(entry["y"] / entry["x"], 4)
                else:
                    quality_per_aud = 0

                leaderboard.append({
                    "model_id": entry["model"],
                    "avg_quality": entry["y"],
                    "avg_cost": entry["x"],
                    "quality_per_aud": quality_per_aud,
                    "count": entry["count"],
                    "length_bin": entry["length_bin"],
                    "scenario": entry["scenario"],
                })

            # Sort by quality per AUD ratio
            leaderboard.sort(key=lambda x: x["quality_per_aud"], reverse=True)

            return leaderboard[:20]  # Top 20

        except Exception as e:
            logger.error(f"Error in best quality per AUD analysis: {e}")
            return []

    async def get_prompt_coverage(self) -> dict[str, Any]:
        """Count total prompts used by source and scenario"""
        try:
            # Pipeline to join runs with prompts and count coverage
            pipeline = [
                {"$lookup": {
                    "from": "prompts",
                    "localField": "prompt_id",
                    "foreignField": "prompt_id",
                    "as": "prompt"
                }},
                {"$unwind": "$prompt"},
                {"$group": {
                    "_id": {
                        "source": "$source",
                        "scenario": "$prompt.scenario"
                    },
                    "unique_prompts": {"$addToSet": "$prompt.text"},
                    "total_runs": {"$sum": 1}
                }},
                {"$project": {
                    "source": "$_id.source",
                    "scenario": "$_id.scenario",
                    "unique_prompt_count": {"$size": "$unique_prompts"},
                    "total_runs": 1,
                    "_id": 0
                }}
            ]
            
            cursor = self.db.runs.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {
                "coverage": results,
                "summary": {
                    "total_unique_prompts": sum(r["unique_prompt_count"] for r in results),
                    "total_runs": sum(r["total_runs"] for r in results)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in prompt coverage analysis: {e}")
            return {"error": str(e)}

    async def get_ensemble_analytics(
        self,
        scenario: ScenarioType | None = None,
        length_bin: LengthBin | None = None,
        experiment_id: str | None = None
    ) -> dict[str, Any]:
        """Get ensemble evaluation analytics"""
        
        try:
            # Build aggregation pipeline for ensemble evaluations
            match_stage = {"ensemble_evaluation": {"$exists": True}}
            if scenario:
                match_stage["scenario"] = scenario
            if length_bin:
                match_stage["prompt_length_bin"] = length_bin
            if experiment_id:
                match_stage["experiment_id"] = experiment_id
                
            pipeline = [
                {"$match": match_stage},
                {"$project": {
                    "run_id": 1,
                    "scenario": 1,
                    "prompt_length_bin": 1,
                    "ensemble_mean": "$ensemble_evaluation.aggregated.mean_scores",
                    "reliability": "$ensemble_evaluation.reliability_metrics",
                    "individual_judges": {
                        "primary": "$ensemble_evaluation.primary_judge.scores",
                        "secondary": "$ensemble_evaluation.secondary_judge.scores", 
                        "tertiary": "$ensemble_evaluation.tertiary_judge.scores"
                    }
                }}
            ]
            
            cursor = self.db.runs.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            if not results:
                return {"message": "No ensemble evaluations found", "total_ensemble_evaluations": 0}
            
            # Calculate overall reliability metrics
            avg_correlations = []
            agreement_levels = []
            
            for result in results:
                if result.get("reliability", {}).get("pearson_correlations"):
                    correlations = list(result["reliability"]["pearson_correlations"].values())
                    mean_corr = np.mean(correlations)
                    # Handle NaN and inf values
                    if np.isfinite(mean_corr):
                        avg_correlations.append(float(mean_corr))
                agreement_levels.append(result.get("reliability", {}).get("inter_judge_agreement", "unknown"))
            
            # Judge comparison analysis
            judge_performance = {}
            dimensions = ["technical_accuracy", "actionability", "completeness", 
                         "compliance_alignment", "risk_awareness", "relevance", "clarity", "composite"]
            
            for dimension in dimensions:
                primary_scores = []
                secondary_scores = []
                tertiary_scores = []
                
                for result in results:
                    judges = result.get("individual_judges", {})
                    if judges.get("primary", {}).get(dimension) is not None:
                        primary_scores.append(judges["primary"][dimension])
                    if judges.get("secondary", {}).get(dimension) is not None:
                        secondary_scores.append(judges["secondary"][dimension])
                    if judges.get("tertiary", {}).get(dimension) is not None:
                        tertiary_scores.append(judges["tertiary"][dimension])
                
                if primary_scores or secondary_scores or tertiary_scores:
                    # Helper function to safely convert numpy values
                    def safe_float(value, default=0.0):
                        if np.isfinite(value):
                            return float(value)
                        return default
                    
                    judge_performance[dimension] = {
                        "primary_avg": safe_float(np.mean(primary_scores)) if primary_scores else 0.0,
                        "primary_std": safe_float(np.std(primary_scores)) if len(primary_scores) > 1 else 0.0,
                        "secondary_avg": safe_float(np.mean(secondary_scores)) if secondary_scores else 0.0,
                        "secondary_std": safe_float(np.std(secondary_scores)) if len(secondary_scores) > 1 else 0.0,
                        "tertiary_avg": safe_float(np.mean(tertiary_scores)) if tertiary_scores else 0.0,
                        "tertiary_std": safe_float(np.std(tertiary_scores)) if len(tertiary_scores) > 1 else 0.0
                    }
            
            # Agreement level distribution
            from collections import Counter
            agreement_distribution = Counter(agreement_levels)
            
            return {
                "total_ensemble_evaluations": len(results),
                "overall_reliability": {
                    "average_correlation": float(np.mean(avg_correlations)) if avg_correlations else 0.0,
                    "agreement_distribution": dict(agreement_distribution)
                },
                "judge_performance_by_dimension": judge_performance,
                "scenario": scenario.value if scenario else None,
                "length_bin": length_bin.value if length_bin else None,
                "experiment_id": experiment_id
            }
            
        except Exception as e:
            logger.error(f"Error in ensemble analytics: {e}")
            return {"error": str(e)}

    async def get_inter_judge_correlation(
        self,
        scenario: ScenarioType | None = None,
        min_evaluations: int = 10
    ) -> dict[str, Any]:
        """Detailed correlation analysis between judges"""
        
        try:
            match_stage = {
                "ensemble_evaluation": {"$exists": True},
                "ensemble_evaluation.aggregated.mean_scores.composite": {"$exists": True}
            }
            if scenario:
                match_stage["scenario"] = scenario
                
            pipeline = [
                {"$match": match_stage},
                {"$project": {
                    "scenario": 1,
                    "prompt_length_bin": 1,
                    "correlations": "$ensemble_evaluation.reliability_metrics.pearson_correlations"
                }}
            ]
            
            cursor = self.db.runs.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            if len(results) < min_evaluations:
                return {
                    "error": f"Insufficient data ({len(results)} evaluations, need {min_evaluations}+)",
                    "total_evaluations": len(results)
                }
            
            # Aggregate correlations across evaluations
            correlation_pairs = {}
            
            for result in results:
                correlations = result.get("correlations", {})
                for pair, correlation in correlations.items():
                    if pair not in correlation_pairs:
                        correlation_pairs[pair] = []
                    correlation_pairs[pair].append(correlation)
            
            # Calculate statistics
            correlation_stats = {}
            for pair, correlations in correlation_pairs.items():
                correlation_stats[pair] = {
                    "mean": round(np.mean(correlations), 4),
                    "std": round(np.std(correlations), 4),
                    "min": round(np.min(correlations), 4),
                    "max": round(np.max(correlations), 4),
                    "count": len(correlations)
                }
            
            return {
                "total_evaluations": len(results),
                "correlation_statistics": correlation_stats,
                "overall_mean_correlation": round(np.mean([
                    stats["mean"] for stats in correlation_stats.values()
                ]), 4)
            }
            
        except Exception as e:
            logger.error(f"Error in inter-judge correlation analysis: {e}")
            return {"error": str(e)}



