#!/usr/bin/env python3
"""
Simplify Research Data - Clean up overly complex identifiers and versioning

This script simplifies:
1. Dataset versions: complex dates/decimals → simple categories
2. Experiment IDs: complex ULIDs → simple sequential numbers  
3. Length bins: inconsistent values → clean S/M/L
4. Source types: multiple variations → clean categories
5. Prompt IDs: complex ULIDs → simple sequential numbers

Usage:
    python scripts/simplify_research_data.py          # Dry run
    python scripts/simplify_research_data.py --apply  # Apply changes
"""

import argparse
import asyncio
import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def simplify_research_data(apply_changes=False):
    """Simplify all overly complex research identifiers and versioning."""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    
    logger.info("🔍 Analyzing current data complexity...")
    
    # 1. SIMPLIFY DATASET VERSIONS
    logger.info("\n📊 Dataset Versions:")
    
    # Check current dataset versions
    cursor = db.prompts.aggregate([
        {"$group": {"_id": "$dataset_version", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    current_versions = await cursor.to_list(length=None)
    
    for version in current_versions:
        logger.info(f"  {version['_id'] or 'null'}: {version['count']} prompts")
    
    # Simplification mapping
    version_mapping = {
        "1.0": "static",
        "20240115": "static", 
        "20240116": "static",
        None: "static",
        "adaptive_v1.0": "adaptive",
        "adaptive_v1.1": "adaptive"
    }
    
    if apply_changes:
        for old_version, new_version in version_mapping.items():
            if old_version is None:
                filter_query = {"dataset_version": {"$exists": False}}
            else:
                filter_query = {"dataset_version": old_version}
            
            result = await db.prompts.update_many(
                filter_query,
                {"$set": {"dataset_version": new_version}}
            )
            if result.modified_count > 0:
                logger.info(f"  ✅ Updated {result.modified_count} prompts: {old_version} → {new_version}")
        
        # Also update runs
        for old_version, new_version in version_mapping.items():
            if old_version is None:
                filter_query = {"dataset_version": {"$exists": False}}
            else:
                filter_query = {"dataset_version": old_version}
            
            result = await db.runs.update_many(
                filter_query,
                {"$set": {"dataset_version": new_version}}
            )
            if result.modified_count > 0:
                logger.info(f"  ✅ Updated {result.modified_count} runs: {old_version} → {new_version}")
    else:
        logger.info("  📋 Would simplify to: static, adaptive")
    
    # 2. SIMPLIFY EXPERIMENT IDs
    logger.info("\n🧪 Experiment IDs:")
    
    cursor = db.runs.aggregate([
        {"$group": {"_id": "$experiment_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    current_experiments = await cursor.to_list(length=None)
    
    for exp in current_experiments:
        logger.info(f"  {exp['_id'] or 'null'}: {exp['count']} runs")
    
    if apply_changes:
        # Get all unique experiment IDs and assign simple sequential numbers
        cursor = db.runs.distinct("experiment_id", {"experiment_id": {"$exists": True}})
        unique_experiments = await cursor
        
        for i, old_exp_id in enumerate(sorted(unique_experiments), 1):
            new_exp_id = f"exp_{i:03d}"
            result = await db.runs.update_many(
                {"experiment_id": old_exp_id},
                {"$set": {"experiment_id": new_exp_id}}
            )
            if result.modified_count > 0:
                logger.info(f"  ✅ Updated experiment: {old_exp_id} → {new_exp_id} ({result.modified_count} runs)")
        
        # Handle runs without experiment_id
        no_exp_count = await db.runs.count_documents({"experiment_id": {"$exists": False}})
        if no_exp_count > 0:
            next_exp_num = len(unique_experiments) + 1
            await db.runs.update_many(
                {"experiment_id": {"$exists": False}},
                {"$set": {"experiment_id": f"exp_{next_exp_num:03d}"}}
            )
            logger.info(f"  ✅ Assigned exp_{next_exp_num:03d} to {no_exp_count} runs without experiment_id")
    else:
        logger.info("  📋 Would simplify to: exp_001, exp_002, exp_003...")
    
    # 3. SIMPLIFY LENGTH BINS
    logger.info("\n📏 Length Bins:")
    
    # Check prompts length bins
    cursor = db.prompts.aggregate([
        {"$group": {"_id": "$length_bin", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    current_length_bins = await cursor.to_list(length=None)
    
    for bin_data in current_length_bins:
        logger.info(f"  {bin_data['_id'] or 'null'}: {bin_data['count']} prompts")
    
    # Also check metadata.length_bin
    cursor = db.prompts.aggregate([
        {"$group": {"_id": "$metadata.length_bin", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    metadata_length_bins = await cursor.to_list(length=None)
    
    logger.info("  metadata.length_bin:")
    for bin_data in metadata_length_bins:
        logger.info(f"    {bin_data['_id'] or 'null'}: {bin_data['count']} prompts")
    
    if apply_changes:
        # Standardize length bins - map various formats to S/M/L
        length_mapping = {
            "short": "S",
            "medium": "M", 
            "long": "L",
            "XS": "S",  # Extra small → Small
            "XL": "L",  # Extra large → Large
        }
        
        for old_bin, new_bin in length_mapping.items():
            # Update main length_bin field
            result = await db.prompts.update_many(
                {"length_bin": old_bin},
                {"$set": {"length_bin": new_bin}}
            )
            if result.modified_count > 0:
                logger.info(f"  ✅ Updated {result.modified_count} prompts: length_bin {old_bin} → {new_bin}")
            
            # Update metadata.length_bin field
            result = await db.prompts.update_many(
                {"metadata.length_bin": old_bin},
                {"$set": {"metadata.length_bin": new_bin}}
            )
            if result.modified_count > 0:
                logger.info(f"  ✅ Updated {result.modified_count} prompts: metadata.length_bin {old_bin} → {new_bin}")
        
        # Also update runs prompt_length_bin
        for old_bin, new_bin in length_mapping.items():
            result = await db.runs.update_many(
                {"prompt_length_bin": old_bin},
                {"$set": {"prompt_length_bin": new_bin}}
            )
            if result.modified_count > 0:
                logger.info(f"  ✅ Updated {result.modified_count} runs: prompt_length_bin {old_bin} → {new_bin}")
    else:
        logger.info("  📋 Would standardize to: S, M, L")
    
    # 4. SIMPLIFY SOURCE TYPES
    logger.info("\n📚 Source Types:")
    
    cursor = db.prompts.aggregate([
        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    current_sources = await cursor.to_list(length=None)
    
    for source in current_sources:
        logger.info(f"  {source['_id'] or 'null'}: {source['count']} prompts")
    
    if apply_changes:
        # Standardize source types
        source_mapping = {
            "cysecbench": "static",
            "CySecBench": "static",
            "curated": "static",
            "CURATED": "static",
            "adaptive": "adaptive",
            "ADAPTIVE": "adaptive"
        }
        
        for old_source, new_source in source_mapping.items():
            result = await db.prompts.update_many(
                {"source": old_source},
                {"$set": {"source": new_source}}
            )
            if result.modified_count > 0:
                logger.info(f"  ✅ Updated {result.modified_count} prompts: source {old_source} → {new_source}")
        
        # Also update runs
        for old_source, new_source in source_mapping.items():
            result = await db.runs.update_many(
                {"source": old_source},
                {"$set": {"source": new_source}}
            )
            if result.modified_count > 0:
                logger.info(f"  ✅ Updated {result.modified_count} runs: source {old_source} → {new_source}")
    else:
        logger.info("  📋 Would standardize to: static, adaptive")
    
    # 5. SIMPLIFY PROMPT IDs (Optional - only if requested)
    logger.info("\n🆔 Prompt IDs:")
    
    # Count ULID vs simple IDs
    ulid_count = await db.prompts.count_documents({"prompt_id": {"$regex": "^[0-9A-Z]{26}$"}})
    simple_count = await db.prompts.count_documents({"prompt_id": {"$regex": "^prompt_"}})
    total_prompts = await db.prompts.count_documents({})
    
    logger.info(f"  ULID format: {ulid_count} prompts")
    logger.info(f"  Simple format: {simple_count} prompts") 
    logger.info(f"  Other/null: {total_prompts - ulid_count - simple_count} prompts")
    
    if apply_changes and ulid_count > 0:
        logger.info("  ⚠️  Prompt ID simplification requires careful handling of references")
        logger.info("  📋 Skipping prompt ID changes to preserve data integrity")
    else:
        logger.info("  📋 Would convert ULIDs to: prompt_001, prompt_002, prompt_003...")
    
    # 6. SUMMARY
    logger.info("\n📊 Simplification Summary:")
    
    if apply_changes:
        logger.info("✅ Applied simplifications:")
        logger.info("  • Dataset versions → static, adaptive")
        logger.info("  • Experiment IDs → exp_001, exp_002, exp_003...")
        logger.info("  • Length bins → S, M, L")
        logger.info("  • Source types → static, adaptive")
        logger.info("  • Prompt IDs → preserved for data integrity")
    else:
        logger.info("📋 Dry run completed. Use --apply to make changes.")
    
    # Final verification
    if apply_changes:
        logger.info("\n🔍 Final verification:")
        
        # Check dataset versions
        cursor = db.prompts.aggregate([
            {"$group": {"_id": "$dataset_version", "count": {"$sum": 1}}}
        ])
        final_versions = await cursor.to_list(length=None)
        logger.info("  Dataset versions:")
        for version in final_versions:
            logger.info(f"    {version['_id']}: {version['count']} prompts")
        
        # Check length bins
        cursor = db.prompts.aggregate([
            {"$group": {"_id": "$length_bin", "count": {"$sum": 1}}}
        ])
        final_bins = await cursor.to_list(length=None)
        logger.info("  Length bins:")
        for bin_data in final_bins:
            logger.info(f"    {bin_data['_id']}: {bin_data['count']} prompts")
    
    client.close()
    return {"status": "completed" if apply_changes else "dry_run"}


async def main():
    parser = argparse.ArgumentParser(description="Simplify research data complexity")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    args = parser.parse_args()
    
    logger.info("🚀 Starting research data simplification...")
    logger.info("Goal: Clean, simple identifiers for academic research")
    
    result = await simplify_research_data(apply_changes=args.apply)
    
    if args.apply:
        logger.info("✅ Research data simplification completed!")
        logger.info("📊 Your data now uses clean, simple identifiers perfect for academic analysis")
    else:
        logger.info("📋 Dry run completed. Review changes above, then use --apply to execute")


if __name__ == "__main__":
    asyncio.run(main())