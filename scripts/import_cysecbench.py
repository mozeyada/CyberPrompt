#!/usr/bin/env python3
"""
CySecBench Data Import Script
Maps CySecBench categories to research scenarios and imports with length metadata
"""

import asyncio
import csv
import re
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.utils.ulid import generate_ulid

# Category mapping to research scenarios
CATEGORY_MAPPING = {
    # SOC_INCIDENT: Incident response, network security, malware analysis
    "Network Attacks": "SOC_INCIDENT",
    "Intrusion Techniques": "SOC_INCIDENT",
    "Malware Attacks": "SOC_INCIDENT",

    # CTI_SUMMARY: Threat intelligence, evasion, emerging threats
    "Evasion Techniques": "CTI_SUMMARY",
    "IoT Attacks": "CTI_SUMMARY",
    "Hardware Attacks": "CTI_SUMMARY",

    # GRC_MAPPING: Compliance, governance, risk management
    "Cloud Attacks": "GRC_MAPPING",
    "Web Application Attacks": "GRC_MAPPING",
    "Control System Attacks": "GRC_MAPPING",
    "Cryptographic Attacks": "GRC_MAPPING",
}

def calculate_length_bin(text: str) -> str:
    """Calculate length bin for research analysis"""
    word_count = len(text.split())
    if word_count <= 15:
        return "short"
    elif word_count <= 30:
        return "medium"
    else:
        return "long"

def clean_prompt_text(text: str) -> str:
    """Clean and normalize prompt text"""
    # Remove extra whitespace and normalize
    text = re.sub(r"\s+", " ", text.strip())
    # Remove quotes if they wrap the entire text
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    return text

async def import_cysecbench_data():
    """Import CySecBench data mapped to research scenarios (subset for research)"""

    # Research configuration - balanced dataset for academic analysis
    MAX_PER_SCENARIO = 150  # 450 total prompts for research
    TARGET_PER_LENGTH = 50  # 50 per length bin per scenario

    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    collection = db.prompts

    # Path to CySecBench CSV
    csv_path = Path("cysecbench-data/Dataset/Full dataset/cysecbench.csv")

    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        return

    # Track counts per scenario and length bin
    scenario_counts = {scenario: {"short": 0, "medium": 0, "long": 0} for scenario in ["SOC_INCIDENT", "CTI_SUMMARY", "GRC_MAPPING"]}
    imported_count = 0
    skipped_count = 0

    print("Starting targeted CySecBench import for research...")
    print(f"Target: {MAX_PER_SCENARIO} prompts per scenario ({MAX_PER_SCENARIO * 3} total)")

    with open(csv_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            prompt_text = clean_prompt_text(row["Prompt"])
            category = row["Category"].strip()

            # Skip if category not in our mapping
            if category not in CATEGORY_MAPPING:
                skipped_count += 1
                continue

            scenario = CATEGORY_MAPPING[category]
            length_bin = calculate_length_bin(prompt_text)
            word_count = len(prompt_text.split())

            # Check if we've reached limits for this scenario/length combination
            if scenario_counts[scenario][length_bin] >= TARGET_PER_LENGTH:
                skipped_count += 1
                continue

            # Check if scenario is full
            scenario_total = sum(scenario_counts[scenario].values())
            if scenario_total >= MAX_PER_SCENARIO:
                skipped_count += 1
                continue

            # Create prompt document
            prompt_doc = {
                "_id": generate_ulid(),
                "text": prompt_text,
                "scenario": scenario,
                "category": category,
                "source": "CySecBench",
                "metadata": {
                    "word_count": word_count,
                    "length_bin": length_bin,
                    "original_category": category,
                    "dataset_version": "1.0",
                },
                "tags": [scenario.lower(), category.lower().replace(" ", "_")],
                "created_at": None,  # Will be set by database
                "updated_at": None,
            }

            # Insert into database
            try:
                await collection.insert_one(prompt_doc)
                scenario_counts[scenario][length_bin] += 1
                imported_count += 1

                if imported_count % 50 == 0:
                    print(f"Imported {imported_count} prompts...")

            except Exception as e:
                print(f"Error inserting prompt: {e}")
                skipped_count += 1

    await client.close()

    print("\nImport completed!")
    print(f"Imported: {imported_count} prompts")
    print(f"Skipped: {skipped_count} prompts")

    # Print detailed distribution
    print("\nResearch dataset distribution:")
    for scenario in ["SOC_INCIDENT", "CTI_SUMMARY", "GRC_MAPPING"]:
        total = sum(scenario_counts[scenario].values())
        print(f"  {scenario}: {total} prompts")
        for length_bin in ["short", "medium", "long"]:
            count = scenario_counts[scenario][length_bin]
            print(f"    {length_bin}: {count} prompts")

    # Verify in database
    print("\nDatabase verification:")
    for scenario in ["SOC_INCIDENT", "CTI_SUMMARY", "GRC_MAPPING"]:
        count = await collection.count_documents({"scenario": scenario})
        print(f"  {scenario}: {count} prompts")

    await client.close()

if __name__ == "__main__":
    asyncio.run(import_cysecbench_data())
