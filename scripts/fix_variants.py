#!/usr/bin/env python3
"""
Fix the variant mess and create proper structure:
- 330 original Short prompts
- 330 Medium variants (from Short)  
- 330 Long variants (from Short)
Total: 990 prompts
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

# Add the app directory to Python path
sys.path.append('/home/zeyada/CyberCQBench')

from app.utils.token_meter import count_tokens
from app.utils.token_classification import classify_length

async def fix_variants():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['genai_bench']
    
    print("🧹 Cleaning up variant mess...")
    
    # 1. Delete all variants, keep only originals
    result = await db.prompts.delete_many({
        'metadata.variant_of': {'$exists': True}
    })
    print(f"Deleted {result.deleted_count} variant prompts")
    
    # 2. Get all original prompts (should be ~330)
    originals = await db.prompts.find({
        'metadata.variant_of': {'$exists': False}
    }).to_list(None)
    
    print(f"Found {len(originals)} original prompts")
    
    # 3. Create proper Medium and Long variants
    medium_variants = []
    long_variants = []
    
    for orig in originals:
        # Extract base ID (remove any prefixes)
        base_id = orig['prompt_id']
        if base_id.startswith('medium_'):
            base_id = base_id[7:]  # Remove 'medium_'
        if base_id.startswith('long_'):
            base_id = base_id[5:]   # Remove 'long_'
            
        # Medium variant
        medium_text = f"""**INCIDENT CONTEXT**: A SOC analyst is investigating a security incident involving {orig['scenario'].lower()} activity. The incident was detected by automated monitoring systems and requires immediate triage and response planning.

**ORIGINAL TASK**: {orig['text']}

**ADDITIONAL REQUIREMENTS**: 
- Provide step-by-step incident response procedures
- Include relevant MITRE ATT&CK techniques if applicable  
- Consider compliance implications (ISO 27001, NIST frameworks)
- Assess potential business impact and containment strategies"""

        medium_tokens = count_tokens(medium_text, 'gpt-4')
        medium_variant = {
            'prompt_id': f'medium_{base_id}',
            'text': medium_text,
            'scenario': orig['scenario'],
            'prompt_type': orig['prompt_type'],
            'length_bin': classify_length(medium_tokens),
            'token_count': medium_tokens,
            'metadata': {
                'variant_of': orig['prompt_id'],
                'variant_type': 'medium',
                'created_by': 'academic_variant_script'
            }
        }
        medium_variants.append(medium_variant)
        
        # Long variant  
        long_text = f"""**COMPREHENSIVE SOC ANALYSIS REQUEST**

**INCIDENT CONTEXT**: A critical security incident involving {orig['scenario'].lower()} has been escalated to senior SOC analysts. This incident requires comprehensive analysis, detailed response planning, and executive reporting.

**PRIMARY TASK**: {orig['text']}

**COMPREHENSIVE ANALYSIS REQUIREMENTS**:

1. **Technical Analysis**: 
   - Detailed technical breakdown of the security event
   - Root cause analysis and attack vector identification
   - System and network impact assessment

2. **Threat Intelligence Integration**:
   - Map to relevant MITRE ATT&CK techniques and tactics
   - Identify potential threat actor TTPs (Tactics, Techniques, Procedures)
   - Assess threat landscape context and similar incidents

3. **Risk and Impact Assessment**:
   - Business impact analysis (operational, financial, reputational)
   - Data exposure and privacy implications
   - Regulatory compliance considerations (GDPR, HIPAA, PCI-DSS as applicable)

4. **Response and Containment Strategy**:
   - Immediate containment and mitigation steps
   - Evidence preservation procedures
   - Communication plan for stakeholders

5. **Compliance and Governance**:
   - Alignment with organizational security policies
   - Regulatory reporting requirements
   - Audit trail and documentation standards

6. **Lessons Learned and Recommendations**:
   - Process improvements and security control enhancements
   - Training and awareness recommendations
   - Technology and tooling gaps identified

**DELIVERABLE FORMAT**: Provide a structured executive summary suitable for CISO briefing, followed by detailed technical analysis for SOC team implementation."""

        long_tokens = count_tokens(long_text, 'gpt-4')
        long_variant = {
            'prompt_id': f'long_{base_id}',
            'text': long_text,
            'scenario': orig['scenario'],
            'prompt_type': orig['prompt_type'], 
            'length_bin': classify_length(long_tokens),
            'token_count': long_tokens,
            'metadata': {
                'variant_of': orig['prompt_id'],
                'variant_type': 'long',
                'created_by': 'academic_variant_script'
            }
        }
        long_variants.append(long_variant)
    
    # 4. Insert variants
    if medium_variants:
        await db.prompts.insert_many(medium_variants)
        print(f"✅ Created {len(medium_variants)} Medium variants")
        
    if long_variants:
        await db.prompts.insert_many(long_variants)
        print(f"✅ Created {len(long_variants)} Long variants")
    
    # 5. Verify final counts
    final_counts = await db.prompts.aggregate([
        {'$group': {'_id': '$length_bin', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]).to_list(None)
    
    total = sum(c['count'] for c in final_counts)
    print(f"\n📊 FINAL COUNTS:")
    for c in final_counts:
        print(f"  {c['_id']}: {c['count']}")
    print(f"  TOTAL: {total}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_variants())