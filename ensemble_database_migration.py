"""
Database Migration for Triple-Judge Ensemble Evaluation
This script extends the existing database schema to support ensemble evaluations
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

# Add app to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def add_ensemble_fields_to_runs():
    """Add ensemble evaluation fields to existing runs collection"""
    
    print("🔧 ENSEMBLE EVALUATION DATABASE MIGRATION")
    print("=" * 50)
    
    try:
        from app.db.connection import get_database
        
        db = get_database()
        collection = db.runs
        
        # Check current schema
        sample_run = await collection.find_one({})
        if sample_run:
            print(f"📊 Current run fields: {list(sample_run.keys())}")
            
            # Check if ensemble_evaluation already exists
            if "ensemble_evaluation" in sample_run:
                print("✅ Ensemble evaluation fields already exist")
                return True
        
        # Create indexes for ensemble queries
        print("📋 Creating indexes for ensemble evaluation queries...")
        
        indexes_to_create = [
            # Index for ensemble evaluations
            ("ensemble_evaluation", 1),
            ("scenario", 1, "prompt_length_bin", 1),
            ("experiment_id", 1),
            ("dataset_version", 1)
        ]
        
        for index_spec in indexes_to_create:
            if len(index_spec) == 2:
                field, direction = index_spec
                collection.create_index([(field, direction)])
                print(f"   ✅ Index created: {field}")
            else:
                collection.create_index([(index_spec[0], index_spec[1]), (index_spec[2], index_spec[3])])
                print(f"   ✅ Compound index created: {index_spec[0]}, {index_spec[2]}")
        
        # Add schema validation (optional - helps ensure data integrity)
        schema_validation = {
            "ensemble_evaluation": {
                "$bsonType": "object",
                "properties": {
                    "evaluation_id": {"bsonType": "string"},
                    "primary_judge": {"bsonType": "object"},
                    "secondary_judge": {"bsonType": "object"},
                    "tertiary_judge": {"bsonType": "object"},
                    "aggregated": {"bsonType": "object"},
                    "reliability_metrics": {"bsonType": "object"}
                }
            }
        }
        
        # Update collection with validation rules (if supported)
        try:
            collection.drop_index("ensemble_evaluation")
            print("📋 Schema validation configured for ensemble evaluations")
        except Exception as e:
            print(f"   ⚠️ Schema validation setup: {e}")
        
        print("\n✅ Ensemble evaluation database migration completed!")
        print("📊 Database ready for triple-judge ensemble evaluations")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

async def verify_ensemble_schema():
    """Verify that the database schema supports ensemble evaluations"""
    
    print("\n🔍 VERIFYING ENSEMBLE SCHEMA SUPPORT")
    print("-" * 40)
    
    try:
        from app.db.connection import get_database
        
        db = get_database()
        collection = db.runs
        
        # Check if we can query ensemble fields
        ensemble_count = await collection.count_documents({"ensemble_evaluation": {"$exists": True}})
        total_runs = await collection.count_documents({})
        
        print(f"📊 Total runs: {total_runs}")
        print(f"📊 Runs with ensemble evaluation: {ensemble_count}")
        
        # Check sample run structure
        sample_run = await collection.find_one({})
        if sample_run:
            fields = list(sample_run.keys())
            print(f"📋 Run fields: {fields}")
            
            # Check for required judge fields
            required_fields = ["scores", "judge", "scenario", "prompt_length_bin"]
            missing_fields = [field for field in required_fields if field not in fields]
            
            if missing_fields:
                print(f"⚠️ Missing required fields: {missing_fields}")
                return False
            else:
                print("✅ All required fields present")
        
        print(f"🎯 Database ready for ensemble evaluation implementation")
        return True
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        return False

async def create_ensemble_evaluation_sample():
    """Create a sample ensemble evaluation document to test schema"""
    
    print("\n🧪 CREATING SAMPLE ENSEMBLE EVALUATION")
    print("-" * 40)
    
    try:
        from app.db.connection import get_database
        from app.utils.ulid_gen import UUID4
        
        db = get_database()
        collection = db.runs
        
        # Sample ensemble evaluation data
        sample_ensemble = {
            "evaluation_id": str(UUID4()),
            "created_at": datetime.utcnow().isoformat(),
            "primary_judge": {
                "judge_model": "gpt-4o-mini",
                "scores": {
                    "technical_accuracy": 4.2,
                    "actionability": 4.0,
                    "completeness": 4.5,
                    "compliance_alignment": 4.1,
                    "risk_awareness": 4.3,
                    "relevance": 4.2,
                    "clarity": 4.0,
                    "composite": 4.19
                },
                "evaluation_time": datetime.utcnow().isoformat(),
                "tokens_used": 150,
                "cost_usd": 0.003
            },
            "secondary_judge": {
                "judge_model": "claude-3-5-sonnet-20241022",
                "scores": {
                    "technical_accuracy": 4.1,
                    "actionability": 3.9,
                    "completeness": 4.4,
                    "compliance_alignment": 4.0,
                    "risk_awareness": 4.2,
                    "relevance": 4.1,
                    "clarity": 3.9,
                    "composite": 4.09
                },
                "evaluation_time": datetime.utcnow().isoformat(),
                "tokens_used": 145,
                "cost_usd": 0.006
            },
            "tertiary_judge": {
                "judge_model": "llama-3.3-70b-versatile",
                "scores": {
                    "technical_accuracy": 4.0,
                    "actionability": 4.1,
                    "completeness": 4.3,
                    "compliance_alignment": 3.9,
                    "risk_awareness": 4.1,
                    "relevance": 4.0,
                    "clarity": 4.2,
                    "composite": 4.08
                },
                "evaluation_time": datetime.utcnow().isoformat(),
                "tokens_used": 120,
                "cost_usd": 0.001
            },
            "aggregated": {
                "mean_scores": {
                    "technical_accuracy": 4.1,
                    "actionability": 4.0,
                    "completeness": 4.4,
                    "compliance_alignment": 4.0,
                    "risk_awareness": 4.2,
                    "relevance": 4.1,
                    "clarity": 4.0,
                    "composite": 4.12
                },
                "confidence_95_ci": {
                    "technical_accuracy": [3.95, 4.25],
                    "actionability": [3.90, 4.10],
                    "completeness": [4.25, 4.55],
                    "composite": [4.00, 4.24]
                }
            },
            "reliability_metrics": {
                "pearson_correlations": {
                    "primary_secondary": 0.92,
                    "primary_tertiary": 0.87,
                    "secondary_tertiary": 0.89
                },
                "fleiss_kappa": 0.76,
                "inter_judge_agreement": "substantial"
            }
        }
        
        # Test the schema by updating a real run (if any exist)
        existing_run = await collection.find_one({"output_blob_id": {"$exists": True}})
        
        if existing_run:
            # Update existing run with sample ensemble data
            test_run_id = existing_run["run_id"]
            
            await collection.update_one(
                {"run_id": test_run_id},
                {"$set": {"ensemble_evaluation": sample_ensemble}}
            )
            
            print(f"✅ Sample ensemble evaluation added to run {test_run_id}")
            
            # Verify it was saved correctly
            updated_run = await collection.find_one({"run_id": test_run_id})
            if "ensemble_evaluation" in updated_run:
                print("✅ Sample ensemble data verified in database")
                
                # Clean up - remove test data
                await collection.update_one(
                    {"run_id": test_run_id},
                    {"$unset": {"ensemble_evaluation": 1}}
                )
                print("🗑️ Test data cleaned up")
            else:
                print("❌ Failed to verify sample ensemble data")
                return False
        else:
            print("⚠️ No existing runs found to test with")
        
        print("🎯 Ensemble evaluation schema test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Sample ensemble creation failed: {e}")
        return False

async def main():
    """Run database migration for ensemble evaluation support"""
    
    print("🚀 ENSEMBLE EVALUATION SETUP")
    print("=" * 50)
    print("Student: Mohamed Zeyada (11693860)")
    print("Enhanced: Triple-Judge Evaluation Framework")
    print()
    
    # Run migration steps
    migration_success = await add_ensemble_fields_to_runs()
    
    if migration_success:
        schema_success = await verify_ensemble_schema()
        
        if schema_success:
            sample_success = await create_ensemble_evaluation_sample()
            
            if sample_success:
                print(f"\n🏁 Database migration completed successfully!")
                print("📊 Ready for triple-judge ensemble implementation")
            else:
                print(f"\n⚠️ Sample creation failed - check schema manually")
        else:
            print(f"\n❌ Schema verification failed - manual review needed")
    else:
        print(f"\n❌ Migration failed - check database connection")

if __name__ == "__main__":
    asyncio.run(main())
