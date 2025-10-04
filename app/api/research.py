import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query

from app.core.security import validate_api_key_header

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research", tags=["research"])

@router.get("/prompts/filter")
async def filter_research_prompts(
    scenario: str | None = Query(None, description="Research scenario: SOC_INCIDENT, CTI_SUMMARY, GRC_MAPPING"),
    length_bin: str | None = Query(None, description="Length bin: short, medium, long"),
    category: str | None = Query(None, description="Original CySecBench category"),
    min_words: int | None = Query(None, ge=1, description="Minimum word count for RQ1 analysis"),
    max_words: int | None = Query(None, ge=1, description="Maximum word count for RQ1 analysis"),
    sample_size: int | None = Query(None, ge=1, le=200, description="Random sample size for experiments"),
    x_api_key: str = Header(..., description="API key"),
) -> dict[str, Any]:
    """Research-focused prompt filtering for academic analysis"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.connection import get_database
        db = get_database()
        collection = db.prompts

        # Build filter query - include all prompts
        filter_query = {}

        if scenario:
            filter_query["scenario"] = scenario
        if length_bin:
            filter_query["length_bin"] = length_bin
        if category:
            filter_query["category"] = category
        if min_words or max_words:
            word_filter = {}
            if min_words:
                word_filter["$gte"] = min_words
            if max_words:
                word_filter["$lte"] = max_words
            filter_query["token_count"] = word_filter

        # Get total count
        total_count = await collection.count_documents(filter_query)

        # Simple approach - get prompts directly
        cursor = collection.find(filter_query)
        prompts = await cursor.to_list(length=sample_size if sample_size else None)
        
        # Convert ObjectIds to strings (with error handling)
        try:
            from app.utils.mongodb import convert_objectid_list
            prompts = convert_objectid_list(prompts)
        except Exception as e:
            logger.warning(f"Error converting ObjectIds: {e}")
            # If conversion fails, just use the prompts as-is

        # Calculate metadata
        if prompts:
            avg_token_count = sum(p.get("token_count", 0) for p in prompts) / len(prompts)
            length_dist = {}
            for prompt in prompts:
                length_bin = prompt.get("length_bin", "unknown")
                length_dist[length_bin] = length_dist.get(length_bin, 0) + 1
        else:
            avg_token_count = 0
            length_dist = {}

        return {
            "prompts": prompts,
            "total_count": total_count,
            "sample_size": len(prompts),
            "research_metadata": {
                "avg_token_count": round(avg_token_count, 2),
                "length_distribution": length_dist,
                "filter_applied": {
                    "scenario": scenario,
                    "length_bin": length_bin,
                    "category": category,
                    "token_range": f"{min_words or 'any'}-{max_words or 'any'}",
                },
            },
        }

    except Exception as e:
        logger.error(f"Error filtering research prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios/stats")
async def get_scenario_statistics(
    x_api_key: str = Header(..., description="API key"),
) -> dict[str, Any]:
    """Get research dataset statistics by scenario for RQ analysis"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.connection import get_database
        db = get_database()
        collection = db.prompts

        # Aggregation pipeline for scenario statistics
        pipeline = [
            {"$match": {}},  # Include all prompts
            {
                "$group": {
                    "_id": {
                        "scenario": "$scenario",
                        "length_bin": "$length_bin",
                    },
                    "count": {"$sum": 1},
                    "avg_token_count": {"$avg": "$token_count"},
                    "min_token_count": {"$min": "$token_count"},
                    "max_token_count": {"$max": "$token_count"},
                },
            },
            {
                "$group": {
                    "_id": "$_id.scenario",
                    "total_prompts": {"$sum": "$count"},
                    "length_bins": {
                        "$push": {
                            "length_bin": "$_id.length_bin",
                            "count": "$count",
                            "avg_tokens": "$avg_token_count",
                            "min_tokens": "$min_token_count",
                            "max_tokens": "$max_token_count",
                        },
                    },
                },
            },
        ]

        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        # Format results for research analysis
        scenario_stats = {}
        total_dataset_size = 0

        for result in results:
            scenario = result["_id"]
            total_prompts = result["total_prompts"]
            total_dataset_size += total_prompts

            # Organize length bin data
            length_data = {}
            for bin_data in result["length_bins"]:
                length_data[bin_data["length_bin"]] = {
                    "count": bin_data["count"],
                    "avg_tokens": round(bin_data["avg_tokens"], 2),
                    "token_range": f"{bin_data['min_tokens']}-{bin_data['max_tokens']}",
                }

            scenario_stats[scenario] = {
                "total_prompts": total_prompts,
                "length_bins": length_data,
            }

        return {
            "research_dataset": {
                "total_prompts": total_dataset_size,
                "scenarios": scenario_stats,
            },
            "research_notes": {
                "RQ1_analysis": "Use length_bins for prompt length vs performance correlation",
                "RQ2_analysis": "Compare scenarios for adaptive vs static benchmarking",
                "sample_recommendations": {
                    "small_experiment": "50 prompts per scenario (150 total)",
                    "full_experiment": "All available prompts per scenario",
                },
            },
        }

    except Exception as e:
        logger.error(f"Error getting scenario statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
