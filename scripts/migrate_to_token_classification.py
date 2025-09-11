#!/usr/bin/env python3
"""
Migration script to update prompt classification from word-count to token-count.

Updates:
- Adds token_count field to all prompts
- Reclassifies prompts using continuous token-based bins:
  - S: ≤300 tokens
  - M: 301-800 tokens  
  - L: >800 tokens
- Removes XS classification entirely
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.token_classification import get_token_count_and_bin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_to_token_classification():
    """Migrate all prompts to token-based classification."""
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
        "errors": 0,
        "unclassified": 0
    }
    
    bin_counts = {"S": 0, "M": 0, "L": 0, "unclassified": 0}
    
    for prompt in prompts:
        try:
            text = prompt.get("text", "")
            if not text:
                logger.warning(f"Empty text for prompt {prompt.get('prompt_id', 'unknown')}")
                stats["errors"] += 1
                continue
            
            # Get token count and new classification
            token_count, new_bin = get_token_count_and_bin(text)
            
            current_token_count = prompt.get("token_count")
            current_bin = prompt.get("length_bin")
            
            # Prepare update data
            update_data = {"token_count": token_count}
            
            if new_bin:
                update_data["length_bin"] = new_bin.value
                bin_counts[new_bin.value] += 1
            else:
                # Remove length_bin for unclassified prompts
                update_data["length_bin"] = None
                bin_counts["unclassified"] += 1
                stats["unclassified"] += 1
            
            # Check if update needed
            needs_update = (
                current_token_count != token_count or
                current_bin != update_data["length_bin"]
            )
            
            if needs_update:
                await collection.update_one(
                    {"_id": prompt["_id"]},
                    {"$set": update_data}
                )
                stats["updated"] += 1
                
                bin_str = new_bin.value if new_bin else "unclassified"
                logger.info(f"Updated {prompt.get('prompt_id', 'unknown')}: {token_count} tokens -> {bin_str}")
            else:
                stats["unchanged"] += 1
                
        except Exception as e:
            logger.error(f"Error processing prompt {prompt.get('prompt_id', 'unknown')}: {e}")
            stats["errors"] += 1
    
    # Log final statistics
    logger.info("Migration completed!")
    logger.info(f"Total prompts: {stats['total']}")
    logger.info(f"Updated: {stats['updated']}")
    logger.info(f"Unchanged: {stats['unchanged']}")
    logger.info(f"Unclassified: {stats['unclassified']}")
    logger.info(f"Errors: {stats['errors']}")
    
    logger.info("Final token-based length bin distribution:")
    for bin_name, count in bin_counts.items():
        percentage = (count / stats['total']) * 100 if stats['total'] > 0 else 0
        logger.info(f"  {bin_name}: {count} prompts ({percentage:.1f}%)")
    
    client.close()
    return stats


async def validate_migration():
    """Validate migration by checking 10 random prompts."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    # Get 10 random prompts
    pipeline = [{"$sample": {"size": 10}}]
    cursor = collection.aggregate(pipeline)
    prompts = await cursor.to_list(length=10)
    
    logger.info("Validation - comparing word count vs token count for 10 random prompts:")
    logger.info("Prompt ID | Word Count | Token Count | Classification")
    logger.info("-" * 60)
    
    for prompt in prompts:
        text = prompt.get("text", "")
        word_count = len(text.split())
        token_count = prompt.get("token_count", 0)
        length_bin = prompt.get("length_bin", "None")
        prompt_id = prompt.get("prompt_id", "unknown")[:12]
        
        logger.info(f"{prompt_id} | {word_count:10d} | {token_count:11d} | {length_bin}")
    
    client.close()


async def main():
    """Main migration function."""
    logger.info("Starting token-based classification migration...")
    
    # Run migration
    stats = await migrate_to_token_classification()
    
    # Validate results
    logger.info("Validating migration...")
    await validate_migration()
    
    logger.info("✅ Migration completed successfully!")
    return stats


if __name__ == "__main__":
    asyncio.run(main())