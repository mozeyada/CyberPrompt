#!/usr/bin/env python3
"""
Seed script to populate database with sample prompts across different length bins
"""

import asyncio
import os
import sys

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.db.connection import close_mongo_connection, connect_to_mongo
from app.db.repositories import PromptRepository
from app.models import LengthBin, Prompt, SafetyTag, ScenarioType, SourceType
from app.utils.ulid_gen import generate_ulid

# Sample prompts for different scenarios and length bins
SAMPLE_PROMPTS = {
    ScenarioType.SOC_INCIDENT: {
        LengthBin.XS: [
            "Analyze this security alert: Suspicious login from IP 192.168.1.100. Provide immediate response steps.",
            "Critical malware detected on workstation. What are the containment priorities?",
        ],
        LengthBin.S: [
            """Security Alert Analysis Required:

Event: Multiple failed login attempts detected
Source IP: 203.0.113.45 (External)
Target: Domain Controller (srv-dc01.company.local)
Time: 2024-01-15 14:30-14:45 UTC
Count: 147 attempts across 23 different usernames

Provide incident classification, immediate containment steps, and evidence collection requirements.""",
        ],
        LengthBin.M: [
            """SOC Incident Response Analysis:

SIEM Alert Details:
- Event ID: INC-2024-001234
- Classification: Potential Data Exfiltration
- Severity: High
- First Detected: 2024-01-15 09:30 UTC
- Last Activity: 2024-01-15 11:45 UTC

Technical Details:
- Source: Internal workstation (10.0.2.45 - DESK-USER01)
- Destination: External server (185.199.108.153)
- Protocol: HTTPS (Port 443)
- Data Volume: 2.3 GB transferred over 2.5 hours
- User Context: john.doe@company.com (Finance Department)
- Process: chrome.exe, powershell.exe

Additional Context:
- User reported computer "running slowly" this morning
- Recent email with suspicious attachment opened yesterday
- Endpoint protection shows quarantined file: invoice_urgent.pdf.exe
- Network logs show DNS queries to multiple suspicious domains

Provide comprehensive incident analysis including threat classification, business impact assessment, containment strategy, investigation steps, and reporting requirements.""",
        ],
        LengthBin.L: [
            """Comprehensive SOC Incident Investigation Required:

Initial Alert Summary:
A sophisticated multi-stage attack has been detected across our enterprise environment. The incident began with a spear-phishing email targeting our finance department and has potentially escalated to lateral movement and data exfiltration attempts.

Timeline of Events:
- Day 1 (2024-01-14):
  * 08:45 - Spear-phishing email received by 3 finance team members
  * 09:15 - Email attachment opened by john.doe@company.com
  * 09:20 - Suspicious process execution detected (invoice_urgent.pdf.exe)
  * 10:30 - Network beaconing to external C2 server observed
  * 11:45 - Endpoint detection shows credential harvesting tools

- Day 2 (2024-01-15):
  * 07:30 - Unusual domain administrator authentication from john.doe's workstation
  * 08:15 - File access patterns suggest automated data collection
  * 09:30 - Large data transfers initiated to external IP addresses
  * 11:45 - Additional workstations showing similar infection patterns

Technical Indicators:
- Malware Hash: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
- C2 Domains: secure-updates[.]net, cloud-backup[.]org
- IP Addresses: 185.199.108.153, 203.0.113.78, 192.0.2.44
- File Paths: %TEMP%\\\\svchost32.exe, %APPDATA%\\\\Microsoft\\\\credentials.db
- Registry Keys Modified: HKLM\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run

Affected Systems:
1. DESK-USER01 (10.0.2.45) - Patient Zero, Finance Workstation
2. DESK-USER07 (10.0.2.51) - Secondary infection, HR Department
3. SRV-FILE01 (10.0.1.15) - File server with abnormal access patterns
4. SRV-DC01 (10.0.1.10) - Domain controller with suspicious authentication

Business Context:
- Finance department handles sensitive financial data and vendor payments
- Recent audit preparations mean additional sensitive documents are accessible
- Q4 earnings announcement scheduled for next week
- Critical vendor payments due this Friday

Provide a comprehensive incident response plan including threat actor attribution assessment, technical impact analysis, business impact evaluation, immediate containment and eradication steps, long-term remediation strategy, communication plan for stakeholders, evidence preservation procedures, and lessons learned for future prevention.""",
        ],
    },
    ScenarioType.CTI_SUMMARY: {
        LengthBin.XS: [
            "Summarize the latest APT29 campaign targeting healthcare organizations.",
            "Brief: New ransomware family 'BlackCrypt' analysis from recent samples.",
        ],
        LengthBin.S: [
            """CTI Analysis Request:

Recent intelligence indicates a new campaign by the Lazarus Group targeting cryptocurrency exchanges in Southeast Asia. Initial reports suggest:

- Custom malware with previously unseen TTPs
- Supply chain compromise of trading software
- Estimated $50M in cryptocurrency theft
- Active since November 2023

Provide threat landscape summary, attribution assessment, and defensive recommendations.""",
        ],
        LengthBin.M: [
            """Comprehensive Threat Intelligence Analysis Required:

Subject: Emerging APT Campaign - "Operation CloudSiphon"
Priority: High
Classification: TLP:AMBER

Executive Summary Request:
Multiple security vendors and government agencies have reported a sophisticated new APT campaign dubbed "Operation CloudSiphon." The campaign appears to be targeting cloud infrastructure and SaaS platforms across multiple sectors including technology, finance, and government.

Initial Indicators:
- First observed: October 2023
- Primary targets: Cloud service providers and managed service providers
- Geographic focus: North America and Europe
- Estimated affected organizations: 50+ confirmed, potentially hundreds more
- Data types targeted: Cloud credentials, customer data, source code repositories

Technical Analysis Needed:
- Malware family analysis (custom tools and living-off-the-land techniques)
- Attack vector assessment (supply chain, credential stuffing, API abuse)
- Infrastructure analysis (C2 servers, staging areas, exfiltration methods)
- Victimology patterns and targeting selection criteria
- Attribution assessment based on TTPs, infrastructure, and timing

Requested Deliverables:
Produce a comprehensive threat intelligence report covering threat actor profiling, technical analysis of malware and infrastructure, impact assessment across affected sectors, attribution analysis with confidence levels, defensive recommendations and hunting queries, and strategic implications for cloud security posture.""",
        ],
    },
    ScenarioType.GRC_MAPPING: {
        LengthBin.XS: [
            "Map our password policy to NIST 800-53 controls.",
            "How does our incident response align with ISO 27001 requirements?",
        ],
        LengthBin.S: [
            """GRC Compliance Mapping Exercise:

Our organization needs to demonstrate compliance with multiple frameworks for an upcoming audit:
- SOC 2 Type II (Security and Availability)
- PCI DSS Level 1
- NIST Cybersecurity Framework

Current Implementation:
- Multi-factor authentication deployed enterprise-wide
- Encryption at rest and in transit for all systems
- Quarterly vulnerability assessments
- Annual penetration testing
- Incident response team with 24/7 coverage

Provide control mapping analysis and gap assessment.""",
        ],
        LengthBin.M: [
            """Comprehensive GRC Framework Alignment Assessment:

Organization Context:
We are a mid-size financial services company processing credit card transactions and handling sensitive financial data. Our regulatory requirements include PCI DSS, SOX, GLBA, and state data protection laws. We're also pursuing SOC 2 Type II certification and want to align with NIST CSF.

Current Security Posture:
1. Identity and Access Management:
   - Active Directory with role-based access control
   - Multi-factor authentication for all privileged accounts
   - Quarterly access reviews and deprovisioning procedures
   - Privileged access management solution deployed

2. Data Protection:
   - AES-256 encryption for data at rest
   - TLS 1.3 for data in transit
   - Database encryption with key rotation
   - Data loss prevention tools monitoring egress
   - Data classification and handling procedures

3. Network Security:
   - Next-generation firewalls with IPS capabilities
   - Network segmentation between card data environment and corporate
   - Wireless networks using WPA3-Enterprise
   - VPN access with certificate-based authentication

4. Monitoring and Detection:
   - SIEM solution with 24/7 SOC monitoring
   - Endpoint detection and response platform
   - File integrity monitoring on critical systems
   - Log retention for 13 months minimum

5. Vulnerability Management:
   - Monthly vulnerability scans (internal and external)
   - Automated patch management for workstations
   - Change management process for production systems
   - Annual penetration testing by third-party firm

Provide detailed analysis mapping our current controls to PCI DSS requirements, SOC 2 Trust Service Criteria, NIST CSF subcategories, and GLBA safeguards. Include gap analysis, risk assessment of missing controls, remediation priorities with business impact consideration, and compliance roadmap with timelines.""",
        ],
    },
}


