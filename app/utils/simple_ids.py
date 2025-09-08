"""Simple ID generators for runs and experiments."""

import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os


async def get_next_run_id() -> str:
    """Get next sequential run ID like run_001, run_002, etc."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    
    # Get the highest run number
    pipeline = [
        {"$match": {"run_id": {"$regex": "^run_"}}},
        {"$addFields": {
            "run_num": {"$toInt": {"$substr": ["$run_id", 4, -1]}}
        }},
        {"$sort": {"run_num": -1}},
        {"$limit": 1}
    ]
    
    result = await db.runs.aggregate(pipeline).to_list(1)
    next_num = (result[0]["run_num"] + 1) if result else 1
    
    client.close()
    return f"run_{next_num:03d}"


async def get_next_experiment_id() -> str:
    """Get next sequential experiment ID like exp_001, exp_002, etc."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    
    # Get unique experiment IDs and find the highest number
    pipeline = [
        {"$match": {"experiment_id": {"$regex": "^exp_"}}},
        {"$group": {"_id": "$experiment_id"}},
        {"$addFields": {
            "exp_num": {"$toInt": {"$substr": ["$_id", 4, -1]}}
        }},
        {"$sort": {"exp_num": -1}},
        {"$limit": 1}
    ]
    
    result = await db.runs.aggregate(pipeline).to_list(1)
    next_num = (result[0]["exp_num"] + 1) if result else 1
    
    client.close()
    return f"exp_{next_num:03d}"


def generate_simple_run_id() -> str:
    """Synchronous wrapper - use only when async is not available."""
    return asyncio.run(get_next_run_id())


def generate_simple_experiment_id() -> str:
    """Synchronous wrapper - use only when async is not available."""
    return asyncio.run(get_next_experiment_id())