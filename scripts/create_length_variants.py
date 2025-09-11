#!/usr/bin/env python3
"""
Create realistic length variants from existing short prompts.

Takes short CySecBench prompts and creates Medium/Long variants
suitable for SOC/GRC research analysis.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    import tiktoken
except ImportError:
    print("❌ Missing dependencies")
    sys.exit(1)


def calculate_tokens(text: str) -> int:
    """Calculate tokens using tiktoken"""
    try:
        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))
    except Exception:
        return int(len(text.split()) * 1.3)


def classify_tokens(token_count: int) -> str:
    """Classify tokens into length bins"""
    if token_count <= 300:
        return "S"
    elif 301 <= token_count <= 800:
        return "M"
    else:
        return "L"


def create_medium_variant(short_prompt: str, category: str) -> str:
    """Create medium-length SOC/GRC variant (400-600 tokens)"""
    
    # SOC Incident templates
    soc_template = f"""SOC Incident Analysis Required:

Alert Details:
- Event Type: {category.replace('_', ' ').title()}
- Severity: High
- First Detected: 2024-01-15 09:30 UTC
- Status: Active Investigation

Technical Context:
{short_prompt}

Environment Details:
- Affected Systems: Multiple workstations and servers
- Network Segments: Corporate LAN, DMZ, Cloud Infrastructure  
- User Impact: Potential data exposure and service disruption
- Business Context: Critical operations may be affected

Investigation Requirements:
1. Immediate threat containment and isolation procedures
2. Evidence collection and forensic analysis protocols
3. Impact assessment across all affected business units
4. Communication plan for stakeholders and management
5. Recovery procedures and business continuity measures

Compliance Considerations:
- Regulatory reporting requirements (GDPR, HIPAA, SOX)
- Legal hold and evidence preservation protocols
- Third-party notification obligations
- Audit trail documentation standards

Provide comprehensive incident response analysis including threat classification, business impact assessment, containment strategy, investigation steps, and reporting requirements."""

    # GRC Compliance templates  
    grc_template = f"""GRC Compliance Assessment Required:

Control Evaluation Context:
{short_prompt}

Regulatory Framework Alignment:
- Primary Standards: NIST CSF, ISO 27001, SOC 2 Type II
- Industry Requirements: PCI DSS, HIPAA, GDPR compliance
- Audit Timeline: Quarterly assessments with annual certification

Current Security Posture:
- Identity and Access Management with role-based controls
- Multi-factor authentication deployed enterprise-wide
- Encryption at rest and in transit for all sensitive data
- Network segmentation between production and development
- Continuous monitoring with SIEM and EDR solutions

Risk Assessment Scope:
- Technical controls effectiveness evaluation
- Process maturity and documentation review
- Staff training and awareness program assessment
- Vendor risk management and third-party assessments
- Incident response capability and testing procedures

Deliverables Required:
1. Gap analysis against applicable regulatory frameworks
2. Risk assessment with likelihood and impact ratings
3. Remediation roadmap with prioritized action items
4. Cost-benefit analysis for recommended improvements
5. Executive summary for board and senior management

Provide detailed compliance mapping analysis, risk evaluation, and strategic recommendations."""

    # Choose template based on content
    if any(word in short_prompt.lower() for word in ['incident', 'attack', 'malware', 'breach', 'threat']):
        return soc_template
    else:
        return grc_template


def create_long_variant(short_prompt: str, category: str) -> str:
    """Create long comprehensive variant (1000+ tokens)"""
    
    return f"""Comprehensive Cybersecurity Analysis and Strategic Response Framework

Executive Summary:
This analysis addresses critical cybersecurity concerns related to {category.replace('_', ' ').lower()} within our enterprise environment. The following assessment provides detailed technical analysis, business impact evaluation, and strategic recommendations for organizational resilience.

Technical Analysis Context:
{short_prompt}

Threat Landscape Assessment:
The current threat environment presents significant challenges across multiple attack vectors. Advanced persistent threats (APTs) continue to evolve, leveraging sophisticated techniques including zero-day exploits, supply chain compromises, and social engineering campaigns. Our analysis indicates increased targeting of critical infrastructure, financial services, and healthcare organizations.

Key threat actors include:
- Nation-state sponsored groups with advanced capabilities
- Cybercriminal organizations focused on financial gain
- Insider threats from privileged users and contractors
- Hacktivist groups targeting specific industries or causes

Environmental Context and Infrastructure:
Our enterprise environment consists of hybrid cloud infrastructure spanning multiple geographic regions. Critical assets include:
- Production systems hosting customer-facing applications
- Database servers containing sensitive financial and personal data
- Network infrastructure including firewalls, routers, and switches
- Endpoint devices across corporate, remote, and mobile environments
- Third-party integrations and supply chain dependencies

Current security architecture implements defense-in-depth principles with multiple layers of protection. However, evolving threat landscapes require continuous assessment and improvement of security controls.

Risk Assessment and Business Impact Analysis:
The potential impact of security incidents extends beyond immediate technical concerns to encompass:

Financial Impact:
- Direct costs including incident response, forensic analysis, and system recovery
- Regulatory fines and legal expenses from compliance violations
- Business disruption and lost revenue during service outages
- Long-term reputation damage affecting customer trust and market position

