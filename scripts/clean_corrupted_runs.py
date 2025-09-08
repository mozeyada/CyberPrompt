#!/usr/bin/env python3
"""
Clean up corrupted, failed, and incomplete runs.

Usage:
    python scripts/clean_corrupted_runs.py --apply
"""

import argparse
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def clean_corrupted_runs(apply_changes=False):
    """Remove corrupted, failed, and incomplete runs."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    runs_collection = db.runs
    
    logger.info("Connected to MongoDB")
    
    # Count different types of problematic runs
    failed_count = await runs_collection.count_documents({"status": "failed"})
    queued_count = await runs_collection.count_documents({"status": "queued"})
    succeeded_no_scores = await runs_collection.count_documents({
        "status": "succeeded", 
        "scores.composite": {"$exists": False}
    })
    
    total_to_remove = failed_count + queued_count + succeeded_no_scores
    
    logger.info(f"Found problematic runs:")
    logger.info(f"  - Failed runs: {failed_count}")
    logger.info(f"  - Queued (stuck) runs: {queued_count}")
    logger.info(f"  - Succeeded but no scores: {succeeded_no_scores}")
    logger.info(f"  - Total to remove: {total_to_remove}")
    
    if total_to_remove == 0:
        logger.info("No corrupted runs found!")
        client.close()
        return 0
    
    if not apply_changes:
        logger.info("DRY RUN: Use --apply to make actual changes")
        client.close()
        return total_to_remove
    
    # Remove problematic runs
    result1 = await runs_collection.delete_many({"status": "failed"})
    result2 = await runs_collection.delete_many({"status": "queued"})
    result3 = await runs_collection.delete_many({
        "status": "succeeded", 
        "scores.composite": {"$exists": False}
    })
    
    total_removed = result1.deleted_count + result2.deleted_count + result3.deleted_count
    
    logger.info(f"Removed {result1.deleted_count} failed runs")
    logger.info(f"Removed {result2.deleted_count} queued runs")
    logger.info(f"Removed {result3.deleted_count} succeeded runs without scores")
    logger.info(f"Total removed: {total_removed}")
    
    # Show final stats
    final_count = await runs_collection.count_documents({})
    succeeded_with_scores = await runs_collection.count_documents({
        "status": "succeeded",
        "scores.composite": {"$exists": True}
    })
    
    logger.info(f"Final database state:")
    logger.info(f"  - Total runs: {final_count}")
    logger.info(f"  - Valid runs with scores: {succeeded_with_scores}")
    
    client.close()
    return total_removed


async def main():
    parser = argparse.ArgumentParser(description="Clean corrupted runs")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    logger.info("Starting run cleanup...")
    removed_count = await clean_corrupted_runs(apply_changes=args.apply)
    
    if args.apply:
        logger.info(f"✅ Cleaned up {removed_count} corrupted runs")
    else:
        logger.info(f"📋 Would remove {removed_count} corrupted runs (use --apply to clean)")


if __name__ == "__main__":
    asyncio.run(main())