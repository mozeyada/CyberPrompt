#!/usr/bin/env python3
"""
Generate Adaptive Prompts for RQ2 Research

Creates adaptive prompts from SOC/GRC documents using Groq API.
This validates RQ2: Can adaptive benchmarking improve coverage vs static datasets?

Usage:
    python scripts/generate_adaptive_prompts.py --count 50
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.services.groq_client import GroqClient, GROQ_MODELS
from app.utils.token_classification import get_token_count_and_bin
from app.utils.ulid_gen import generate_ulid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_policy_documents(db):
    """Get actual policy documents from database for research validation."""
    cursor = db.documents.find({"source_type": {"$in": ["GRC_POLICY", "CTI_FEED"]}})
    documents = await cursor.to_list(length=None)
    
    if not documents:
        logger.warning("No policy documents found. Using research-grade samples.")
        # Fallback to research-grade samples for validation
        return {
            "nist_framework": """
            NIST CYBERSECURITY FRAMEWORK 1.1
            
            IDENTIFY (ID)
            ID.AM-1: Physical devices and systems within the organization are inventoried
            ID.AM-2: Software platforms and applications within the organization are inventoried
            ID.GV-1: Organizational cybersecurity policy is established and communicated
            
            PROTECT (PR)
            PR.AC-1: Identities and credentials are issued, managed, verified, revoked, and audited
            PR.DS-1: Data-at-rest is protected
            PR.PT-1: Audit/log records are determined, documented, implemented, and reviewed
            
            DETECT (DE)
            DE.AE-1: A baseline of network operations and expected data flows is established
            DE.CM-1: The network is monitored to detect potential cybersecurity events
            
            RESPOND (RS)
            RS.RP-1: Response plan is executed during or after an incident
            RS.CO-2: Incidents are reported consistent with established criteria
            
            RECOVER (RC)
            RC.RP-1: Recovery plan is executed during or after a cybersecurity incident
            """,
            
            "iso27001_controls": """
            ISO/IEC 27001:2022 ANNEX A CONTROLS
            
            A.5 ORGANIZATIONAL CONTROLS
            A.5.1 Policies for information security
            A.5.8 Information security in project management
            A.5.15 Access control
            
            A.8 TECHNOLOGY CONTROLS  
            A.8.2 Privileged access rights
            A.8.9 Configuration management
            A.8.23 Web filtering
            A.8.26 Application security requirements
            
            Implementation requires:
            - Risk assessment methodology
            - Statement of Applicability (SoA)
            - Risk treatment plan
            - Incident response procedures
            - Business continuity planning
            """,
            
            "mitre_attack": """
            MITRE ATT&CK FRAMEWORK - ENTERPRISE TACTICS
            
            TA0001 Initial Access
            T1566 Phishing: Adversaries may send phishing messages to gain access
            T1190 Exploit Public-Facing Application
            
            TA0003 Persistence
            T1053 Scheduled Task/Job
            T1547 Boot or Logon Autostart Execution
            
            TA0004 Privilege Escalation
            T1068 Exploitation for Privilege Escalation
            T1134 Access Token Manipulation
            
            TA0005 Defense Evasion
            T1055 Process Injection
            T1027 Obfuscated Files or Information
            
            Detection and Mitigation:
            - Implement endpoint detection and response (EDR)
            - Monitor process creation events
            - Deploy application control solutions
            """
        }
    
    # Convert database documents to usable format
    policy_docs = {}
    for doc in documents:
        key = f"{doc['source_type'].lower()}_{doc['doc_id']}"
        policy_docs[key] = doc['content']
    
    return policy_docs


def create_adaptive_meta_prompt(document_text: str, task_type: str) -> str:
    """Create meta-prompt for generating SOC/GRC benchmark prompts."""
    
    return f"""You are a cybersecurity expert creating benchmark prompts for evaluating AI models in SOC/GRC operations.

DOCUMENT CONTENT:
{document_text}

TASK: Generate 4 distinct cybersecurity benchmark prompts based on this document for "{task_type}" evaluation.

REQUIREMENTS:
- Each prompt tests different SOC/GRC skills: analysis, classification, recommendations, compliance
- Prompts should be realistic scenarios that SOC analysts or GRC professionals would encounter
- Include specific cybersecurity frameworks (MITRE ATT&CK, NIST, ISO 27001)
- Vary complexity from tactical (immediate response) to strategic (policy development)
- Each prompt should be 50-200 words

FORMAT: Return exactly 4 prompts separated by "---PROMPT---" markers.

