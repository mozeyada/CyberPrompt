#!/usr/bin/env python3
"""
Check variant connections and show which prompts have complete variant sets.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    print("❌ Missing dependencies")
    sys.exit(1)


async def check_variant_connections():
    """Check which prompts have complete variant sets"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    # Get all original short prompts (not variants)
    original_prompts = await collection.find({
        "length_bin": "S", 
        "metadata.variant_of": {"$exists": False}
    }).to_list(length=None)
    
    print(f"📊 Found {len(original_prompts)} original short prompts")
    
    complete_sets = 0
    incomplete_sets = 0
    
    # Check first 10 for detailed view
    for i, prompt in enumerate(original_prompts[:10]):
        prompt_id = prompt.get("prompt_id")
        
        # Find variants of this prompt
        variants = await collection.find({
            "metadata.variant_of": prompt_id
        }).to_list(length=None)
        
        variant_types = [v.get("metadata", {}).get("variant_type") for v in variants]
        has_medium = "medium" in variant_types
        has_long = "long" in variant_types
        
        status = "✅ COMPLETE" if (has_medium and has_long) else "❌ INCOMPLETE"
        print(f"{status} | {prompt_id} | Variants: {variant_types}")
        
        if has_medium and has_long:
            complete_sets += 1
        else:
            incomplete_sets += 1
    
    # Count all complete sets
    print(f"\n📈 Checking all {len(original_prompts)} prompts...")
    
    for prompt in original_prompts:
        prompt_id = prompt.get("prompt_id")
        
        # Count variants
        variant_count = await collection.count_documents({
            "metadata.variant_of": prompt_id
        })
        
        if variant_count >= 2:  # Has both medium and long
            complete_sets += 1
        else:
            incomplete_sets += 1
    
    print(f"\n📊 Summary:")
    print(f"✅ Complete sets (S+M+L): {complete_sets}")
    print(f"❌ Incomplete sets: {incomplete_sets}")
    print(f"📈 Coverage: {complete_sets/len(original_prompts)*100:.1f}%")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(check_variant_connections())