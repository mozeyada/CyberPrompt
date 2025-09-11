#!/usr/bin/env python3
"""
Create academic length variants from existing CySecBench prompts.

Following the research methodology: "Craft short, medium, and long prompt variants"
This creates controlled length variations while maintaining task consistency.
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
    """Create medium-length SOC incident variant (400-600 tokens)"""
    
    # Map categories to SOC scenarios
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
    
    return f"""SOC Incident Analysis Required:

Alert Classification: {category}
Incident Type: {scenario_type.title()}
Severity Level: High
Detection Time: 2024-01-15 14:30 UTC
Status: Active Investigation

Technical Question:
{short_prompt}

Organizational Context:
- Environment: Enterprise hybrid cloud infrastructure
- Affected Systems: Production servers, user workstations, network devices
- Business Impact: Potential service disruption and data exposure
- Compliance Requirements: SOC 2, ISO 27001, industry-specific regulations

Investigation Requirements:
1. Immediate threat containment and system isolation procedures
2. Evidence collection following forensic best practices
3. Impact assessment across all potentially affected business units
4. Stakeholder communication plan including management and legal teams
5. Recovery procedures and business continuity activation

Compliance Considerations:
- Regulatory notification requirements (GDPR, HIPAA, sector-specific)
- Legal hold procedures for evidence preservation
- Third-party vendor notification obligations
- Audit trail documentation and chain of custody

Deliverables Required:
Provide comprehensive incident response analysis including threat classification, technical analysis of the attack vector, business impact assessment, immediate containment strategy, detailed investigation steps, evidence collection procedures, and regulatory compliance recommendations."""


def create_long_variant(short_prompt: str, category: str) -> str:
    """Create long comprehensive variant (1000+ tokens)"""
    
    return f"""Comprehensive Cybersecurity Analysis and Strategic Response Framework

Executive Summary:
This analysis addresses a critical cybersecurity incident involving {(category or 'security issues').lower()} within our enterprise environment. The following comprehensive assessment provides detailed technical analysis, business impact evaluation, regulatory compliance considerations, and strategic recommendations for organizational resilience and recovery.

Incident Classification and Context:
Primary Category: {category}
Threat Vector Analysis: {short_prompt}

Current Threat Landscape Assessment:
The contemporary cybersecurity threat environment presents unprecedented challenges across multiple attack vectors and threat actor categories. Advanced persistent threats (APTs) continue to evolve their tactics, techniques, and procedures (TTPs), leveraging sophisticated methodologies including zero-day exploits, supply chain compromises, social engineering campaigns, and living-off-the-land techniques.

Key threat actors currently active in this domain include:
- Nation-state sponsored groups with advanced capabilities and significant resources
- Cybercriminal organizations focused on financial gain through ransomware and data theft
- Insider threats from privileged users, contractors, and disgruntled employees
- Hacktivist groups targeting specific industries, organizations, or political causes
- Opportunistic attackers exploiting publicly disclosed vulnerabilities

Organizational Environment and Infrastructure Context:
Our enterprise environment consists of a complex hybrid cloud infrastructure spanning multiple geographic regions and business units. Critical digital assets include:

Production Systems:
- Customer-facing web applications and mobile platforms
- Core business applications supporting daily operations
- Database servers containing sensitive financial, personal, and proprietary data
- API gateways and microservices architecture components

Network Infrastructure:
- Next-generation firewalls with intrusion prevention capabilities
- Network segmentation between production, development, and administrative zones
- Software-defined networking (SDN) and network function virtualization (NFV)
- Wireless networks supporting corporate and guest access

Endpoint Environment:
- Corporate workstations and laptops across multiple operating systems
- Mobile devices including smartphones and tablets with BYOD policies
- Internet of Things (IoT) devices and operational technology (OT) systems
- Remote access solutions supporting distributed workforce

Third-Party Integrations:
- Cloud service providers (AWS, Azure, Google Cloud Platform)
- Software-as-a-Service (SaaS) applications and platforms
- Managed security service providers (MSSPs) and security operations centers
- Supply chain partners and vendor ecosystem dependencies

Risk Assessment and Business Impact Analysis:
The potential impact of this security incident extends far beyond immediate technical concerns to encompass comprehensive business, financial, operational, and strategic implications:

Financial Impact Assessment:
- Direct incident response costs including forensic analysis, system recovery, and remediation
- Regulatory fines and penalties from compliance violations and data protection breaches
- Legal expenses related to litigation, regulatory proceedings, and customer notifications
- Business disruption costs including lost revenue during service outages
- Long-term reputation damage affecting customer trust, market position, and competitive advantage
- Increased insurance premiums and potential coverage limitations for future incidents

Operational Impact Evaluation:
- Service availability degradation affecting customer experience and satisfaction
- Data integrity concerns impacting business decision-making and operational efficiency
- Compliance violations resulting in regulatory scrutiny and additional oversight requirements
- Supply chain disruptions affecting partner relationships and vendor management
- Employee productivity losses due to system unavailability and security restrictions

