#!/usr/bin/env python3
"""Fix Medium variants to actually reach M length classification (301-800 tokens)"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
import tiktoken

def calculate_tokens(text: str) -> int:
    try:
        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))
    except Exception:
        return int(len(text.split()) * 1.3)

def classify_tokens(token_count: int) -> str:
    if token_count <= 300:
        return "S"
    elif 301 <= token_count <= 800:
        return "M"
    else:
        return "L"

def create_proper_medium_variant(short_prompt: str, category: str) -> str:
    """Create medium-length variant that reaches 400-600 tokens"""
    
    scenario_mapping = {
        "Cloud Attacks": "cloud infrastructure compromise",
        "Malware Attacks": "malware incident", 
        "Network Attacks": "network intrusion",
        "Web Application Attacks": "web application breach",
        "Cryptographic Attacks": "cryptographic vulnerability",
        "IoT Attacks": "IoT device compromise",
        "Control System Attacks": "industrial control system attack",
        "Hardware Attacks": "hardware security incident",
        "Intrusion Techniques": "advanced persistent threat",
        "Evasion Techniques": "security control bypass"
    }
    
    scenario_type = scenario_mapping.get(category or "Security Analysis", "security incident")
    
    return f"""**SECURITY OPERATIONS CENTER - INCIDENT ANALYSIS REQUEST**

**ALERT CLASSIFICATION**: {category}
**INCIDENT TYPE**: {scenario_type.title()}
**SEVERITY LEVEL**: High Priority
**DETECTION TIMESTAMP**: 2024-01-15 14:30:00 UTC
**INVESTIGATION STATUS**: Active - Requires Immediate Analysis
**ASSIGNED ANALYST**: SOC Tier 2 Analyst
**ESCALATION REQUIRED**: Yes - Management Notification Pending

**PRIMARY TECHNICAL QUESTION**:
{short_prompt}

**ORGANIZATIONAL CONTEXT AND ENVIRONMENT**:
- **Infrastructure**: Enterprise hybrid cloud environment spanning AWS, Azure, and on-premises data centers
- **Affected Systems**: Production web servers, database clusters, user workstations, and network infrastructure devices
- **Business Impact Assessment**: Potential service disruption affecting customer-facing applications and internal business operations
- **Compliance Framework**: Organization operates under SOC 2 Type II, ISO 27001:2013, and industry-specific regulatory requirements
- **Data Classification**: Systems contain PII, financial records, intellectual property, and regulated healthcare information

**DETAILED INVESTIGATION REQUIREMENTS**:

1. **Immediate Response Actions**:
   - Execute containment procedures to prevent lateral movement and additional system compromise
   - Implement network segmentation and traffic isolation for affected systems and network segments
   - Preserve digital evidence following established forensic procedures and chain of custody protocols
   - Document all investigative steps and findings for audit trail and legal requirements

2. **Technical Analysis Framework**:
   - Conduct comprehensive log analysis across SIEM, endpoint detection, network monitoring, and application security tools
   - Perform threat hunting activities to identify additional indicators of compromise and affected systems
   - Analyze attack vectors, tactics, techniques, and procedures using MITRE ATT&CK framework mapping
   - Assess data exposure risks and potential exfiltration activities through network traffic analysis

3. **Business Impact and Risk Assessment**:
   - Evaluate operational disruption to critical business processes and customer service delivery
   - Assess financial implications including direct costs, regulatory fines, and reputational damage
   - Review compliance obligations and regulatory notification requirements under applicable frameworks
   - Coordinate with legal, privacy, and executive teams for stakeholder communication planning

4. **Recovery and Remediation Planning**:
   - Develop system restoration procedures ensuring clean recovery from known good backups
   - Implement additional security controls and monitoring to prevent similar incidents
   - Plan phased service restoration with appropriate testing and validation procedures
   - Schedule post-incident review and lessons learned documentation for process improvement

**COMPLIANCE AND REGULATORY CONSIDERATIONS**:
- **Data Protection**: GDPR Article 33 breach notification requirements (72-hour timeline)
- **Industry Standards**: PCI DSS incident response procedures for payment card data
- **Regulatory Bodies**: Notification requirements for financial services, healthcare, and critical infrastructure sectors
- **Legal Obligations**: Evidence preservation, litigation hold procedures, and law enforcement coordination

**DELIVERABLE REQUIREMENTS**:
Provide comprehensive incident analysis including threat classification, detailed technical assessment of the attack methodology, business impact evaluation, immediate containment strategy recommendations, step-by-step investigation procedures, evidence collection and preservation protocols, and specific regulatory compliance recommendations with timeline requirements for notifications and remediation activities."""

async def fix_medium_variants():
    client = AsyncIOMotorClient('mongodb://mongo:27017')
    db = client['genai_bench']
    
    # Get all medium variants
    medium_variants = await db.prompts.find({'metadata.variant_type': 'medium'}).to_list(None)
    print(f"Found {len(medium_variants)} medium variants to fix")
    
    fixed_count = 0
    
    for variant in medium_variants:
        # Get original prompt
        original_id = variant['metadata']['variant_of']
        original = await db.prompts.find_one({'prompt_id': original_id})
        
        if not original:
            continue
            
        # Create new medium text
        new_text = create_proper_medium_variant(
            original['text'], 
            original.get('category', 'Security Analysis')
        )
        
        new_tokens = calculate_tokens(new_text)
        new_bin = classify_tokens(new_tokens)
        
        # Update the variant
        await db.prompts.update_one(
            {'_id': variant['_id']},
            {
                '$set': {
                    'text': new_text,
                    'token_count': new_tokens,
                    'length_bin': new_bin
                }
            }
        )
        
        fixed_count += 1
        
        if fixed_count <= 3:
            print(f"Fixed {variant['prompt_id']}: {new_tokens} tokens -> {new_bin}")
    
    print(f"\n✅ Fixed {fixed_count} medium variants")
    
    # Verify results
    counts = await db.prompts.aggregate([
        {'$match': {'metadata.variant_type': 'medium'}},
        {'$group': {'_id': '$length_bin', 'count': {'$sum': 1}}}
    ]).to_list(None)
    
    print("\n📊 Medium variants now classified as:")
    for c in counts:
        print(f"  {c['_id']}: {c['count']}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_medium_variants())