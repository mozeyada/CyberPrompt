#!/usr/bin/env python3
"""Research-grade seed data with prompt length variants for academic analysis"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.connection import connect_to_mongo, get_database
from app.models import LengthBin, Prompt, SafetyTag, ScenarioType, SourceType
from app.utils.ulid_gen import generate_ulid


async def seed_research_data():
    """Add research-grade prompts with length variants for RQ1 analysis"""

    # Connect to database
    await connect_to_mongo()
    db = get_database()

    # Clear existing data
    await db.prompts.delete_many({})
    await db.runs.delete_many({})
    await db.output_blobs.delete_many({})

    print("Cleared existing data")

    # Base prompts for research
    base_prompts = [
        {
            "base_text": "A user reported receiving a suspicious email with an attachment named 'invoice.pdf.exe'. Analyze this incident.",
            "scenario": ScenarioType.SOC_INCIDENT,
            "complexity": 2,
        },
        {
            "base_text": "Map GDPR Article 32 requirements to technical security controls.",
            "scenario": ScenarioType.GRC_MAPPING,
            "complexity": 4,
        },
        {
            "base_text": "Summarize threat intelligence on APT29 PowerShell backdoors.",
            "scenario": ScenarioType.CTI_SUMMARY,
            "complexity": 3,
        },
    ]

    prompt_ids = []

    for base_prompt in base_prompts:
        # Create SHORT variant (≤200 words)
        short_text = create_short_variant(base_prompt["base_text"], base_prompt["scenario"])
        short_prompt = Prompt(
            prompt_id=generate_ulid(),
            text=short_text,
            source=SourceType.CURATED,
            scenario=base_prompt["scenario"],
            length_bin=LengthBin.S,
            complexity=max(1, base_prompt["complexity"] - 1),
            safety_tag=SafetyTag.SAFE_DOC,
            dataset_version="research_v1_short",
            created_at=datetime.utcnow(),
        )

        # Create MEDIUM variant (500-1000 words)
        medium_text = create_medium_variant(base_prompt["base_text"], base_prompt["scenario"])
        medium_prompt = Prompt(
            prompt_id=generate_ulid(),
            text=medium_text,
            source=SourceType.CURATED,
            scenario=base_prompt["scenario"],
            length_bin=LengthBin.M,
            complexity=base_prompt["complexity"],
            safety_tag=SafetyTag.SAFE_DOC,
            dataset_version="research_v1_medium",
            created_at=datetime.utcnow(),
        )

        # Create LONG variant (1000+ words)
        long_text = create_long_variant(base_prompt["base_text"], base_prompt["scenario"])
        long_prompt = Prompt(
            prompt_id=generate_ulid(),
            text=long_text,
            source=SourceType.CURATED,
            scenario=base_prompt["scenario"],
            length_bin=LengthBin.L,
            complexity=min(5, base_prompt["complexity"] + 1),
            safety_tag=SafetyTag.SAFE_DOC,
            dataset_version="research_v1_long",
            created_at=datetime.utcnow(),
        )

        # Insert all variants
        for prompt in [short_prompt, medium_prompt, long_prompt]:
            await db.prompts.insert_one(prompt.model_dump())
            prompt_ids.append(prompt.prompt_id)
            print(f"Created {prompt.length_bin.value} variant: {prompt.scenario.value}")

    print(f"✅ Seeded {len(prompt_ids)} research prompts with length variants")
    print("🔬 Ready for RQ1 analysis: Prompt length vs quality/cost")

    return prompt_ids

def create_short_variant(base_text: str, scenario: ScenarioType) -> str:
    """Create concise version for SHORT length bin"""

    templates = {
        ScenarioType.SOC_INCIDENT: f"{base_text} Provide immediate response steps.",
        ScenarioType.GRC_MAPPING: f"{base_text} List key technical controls.",
        ScenarioType.CTI_SUMMARY: f"{base_text} Include actionable IOCs and TTPs.",
    }

    return templates.get(scenario, f"{base_text} Provide a concise analysis.")

def create_medium_variant(base_text: str, scenario: ScenarioType) -> str:
    """Create detailed version for MEDIUM length bin"""

    additions = {
        ScenarioType.SOC_INCIDENT: """

