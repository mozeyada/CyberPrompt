#!/usr/bin/env python3
"""Export static prompts from database to JSON file"""

import asyncio
import json
from datetime import datetime
from app.db.connection import connect_to_mongo, database
from app.utils.mongodb import convert_objectid

async def export_static_prompts():
    await connect_to_mongo()
    
    # Get only static prompts (exclude adaptive)
    prompts = await database.db.prompts.find({"prompt_type": "static"}).to_list(None)
    prompts_clean = [convert_objectid(p) for p in prompts]
    
    # Create data directory
    import os
    os.makedirs("data", exist_ok=True)
    
    # Export to JSON
    with open("data/prompts.json", 'w') as f:
        json.dump({
            "exported_at": datetime.utcnow().isoformat(),
            "total_prompts": len(prompts_clean),
            "prompts": prompts_clean
        }, f, indent=2, default=str)
    
    print(f"✅ Exported {len(prompts_clean)} static prompts to data/prompts.json")

if __name__ == "__main__":
    asyncio.run(export_static_prompts())