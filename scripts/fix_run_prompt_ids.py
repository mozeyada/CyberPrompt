#!/usr/bin/env python3
"""
Fix run prompt_ids to match the new simple prompt IDs.

Usage:
    python scripts/fix_run_prompt_ids.py --apply
"""

import argparse
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fix_run_prompt_ids(apply_changes=False):
    """Fix run prompt_ids to match new simple prompt IDs."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    
    logger.info("Connected to MongoDB")
    
    # Get all runs with old ULID prompt_ids
    runs = await db.runs.find({}).to_list(length=None)
    logger.info(f"Found {len(runs)} runs to check")
    
    # Get all prompts for text matching
    prompts = await db.prompts.find({}).to_list(length=None)
    logger.info(f"Found {len(prompts)} prompts available")
    
    # Create a text-to-prompt_id mapping
    text_to_prompt_id = {prompt['text']: prompt['prompt_id'] for prompt in prompts}
    
    fixed_count = 0
    not_found_count = 0
    
    for run in runs:
        old_prompt_id = run.get('prompt_id')
        if not old_prompt_id:
            continue
            
        # Try to find the prompt by old ID first
        old_prompt = await db.prompts.find_one({'prompt_id': old_prompt_id})
        if old_prompt:
            # Already matches, skip
            continue
            
        # Try to find by text content if we have prompt_text in the run
        prompt_text = run.get('prompt_text')
        if prompt_text and prompt_text in text_to_prompt_id:
            new_prompt_id = text_to_prompt_id[prompt_text]
            
            if apply_changes:
                await db.runs.update_one(
                    {'_id': run['_id']},
                    {'$set': {'prompt_id': new_prompt_id}}
                )
            
            fixed_count += 1
            if fixed_count <= 5:
                logger.info(f"Fixed: {old_prompt_id} -> {new_prompt_id}")
        else:
            not_found_count += 1
            if not_found_count <= 3:
                logger.warning(f"Could not find matching prompt for run {run.get('run_id', 'unknown')}")
    
    logger.info(f"Summary:")
    logger.info(f"  - Fixed: {fixed_count}")
    logger.info(f"  - Not found: {not_found_count}")
    
    if not apply_changes:
        logger.info("DRY RUN: Use --apply to make actual changes")
    
    client.close()
    return fixed_count


async def main():
    parser = argparse.ArgumentParser(description="Fix run prompt_ids")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    logger.info("Starting run prompt_id fix...")
    fixed_count = await fix_run_prompt_ids(apply_changes=args.apply)
    
    if args.apply:
        logger.info(f"✅ Fixed {fixed_count} run prompt_ids")
    else:
        logger.info(f"📋 Would fix {fixed_count} run prompt_ids (use --apply to fix)")


if __name__ == "__main__":
    asyncio.run(main())