Context: You are a SOC analyst responding to this security incident. Consider:
- Incident classification and severity assessment
- Immediate containment and isolation steps
- Evidence preservation requirements
- Investigation procedures and forensic analysis
- Stakeholder communication and escalation
- Recovery and lessons learned documentation

Provide a structured incident response including immediate actions, detailed investigation steps, and recommendations for preventing similar incidents.""",

        ScenarioType.GRC_MAPPING: """

Context: You are a GRC analyst mapping compliance requirements. Consider:
- Regulatory framework alignment (NIST, ISO 27001, GDPR)
- Risk assessment and impact analysis
- Technical and organizational control implementation
- Audit trail and documentation requirements
- Monitoring and continuous compliance validation

Provide detailed control mapping with specific implementation guidance, risk assessments, and compliance validation procedures.""",

        ScenarioType.CTI_SUMMARY: """

Context: You are a threat intelligence analyst creating actionable summaries. Consider:
- IOC extraction and validation procedures
- TTPs mapping to MITRE ATT&CK framework
- Attribution confidence levels and source reliability
- Impact assessment and targeting analysis
- Defensive recommendations and countermeasures

Provide structured threat intelligence with confidence assessments, technical details, and specific defensive measures for SOC teams.""",
    }

    return base_text + additions.get(scenario, "\n\nProvide comprehensive analysis with detailed recommendations.")

def create_long_variant(base_text: str, scenario: ScenarioType) -> str:
    """Create comprehensive version for LONG length bin"""

    comprehensive_additions = {
        ScenarioType.SOC_INCIDENT: """

COMPREHENSIVE INCIDENT RESPONSE FRAMEWORK

Background Context:
You are the lead SOC analyst for a Fortune 500 financial services company with strict regulatory requirements (SOX, PCI-DSS, GDPR, FFIEC). This incident occurred during business hours and may impact customer financial data and trading systems.

Detailed Response Requirements:

1. IMMEDIATE RESPONSE (0-1 hour):
   - Threat containment and network isolation procedures
   - Evidence preservation following chain of custody protocols
   - Initial impact assessment and business continuity evaluation
   - Stakeholder notification (CISO, Legal, Compliance, PR, Regulators)
   - Crisis management team activation

2. INVESTIGATION PHASE (1-24 hours):
   - Forensic analysis using industry-standard tools (EnCase, FTK, Volatility)
   - Timeline reconstruction and attack vector analysis
   - Root cause analysis and vulnerability assessment
   - Scope determination and data impact classification
   - Regulatory notification requirements (within 72 hours for GDPR)

3. CONTAINMENT AND ERADICATION:
   - Malware analysis and IOC extraction
   - Network segmentation and access control updates
   - System patching and vulnerability remediation
   - Threat hunting across the enterprise environment
   - Security control enhancement and monitoring improvements

4. RECOVERY AND VALIDATION:
   - System restoration from clean backups
   - Security validation and penetration testing
   - Business process restoration and validation
   - Performance monitoring and stability assessment

5. POST-INCIDENT ACTIVITIES:
   - Comprehensive incident report with executive summary
   - Lessons learned and process improvement recommendations
   - Staff training and security awareness updates
   - Regulatory compliance documentation and audit preparation
   - Insurance claim documentation and legal considerations

Consider industry frameworks (NIST Cybersecurity Framework, SANS Incident Response, ISO 27035), regulatory requirements, business continuity needs, and stakeholder communication protocols. Provide step-by-step guidance with specific tools, techniques, timeframes, and decision points.""",

        ScenarioType.GRC_MAPPING: """

COMPREHENSIVE REGULATORY COMPLIANCE MAPPING FRAMEWORK

Background Context:
You are the Chief Compliance Officer for a multinational healthcare technology company processing PHI across multiple jurisdictions. This mapping will support SOX 404 compliance, HIPAA audits, GDPR assessments, and FDA cybersecurity requirements.

Regulatory Framework Integration:

1. PRIMARY REGULATIONS:
   - GDPR (General Data Protection Regulation) - EU data protection
   - HIPAA (Health Insurance Portability and Accountability Act) - US healthcare
   - SOX (Sarbanes-Oxley Act) - Financial reporting controls
   - FDA Cybersecurity Guidelines - Medical device security
   - NIST Cybersecurity Framework - Risk management baseline
   - ISO 27001/27002 - Information security management

