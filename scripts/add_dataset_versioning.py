#!/usr/bin/env python3
"""
Add dataset versioning to prompts and runs collections.

Usage:
    python scripts/add_dataset_versioning.py          # Dry run
    python scripts/add_dataset_versioning.py --apply  # Apply changes
"""

import argparse
import asyncio
import logging
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_dataset_versioning(apply_changes=False):
    """Add dataset versioning to prompts and runs."""
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    
    logger.info("Connected to MongoDB")
    
    # Current timestamp for versioning
    current_version = datetime.now().strftime("%Y%m%d")
    
    # 1. Update prompts collection
    prompts_without_version = await db.prompts.count_documents({
        "dataset_version": {"$exists": False}
    })
    
    logger.info(f"Found {prompts_without_version} prompts without dataset_version")
    
    if prompts_without_version > 0:
        if apply_changes:
            result = await db.prompts.update_many(
                {"dataset_version": {"$exists": False}},
                {"$set": {"dataset_version": current_version}}
            )
            logger.info(f"Updated {result.modified_count} prompts with dataset_version: {current_version}")
        else:
            logger.info(f"DRY RUN: Would add dataset_version: {current_version} to {prompts_without_version} prompts")
    
    # 2. Update runs collection
    runs_without_version = await db.runs.count_documents({
        "dataset_version": {"$exists": False}
    })
    
    logger.info(f"Found {runs_without_version} runs without dataset_version")
    
    if runs_without_version > 0:
        if apply_changes:
            result = await db.runs.update_many(
                {"dataset_version": {"$exists": False}},
                {"$set": {"dataset_version": current_version}}
            )
            logger.info(f"Updated {result.modified_count} runs with dataset_version: {current_version}")
        else:
            logger.info(f"DRY RUN: Would add dataset_version: {current_version} to {runs_without_version} runs")
    
    # 3. Add experiment_id to runs without it
    runs_without_experiment = await db.runs.count_documents({
        "experiment_id": {"$exists": False}
    })
    
    logger.info(f"Found {runs_without_experiment} runs without experiment_id")
    
    if runs_without_experiment > 0:
        if apply_changes:
            # Group runs by created_at date and assign experiment IDs
            cursor = db.runs.find(
                {"experiment_id": {"$exists": False}},
                {"run_id": 1, "created_at": 1}
            ).sort("created_at", 1)
            
            runs = await cursor.to_list(length=None)
            experiment_groups = {}
            
            for run in runs:
                # Group by date (same day = same experiment)
                date_key = run["created_at"].strftime("%Y%m%d")
                if date_key not in experiment_groups:
                    experiment_groups[date_key] = f"exp_{date_key}"
                
                await db.runs.update_one(
                    {"_id": run["_id"]},
                    {"$set": {"experiment_id": experiment_groups[date_key]}}
                )
            
            logger.info(f"Updated {len(runs)} runs with experiment_id grouping")
        else:
            logger.info(f"DRY RUN: Would add experiment_id to {runs_without_experiment} runs")
    
    client.close()
    return {
        "prompts_updated": prompts_without_version,
        "runs_updated": runs_without_version,
        "experiments_grouped": runs_without_experiment
    }


async def main():
    parser = argparse.ArgumentParser(description="Add dataset versioning and experiment grouping")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    logger.info("Starting dataset versioning migration...")
    stats = await add_dataset_versioning(apply_changes=args.apply)
    
    if args.apply:
        logger.info("✅ Dataset versioning migration completed!")
        logger.info(f"  Prompts updated: {stats['prompts_updated']}")
        logger.info(f"  Runs updated: {stats['runs_updated']}")
        logger.info(f"  Experiments grouped: {stats['experiments_grouped']}")
    else:
        logger.info("📋 Dataset versioning migration preview completed")


if __name__ == "__main__":
    asyncio.run(main())