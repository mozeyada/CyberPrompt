#!/usr/bin/env python3
"""
Fix token counts and classifications in MongoDB database.

This script:
1. Connects to your existing MongoDB database
2. Recalculates token counts using tiktoken (consistent method)
3. Applies new continuous classification ranges (≤300, 301-800, >800)
4. Updates all prompts in place
"""

import asyncio
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import tiktoken
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    print("❌ Missing dependencies. Install with: pip install tiktoken motor")
    sys.exit(1)


def calculate_tokens_tiktoken(text: str) -> int:
    """Calculate tokens using tiktoken cl100k_base (GPT-4 standard)"""
    try:
        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))
    except Exception:
        # Fallback: rough estimation
        return int(len(text.split()) * 1.3)


def classify_tokens(token_count: int) -> str:
    """Apply new continuous classification ranges"""
    if token_count <= 300:
        return "S"
    elif 301 <= token_count <= 800:
        return "M"
    else:  # > 800
        return "L"


async def fix_all_token_counts():
    """Fix all token counts and classifications in database"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    print(f"🔌 Connecting to {mongo_uri}/{mongo_db}")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    # Get all prompts
    print("📊 Fetching all prompts...")
    cursor = collection.find({})
    prompts = await cursor.to_list(length=None)
    
    print(f"🔍 Found {len(prompts)} prompts to process")
    
    # Process each prompt
    stats = {"updated": 0, "unchanged": 0, "errors": 0}
    bin_counts = {"S": 0, "M": 0, "L": 0}
    
    for i, prompt in enumerate(prompts, 1):
        try:
            text = prompt.get("text", "")
            if not text:
                print(f"⚠️  Empty text for prompt {prompt.get('prompt_id', 'unknown')}")
                stats["errors"] += 1
                continue
            
            # Calculate new token count and classification
            new_token_count = calculate_tokens_tiktoken(text)
            new_length_bin = classify_tokens(new_token_count)
            
            # Check if update needed
            current_token_count = prompt.get("token_count")
            current_length_bin = prompt.get("length_bin")
            
            needs_update = (
                current_token_count != new_token_count or
                current_length_bin != new_length_bin
            )
            
            if needs_update:
                # Update in database
                await collection.update_one(
                    {"_id": prompt["_id"]},
                    {"$set": {
                        "token_count": new_token_count,
                        "length_bin": new_length_bin
                    }}
                )
                stats["updated"] += 1
                
                if i <= 10:  # Show first 10 updates
                    print(f"✅ Updated {prompt.get('prompt_id', 'unknown')[:12]}: {new_token_count} tokens → {new_length_bin}")
            else:
                stats["unchanged"] += 1
            
            # Count bins
            bin_counts[new_length_bin] += 1
            
            # Progress indicator
            if i % 100 == 0:
                print(f"📈 Processed {i}/{len(prompts)} prompts...")
                
        except Exception as e:
            print(f"❌ Error processing prompt {prompt.get('prompt_id', 'unknown')}: {e}")
            stats["errors"] += 1
    
    # Final statistics
    print("\n" + "="*50)
    print("🎉 Token count fix completed!")
    print(f"📊 Total prompts: {len(prompts)}")
    print(f"✅ Updated: {stats['updated']}")
    print(f"➡️  Unchanged: {stats['unchanged']}")
    print(f"❌ Errors: {stats['errors']}")
    
    print("\n📏 New length bin distribution:")
    total = sum(bin_counts.values())
    for bin_name, count in bin_counts.items():
        percentage = (count / total) * 100 if total > 0 else 0
        print(f"  {bin_name}: {count:4d} prompts ({percentage:5.1f}%)")
    
    client.close()
    return stats


async def main():
    """Main function"""
    print("🔧 CyberCQBench Token Count Fix")
    print("="*40)
    print("This will recalculate ALL token counts using tiktoken")
    print("and apply new continuous classification ranges.")
    print()
    
    # Confirm before proceeding
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cancelled by user")
        return
    
    try:
        stats = await fix_all_token_counts()
        print(f"\n✅ Successfully updated {stats['updated']} prompts!")
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)