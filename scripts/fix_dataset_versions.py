#!/usr/bin/env python3
"""
Fix Dataset Versions - Simplify date-based versions to categorical

Only fixes dataset_version field since everything else is already simplified.

Usage:
    python scripts/fix_dataset_versions.py          # Dry run
    python scripts/fix_dataset_versions.py --apply  # Apply changes
"""

import argparse
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_dataset_versions(apply_changes=False):
    """Fix only dataset_version field - everything else is already clean."""
    
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    
    logger.info("🔍 Checking dataset versions...")
    
    # Check current dataset versions in prompts
    cursor = db.prompts.aggregate([
        {"$group": {"_id": "$dataset_version", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    prompt_versions = await cursor.to_list(length=None)
    
    logger.info("📊 Prompts dataset versions:")
    for version in prompt_versions:
        logger.info(f"  {version['_id'] or 'null'}: {version['count']} prompts")
    
    # Check current dataset versions in runs
    cursor = db.runs.aggregate([
        {"$group": {"_id": "$dataset_version", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    run_versions = await cursor.to_list(length=None)
    
    logger.info("🏃 Runs dataset versions:")
    for version in run_versions:
        logger.info(f"  {version['_id'] or 'null'}: {version['count']} runs")
    
    if apply_changes:
        logger.info("\n✅ Applying fixes...")
        
        # Fix prompts - date versions → "static", adaptive versions → "adaptive"
        date_pattern_updates = 0
        
        # Update date-based versions (like "20250913") to "static"
        result = await db.prompts.update_many(
            {"dataset_version": {"$regex": "^[0-9]{8}$"}},
            {"$set": {"dataset_version": "static"}}
        )
        date_pattern_updates += result.modified_count
        
        # Update other static variants
        static_variants = ["1.0", "v1.0", "cysecbench", "curated"]
        for variant in static_variants:
            result = await db.prompts.update_many(
                {"dataset_version": variant},
                {"$set": {"dataset_version": "static"}}
            )
            date_pattern_updates += result.modified_count
        
        # Update adaptive variants
        result = await db.prompts.update_many(
            {"dataset_version": {"$regex": "adaptive"}},
            {"$set": {"dataset_version": "adaptive"}}
        )
        adaptive_updates = result.modified_count
        
        # Handle null/missing versions → "static"
        result = await db.prompts.update_many(
            {"dataset_version": {"$exists": False}},
            {"$set": {"dataset_version": "static"}}
        )
        null_updates = result.modified_count
        
        logger.info(f"  📊 Prompts: {date_pattern_updates} → static, {adaptive_updates} → adaptive, {null_updates} null → static")
        
        # Fix runs - same logic
        run_date_updates = 0
        
        result = await db.runs.update_many(
            {"dataset_version": {"$regex": "^[0-9]{8}$"}},
            {"$set": {"dataset_version": "static"}}
        )
        run_date_updates += result.modified_count
        
        for variant in static_variants:
            result = await db.runs.update_many(
                {"dataset_version": variant},
                {"$set": {"dataset_version": "static"}}
            )
            run_date_updates += result.modified_count
        
        result = await db.runs.update_many(
            {"dataset_version": {"$regex": "adaptive"}},
            {"$set": {"dataset_version": "adaptive"}}
        )
        run_adaptive_updates = result.modified_count
        
        result = await db.runs.update_many(
            {"dataset_version": {"$exists": False}},
            {"$set": {"dataset_version": "static"}}
        )
        run_null_updates = result.modified_count
        
        logger.info(f"  🏃 Runs: {run_date_updates} → static, {run_adaptive_updates} → adaptive, {run_null_updates} null → static")
        
        # Verification
        logger.info("\n🔍 Final verification:")
        
        cursor = db.prompts.aggregate([
            {"$group": {"_id": "$dataset_version", "count": {"$sum": 1}}}
        ])
        final_prompt_versions = await cursor.to_list(length=None)
        logger.info("  Prompts:")
        for version in final_prompt_versions:
            logger.info(f"    {version['_id']}: {version['count']}")
        
        cursor = db.runs.aggregate([
            {"$group": {"_id": "$dataset_version", "count": {"$sum": 1}}}
        ])
        final_run_versions = await cursor.to_list(length=None)
        logger.info("  Runs:")
        for version in final_run_versions:
            logger.info(f"    {version['_id']}: {version['count']}")
            
    else:
        logger.info("\n📋 Would fix:")
        logger.info("  • Date versions (20250913, etc.) → static")
        logger.info("  • Version numbers (1.0, v1.0) → static") 
        logger.info("  • Adaptive variants → adaptive")
        logger.info("  • Null/missing → static")
    
    client.close()
    return {"status": "completed" if apply_changes else "dry_run"}


async def main():
    parser = argparse.ArgumentParser(description="Fix dataset versions only")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    logger.info("🚀 Fixing dataset versions...")
    logger.info("Target: static, adaptive (everything else is already clean)")
    
    result = await fix_dataset_versions(apply_changes=args.apply)
    
    if args.apply:
        logger.info("✅ Dataset versions fixed!")
        logger.info("📊 Now using clean categories: static, adaptive")
    else:
        logger.info("📋 Dry run completed. Use --apply to fix dataset versions")


if __name__ == "__main__":
    asyncio.run(main())