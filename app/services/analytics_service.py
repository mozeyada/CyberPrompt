import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from scipy import stats

from app.db.connection import get_database
from app.models import JudgeType, LengthBin, ScenarioType

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating analytics and insights"""

    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db or get_database()

    async def cost_quality_analysis(
        self,
        scenario: ScenarioType | None = None,
        models: list[str] | None = None,
        length_bins: list[LengthBin] | None = None,
        judge_type: JudgeType | None = None,
    ) -> list[dict[str, Any]]:
        """Generate cost vs quality frontier analysis"""
        try:
            # Build aggregation pipeline
            match_stage = {
                "status": "succeeded",
                "economics.aud_cost": {"$exists": True, "$gt": 0},
                "scores.composite": {"$exists": True},
            }

            if scenario:
                # Join with prompts to get scenario
                pipeline = [
                    {"$lookup": {
                        "from": "prompts",
                        "localField": "prompt_id",
                        "foreignField": "prompt_id",
                        "as": "prompt",
                    }},
                    {"$unwind": "$prompt"},
                    {"$match": {**match_stage, "prompt.scenario": scenario.value}},
                ]
            else:
                pipeline = [{"$match": match_stage}]

            if models:
                pipeline.append({"$match": {"model": {"$in": models}}})

            if length_bins:
                if not scenario:  # Add lookup if not already done
                    pipeline.extend([
                        {"$lookup": {
                            "from": "prompts",
                            "localField": "prompt_id",
                            "foreignField": "prompt_id",
                            "as": "prompt",
                        }},
                        {"$unwind": "$prompt"},
                    ])
                pipeline.append({"$match": {"prompt.length_bin": {"$in": [lb.value for lb in length_bins]}}})

            if judge_type:
                pipeline.append({"$match": {"judge.type": judge_type.value}})

            # Group and calculate metrics
            pipeline.extend([
                {"$group": {
                    "_id": {
                        "model": "$model",
                        "length_bin": "$prompt.length_bin" if scenario or length_bins else None,
                        "scenario": "$prompt.scenario" if not scenario else scenario.value,
                    },
                    "avg_cost_per_1k": {"$avg": {
                        "$divide": [
                            {"$multiply": ["$economics.aud_cost", 1000]},
                            "$tokens.total",
                        ],
                    }},
                    "avg_composite": {"$avg": "$scores.composite"},
                    "count": {"$sum": 1},
                    "cost_std": {"$stdDevPop": "$economics.aud_cost"},
                    "composite_std": {"$stdDevPop": "$scores.composite"},
                }},
                {"$match": {"count": {"$gte": 3}}},  # Minimum runs for statistical significance
            ])

            cursor = self.db.runs.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "model": result["_id"]["model"],
                    "length_bin": result["_id"]["length_bin"],
                    "scenario": result["_id"]["scenario"],
                    "x": round(result["avg_cost_per_1k"], 6),  # AUD per 1k tokens
                    "y": round(result["avg_composite"], 3),    # Composite score
                    "count": result["count"],
                    "cost_std": result.get("cost_std", 0),
                    "composite_std": result.get("composite_std", 0),
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
                {"$match": {"count": {"$gte": 3}}},
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
                    x_vals = [length_bin_order[bin_name] for bin_name in bins]
                    y_vals = [bin_data["avg_score"] for bin_data in bins.values()]

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
                        "$divide": ["$risk_metrics.hallucination_flags", {"$max": [1, "$tokens.output"]}],
                    }},
                    "count": {"$sum": 1},
                }},
                {"$match": {"count": {"$gte": 3}}},
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


# Global service instance
analytics_service = AnalyticsService()
