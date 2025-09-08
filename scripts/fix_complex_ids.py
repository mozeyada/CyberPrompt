#!/usr/bin/env python3
"""
Fix complex run and experiment IDs to simple sequential format.

Usage:
    python scripts/fix_complex_ids.py --apply
"""

import argparse
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_complex_ids(apply_changes=False):
    """Fix complex IDs to simple sequential format."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    
    logger.info("Connected to MongoDB")
    
    # Get all runs
    runs = await db.runs.find({}).to_list(length=None)
    logger.info(f"Found {len(runs)} runs to fix")
    
    if not apply_changes:
        logger.info("DRY RUN: Use --apply to make actual changes")
        for i, run in enumerate(runs[:3], 1):
            logger.info(f"Would change run_id: {run.get('run_id')} -> run_{i:03d}")
            logger.info(f"Would change experiment_id: {run.get('experiment_id')} -> exp_001")
        client.close()
        return len(runs)
    
    # Group runs by experiment_id to assign same exp_id to same experiment
    experiment_mapping = {}
    exp_counter = 1
    
    for run in runs:
        old_exp_id = run.get('experiment_id')
        if old_exp_id not in experiment_mapping:
            experiment_mapping[old_exp_id] = f"exp_{exp_counter:03d}"
            exp_counter += 1
    
    # Update runs with simple IDs
    for i, run in enumerate(runs, 1):
        new_run_id = f"run_{i:03d}"
        new_exp_id = experiment_mapping[run.get('experiment_id')]
        
        await db.runs.update_one(
            {"_id": run["_id"]},
            {"$set": {
                "run_id": new_run_id,
                "experiment_id": new_exp_id
            }}
        )
        
        if i <= 5:
            logger.info(f"Updated run {i}: {run.get('run_id')} -> {new_run_id}")
            logger.info(f"  experiment: {run.get('experiment_id')} -> {new_exp_id}")
    
    logger.info(f"Successfully updated {len(runs)} runs with simple IDs")
    logger.info(f"Created {len(experiment_mapping)} unique experiments")
    
    client.close()
    return len(runs)


async def main():
    parser = argparse.ArgumentParser(description="Fix complex IDs")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    logger.info("Starting ID cleanup...")
    fixed_count = await fix_complex_ids(apply_changes=args.apply)
    
    if args.apply:
        logger.info(f"✅ Fixed {fixed_count} complex IDs")
    else:
        logger.info(f"📋 Would fix {fixed_count} complex IDs (use --apply to fix)")


if __name__ == "__main__":
    asyncio.run(main())