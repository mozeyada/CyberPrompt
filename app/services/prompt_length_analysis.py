"""Research module for RQ1: Prompt length vs quality/cost analysis"""

import logging
from typing import Any

from scipy import stats

from app.db.repositories import PromptRepository, RunRepository
from app.models import ScenarioType

logger = logging.getLogger(__name__)

class PromptLengthResearcher:
    """Research module for analyzing prompt length effects on quality and cost"""

    def __init__(self):
        self._prompt_repo = None
        self._run_repo = None

    @property
    def prompt_repo(self):
        if self._prompt_repo is None:
            self._prompt_repo = PromptRepository()
        return self._prompt_repo

    @property
    def run_repo(self):
        if self._run_repo is None:
            self._run_repo = RunRepository()
        return self._run_repo

    async def analyze_length_effects(self, scenario: ScenarioType = None,
                                   models: list[str] | None = None) -> dict[str, Any]:
        """Analyze the effects of prompt length on quality and cost (RQ1)"""

        try:
            # Build query filters
            filters = {"status": "succeeded"}
            if scenario:
                pass  # Will be handled in aggregation
            if models:
                filters["model"] = {"$in": models}

            # Aggregation pipeline for length analysis
            pipeline = [
                {"$lookup": {
                    "from": "prompts",
                    "localField": "prompt_id",
                    "foreignField": "prompt_id",
                    "as": "prompt",
                }},
                {"$unwind": "$prompt"},
                {"$match": filters},
            ]

            if scenario:
                pipeline.append({"$match": {"prompt.scenario": scenario.value}})

            # Group by length bin and model
            pipeline.extend([
                {"$group": {
                    "_id": {
                        "length_bin": "$prompt.length_bin",
                        "model": "$model",
                    },
                    "avg_composite_score": {"$avg": "$scores.composite"},
                    "avg_cost_per_1k": {"$avg": {
                        "$divide": [
                            {"$multiply": ["$economics.aud_cost", 1000]},
                            "$tokens.total",
                        ],
                    }},
                    "avg_tokens": {"$avg": "$tokens.total"},
                    "count": {"$sum": 1},
                    "scores": {"$push": "$scores.composite"},
                    "costs": {"$push": "$economics.aud_cost"},
                }},
                {"$match": {"count": {"$gte": 3}}},  # Minimum for statistical significance
            ])

            # Execute aggregation (using db connection)
            from app.db.connection import get_database
            db = get_database()
            cursor = db.runs.aggregate(pipeline)
            results = await cursor.to_list(length=None)

            # Statistical analysis
            length_order = {"XS": 1, "S": 2, "M": 3, "L": 4, "XL": 5}
            model_analysis = {}

            # Group by model for regression analysis
            for result in results:
                model = result["_id"]["model"]
                length_bin = result["_id"]["length_bin"]

                if model not in model_analysis:
                    model_analysis[model] = []

                model_analysis[model].append({
                    "length_numeric": length_order.get(length_bin, 3),
                    "length_bin": length_bin,
                    "quality": result["avg_composite_score"],
                    "cost_per_1k": result["avg_cost_per_1k"],
                    "tokens": result["avg_tokens"],
                    "count": result["count"],
                })

            # Perform regression analysis for each model
            regression_results = {}
            for model, data_points in model_analysis.items():
                if len(data_points) >= 3:
                    x_vals = [dp["length_numeric"] for dp in data_points]
                    y_quality = [dp["quality"] for dp in data_points]
                    y_cost = [dp["cost_per_1k"] for dp in data_points]

                    # Quality vs Length regression
                    quality_slope, quality_intercept, quality_r, quality_p, quality_se = stats.linregress(x_vals, y_quality)

                    # Cost vs Length regression
                    cost_slope, cost_intercept, cost_r, cost_p, cost_se = stats.linregress(x_vals, y_cost)

                    regression_results[model] = {
                        "quality_regression": {
                            "slope": round(quality_slope, 4),
                            "intercept": round(quality_intercept, 4),
                            "r_squared": round(quality_r ** 2, 4),
                            "p_value": round(quality_p, 6),
                            "significance": "significant" if quality_p < 0.05 else "not_significant",
                        },
                        "cost_regression": {
                            "slope": round(cost_slope, 6),
                            "intercept": round(cost_intercept, 6),
                            "r_squared": round(cost_r ** 2, 4),
                            "p_value": round(cost_p, 6),
                            "significance": "significant" if cost_p < 0.05 else "not_significant",
                        },
                        "data_points": data_points,
                    }

            return {
                "scenario": scenario.value if scenario else "all",
                "models_analyzed": list(regression_results.keys()),
                "regression_analysis": regression_results,
                "raw_data": results,
                "research_insights": self._generate_rq1_insights(regression_results),
            }

        except Exception as e:
            logger.error(f"Error in prompt length analysis: {e}")
            return {"error": str(e)}

    def _generate_rq1_insights(self, regression_results: dict[str, Any]) -> dict[str, Any]:
        """Generate research insights for RQ1"""

        insights = {
            "quality_length_relationship": {},
            "cost_length_relationship": {},
            "efficiency_analysis": {},
            "recommendations": [],
        }

        for model, results in regression_results.items():
            quality_reg = results["quality_regression"]
            cost_reg = results["cost_regression"]

            # Quality-length relationship
            if quality_reg["significance"] == "significant":
                if quality_reg["slope"] > 0:
                    insights["quality_length_relationship"][model] = "positive_correlation"
                    insights["recommendations"].append(f"{model}: Longer prompts improve quality (slope: {quality_reg['slope']})")
                else:
                    insights["quality_length_relationship"][model] = "negative_correlation"
                    insights["recommendations"].append(f"{model}: Shorter prompts maintain quality (slope: {quality_reg['slope']})")
            else:
                insights["quality_length_relationship"][model] = "no_significant_relationship"

            # Cost-length relationship
            if cost_reg["significance"] == "significant":
                insights["cost_length_relationship"][model] = {
                    "cost_increase_per_length_unit": cost_reg["slope"],
                    "relationship": "linear" if cost_reg["r_squared"] > 0.7 else "weak",
                }

        return insights

# Global research instance - will be initialized lazily
prompt_length_researcher = None

def get_prompt_length_researcher():
    global prompt_length_researcher
    if prompt_length_researcher is None:
        prompt_length_researcher = PromptLengthResearcher()
    return prompt_length_researcher
