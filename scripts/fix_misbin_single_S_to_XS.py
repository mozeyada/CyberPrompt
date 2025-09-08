#!/usr/bin/env python3
"""
Fix single mis-binned prompt: S category with <21 words should be XS.

Usage:
    python scripts/fix_misbin_single_S_to_XS.py          # Dry run
    python scripts/fix_misbin_single_S_to_XS.py --apply  # Apply changes
"""

import argparse
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_misbin_s_to_xs(apply_changes=False):
    """Fix S category prompts with <21 words to XS category."""
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    logger.info("Connected to MongoDB")
    
    # Find S category prompts with <21 words
    pipeline = [
        {"$match": {"length_bin": "S"}},
        {"$addFields": {"word_count": {"$size": {"$split": ["$text", " "]}}}},
        {"$match": {"word_count": {"$lt": 21}}}
    ]
    
    cursor = collection.aggregate(pipeline)
    misbin_prompts = await cursor.to_list(length=None)
    
    logger.info(f"Found {len(misbin_prompts)} S-category prompts with <21 words")
    
    if len(misbin_prompts) == 0:
        logger.info("No mis-binned prompts found. Database is already correct.")
        client.close()
        return 0
    
    # Show details
    for prompt in misbin_prompts:
        logger.info(f"  {prompt['prompt_id']}: {prompt['word_count']} words - '{prompt['text'][:50]}...'")
    
    if not apply_changes:
        logger.info("DRY RUN: Use --apply to make actual changes")
        client.close()
        return len(misbin_prompts)
    
    # Apply fix
    update_count = 0
    for prompt in misbin_prompts:
        result = await collection.update_one(
            {"_id": prompt["_id"]},
            {"$set": {"length_bin": "XS"}}
        )
        if result.modified_count > 0:
            update_count += 1
            logger.info(f"Updated {prompt['prompt_id']}: S -> XS")
    
    logger.info(f"Successfully updated {update_count} prompts from S to XS")
    client.close()
    return update_count


async def main():
    parser = argparse.ArgumentParser(description="Fix mis-binned S category prompts")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    logger.info("Starting mis-bin fix...")
    count = await fix_misbin_s_to_xs(apply_changes=args.apply)
    
    if args.apply:
        logger.info(f"✅ Fixed {count} mis-binned prompts")
    else:
        logger.info(f"📋 Found {count} prompts that need fixing (use --apply to fix)")


if __name__ == "__main__":
    asyncio.run(main())