#!/usr/bin/env python3
"""
Direct MongoDB migration script to fix prompt length_bin assignments.

Ground Truth (CySecBench + Domhan & Zhu 2025):
- XS: 1-20 words
- S: 21-80 words  
- M: 81-200 words
- L: 201-400 words
- XL: 401+ words
"""

import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_correct_length_bin(word_count: int) -> str:
    """Determine correct length bin based on word count."""
    if word_count <= 20:
        return "XS"
    elif word_count <= 80:
        return "S"
    elif word_count <= 200:
        return "M"
    elif word_count <= 400:
        return "L"
    else:
        return "XL"


async def fix_length_bins():
    """Fix all prompt length_bin assignments."""
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    logger.info("Connected to MongoDB")
    
    # Get all prompts
    cursor = collection.find({})
    prompts = await cursor.to_list(length=None)
    
    logger.info(f"Processing {len(prompts)} prompts...")
    
    stats = {
        "total": len(prompts),
        "updated": 0,
        "unchanged": 0,
        "errors": 0
    }
    
    bin_counts = {"XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0}
    
    for prompt in prompts:
        try:
            # Calculate word count
            text = prompt.get("text", "")
            word_count = len(text.split())
            correct_bin = get_correct_length_bin(word_count)
            
            current_bin = prompt.get("length_bin")
            
            # Check if update needed
            if current_bin != correct_bin:
                # Update the prompt
                update_data = {
                    "length_bin": correct_bin,
                    "metadata.word_count": word_count,
                    "metadata.length_bin": correct_bin.lower()
                }
                
                await collection.update_one(
                    {"_id": prompt["_id"]},
                    {"$set": update_data}
                )
                
                stats["updated"] += 1
                logger.info(f"Updated {prompt.get('prompt_id', 'unknown')}: {word_count} words -> {correct_bin}")
            else:
                stats["unchanged"] += 1
            
            # Count final bins
            bin_counts[correct_bin] += 1
            
        except Exception as e:
            logger.error(f"Error processing prompt {prompt.get('prompt_id', 'unknown')}: {e}")
            stats["errors"] += 1
    
    # Log final statistics
    logger.info("Migration completed!")
    logger.info(f"Total prompts: {stats['total']}")
    logger.info(f"Updated: {stats['updated']}")
    logger.info(f"Unchanged: {stats['unchanged']}")
    logger.info(f"Errors: {stats['errors']}")
    
    logger.info("Final length bin distribution:")
    for bin_name, count in bin_counts.items():
        percentage = (count / stats['total']) * 100 if stats['total'] > 0 else 0
        logger.info(f"  {bin_name}: {count} prompts ({percentage:.1f}%)")
    
    # Close connection
    client.close()
    
    return stats


async def verify_migration():
    """Verify the migration results."""
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    # Get all prompts
    cursor = collection.find({})
    prompts = await cursor.to_list(length=None)
    
    bin_counts = {"XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "null": 0}
    mismatches = []
    
    for prompt in prompts:
        text = prompt.get("text", "")
        word_count = len(text.split())
        expected_bin = get_correct_length_bin(word_count)
        current_bin = prompt.get("length_bin")
        
        if current_bin is None:
            bin_counts["null"] += 1
            mismatches.append(f"{prompt.get('prompt_id', 'unknown')}: null (expected {expected_bin})")
        elif current_bin != expected_bin:
            bin_counts[current_bin] += 1
            mismatches.append(f"{prompt.get('prompt_id', 'unknown')}: {current_bin} (expected {expected_bin})")
        else:
            bin_counts[current_bin] += 1
    
    logger.info("Verification results:")
    for bin_name, count in bin_counts.items():
        logger.info(f"  {bin_name}: {count} prompts")
    
    if mismatches:
        logger.warning(f"Found {len(mismatches)} mismatches:")
        for mismatch in mismatches[:10]:  # Show first 10
            logger.warning(f"  {mismatch}")
        if len(mismatches) > 10:
            logger.warning(f"  ... and {len(mismatches) - 10} more")
    else:
        logger.info("✅ All prompts have correct length_bin assignments!")
    
    # Close connection
    client.close()
    
    return len(mismatches) == 0


async def main():
    """Main migration function."""
    logger.info("Starting length_bin migration...")
    
    # Run migration
    stats = await fix_length_bins()
    
    # Verify results
    logger.info("Verifying migration...")
    success = await verify_migration()
    
    if success:
        logger.info("✅ Migration completed successfully!")
    else:
        logger.warning("⚠️ Migration completed with some issues - check logs above")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())