EXAMPLE OUTPUT:
---PROMPT---
[Tactical analysis prompt based on document]
---PROMPT---
[Strategic assessment prompt based on document]
---PROMPT---
[Compliance mapping prompt based on document]
---PROMPT---
[Incident response prompt based on document]"""


def parse_generated_prompts(response: str) -> list[str]:
    """Parse LLM response into individual prompt strings."""
    try:
        raw_prompts = response.split("---PROMPT---")
        
        prompts = []
        for prompt in raw_prompts:
            cleaned = prompt.strip()
            if cleaned and len(cleaned) > 30:  # Filter out empty/too short
                prompts.append(cleaned)
        
        return prompts[:4]  # Cap at 4 prompts
        
    except Exception as e:
        logger.error(f"Error parsing prompts: {e}")
        return [response.strip()] if response.strip() else []


async def generate_adaptive_prompts(count: int = 50):
    """Generate adaptive prompts for RQ2 research validation."""
    
    # Setup
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("GROQ_API_KEY not found in environment")
        return
    
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    groq_client = GroqClient(groq_api_key)
    
    logger.info(f"🚀 Generating {count} adaptive prompts for RQ2 research...")
    logger.info("Using Groq Llama-3.1-70B for cost-effective generation")
    
    # Get actual policy documents for research validation
    policy_documents = await get_policy_documents(db)
    
    if not policy_documents:
        logger.error("No policy documents available for adaptive generation")
        return
    
    # Track generation
    generated_count = 0
    scenarios = ["SOC_INCIDENT", "GRC_MAPPING", "CTI_SUMMARY"]
    doc_types = list(policy_documents.keys())
    
    for i in range(count // 4):  # 4 prompts per generation
        try:
            # Rotate through document types and scenarios
            doc_type = doc_types[i % len(doc_types)]
            scenario = scenarios[i % len(scenarios)]
            document_text = policy_documents[doc_type]
            
            # Generate prompts using Groq
            meta_prompt = create_adaptive_meta_prompt(document_text, scenario)
            
            response = await groq_client.generate(
                model=GROQ_MODELS["llama-3.1-70b"],
                prompt=meta_prompt,
                temperature=0.7,
                max_tokens=1200
            )
            
            # Parse and save prompts
            prompts = parse_generated_prompts(response)
            
            for j, prompt_text in enumerate(prompts):
                if generated_count >= count:
                    break
                
                # Calculate token classification
                token_count, length_bin = get_token_count_and_bin(prompt_text)
                
                # Create prompt document
                prompt_doc = {
                    "prompt_id": f"adaptive_{generated_count + 1:03d}",
                    "text": prompt_text,
                    "source": "adaptive",
                    "prompt_type": "adaptive",
                    "scenario": scenario,
                    "length_bin": length_bin.value,
                    "token_count": token_count,
                    "dataset_version": "adaptive",
                    "category": f"Adaptive_{doc_type}",
                    "metadata": {
                        "generation_method": "groq_llama_3.1_70b",
                        "source_document": doc_type,
                        "generation_batch": i + 1,
                        "prompt_index": j + 1,
                        "length_bin": length_bin.value,
                        "word_count": len(prompt_text.split())
                    },
                    "safety_tag": "SAFE_DOC"
                }
                
                # Insert into database
                await collection.insert_one(prompt_doc)
                generated_count += 1
                
                if generated_count % 10 == 0:
                    logger.info(f"Generated {generated_count}/{count} adaptive prompts...")
            
        except Exception as e:
            logger.error(f"Error generating batch {i}: {e}")
            continue
    
    # Summary
    logger.info(f"\n✅ Generated {generated_count} adaptive prompts!")
    
    # Verify distribution
    cursor = collection.aggregate([
        {"$match": {"source": "adaptive"}},
        {"$group": {
            "_id": {"scenario": "$scenario", "length_bin": "$length_bin"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.scenario": 1, "_id.length_bin": 1}}
    ])
    
    distribution = await cursor.to_list(length=None)
    
    logger.info("\n📊 Adaptive prompt distribution:")
    for item in distribution:
        scenario = item["_id"]["scenario"]
        length_bin = item["_id"]["length_bin"]
        count = item["count"]
        logger.info(f"  {scenario} {length_bin}: {count} prompts")
    
    # Total counts for RQ2 validation
    static_count = await collection.count_documents({"source": "static"})
    adaptive_count = await collection.count_documents({"source": "adaptive"})
    
    logger.info(f"\n🔬 RQ2 Research Dataset:")
    logger.info(f"  Static (CySecBench): {static_count} prompts")
    logger.info(f"  Adaptive (Generated): {adaptive_count} prompts")
    logger.info(f"  Ready for KL divergence validation!")
    
    client.close()


async def main():
    parser = argparse.ArgumentParser(description="Generate adaptive prompts for RQ2")
    parser.add_argument("--count", type=int, default=50, help="Number of prompts to generate")
    args = parser.parse_args()
    
    await generate_adaptive_prompts(args.count)


if __name__ == "__main__":
    asyncio.run(main())