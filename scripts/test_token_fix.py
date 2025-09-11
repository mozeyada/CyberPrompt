#!/usr/bin/env python3
"""
Test token calculation on a few sample prompts before running the full fix.
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
        return int(len(text.split()) * 1.3)


def classify_tokens(token_count: int) -> str:
    """Apply new continuous classification ranges"""
    if token_count <= 300:
        return "S"
    elif 301 <= token_count <= 800:
        return "M"
    else:
        return "L"


async def test_token_calculation():
    """Test token calculation on first 5 prompts"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    # Get first 5 prompts
    cursor = collection.find({}).limit(5)
    prompts = await cursor.to_list(length=5)
    
    print("🧪 Testing token calculation on 5 sample prompts:")
    print("="*80)
    
    for prompt in prompts:
        text = prompt.get("text", "")
        current_tokens = prompt.get("token_count", 0)
        current_bin = prompt.get("length_bin", "None")
        
        # Calculate new values
        new_tokens = calculate_tokens_tiktoken(text)
        new_bin = classify_tokens(new_tokens)
        
        # Show comparison
        print(f"Prompt ID: {prompt.get('prompt_id', 'unknown')[:15]}")
        print(f"Text: {text[:60]}{'...' if len(text) > 60 else ''}")
        print(f"Current: {current_tokens} tokens → {current_bin}")
        print(f"New:     {new_tokens} tokens → {new_bin}")
        print(f"Change:  {'✅ SAME' if current_tokens == new_tokens and current_bin == new_bin else '🔄 DIFFERENT'}")
        print("-" * 80)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(test_token_calculation())