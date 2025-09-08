#!/usr/bin/env python3
"""
Migration script to fix prompt length_bin assignments based on word count.

Ground Truth (CySecBench + Domhan & Zhu 2025):
- XS: 1-20 words
- S: 21-80 words  
- M: 81-200 words
- L: 201-400 words
- XL: 401+ words

Usage:
    python -m app.services.migrations.fix_length_bins
"""

import asyncio
import logging

from app.db.repositories import PromptRepository
from app.models import LengthBin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_correct_length_bin(word_count: int) -> LengthBin:
    """Determine correct length bin based on word count."""
    if word_count <= 20:
        return LengthBin.XS
    elif word_count <= 80:
        return LengthBin.S
    elif word_count <= 200:
        return LengthBin.M
    elif word_count <= 400:
        return LengthBin.L
    else:
        return LengthBin.XL


async def fix_length_bins():
    """Fix all prompt length_bin assignments."""
    repo = PromptRepository()
    
    # Get all prompts
    all_prompts = await repo.list_prompts(limit=10000)
    
    logger.info(f"Processing {len(all_prompts)} prompts...")
    
    stats = {
        "total": len(all_prompts),
        "updated": 0,
        "unchanged": 0,
        "errors": 0
    }
    
    bin_counts = {"XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0}
    
    for prompt in all_prompts:
        try:
            # Calculate word count
            word_count = len(prompt.text.split())
            correct_bin = get_correct_length_bin(word_count)
            
            # Check if update needed
            if prompt.length_bin != correct_bin:
                # Update the prompt
                prompt.length_bin = correct_bin
                
                # Update metadata if it exists
                if prompt.metadata:
                    prompt.metadata["word_count"] = word_count
                    prompt.metadata["length_bin"] = correct_bin.value.lower()
                else:
                    prompt.metadata = {
                        "word_count": word_count,
                        "length_bin": correct_bin.value.lower()
                    }
                
                # Save to database
                await repo.upsert(prompt)
                stats["updated"] += 1
                
                logger.info(f"Updated {prompt.prompt_id}: {word_count} words -> {correct_bin.value}")
            else:
                stats["unchanged"] += 1
            
            # Count final bins
            bin_counts[correct_bin.value] += 1
            
        except Exception as e:
            logger.error(f"Error processing prompt {prompt.prompt_id}: {e}")
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
    
    return stats


async def verify_migration():
    """Verify the migration results."""
    repo = PromptRepository()
    
    # Count prompts by length_bin
    all_prompts = await repo.list_prompts(limit=10000)
    
    bin_counts = {"XS": 0, "S": 0, "M": 0, "L": 0, "XL": 0, "null": 0}
    mismatches = []
    
    for prompt in all_prompts:
        word_count = len(prompt.text.split())
        expected_bin = get_correct_length_bin(word_count)
        
        if prompt.length_bin is None:
            bin_counts["null"] += 1
            mismatches.append(f"{prompt.prompt_id}: null (expected {expected_bin.value})")
        elif prompt.length_bin != expected_bin:
            bin_counts[prompt.length_bin.value] += 1
            mismatches.append(f"{prompt.prompt_id}: {prompt.length_bin.value} (expected {expected_bin.value})")
        else:
            bin_counts[prompt.length_bin.value] += 1
    
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