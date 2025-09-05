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

        # Build filter query - support both research and curated data
        filter_query = {"$or": [{"source": "CySecBench"}, {"source": "curated"}]}

        if scenario:
            filter_query["scenario"] = scenario
        if length_bin:
            filter_query["metadata.length_bin"] = length_bin
        if category:
            filter_query["category"] = category
        if min_words or max_words:
            word_filter = {}
            if min_words:
                word_filter["$gte"] = min_words
            if max_words:
                word_filter["$lte"] = max_words
            filter_query["metadata.word_count"] = word_filter

        # Get total count
        total_count = await collection.count_documents(filter_query)

        # Build aggregation pipeline
        pipeline = [{"$match": filter_query}]

        # Add sampling if requested
        if sample_size and sample_size < total_count:
            pipeline.append({"$sample": {"size": sample_size}})

        # Add metadata aggregation
        pipeline.extend([
            {
                "$group": {
                    "_id": None,
                    "prompts": {"$push": "$$ROOT"},
                    "avg_word_count": {"$avg": "$metadata.word_count"},
                    "length_distribution": {
                        "$push": {
                            "length_bin": "$metadata.length_bin",
                            "word_count": "$metadata.word_count",
                        },
                    },
                },
            },
        ])

        # Execute aggregation
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)

        if not result:
            return {
                "prompts": [],
                "total_count": 0,
                "sample_size": 0,
                "research_metadata": {
                    "avg_word_count": 0,
                    "length_distribution": {},
                },
            }

        data = result[0]
        prompts = data.get("prompts", [])
        
        # Convert ObjectIds to strings
        from app.utils.mongodb import convert_objectid_list
        prompts = convert_objectid_list(prompts)

        # Calculate length distribution
        length_dist = {}
        for item in data.get("length_distribution", []):
            length_bin = item["length_bin"]
            length_dist[length_bin] = length_dist.get(length_bin, 0) + 1

        return {
            "prompts": prompts,
            "total_count": total_count,
            "sample_size": len(prompts),
            "research_metadata": {
                "avg_word_count": round(data.get("avg_word_count", 0), 2),
                "length_distribution": length_dist,
                "filter_applied": {
                    "scenario": scenario,
                    "length_bin": length_bin,
                    "category": category,
                    "word_range": f"{min_words or 'any'}-{max_words or 'any'}",
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
            {"$match": {"source": "CySecBench"}},
            {
                "$group": {
                    "_id": {
                        "scenario": "$scenario",
                        "length_bin": "$metadata.length_bin",
                    },
                    "count": {"$sum": 1},
                    "avg_word_count": {"$avg": "$metadata.word_count"},
                    "min_word_count": {"$min": "$metadata.word_count"},
                    "max_word_count": {"$max": "$metadata.word_count"},
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
                            "avg_words": "$avg_word_count",
                            "min_words": "$min_word_count",
                            "max_words": "$max_word_count",
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
                    "avg_words": round(bin_data["avg_words"], 2),
                    "word_range": f"{bin_data['min_words']}-{bin_data['max_words']}",
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
