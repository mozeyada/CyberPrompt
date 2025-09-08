#!/usr/bin/env python3
"""
Fix null prompt_ids with simple sequential IDs like prompt_001, prompt_002, etc.

Usage:
    python scripts/fix_null_prompt_ids_simple.py --apply
"""

import argparse
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_null_prompt_ids_simple(apply_changes=False):
    """Fix null prompt_ids with simple sequential IDs."""
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    logger.info("Connected to MongoDB")
    
    # Find prompts with null prompt_id
    cursor = collection.find({"prompt_id": None})
    null_prompts = await cursor.to_list(length=None)
    
    logger.info(f"Found {len(null_prompts)} prompts with null prompt_id")
    
    if len(null_prompts) == 0:
        logger.info("No null prompt_ids found. Database is already correct.")
        client.close()
        return 0
    
    if not apply_changes:
        logger.info("DRY RUN: Use --apply to make actual changes")
        client.close()
        return len(null_prompts)
    
    # Apply fix with simple sequential IDs
    update_count = 0
    for i, prompt in enumerate(null_prompts, 1):
        new_prompt_id = f"prompt_{i:03d}"  # prompt_001, prompt_002, etc.
        result = await collection.update_one(
            {"_id": prompt["_id"]},
            {"$set": {"prompt_id": new_prompt_id}}
        )
        if result.modified_count > 0:
            update_count += 1
            if update_count <= 10:  # Log first 10
                logger.info(f"Updated: null -> {new_prompt_id}")
    
    logger.info(f"Successfully updated {update_count} prompts with simple IDs")
    client.close()
    return update_count


async def main():
    parser = argparse.ArgumentParser(description="Fix null prompt_ids with simple IDs")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    logger.info("Starting simple prompt_id fix...")
    count = await fix_null_prompt_ids_simple(apply_changes=args.apply)
    
    if args.apply:
        logger.info(f"✅ Fixed {count} null prompt_ids with simple sequential IDs")
    else:
        logger.info(f"📋 Found {count} prompts that need fixing (use --apply to fix)")


if __name__ == "__main__":
    asyncio.run(main())