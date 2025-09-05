import logging

from fastapi import APIRouter, Header, HTTPException

from app.core.security import validate_api_key_header
from app.db.connection import get_database
from app.models import LastRunItem, StatsOverview

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverview)
async def get_overview(
    x_api_key: str = Header(..., description="API key"),
) -> StatsOverview:
    """Get dashboard overview statistics"""
    validate_api_key_header(x_api_key)

    try:
        db = get_database()

        # Get counts
        total_runs = await db.runs.count_documents({})
        available_prompts = await db.prompts.count_documents({})

        # Get total cost (sum of all aud_cost where exists)
        cost_pipeline = [
            {"$match": {"economics.aud_cost": {"$exists": True}}},
            {"$group": {"_id": None, "total": {"$sum": "$economics.aud_cost"}}},
        ]
        cost_result = await db.runs.aggregate(cost_pipeline).to_list(length=1)
        total_cost_aud = cost_result[0]["total"] if cost_result else 0.0

        # Get average quality (average of scores.composite where exists)
        quality_pipeline = [
            {"$match": {"scores.composite": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": None, "avg": {"$avg": "$scores.composite"}}},
        ]
        quality_result = await db.runs.aggregate(quality_pipeline).to_list(length=1)
        avg_quality_overall = quality_result[0]["avg"] if quality_result else None

        # Get last 5 runs with prompt details
        last_runs_pipeline = [
            {"$lookup": {
                "from": "prompts",
                "localField": "prompt_id",
                "foreignField": "prompt_id",
                "as": "prompt",
            }},
            {"$unwind": "$prompt"},
            {"$sort": {"created_at": -1}},
            {"$limit": 5},
            {"$project": {
                "_id": 0,  # Exclude ObjectId
                "run_id": 1,
                "model_id": "$model",  # Use model field
                "scenario": "$prompt.scenario",
                "fsp_enabled": {"$ifNull": ["$bias_controls.fsp", False]},
                "overall": "$scores.composite",
                "aud_cost": {"$ifNull": ["$economics.aud_cost", 0.0]},
                "created_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S.%LZ", "date": "$created_at"}},
            }},
        ]
        last_runs_docs = await db.runs.aggregate(last_runs_pipeline).to_list(length=5)

        # Convert to proper format
        last_runs = []
        for doc in last_runs_docs:
            last_runs.append(LastRunItem(
                run_id=doc.get("run_id", ""),
                model_id=doc.get("model_id", ""),
                scenario=doc.get("scenario", ""),
                fsp_enabled=doc.get("fsp_enabled", False),
                overall=doc.get("overall"),
                aud_cost=doc.get("aud_cost", 0.0),
                created_at=doc.get("created_at", ""),
            ))

        return StatsOverview(
            total_runs=total_runs,
            available_prompts=available_prompts,
            total_cost_aud=total_cost_aud,
            avg_quality_overall=avg_quality_overall,
            last_runs=last_runs,
        )

    except Exception as e:
        logger.error(f"Error getting overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics-summary")
async def get_analytics_summary(
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Get analytics summary data for insights panels."""
    validate_api_key_header(x_api_key)

    try:
        db = get_database()

        # Complex aggregation for analytics insights
        pipeline = [
            {
                "$facet": {
                    # Best value model (highest quality/cost ratio)
                    "best_value": [
                        {"$match": {"scores.composite": {"$ne": None}, "economics.aud_cost": {"$gt": 0}}},
                        {
                            "$group": {
                                "_id": "$model",
                                "avg_quality": {"$avg": "$scores.composite"},
                                "avg_cost": {"$avg": "$economics.aud_cost"},
                                "total_runs": {"$sum": 1},
                            },
                        },
                        {
                            "$addFields": {
                                "quality_per_cost": {"$divide": ["$avg_quality", "$avg_cost"]},
                            },
                        },
                        {"$sort": {"quality_per_cost": -1}},
                        {"$limit": 1},
                    ],
                    # Highest quality model
                    "highest_quality": [
                        {"$match": {"scores.composite": {"$ne": None}}},
                        {
                            "$group": {
                                "_id": "$model",
                                "avg_quality": {"$avg": "$scores.composite"},
                                "total_runs": {"$sum": 1},
                            },
                        },
                        {"$sort": {"avg_quality": -1}},
                        {"$limit": 1},
                    ],
                    # Lowest cost model
                    "lowest_cost": [
                        {"$match": {"economics.aud_cost": {"$gt": 0}}},
                        {
                            "$group": {
                                "_id": "$model",
                                "avg_cost": {"$avg": "$economics.aud_cost"},
                                "total_runs": {"$sum": 1},
                            },
                        },
                        {"$sort": {"avg_cost": 1}},
                        {"$limit": 1},
                    ],
                    # Performance stats
                    "performance_stats": [
                        {
                            "$group": {
                                "_id": None,
                                "total_evaluations": {"$sum": 1},
                                "completed_runs": {
                                    "$sum": {"$cond": [{"$ne": ["$scores.composite", None]}, 1, 0]},
                                },
                                "avg_composite": {"$avg": "$scores.composite"},
                                "scenarios": {"$addToSet": "$scenario"},
                            },
                        },
                    ],
                },
            },
        ]

        results = await db.runs.aggregate(pipeline).to_list(1)
        result = results[0] if results else {}

        # Extract and format results
        best_value = result.get("best_value", [])
        highest_quality = result.get("highest_quality", [])
        lowest_cost = result.get("lowest_cost", [])
        performance_stats = result.get("performance_stats", [{}])[0]

        return {
            "best_value_model": best_value[0]["_id"] if best_value else "No data",
            "best_value_ratio": best_value[0]["quality_per_cost"] if best_value else 0,
            "highest_quality_model": highest_quality[0]["_id"] if highest_quality else "No data",
            "highest_quality_score": highest_quality[0]["avg_quality"] if highest_quality else None,
            "lowest_cost_model": lowest_cost[0]["_id"] if lowest_cost else "No data",
            "lowest_cost_amount": lowest_cost[0]["avg_cost"] if lowest_cost else 0,
            "total_evaluations": performance_stats.get("total_evaluations", 0),
            "completed_runs": performance_stats.get("completed_runs", 0),
            "avg_composite_score": performance_stats.get("avg_composite", None),
            "scenarios_covered": len(performance_stats.get("scenarios", [])),
            "unique_scenarios": performance_stats.get("scenarios", []),
        }

    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
