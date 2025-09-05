#!/usr/bin/env python3
"""Quick seed script to add minimal test data for CyberCQBench"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.connection import connect_to_mongo, get_database
from app.models import LengthBin, Prompt, SafetyTag, ScenarioType, SourceType
from app.utils.ulid_gen import generate_ulid


async def seed_minimal_data():
    """Add minimal test data"""

    # Connect to database
    await connect_to_mongo()
    db = get_database()

    # Clear existing data
    await db.prompts.delete_many({})
    await db.runs.delete_many({})
    await db.output_blobs.delete_many({})

    print("Cleared existing data")

    # Create test prompts
    test_prompts = [
        {
            "text": "Analyze this security incident: A user reported suspicious email attachments. The email came from an external domain mimicking our company domain. What are the immediate steps a SOC analyst should take?",
            "scenario": ScenarioType.SOC_INCIDENT,
            "length_bin": LengthBin.M,
            "complexity": 3,
        },
        {
            "text": "Create a compliance mapping for GDPR Article 32 (Security of processing) requirements. Include technical and organizational measures that should be implemented.",
            "scenario": ScenarioType.GRC_MAPPING,
            "length_bin": LengthBin.L,
            "complexity": 4,
        },
        {
            "text": "Summarize the latest threat intelligence: APT29 has been observed using new PowerShell-based backdoors targeting government entities. Provide actionable intelligence for SOC teams.",
            "scenario": ScenarioType.CTI_SUMMARY,
            "length_bin": LengthBin.S,
            "complexity": 3,
        },
        {
            "text": "A firewall detected multiple failed login attempts from IP 192.168.1.100 targeting our web server. Investigate and recommend response actions.",
            "scenario": ScenarioType.SOC_INCIDENT,
            "length_bin": LengthBin.S,
            "complexity": 2,
        },
        {
            "text": "Develop a comprehensive incident response plan for a ransomware attack scenario. Include containment, eradication, recovery phases and communication protocols with stakeholders.",
            "scenario": ScenarioType.SOC_INCIDENT,
            "length_bin": LengthBin.XL,
            "complexity": 5,
        },
    ]

    prompt_ids = []
    for prompt_data in test_prompts:
        prompt = Prompt(
            prompt_id=generate_ulid(),
            text=prompt_data["text"],
            source=SourceType.CURATED,
            scenario=prompt_data["scenario"],
            length_bin=prompt_data["length_bin"],
            complexity=prompt_data["complexity"],
            safety_tag=SafetyTag.SAFE_DOC,
            dataset_version="test_v1",
            created_at=datetime.utcnow(),
        )

        await db.prompts.insert_one(prompt.model_dump())
        prompt_ids.append(prompt.prompt_id)
        print(f"Created prompt: {prompt.scenario.value} - {prompt.length_bin.value}")

    print(f"✅ Seeded {len(prompt_ids)} test prompts")
    print("🚀 Ready to create experiments!")

    return prompt_ids

if __name__ == "__main__":
    asyncio.run(seed_minimal_data())