async def create_sample_prompts() -> list[Prompt]:
    """Generate sample prompts for seeding"""
    prompts = []

    for scenario, length_bins in SAMPLE_PROMPTS.items():
        for length_bin, prompt_texts in length_bins.items():
            for _i, text in enumerate(prompt_texts):
                word_count = len(text.split())
                prompt = Prompt(
                    prompt_id=generate_ulid(),
                    text=text,
                    source=SourceType.CURATED,
                    scenario=scenario,
                    length_bin=length_bin,
                    complexity=3 if length_bin in [LengthBin.M, LengthBin.L] else 2,
                    safety_tag=SafetyTag.SAFE_DOC,
                    metadata={
                        "length_bin": length_bin.value.lower(),
                        "word_count": word_count
                    }
                )
                prompts.append(prompt)

    return prompts


async def seed_database():
    """Main seeding function"""
    try:
        print("🌱 Starting database seeding...")

        # Connect to database
        await connect_to_mongo()
        print("✅ Connected to MongoDB")

        # Create repository
        prompt_repo = PromptRepository()

        # Generate sample prompts
        sample_prompts = await create_sample_prompts()
        print(f"📝 Generated {len(sample_prompts)} sample prompts")

        # Insert prompts
        imported_count = 0
        for prompt in sample_prompts:
            try:
                await prompt_repo.upsert(prompt)
                imported_count += 1
            except Exception as e:
                print(f"⚠️  Failed to insert prompt {prompt.prompt_id}: {e}")

        print(f"✅ Successfully imported {imported_count} prompts")

        # Print summary
        print("\n📊 Seeding Summary:")
        for scenario in ScenarioType:
            scenario_count = len([p for p in sample_prompts if p.scenario == scenario])
            print(f"  {scenario.value}: {scenario_count} prompts")

        print("\n🎯 Length distribution:")
        for length_bin in LengthBin:
            bin_count = len([p for p in sample_prompts if p.length_bin == length_bin])
            print(f"  {length_bin.value}: {bin_count} prompts")

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        await close_mongo_connection()
        print("🔌 Disconnected from database")


if __name__ == "__main__":
    print("CyberCQBench Database Seeding")
    print("=" * 30)
    asyncio.run(seed_database())
    print("🎉 Seeding completed successfully!")
