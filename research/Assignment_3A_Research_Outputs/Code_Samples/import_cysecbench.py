#!/usr/bin/env python3
"""
Import CyberPrompt Research Dataset Script

This script imports the research-grade prompt dataset (300 prompts) generated
by generate_research_dataset.py into the MongoDB database.

Usage:
    python scripts/import_cysecbench.py

Components Imported:
- 150 SOC Incident prompts (50 base × 3 length variants)
- 90 GRC Assessment prompts (30 base × 3 length variants)  
- 60 CTI Analysis prompts (20 base × 3 length variants)
Total: 300 prompts across S/M/L length bins for RQ1 research
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.connection import close_mongo_connection, connect_to_mongo
from app.db.repositories import PromptRepository
from app.models import Prompt, LengthBin, ScenarioType, SourceType


async def import_cysecbench_dataset():
    """Import the CySecBench research dataset into MongoDB"""
    
    print("🎓 CYBERPROMPT RESEARCH DATASET IMPORT")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        print("📡 Connecting to MongoDB...")
        await connect_to_mongo()
        
        # Load dataset from JSON file
        dataset_path = Path(__file__).parent.parent / "data" / "prompts.json"
        
        if not dataset_path.exists():
            print(f"❌ Dataset file not found: {dataset_path}")
            print("💡 Run 'python scripts/generate_research_dataset.py' first to generate the dataset.")
            return False
        
        print(f"📄 Loading dataset from: {dataset_path}")
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        prompts_data = data['prompts']
        print(f"📊 Dataset version: {data['dataset_version']}")
        print(f"📊 Total prompts to import: {len(prompts_data)}")
        
        # Initialize repository
        prompt_repo = PromptRepository()
        
        # Check if prompts already exist to avoid duplicates
        existing_prompts = await prompt_repo.list_prompts(limit=1000)
        existing_count = len(existing_prompts)
        print(f"📊 Existing prompts in database: {existing_count}")
        
        # Import prompts
        imported_count = 0
        skipped_count = 0
        errors = []
        
        print("📥 Starting import process...")
        
        for prompt_data in prompts_data:
            try:
                # Check if prompt already exists
                existing = await prompt_repo.get_by_id(prompt_data['prompt_id'])
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Create Prompt object
                prompt = Prompt(
                    prompt_id=prompt_data['prompt_id'],
                    text=prompt_data['text'],
                    scenario=ScenarioType(prompt_data['scenario']),
                    category=prompt_data['category'],
                    source=SourceType.static,
                    prompt_type="static",
                    length_bin=LengthBin(prompt_data['length_bin']),
                    token_count=prompt_data['token_count'],
                    dataset_version=prompt_data['dataset_version'],
                    metadata=prompt_data.get('metadata', {}),
                    tags=prompt_data.get('tags', [])
                )
                
                # Import to database
                await prompt_repo.create(prompt)
                imported_count += 1
                
                if imported_count % 50 == 0:
                    print(f"  ➤ Imported: {imported_count} prompts...")
                    
            except Exception as e:
                error_msg = f"Error importing {prompt_data.get('prompt_id', 'unknown')}: {str(e)}"
                errors.append(error_msg)
                print(f"⚠️  {error_msg}")
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 IMPORT SUMMARY")
        print("=" * 50)
        print(f"✅ Successfully imported: {imported_count} prompts")
        print(f"⏭️  Skipped (already exist): {skipped_count} prompts")
        
        if errors:
            print(f"❌ Errors encountered: {len(errors)}")
            for error in errors[:5]:  # Show first 5 errors
                print(f"    • {error}")
            if len(errors) > 5:
                print(f"    • ... and {len(errors) - 5} more errors")
        
        # Verify final count
        final_prompts = await prompt_repo.list_prompts(limit=1000)
        final_count = len(final_prompts)
        print(f"📊 Final database count: {final_count} prompts")
        
        # Dataset verification
        if final_count >= 300:
            print("✅ Dataset import completed successfully!")
            print("🎯 Ready for RQ1 research (prompt length analysis)")
            return True
        elif final_count > 0:
            print("⚠️  Dataset partially imported. Check for missing prompts.")
            return False
        else:
            print("❌ No prompts imported. Check for errors above.")
            return False
            
    except Exception as e:
        print(f"❌ Import failed with error: {str(e)}")
        return False
        
    finally:
        await close_mongo_connection()


async def main():
    """Main script entry point"""
    
    # Check if dataset exists
    dataset_path = Path(__file__).parent.parent / "data" / "prompts.json"
    
    if not dataset_path.exists():
        print("❌ Research dataset not found!")
        print()
        print("📋 SOLUTION:")
        print("1. Generate the research dataset first:")
        print("   python scripts/generate_research_dataset.py")
        print()
        print("2. Then run this import script:")
        print("   python scripts/import_cysecbench.py")
        print()
        return
    
    # Check if dataset is valid
    try:
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        if data['total_prompts'] != 300:
            print(f"⚠️  Warning: Dataset has {data['total_prompts']} prompts, expected 300")
        
        print(f"✅ Dataset found: {data['dataset_version']}")
        print(f"✅ Total prompts: {data['total_prompts']}")
        print(f"✅ Generated: {data['exported_at']}")
        
    except Exception as e:
        print(f"❌ Invalid dataset file: {str(e)}")
        return
    
    # Run import
    success = await import_cysecbench_dataset()
    
    if success:
        print()
        print("🚀 CYBERPROMPT RESEARCH DATASET IMPORT COMPLETE!")
        print("📊 The platform is ready for research experiments.")
        print("🎯 Dataset supports RQ1 (prompt length analysis) and RQ2 (cost-effectiveness).")
    else:
        print()
        print("❌ Import completed with issues.")
        print("💡 Check the errors above and resolve them before running experiments.")


if __name__ == "__main__":
    # Handle both direct execution and import
    if __name__ == "__main__":
        print("🎓 CyberPrompt Research Dataset Import Tool")
        print("Student: Mohamed Zeyada (11693860)")
        print("Supervisor: Dr. Gowri Ramachandran")
        print("Project: IFN712 - Research in IT Practice")
        print()
        
        # Run the async main function
        asyncio.run(main())