Strategic Recommendations and Implementation Framework:

Phase 1: Immediate Response and Containment (0-24 hours)
- Activate incident response team and establish command center operations
- Implement immediate containment measures to prevent lateral movement
- Preserve evidence and establish forensic imaging procedures
- Initiate stakeholder communication protocols and regulatory notifications
- Deploy additional monitoring and detection capabilities

Phase 2: Investigation and Analysis (1-7 days)
- Conduct comprehensive forensic analysis of affected systems
- Perform threat hunting activities to identify additional compromised assets
- Analyze attack vectors, tactics, techniques, and procedures (TTPs)
- Assess data exposure and potential exfiltration activities
- Coordinate with law enforcement and regulatory authorities as required

Phase 3: Recovery and Restoration (1-4 weeks)
- Implement system hardening and security control enhancements
- Restore services following validated clean recovery procedures
- Conduct comprehensive security testing and validation
- Update incident response procedures based on lessons learned
- Implement additional monitoring and detection capabilities

Phase 4: Long-term Improvement and Resilience (1-6 months)
- Conduct comprehensive security architecture review and enhancement
- Implement advanced threat detection and response capabilities
- Enhance security awareness training and organizational culture
- Establish continuous improvement processes for security operations
- Develop strategic partnerships with security vendors and service providers

Regulatory Compliance and Legal Considerations:
This incident requires careful consideration of multiple regulatory frameworks and legal obligations:

Data Protection Regulations:
- General Data Protection Regulation (GDPR) notification and reporting requirements
- California Consumer Privacy Act (CCPA) and state-specific data breach laws
- Health Insurance Portability and Accountability Act (HIPAA) for healthcare data
- Payment Card Industry Data Security Standard (PCI DSS) for payment information

Industry-Specific Requirements:
- Financial services regulations (SOX, GLBA, Basel III)
- Critical infrastructure protection standards (NERC CIP, TSA directives)
- Government contractor requirements (DFARS, NIST 800-171)
- International standards and frameworks (ISO 27001, NIST Cybersecurity Framework)

Conclusion and Strategic Outlook:
Addressing this cybersecurity incident requires a comprehensive, multi-faceted approach that combines immediate tactical response with long-term strategic improvements. Success depends on executive leadership commitment, adequate resource allocation, cross-functional collaboration, and continuous adaptation to evolving threat landscapes.

The recommended framework provides a foundation for enhanced security posture while supporting business objectives, regulatory compliance requirements, and stakeholder expectations. Regular assessment and adjustment ensure continued effectiveness against emerging threats and changing business requirements, ultimately building organizational resilience and competitive advantage in an increasingly complex digital environment."""


async def create_variants_for_existing_prompts():
    """Create medium and long variants for existing prompts in database"""
    
    # Connect to MongoDB
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
    mongo_db = os.getenv("MONGO_DB", "genai_bench")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db.prompts
    
    # First, clean up any existing variants
    print("🧹 Cleaning up existing variants...")
    delete_result = await collection.delete_many({"metadata.variant_of": {"$exists": True}})
    print(f"   Deleted {delete_result.deleted_count} existing variants")
    
    # Get ONLY original prompts (no variant_of field)
    cursor = collection.find({
        "metadata.variant_of": {"$exists": False},
        "source": {"$ne": "CURATED"}
    })
    original_prompts = await cursor.to_list(length=None)
    
    print(f"🔍 Found {len(original_prompts)} original prompts to expand")
    print("📝 Creating academic length variants...")
    
    created = {"medium": 0, "long": 0}
    
    # Create variants for ALL original prompts
    for i, prompt in enumerate(original_prompts):
        try:
            base_text = prompt.get("text", "")
            category = prompt.get("category") or "Security Analysis"
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
                "metadata": {
                    "variant_of": prompt.get("prompt_id"), 
                    "variant_type": "medium",
                    "expansion_method": "academic_soc_context"
                }
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
                "metadata": {
                    "variant_of": prompt.get("prompt_id"), 
                    "variant_type": "long",
                    "expansion_method": "academic_comprehensive_analysis"
                }
            }
            
            # Insert variants (skip if already exists)
            try:
                await collection.insert_one(medium_prompt)
                created["medium"] += 1
            except Exception as e:
                if "duplicate key" not in str(e):
                    raise e
            
            try:
                await collection.insert_one(long_prompt)
                created["long"] += 1
            except Exception as e:
                if "duplicate key" not in str(e):
                    raise e
            
            # Counters moved to insert blocks above
            
            if i < 3:  # Show first few
                print(f"✅ Created variants for {prompt.get('prompt_id', 'unknown')}")
                print(f"   Original: {calculate_tokens(base_text)} tokens → S")
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
    print("🚀 Creating academic length variants...")
    print("Following methodology: 'Craft short, medium, and long prompt variants'")
    asyncio.run(create_variants_for_existing_prompts())
    print("✅ Academic variants created successfully!")