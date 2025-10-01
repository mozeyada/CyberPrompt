#!/usr/bin/env python3
"""
Sync prompts from JSON file to database
"""
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient

async def sync_prompts():
    # Connect to database
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['genai_bench']
    collection = db['prompts']
    
    # Load JSON file
    with open('/home/zeyada/CyberCQBench/data/prompts.json', 'r') as f:
        data = json.load(f)
    
    # Get current database prompts
    db_prompts = set()
    async for doc in collection.find({}, {'_id': 1}):
        db_prompts.add(doc['_id'])
    
    # Find missing prompts
    json_prompts = {p['_id']: p for p in data['prompts']}
    missing_prompts = []
    
    for prompt_id, prompt_data in json_prompts.items():
        if prompt_id not in db_prompts:
            missing_prompts.append(prompt_data)
    
    print(f"Database has: {len(db_prompts)} prompts")
    print(f"JSON file has: {len(json_prompts)} prompts")
    print(f"Missing prompts: {len(missing_prompts)}")
    
    if missing_prompts:
        print(f"Missing prompt scenarios:")
        scenarios = {}
        for p in missing_prompts:
            scenario = p['scenario']
            scenarios[scenario] = scenarios.get(scenario, 0) + 1
        for scenario, count in scenarios.items():
            print(f"  {scenario}: {count}")
        
        # Insert missing prompts
        result = await collection.insert_many(missing_prompts)
        print(f"Inserted {len(result.inserted_ids)} prompts")
    else:
        print("No missing prompts found")
    
    # Verify final count
    final_count = await collection.count_documents({})
    print(f"Final database count: {final_count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(sync_prompts())