2. CONTROL MAPPING METHODOLOGY:
   - Map regulatory requirements to specific technical controls
   - Identify control gaps, overlaps, and optimization opportunities
   - Assess current implementation maturity using CMMI levels
   - Document evidence collection and testing procedures
   - Establish control effectiveness metrics and KPIs

3. RISK ASSESSMENT INTEGRATION:
   - Identify compliance risks and potential business impact
   - Assess likelihood using quantitative risk modeling
   - Recommend risk mitigation strategies with cost-benefit analysis
   - Define risk appetite and tolerance levels
   - Establish continuous monitoring and reporting mechanisms

4. IMPLEMENTATION ROADMAP:
   - Prioritize controls based on risk and regulatory deadlines
   - Define implementation phases with resource requirements
   - Establish project timelines and milestone deliverables
   - Identify required technology, process, and personnel changes
   - Create change management and training programs

5. AUDIT PREPARATION:
   - Develop comprehensive audit trail documentation
   - Create control testing procedures and evidence packages
   - Establish audit response protocols and stakeholder roles
   - Prepare management assertions and compliance certifications
   - Design remediation procedures for identified deficiencies

6. CONTINUOUS COMPLIANCE:
   - Implement automated compliance monitoring tools
   - Establish regular control testing and validation schedules
   - Create compliance dashboard and executive reporting
   - Design regulatory change management processes
   - Develop incident response procedures for compliance violations

Include specific control references (NIST 800-53, ISO 27002, COBIT), implementation examples with technical specifications, audit preparation checklists, and regulatory change impact assessments.""",

        ScenarioType.CTI_SUMMARY: """

COMPREHENSIVE THREAT INTELLIGENCE ANALYSIS FRAMEWORK

Background Context:
You are the Senior Threat Intelligence Analyst for a critical infrastructure organization (energy sector) with national security implications. This intelligence will inform executive briefings, operational security decisions, and government agency coordination.

Intelligence Analysis Requirements:

1. THREAT ACTOR PROFILING:
   - Attribution assessment with confidence levels (F3EAD methodology)
   - Motivation analysis (financial, espionage, disruption, ideology)
   - Capability assessment (technical sophistication, resources, persistence)
   - Historical activity patterns and campaign evolution
   - Targeting preferences and victim selection criteria
   - Operational security practices and infrastructure patterns

2. TECHNICAL ANALYSIS:
   - IOC extraction and validation (IPs, domains, file hashes, certificates)
   - TTPs mapping to MITRE ATT&CK framework with sub-techniques
   - Tool and infrastructure analysis (C2 servers, hosting providers, registrars)
   - Malware family classification and variant analysis
   - Campaign timeline reconstruction and phase identification
   - Network infrastructure relationships and shared resources

3. IMPACT ASSESSMENT:
   - Threat relevance to organizational assets and operations
   - Potential attack vectors and entry points analysis
   - Business impact scenarios (operational, financial, reputational)
   - Critical system and data targeting likelihood
   - Supply chain and third-party risk implications
   - Regulatory and compliance impact considerations

4. DEFENSIVE RECOMMENDATIONS:
   - Immediate protective measures and emergency responses
   - Detection and monitoring enhancement recommendations
   - Incident response preparation and playbook updates
   - Threat hunting queries and detection rules
   - Security control improvements and technology investments
   - Staff training and awareness program updates

5. INTELLIGENCE SHARING:
   - Government agency coordination (CISA, FBI, NSA)
   - Industry information sharing (ISAC, threat intelligence platforms)
   - International cooperation and attribution coordination
   - Private sector collaboration and vendor notifications
   - Public-private partnership engagement

6. STRATEGIC INTELLIGENCE:
   - Geopolitical context and nation-state implications
   - Industry targeting trends and campaign patterns
   - Emerging threat landscape and technology risks
   - Adversary capability development and tool evolution
   - Long-term threat forecasting and scenario planning

Provide structured intelligence following industry standards (STIX/TAXII, Diamond Model, Cyber Kill Chain) with confidence assessments using Admiralty Code, source reliability ratings, and actionable defensive measures prioritized by risk and feasibility. Include executive summary for C-suite briefings and technical appendix for SOC operations.""",
    }

    return base_text + comprehensive_additions.get(scenario, "\n\nProvide exhaustive analysis with comprehensive recommendations.")

if __name__ == "__main__":
    asyncio.run(seed_research_data())