Operational Impact:
- Service availability and performance degradation
- Data integrity concerns affecting business decision-making
- Compliance violations resulting in regulatory scrutiny
- Supply chain disruptions affecting partner relationships

Strategic Recommendations:

1. Technical Controls Enhancement:
   - Implement advanced threat detection and response capabilities
   - Enhance network segmentation and zero-trust architecture
   - Deploy behavioral analytics and machine learning-based detection
   - Strengthen endpoint protection with next-generation antivirus solutions

2. Process and Governance Improvements:
   - Establish comprehensive incident response procedures
   - Implement regular security awareness training programs
   - Develop vendor risk management and third-party assessment protocols
   - Create business continuity and disaster recovery plans

3. Compliance and Risk Management:
   - Align security controls with applicable regulatory frameworks
   - Implement continuous compliance monitoring and reporting
   - Establish risk appetite statements and tolerance levels
   - Develop metrics and key performance indicators for security effectiveness

4. Organizational Capabilities:
   - Invest in security team training and professional development
   - Establish threat intelligence sharing and analysis capabilities
   - Implement security orchestration and automated response tools
   - Create executive dashboards for security posture visibility

Implementation Roadmap:
Phase 1 (0-3 months): Critical security gaps and immediate threat mitigation
Phase 2 (3-6 months): Process improvements and compliance alignment
Phase 3 (6-12 months): Advanced capabilities and strategic initiatives
Phase 4 (12+ months): Continuous improvement and maturity enhancement

Budget and Resource Considerations:
Implementation requires significant investment in technology, personnel, and training. Recommended budget allocation includes capital expenditures for security tools and infrastructure, operational expenses for managed services and consulting, and human resources for additional security staff and training programs.

Conclusion:
Addressing these cybersecurity challenges requires comprehensive approach combining technical controls, process improvements, and organizational capabilities. Success depends on executive leadership commitment, adequate resource allocation, and continuous adaptation to evolving threat landscapes.

The recommended framework provides foundation for enhanced security posture while supporting business objectives and regulatory compliance requirements. Regular assessment and adjustment ensure continued effectiveness against emerging threats and changing business requirements."""


async def create_variants():
    """Create medium and long variants from existing short prompts"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    # Get all short prompts
    cursor = collection.find({"length_bin": "S"})
    short_prompts = await cursor.to_list(length=None)
    
    print(f"🔍 Found {len(short_prompts)} short prompts")
    print("📝 Creating medium and long variants...")
    
    created = {"medium": 0, "long": 0}
    
    # Take first 50 short prompts and create variants
    for i, prompt in enumerate(short_prompts[:50]):
        try:
            base_text = prompt.get("text", "")
            category = prompt.get("category", "Security Analysis")
            scenario = prompt.get("scenario", "SOC_INCIDENT")
            
            # Create medium variant
            medium_text = create_medium_variant(base_text, category)
            medium_tokens = calculate_tokens(medium_text)
            medium_bin = classify_tokens(medium_tokens)
            
            medium_prompt = {
                "prompt_id": f"medium_{prompt.get('prompt_id', f'gen_{i}')}",
                "text": medium_text,
                "source": prompt.get("source"),
                "scenario": scenario,
                "length_bin": medium_bin,
                "token_count": medium_tokens,
                "category": category,
                "prompt_type": "static",
                "safety_tag": "SAFE_DOC",
                "metadata": {"variant_of": prompt.get("prompt_id"), "variant_type": "medium"}
            }
            
            # Create long variant
            long_text = create_long_variant(base_text, category)
            long_tokens = calculate_tokens(long_text)
            long_bin = classify_tokens(long_tokens)
            
            long_prompt = {
                "prompt_id": f"long_{prompt.get('prompt_id', f'gen_{i}')}",
                "text": long_text,
                "source": prompt.get("source"),
                "scenario": scenario,
                "length_bin": long_bin,
                "token_count": long_tokens,
                "category": category,
                "prompt_type": "static",
                "safety_tag": "SAFE_DOC",
                "metadata": {"variant_of": prompt.get("prompt_id"), "variant_type": "long"}
            }
            
            # Insert variants
            await collection.insert_one(medium_prompt)
            await collection.insert_one(long_prompt)
            
            created["medium"] += 1
            created["long"] += 1
            
            if i < 5:  # Show first few
                print(f"✅ Created variants for {prompt.get('prompt_id', 'unknown')}")
                print(f"   Medium: {medium_tokens} tokens → {medium_bin}")
                print(f"   Long: {long_tokens} tokens → {long_bin}")
            
        except Exception as e:
            print(f"❌ Error creating variants for prompt {i}: {e}")
    
    print(f"\n🎉 Created {created['medium']} medium and {created['long']} long variants")
    
    # Show new distribution
    cursor = collection.aggregate([
        {"$group": {"_id": "$length_bin", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ])
    
    print("\n📏 New length distribution:")
    async for result in cursor:
        bin_name = result["_id"]
        count = result["count"]
        print(f"  {bin_name}: {count} prompts")
    
    client.close()


if __name__ == "__main__":
    print("🚀 Creating realistic length variants...")
    asyncio.run(create_variants())
    print("✅ Done!")