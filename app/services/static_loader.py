"""Load static prompts from JSON file into database on startup"""

import json
import logging
from pathlib import Path
from app.db.connection import database
from app.models import Prompt

logger = logging.getLogger(__name__)

async def load_static_prompts_if_empty():
    """Load static prompts from data/prompts.json if database is empty"""
    
    # Check if prompts already exist
    count = await database.db.prompts.count_documents({})
    if count > 0:
        logger.info(f"Database already has {count} prompts, skipping static load")
        return
    
    # Load from static file
    static_file = Path("data/prompts.json")
    if not static_file.exists():
        logger.warning("No static prompts file found at data/prompts.json")
        return
    
    try:
        with open(static_file) as f:
            data = json.load(f)
        
        prompts = data.get("prompts", [])
        if not prompts:
            logger.warning("No prompts found in static file")
            return
        
        # Insert prompts into database
        await database.db.prompts.insert_many(prompts)
        logger.info(f"✅ Loaded {len(prompts)} static prompts into database")
        
    except Exception as e:
        logger.error(f"Failed to load static prompts: {e}")