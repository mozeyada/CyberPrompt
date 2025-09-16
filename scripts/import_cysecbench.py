#!/usr/bin/env python3
"""
CySecBench Data Import Script
Imports prompts from JSON file
"""

import asyncio
import json
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

async def import_cysecbench_data():
    """Import prompts from JSON file"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    collection = db.prompts
    
    # Check if data already exists
    count = await collection.count_documents({})
    if count > 0:
        print(f'Database already has {count} prompts')
        await client.close()
        return
    
    # Path to JSON file
    json_path = Path("data/prompts.json")
    
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        await client.close()
        return
    
    print("Starting JSON import...")
    
    # Load and import JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    prompts = data['prompts']
    result = await collection.insert_many(prompts)
    print(f'Imported {len(result.inserted_ids)} prompts')
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(import_cysecbench_data())
