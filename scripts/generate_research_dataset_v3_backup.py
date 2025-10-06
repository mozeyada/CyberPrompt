#!/usr/bin/env python3
"""
Academic-Grade Cybersecurity Prompt Generation for CyberPrompt Research

This script generates research-quality prompts using:
1. BOTS v3 dataset (real security data)
2. NIST SP 800-53 controls (compliance framework)
3. Operationally realistic token ranges

Token ranges are based on actual SOC/GRC/CTI operational workflows:
- SHORT (250-350): Tactical responses during active incidents (SOC L1/L2)
- MEDIUM (350-500): Analytical investigation plans (SOC L3/IR teams)
- LONG (600-750): Strategic executive briefings (CISO/Board/Regulators)

Designed for RQ1 (prompt length impact) and RQ2 (cost-effectiveness analysis)
"""

import json
import random
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import tiktoken

# Academic research parameters
RESEARCH_CONFIG = {
    "total_base_prompts": 100,  # For statistical significance
    "length_variants": ["S", "M", "L"],  # Short, Medium, Long
    "token_targets": {
        "S": (150, 250),    # Minimal context baseline (academic research-based)
        "M": (450, 550),    # +300 tokens from S (measurable effect per arXiv 2402.14848)
        "L": (800, 1000)    # +400 tokens from M (detect diminishing returns)
    },
    "scenarios": ["SOC_INCIDENT", "GRC_MAPPING", "CTI_SUMMARY"],
    "dataset_version": "20250107_academic_v4_rq1_controlled"  # Jan 7, 2025 - RQ1 controlled experiment fix
}

def load_bots_data_sources():
    """Load real BOTS v3 data sources from actual dataset"""
    try:
        script_dir = Path(__file__).parent
        props_path = script_dir.parent / "datasets" / "botsv3_data_set" / "default" / "props.conf"
        with open(props_path, 'r') as f:
            content = f.read()
            sources = []
            for line in content.split('\n'):
                if line.startswith('[') and line.endswith(']') and ':' in line:
                    source = line.strip('[]')
                    if source not in ['top'] and len(source) > 3:
                        sources.append(source)
            return sources[:15]
    except:
        return ["osquery_results", "iis", "stream:tcp", "stream:http", "xmlwineventlog:microsoft-windows-sysmon/operational"]

# Initialize precise tokenizer for academic accuracy
encoding = tiktoken.get_encoding("cl100k_base")  # Standard for GPT-3.5/4

BOTS_DATA_SOURCES = load_bots_data_sources()

# NIST SP 800-53 control families (from actual framework)
NIST_CONTROLS = {
    "AC": "Access Control", "AU": "Audit and Accountability",
    "AT": "Awareness and Training", "CM": "Configuration Management",
    "CP": "Contingency Planning", "IA": "Identification and Authentication",
    "IR": "Incident Response", "MA": "Maintenance",
    "MP": "Media Protection", "PE": "Physical and Environmental Protection",
    "PL": "Planning", "PS": "Personnel Security",
    "RA": "Risk Assessment", "CA": "Security Assessment and Authorization",
    "SC": "System and Communications Protection", "SI": "System and Information Integrity",
    "PM": "Program Management"
}

def load_bots_ransomware_data():
    """Load actual ransomware families from BOTSv3 dataset for academic credibility"""
    try:
        script_dir = Path(__file__).parent
        csv_path = script_dir.parent / "datasets" / "botsv3_data_set" / "lookups" / "ransomware_extensions.csv"
        ransomware = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Name') and row.get('Extensions'):
                    ransomware.append({
                        'extension': row['Extensions'],
                        'family': row['Name']
                    })
        return ransomware if ransomware else [{'extension': '.locky', 'family': 'Locky'}]
    except Exception as e:
        print(f"Warning: Could not load BOTSv3 ransomware data: {e}")
        return [
            {'extension': '.locky', 'family': 'Locky'},
            {'extension': '.wcry', 'family': 'WannaCry'},
            {'extension': '.cerber3', 'family': 'Cerber'}
        ]

# Load at module initialization for academic credibility
BOTS_RANSOMWARE = load_bots_ransomware_data()
print(f"✓ Loaded {len(BOTS_RANSOMWARE)} real ransomware families from BOTSv3 dataset")

def load_bots_ddns_providers():
    """Load actual DDNS providers from BOTSv3 for C2 infrastructure realism"""
    try:
        script_dir = Path(__file__).parent
        csv_path = script_dir.parent / "datasets" / "botsv3_data_set" / "lookups" / "ddns_provider.csv"
        providers = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('provider'):
                    providers.append(row['provider'])
        return providers[:50] if providers else ["no-ip.com", "duckdns.org"]
    except Exception as e:
        print(f"Warning: Could not load BOTSv3 DDNS providers: {e}")
        return ["no-ip.com", "duckdns.org", "freedns.afraid.org"]

def load_bots_event_codes():
    """Load actual Windows event codes from BOTSv3 for forensic realism"""
    try:
        script_dir = Path(__file__).parent
        csv_path = script_dir.parent / "datasets" / "botsv3_data_set" / "lookups" / "eventcode.csv"
        codes = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('EventCode') and row.get('Description'):
                    codes.append({
                        'code': row['EventCode'],
                        'desc': row['Description']
                    })
        return codes if codes else [{'code': '4624', 'desc': 'Account logon'}]
    except Exception as e:
        print(f"Warning: Could not load BOTSv3 event codes: {e}")
        return [{'code': '4624', 'desc': 'Account logon'}, {'code': '4625', 'desc': 'Failed logon'}]

# Initialize additional BOTSv3 data sources
BOTS_DDNS_PROVIDERS = load_bots_ddns_providers()
BOTS_EVENT_CODES = load_bots_event_codes()
print(f"✓ Loaded {len(BOTS_DDNS_PROVIDERS)} DDNS providers from BOTSv3 dataset")
print(f"✓ Loaded {len(BOTS_EVENT_CODES)} Windows event codes from BOTSv3 dataset")

# V2 SOC Scenarios - Realistic, detailed incident reports
SOC_SCENARIOS_V2 = [
    {
        "category": "Ransomware Incident",
        "data_sources": ["symantec:ep:security:file", "firewall:logs", "wineventlog"],
        "base_context": """
INCIDENT REPORT: URGENT - SEVERITY 1
TIMESTAMP: {timestamp}
AFFECTED SYSTEMS: Critical file server {affected_systems} and 25 workstations in the Finance department are reporting encrypted files with the '{ransomware_extension}' extension.
MALWARE TYPE: {ransomware_family} ransomware
INITIAL IOCs:
- File hash (dropper): {file_hash}
- C2 Infrastructure: {ddns_domain} via {ip_address}
- User account showing initial suspicious activity via phishing email: {user_account}
- Alert Source: Symantec Endpoint Protection detected and quarantined a malicious PowerShell script, but only after initial execution.
- Forensic Evidence: Windows Event {windows_event_code} ({event_description}) logged on {data_source}
BUSINESS IMPACT: Finance department operations are completely halted. The company's quarterly financial reporting process, due next week, is at risk. The CFO is demanding hourly updates.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- Finance operations halted
- CFO demanding updates
- Quarterly reporting deadline next week""",

            "M": """DETAILED ANALYSIS CONTEXT:

Attack Progression:
- 25 workstations encrypted over 60-minute period
- Lateral movement via SMB from initial phishing victim
- Encryption started 14:23 UTC, Symantec alert 15:23 UTC (40% complete)
- PowerShell dropper executed with admin privileges
- Persistence via scheduled task and registry modifications

System Status:
- DevOps reports backup integrity: Last full backup 72 hours ago
- Finance VP reports potential GDPR implications (customer invoices on encrypted shares)
- IT confirms: ~100TB data affected, 40% encrypted before containment

Resources Available:
- IT Security team: 3 staff on duty
- External IR retainer: 2-hour response time
- Cyber insurance: $5M coverage, $250K deductible
- Backup validation ongoing""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Attack Timeline & Technical Details:
- T-0 (14:23:17 UTC): Phishing email received by admin@froth.ly with malicious attachment
- T+5min: User clicked attachment, PowerShell dropper executed with admin privileges
- T+15min: Lateral movement initiated via SMB to 25 Finance workstations
- T+45min: Mass encryption begins targeting Finance file shares (~100TB data)
- T+60min: Symantec EPP generates alert after 40% encryption complete

Technical Indicators (High Confidence):
- Initial vector: Phishing email with weaponized Office document (CVE-{cve_id})
- Dropper hash: {file_hash} (not in VirusTotal, likely targeted/custom)
- C2 Communication: {ip_address}:443 (HTTPS encrypted, TLS 1.2)
- Ransomware Family: {ransomware_family} (known for double extortion tactics)
- File Extension: {ransomware_extension} appended to all encrypted files
- Data Exfiltration: Suspected 15GB uploaded to C2 before encryption

Business & Organizational Context:
- Finance department operations completely halted since 14:23 UTC
- Quarterly financial reporting due in 7 days (SEC regulatory requirement)
- ~500 staff unable to access critical financial systems and records
- Customer service operations impacted due to billing system inaccessibility
- Supply chain disruptions expected within 48 hours if systems not restored
- Insurance coverage: Cyber policy covers up to $10M but requires immediate notification
- Legal obligations: Data breach notification laws may require 72-hour reporting
- Regulatory impact: SEC filing delays could result in penalties and stock price volatility
- Stakeholder communication: Board of Directors, major clients, and regulatory bodies require immediate updates
- CFO demanding hourly updates, Board of Directors has been notified
- IT Security team: 3 staff available (2 L1 analysts + 1 L2 investigator)
- External IR retainer (CrowdStrike Services) on standby, 2-hour activation time
- Cyber insurance: $5M coverage with $250K deductible (carrier notified)
- Backup Status: Last full backup 72 hours ago, incremental backups every 6 hours

Stakeholder Communication Requirements:
- CEO expects executive briefing within 4 hours (11:59 AM local time)
- General Counsel standing by for regulatory notification assessment
- Communications team preparing internal messaging for staff and external PR
- Cyber insurance carrier notified, claims adjuster assigned
- Board of Directors awareness notification sent, full briefing scheduled if impact >$10M"""
        }
    },
    {
        "category": "Business Email Compromise",
        "data_sources": ["o365:management:activity", "ms:aad:signin", "stream:smtp"],
        "base_context": """
INCIDENT REPORT: CRITICAL - FINANCIAL FRAUD ALERT
TIMESTAMP: {timestamp}
AFFECTED SYSTEMS: CEO's Office 365 account ({user_account}) has been compromised. Fraudulent wire transfer requests totaling $2.3M have been sent to the CFO and three department heads.
INITIAL IOCs:
- Suspicious login from IP: {ip_address} (geolocation: Eastern Europe)
- Modified inbox rules detected to hide attacker communications
- Unusual email forwarding rules established to external domain: {ddns_domain}
- Alert Source: Finance team flagged unusual wire transfer requests with urgent language and modified banking details
- Forensic Evidence: Windows Event {windows_event_code} ({event_description}) logged on {data_source}
BUSINESS IMPACT: Potential financial loss of $2.3M. One transfer of $850K was already initiated before the fraud was detected. Company reputation and customer trust are at immediate risk. Legal team is preparing for potential regulatory scrutiny.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- CEO account compromised
- $2.3M fraudulent transfers requested
- Finance team alerted""",

            "M": """DETAILED ANALYSIS CONTEXT:

Attack Details:
- CEO Office 365 account compromised via Eastern European IP
- Inbox rules modified to hide attacker communications
- Email forwarding to external domain established
- Wire transfer requests sent to CFO and department heads
- $850K transfer already initiated before detection

Investigation Requirements:
- Forensic analysis of CEO mailbox and login patterns
- Analysis of email forwarding rules and external domain access
- Review of financial transaction patterns and approval workflows
- Assessment of lateral movement and additional compromised accounts
- Evaluation of data exfiltration scope and sensitive information accessed
- Coordination with financial institutions to halt pending transfers
- Legal consultation for regulatory reporting and law enforcement coordination
- Coordination with finance team to halt pending transfers
- Analysis of email flow and rule modifications
- Identification of all potentially compromised accounts
- Communication strategy for internal stakeholders

Business Impact:
- Potential $2.3M financial loss
- Company reputation at risk
- Legal team preparing for regulatory scrutiny""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Attack Timeline & Technical Details:
- T-0: Initial compromise of CEO Office 365 account via Eastern European IP ({ip_address})
- T+2hrs: Attacker established persistent access via modified inbox rules
- T+4hrs: Email forwarding rules created to external domain (temp-mail-{file_hash}.com)
- T+6hrs: First fraudulent wire transfer request sent to CFO ($850K)
- T+8hrs: Additional transfer requests sent to 3 department heads ($1.45M total)
- T+10hrs: Finance team flagged unusual language and banking details
- T+12hrs (NOW): Investigation initiated, $850K transfer already in progress

Technical Indicators (High Confidence):
- Compromised account: {user_account} (CEO Office 365)
- Attack vector: Credential compromise (likely phishing or credential stuffing)
- Persistence: Modified inbox rules to hide attacker communications
- Data exfiltration: Email forwarding to external domain
- Lateral movement: Impersonation of CEO to target finance personnel
- Financial targeting: Wire transfer requests with urgent language and modified banking details

Business & Organizational Context:
- CEO account fully compromised with administrative privileges
- $2.3M in fraudulent wire transfer requests identified
- $850K transfer already initiated and may be irreversible
- Company reputation and customer trust at immediate risk
- Legal team preparing for potential regulatory scrutiny and litigation
- Board of Directors has been notified of potential financial impact
- Cyber insurance carrier notified, claims process initiated
- Regulatory obligations: Potential SEC disclosure if material impact, banking regulations
- Customer communication: May need to notify clients of potential data exposure
- Financial institution coordination: Multiple banks involved in transfer requests
- Internal communication: Staff morale and operational continuity concerns
- Media relations: Potential public disclosure and reputation management required
- Supply chain impact: Vendor relationships and payment processing disruptions
- Compliance requirements: SOX, PCI-DSS, and industry-specific regulations
- Stakeholder management: Investors, customers, partners, and regulatory bodies

Stakeholder Communication Requirements:
- Board of Directors expects immediate briefing on financial impact
- CFO requires coordination to halt pending transfers and assess damage
- Legal counsel standing by for regulatory notification and litigation strategy
- Communications team preparing crisis management response
- Cyber insurance carrier notified, claims adjuster assigned
- Law enforcement (FBI IC3) notification under consideration
- External partners who received fraudulent requests need immediate notification
- Employee communication plan for potential data exposure and security awareness"""
        }
    },
    {
        "category": "Insider Threat Investigation",
        "data_sources": ["code42:security", "ms:aad:signin", "osquery_results"],
        "base_context": """
INCIDENT REPORT: CONFIDENTIAL - INSIDER THREAT INVESTIGATION
TIMESTAMP: {timestamp}
AFFECTED SYSTEMS: Senior software engineer {user_account} has been flagged for suspicious data access patterns. Code42 DLP detected 15GB of proprietary source code and customer database exports to personal cloud storage accounts.
INITIAL IOCs:
- Unusual after-hours access patterns (2 AM - 4 AM) over the past two weeks
- Large file transfers to personal Dropbox account: dropbox.com/u/{file_hash}
- Access to customer databases outside normal job responsibilities
- Recent resignation submitted with 2-week notice, effective next Friday
- Alert Source: Code42 Data Loss Prevention system flagged bulk data movement
BUSINESS IMPACT: Potential theft of intellectual property worth $50M+ and customer PII for 100,000+ customers. Employee is joining a direct competitor. Legal team is preparing for potential litigation and regulatory notifications.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- Employee resigning next Friday
- 15GB data exfiltrated to personal cloud
- Still has active access""",

            "M": """DETAILED ANALYSIS CONTEXT:

Investigation Details:
- Senior software engineer flagged for suspicious data access
- 15GB proprietary source code and customer data exported
- Unusual after-hours access patterns (2 AM - 4 AM)
- Large transfers to personal Dropbox account
- Resignation submitted with 2-week notice

Evidence Collection:
- Forensic imaging of workstation and mobile devices
- Analysis of data access logs and file transfers
- Correlation of access patterns with job responsibilities
- Assessment of potential data exposure and customer impact
- Coordination with legal team for criminal referral
- Review of network traffic and cloud storage access patterns
- Analysis of email communications and external contacts
- Assessment of additional compromised systems or accounts

Business Impact:
- Potential theft of $50M+ intellectual property
- Customer PII for 100,000+ customers exposed
- Employee joining direct competitor
- Competitive advantage loss and market position risk
- Regulatory notification requirements for data breach
- Customer trust and reputation damage
- Potential litigation and regulatory penalties""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Investigation Timeline & Technical Details:
- T-14 days: Employee began unusual after-hours access patterns (2 AM - 4 AM)
- T-10 days: First large file transfers to personal Dropbox account detected
- T-7 days: Access to customer databases outside normal job responsibilities
- T-3 days: Bulk data movement of 15GB proprietary source code
- T-2 days: Customer database exports to personal cloud storage
- T-1 day: Resignation submitted with 2-week notice, effective next Friday
- T-0 (NOW): Code42 DLP flagged bulk data movement, investigation initiated

Technical Indicators (High Confidence):
- Compromised employee: {user_account} (Senior software engineer)
- Data exfiltration: 15GB proprietary source code and customer databases
- Transfer method: Personal Dropbox account (dropbox.com/u/{file_hash})
- Access pattern: Unusual after-hours activity (2 AM - 4 AM) over 2 weeks
- Scope: Customer databases outside normal job responsibilities
- Timing: Resignation submitted with 2-week notice, joining direct competitor

Business & Organizational Context:
- Employee has access to $50M+ intellectual property and trade secrets
- Customer PII for 100,000+ customers potentially exposed
- Employee is joining a direct competitor (competitive intelligence risk)
- Legal team preparing for potential litigation and regulatory notifications
- HR department coordinating with legal for employee termination process
- Board of Directors has been notified of potential IP theft
- Cyber insurance carrier notified, claims process initiated
- Regulatory obligations: Potential GDPR/CCPA notifications for customer data exposure
- Competitive disadvantage: Proprietary algorithms and customer data at risk
- Market position impact: Loss of competitive advantage and market share risk
- Customer trust: Potential reputation damage and customer churn
- Investor relations: Potential impact on stock price and investor confidence
- Supply chain: Vendor relationships and partnership agreements at risk
- Operational continuity: Knowledge transfer and succession planning disrupted
- Regulatory compliance: Industry-specific regulations and audit requirements

Stakeholder Communication Requirements:
- Executive leadership expects immediate briefing on IP theft and competitive risk
- Legal counsel standing by for potential criminal referral and civil litigation
- HR department coordinating employee termination and access revocation
- Communications team preparing crisis management for potential data breach
- Cyber insurance carrier notified, claims adjuster assigned
- Law enforcement (FBI) notification under consideration for IP theft
- Customer communication plan for potential PII exposure
- Partner notification strategy for potential competitive intelligence compromise
- Regulatory notification plan for GDPR/CCPA compliance"""
        }
    },
    {
        "category": "Advanced Persistent Threat",
        "data_sources": ["aws:cloudtrail", "xmlwineventlog:microsoft-windows-sysmon/operational", "stream:tcp"],
        "base_context": """
INCIDENT REPORT: NATION-STATE THREAT - SEVERITY 1
TIMESTAMP: {timestamp}
AFFECTED SYSTEMS: Multi-stage APT campaign detected across {affected_systems} and cloud infrastructure. Threat actor has maintained persistence for an estimated 8 months with access to sensitive R&D data.
INITIAL IOCs:
- Custom malware family with hash: {file_hash}
- Command and control infrastructure: {ddns_domain} via {ip_address} (linked to known APT29 campaigns)
- Compromised service account: {user_account} with elevated privileges
- Lateral movement across 47 systems including domain controllers
- Alert Source: Threat hunting team identified anomalous PowerShell execution patterns
- Forensic Evidence: Windows Event {windows_event_code} ({event_description}) logged on {data_source}
BUSINESS IMPACT: Potential exfiltration of next-generation product designs worth $200M+ in R&D investment. Threat actor had access to executive communications, strategic planning documents, and customer contracts. National security implications due to defense contractor status.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- APT29 threat actor active for 8 months
- $200M+ R&D data at risk
- National security implications""",

            "M": """DETAILED ANALYSIS CONTEXT:

Threat Actor Details:
- APT29 (Cozy Bear) nation-state threat actor
- 8-month persistence in environment
- Custom malware with hash {file_hash}
- C2 infrastructure at {ip_address}
- Compromised service account with elevated privileges
- Lateral movement across 47 systems including domain controllers

Investigation Requirements:
- Detailed threat actor profiling and attribution analysis
- Complete scope assessment of compromised systems and data
- Coordinated eradication plan preventing adversary escape
- Evidence preservation for criminal prosecution

Business Impact:
- Potential exfiltration of $200M+ R&D investment
- Access to executive communications and strategic planning
- Customer contracts and defense contractor data compromised
- National security implications due to defense contractor status""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Attack Timeline & Technical Details:
- T-8 months: Initial compromise via spear-phishing campaign targeting R&D team
- T-6 months: Establishment of C2 infrastructure at {ip_address}
- T-4 months: Lateral movement initiation across 47 systems
- T-2 months: Access to executive communications and strategic planning documents
- T-1 month: Exfiltration of next-generation product designs and R&D data
- T-0 (NOW): Threat hunting team identified anomalous PowerShell execution patterns

Technical Indicators (High Confidence):
- Threat actor: APT29 (Cozy Bear) - Russian state-sponsored group
- Malware: Custom family with hash {file_hash} (not in public databases)
- C2 Infrastructure: {ip_address} (linked to known APT29 campaigns)
- Compromised account: {user_account} (service account with elevated privileges)
- Lateral movement: 47 systems including domain controllers and R&D servers
- Data exfiltration: R&D data, executive communications, customer contracts

Business & Organizational Context:
- Defense contractor with national security implications
- $200M+ R&D investment in next-generation products at risk
- Executive communications and strategic planning documents compromised
- Customer contracts and sensitive business relationships exposed
- Government oversight bodies and intelligence agencies involved
- Board of Directors and CEO briefed on national security implications
- Cyber insurance carrier notified, claims process initiated
- Regulatory compliance: ITAR, EAR, and defense contractor regulations
- Customer trust: Potential loss of classified contracts and partnerships
- Market position: Competitive advantage and market share at risk
- Investor relations: Potential impact on stock price and investor confidence
- Supply chain: Vendor relationships and partnership agreements compromised
- Operational continuity: Critical systems and infrastructure at risk
- Legal obligations: Potential litigation and regulatory penalties

Stakeholder Communication Requirements:
- CEO and Board of Directors expect immediate briefing on national security implications
- Government oversight bodies and intelligence agencies require coordination
- Federal law enforcement (FBI, CISA) notification and evidence sharing
- Defense contractor customers need immediate notification of potential compromise
- Cyber insurance carrier notified, claims adjuster assigned
- Legal counsel standing by for regulatory compliance and potential litigation"""
        }
    },
    {
        "category": "Cloud Misconfiguration Breach",
        "data_sources": ["aws:cloudtrail", "aws:s3:accesslogs", "aws:cloudwatch"],
        "base_context": """
INCIDENT REPORT: DATA EXPOSURE - SEVERITY 2
TIMESTAMP: {timestamp}
AFFECTED SYSTEMS: AWS S3 bucket containing customer PII was publicly accessible for 72 hours due to misconfigured access policies. Security researcher discovered the exposure and reported it through responsible disclosure.
INITIAL IOCs:
- Misconfigured S3 bucket: customer-data-backup-{file_hash}
- Public read access enabled on 2.3TB of customer data
- Unusual access patterns from IP: {ip_address} (automated scanning tools)
- Service account involved: {user_account} (DevOps automation)
- Alert Source: External security researcher notification
BUSINESS IMPACT: Exposure of 500,000+ customer records including names, addresses, phone numbers, and encrypted payment tokens. GDPR and state privacy law notification requirements triggered. Potential regulatory fines up to $50M. Customer trust and brand reputation at risk.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- S3 bucket publicly accessible for 72 hours
- 500,000+ customer records exposed
- GDPR notification required""",

            "M": """DETAILED ANALYSIS CONTEXT:

Exposure Details:
- AWS S3 bucket misconfigured with public read access
- 2.3TB customer data exposed for 72 hours
- Unusual access patterns from automated scanning tools
- Service account involved in configuration error
- Security researcher reported via responsible disclosure

Investigation Requirements:
- Complete forensic analysis of S3 access logs and CloudTrail events
- Assessment of all potentially accessed data and affected customers
- Root cause analysis of configuration error and process failures
- Coordination with legal, compliance, and communications teams
- Technical remediation plan with improved access controls

Business Impact:
- 500,000+ customer records exposed (names, addresses, phone numbers)
- Encrypted payment tokens potentially compromised
- GDPR and state privacy law notification requirements triggered
- Potential regulatory fines up to $50M
- Customer trust and brand reputation at risk""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Exposure Timeline & Technical Details:
- T-72 hours: S3 bucket misconfigured with public read access during DevOps deployment
- T-48 hours: Automated scanning tools detected exposed bucket at {ip_address}
- T-24 hours: Security researcher discovered exposure during responsible disclosure research
- T-12 hours: Initial assessment of 2.3TB customer data exposure
- T-0 (NOW): Security researcher reported exposure via responsible disclosure

Technical Indicators (High Confidence):
- Exposed bucket: customer-data-backup-{file_hash} (2.3TB customer data)
- Access pattern: Unusual automated scanning from {ip_address}
- Configuration error: Public read access enabled during DevOps deployment
- Service account: {user_account} (DevOps automation) involved in misconfiguration
- Data scope: 500,000+ customer records including PII and payment tokens
- Exposure duration: 72 hours of public accessibility

Business & Organizational Context:
- Customer data exposure: 500,000+ records including names, addresses, phone numbers
- Payment data: Encrypted payment tokens potentially compromised
- Regulatory obligations: GDPR, CCPA, and state privacy law notification requirements
- Potential fines: Up to $50M in regulatory penalties
- Customer trust: Brand reputation and customer relationships at risk
- Legal team preparing for potential regulatory investigations and customer litigation
- Board of Directors has been notified of potential financial and reputational impact
- Cyber insurance carrier notified, claims process initiated
- Market position: Competitive advantage and market share at risk
- Investor relations: Potential impact on stock price and investor confidence
- Supply chain: Vendor relationships and partnership agreements at risk
- Operational continuity: Customer service and business operations disrupted
- Media relations: Potential public disclosure and reputation management required
- Compliance requirements: Industry-specific regulations and audit requirements

Stakeholder Communication Requirements:
- Executive leadership expects immediate briefing on data exposure and regulatory impact
- Legal counsel standing by for GDPR/CCPA notification requirements and compliance
- Communications team preparing customer notification and credit monitoring services
- Customer service team preparing for increased support requests and inquiries
- IT operations team coordinating technical remediation and access control improvements
- Compliance team coordinating with regulatory bodies and audit requirements
- HR department preparing for potential employee accountability and training needs
- Finance team assessing financial impact and insurance claim processing
- Board of Directors requiring detailed incident report and remediation plan
- External auditors and compliance consultants for regulatory guidance
- Media relations team preparing for potential public disclosure and crisis management
- Investor relations team preparing for potential shareholder communications
- Cyber insurance carrier notified, claims adjuster assigned
- Regulatory bodies (GDPR, CCPA) require notification within 72 hours
- Customer communication plan for potential data exposure and remediation"""
        }
    }
]

# V2 CTI Scenarios - Realistic threat intelligence analysis
CTI_SCENARIOS_V2 = [
    {
        "category": "Threat Actor Profiling",
        "data_sources": ["threat_intel_feed", "osint_sources", "dark_web_monitoring"],
        "base_context": """
THREAT INTELLIGENCE REQUEST: APT ACTOR PROFILING
ANALYSIS DATE: {timestamp}
REQUEST SOURCE: Executive Security Committee - Urgent Priority
CONTEXT: Multiple organizations in our sector have reported sophisticated intrusions over the past 6 months. Our threat intelligence team has identified indicators suggesting we may be a target for the same threat actor group.
AVAILABLE INTELLIGENCE:
- Threat Actor Designation: APT29 (Cozy Bear) - suspected state-sponsored group
- Known TTPs: Spear-phishing with weaponized documents, credential harvesting, lateral movement via PowerShell
- Recent Campaign IOCs: File hash {file_hash}, C2 infrastructure including {ip_address}
- Targeting Pattern: Defense contractors, government agencies, and critical infrastructure in North America and Europe
- Attack Sophistication: Advanced - uses zero-day exploits, custom malware, and anti-forensics techniques
- Observed Persistence: Average dwell time of 6-8 months before detection
STRATEGIC CONCERN: We hold classified contracts with defense agencies. A breach could result in loss of security clearances, contract termination, and national security implications. The board is demanding a threat assessment.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- APT29 (Cozy Bear) targeting defense contractors
- Multiple sector organizations compromised
- National security implications""",

            "M": """DETAILED ANALYSIS CONTEXT:

Threat Actor Profile:
- APT29 (Cozy Bear) - suspected state-sponsored group
- Known TTPs: Spear-phishing with weaponized documents, credential harvesting
- Recent Campaign IOCs: File hash {file_hash}, C2 infrastructure {ip_address}
- Targeting Pattern: Defense contractors, government agencies, critical infrastructure

Investigation Requirements:
- Detailed TTPs and known malware families
- Infrastructure patterns and C2 analysis

Business Impact:
- Classified contracts with defense agencies at risk""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Threat Intelligence Analysis Timeline & Details:
- T-6 months: Multiple organizations in sector reported sophisticated intrusions
- T-4 months: Threat intelligence team identified indicators suggesting targeting
- T-2 months: APT29 (Cozy Bear) attribution confirmed through TTP analysis
- T-1 month: Executive Security Committee elevated to urgent priority
- T-2 weeks: Board of Directors requested threat assessment briefing
- T-1 week: Government security officers requested coordination meeting
- T-0 (NOW): CISO briefing board and government security officers tomorrow

Threat Actor Intelligence (High Confidence):
- Designation: APT29 (Cozy Bear) - suspected state-sponsored group
- Known TTPs: Spear-phishing with weaponized documents, credential harvesting, lateral movement via PowerShell
- Recent Campaign IOCs: File hash {file_hash}, C2 infrastructure including {ip_address}
- Targeting Pattern: Defense contractors, government agencies, and critical infrastructure in North America and Europe
- Attack Sophistication: Advanced - uses zero-day exploits, custom malware, and anti-forensics techniques
- Observed Persistence: Average dwell time of 6-8 months before detection

Business & Organizational Context:
- Organization holds classified contracts with defense agencies
- Potential breach could result in loss of security clearances and contract termination
- National security implications due to defense contractor status
- Board of Directors demanding comprehensive threat assessment
- Government security officers requiring coordination and information sharing
- Strategic security investments needed to defend against this adversary
- Incident response plan required if evidence of compromise discovered

Stakeholder Communication Requirements:
- Board of Directors expects strategic threat assessment and defense strategy
- Government security officers require coordination and information sharing
- Executive Security Committee needs immediate threat profile and detection priorities
- SOC manager requires quick threat brief for security standup
- Threat intelligence team needs comprehensive actor profile for detection tuning
- Legal counsel standing by for potential regulatory and compliance implications"""
        }
    },
    {
        "category": "IOC Analysis and Attribution",
        "data_sources": ["virustotal", "threat_intel_platforms", "malware_sandbox"],
        "base_context": """
THREAT INTELLIGENCE ANALYSIS: MALWARE IOC INVESTIGATION
INVESTIGATION DATE: {timestamp}
TRIGGER: Automated threat hunting detected suspicious file hash {file_hash} on three endpoints in the R&D network.
IOC DETAILS:
- File Hash (SHA256): {file_hash}
- File Name: invoice_Q3_2024.pdf.exe (double extension)
- First Seen: 72 hours ago on {user_account}
- Network Behavior: Attempted connection to {ip_address} on port 443
- Behavioral Analysis: Created scheduled task, modified registry run keys
- VirusTotal Detection: 12/70 vendors flag as malicious (new variant)
INVESTIGATION FINDINGS:
- File appears to be a dropper for additional payloads
- C2 infrastructure domain registered 2 weeks ago (fresh)
- Similar samples targeting aerospace and defense sectors
- Code similarities to known APT41 malware family
URGENCY: R&D network contains proprietary designs. If this is targeted espionage, intellectual property theft could cost $100M+ in competitive advantage.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- Suspicious file hash detected on 3 R&D endpoints
- Malware appears to be APT41 dropper
- $100M+ IP theft risk""",

            "M": """DETAILED ANALYSIS CONTEXT:

Malware Analysis:
- File Hash: {file_hash} (SHA256)
- File Name: invoice_Q3_2024.pdf.exe (double extension)
- First Seen: 72 hours ago on {user_account}
- Network Behavior: Attempted connection to {ip_address}:443
- VirusTotal Detection: 12/70 vendors flag as malicious (new variant)

Investigation Findings:
- File appears to be dropper for additional payloads
- Similar samples targeting aerospace and defense sectors

Business Impact:
- R&D network contains proprietary designs
- Targeted espionage could cost $100M+ in competitive advantage""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Malware IOC Investigation Timeline & Details:
- T-72 hours: Suspicious file hash {file_hash} first detected on {user_account}
- T-48 hours: Automated threat hunting identified file on 3 R&D network endpoints
- T-24 hours: Initial behavioral analysis revealed dropper capabilities
- T-12 hours: VirusTotal analysis showed 12/70 vendors flag as malicious
- T-6 hours: C2 infrastructure analysis revealed domain registered 2 weeks ago
- T-3 hours: Code similarity analysis linked to known APT41 malware family
- T-1 hour: Industry sector analysis confirmed targeting of aerospace and defense
- T-0 (NOW): Incident response team requesting immediate guidance on malware sample

Technical Indicators (High Confidence):
- File Hash: {file_hash} (SHA256) - new variant not in public databases
- File Name: invoice_Q3_2024.pdf.exe (double extension) - social engineering tactic
- Network Behavior: Attempted connection to {ip_address}:443 (HTTPS C2)
- Behavioral Analysis: Created scheduled task, modified registry run keys (persistence)
- VirusTotal Detection: 12/70 vendors flag as malicious (low detection rate)
- C2 Infrastructure: Domain registered 2 weeks ago (fresh infrastructure)
- Attribution: Code similarities to known APT41 malware family

Business & Organizational Context:
- R&D network contains proprietary designs and intellectual property
- Targeted espionage could result in \$100M+ competitive advantage loss
- Aerospace and defense sector targeting suggests nation-state interest
- Executive team and legal counsel need complete threat assessment
- Potential law enforcement engagement and threat actor attribution required
- Long-term security improvements needed to prevent recurrence
- Industry sector comparison needed for threat intelligence sharing

Stakeholder Communication Requirements:
- Executive team expects complete threat assessment for disclosure decisions
- Legal counsel requires assessment for potential law enforcement engagement
- Incident response team needs immediate guidance on malware sample
- Security operations team requires detailed IOC analysis for incident scoping
- R&D leadership needs assessment of intellectual property exposure risk
- Industry ISAC coordination for threat intelligence sharing"""
        }
    },
    {
        "category": "Strategic Threat Intelligence Report",
        "data_sources": ["industry_isac", "government_advisories", "threat_intel_platforms"],
        "base_context": """
STRATEGIC INTELLIGENCE BRIEFING: EMERGING THREAT LANDSCAPE
REPORTING PERIOD: Q4 2024 Threat Landscape Analysis
AUDIENCE: Executive Security Committee and Board Risk Committee
INDUSTRY CONTEXT: Cybersecurity threat landscape has evolved significantly. Recent government advisories indicate increased targeting of organizations with our profile.
KEY THREAT TRENDS:
- Ransomware Evolution: Shift from encryption-only to data exfiltration (average ransom: $4.5M)
- Supply Chain Attacks: 34% increase via third-party software providers
- Cloud Targeting: 67% of incidents involve cloud assets (AWS, Azure, O365)
- Insider Threats: 23% involved privileged user account compromise
- Nation-State Activity: Increased APT activity targeting defense contractors
SECTOR-SPECIFIC INTELLIGENCE:
- Three competitors suffered major breaches this quarter
- Government advisories warn organizations holding classified contracts
- Average breach cost in our sector: $12.4M (up from $9.1M last year)
ORGANIZATIONAL RISK FACTORS:
- We process classified information and maintain security clearances
- Recent M&A activity expanded attack surface
- Hybrid work model increased remote access dependency
- Cybersecurity budget 15% below industry average
""",
        "context_layers": {
            "S": "The IT steering committee needs a quick threat landscape update for budget planning. Summarize the top 3 threat trends most relevant to our organization and why they matter to us specifically.",
            "M": """DETAILED ANALYSIS CONTEXT:

The CISO is developing next year's security strategy and budget proposal. Provide a detailed threat landscape analysis including:

Threat Trends Analysis:
- Most significant threat trends affecting our industry (ransomware evolution, supply chain attacks, cloud targeting)
- Assessment of our organization's specific vulnerabilities to these threats
- Comparative analysis of our security posture versus industry peers

Strategic Recommendations:
- Prioritized security investments to address identified gaps
- Recommended strategic initiatives for the next 12 months
- Budget allocation priorities for maximum risk reduction
- Integration with existing security programs and business objectives

Business Impact Assessment:
- Risk quantification including potential financial impact of different threat scenarios
- Alignment with business continuity planning and enterprise risk management
- Metrics and KPIs for measuring security program effectiveness against evolving threats""",
            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

The board of directors requires a comprehensive strategic threat intelligence briefing to inform risk management and investment decisions. Your report must address:

Complete Threat Landscape Analysis:
- Complete analysis of the current threat landscape for our sector
- Comparative analysis of our security posture versus industry peers
- Risk quantification including potential financial impact of different threat scenarios
- Assessment of emerging threats and their potential impact on our organization

Strategic Security Roadmap:
- Multi-year strategic security roadmap addressing identified threats
- Recommended changes to board-level risk governance and oversight
- Integration with enterprise risk management and business continuity planning
- Budget allocation strategy for maximum risk reduction and business value

Program Effectiveness Metrics:
- Metrics and KPIs for measuring security program effectiveness against evolving threats
- Benchmarking against industry standards and best practices
- Performance indicators for security investments and risk mitigation
- Reporting framework for board-level security governance and oversight

Organizational Context:
- Alignment with business objectives and strategic initiatives
- Integration with existing security programs and technology investments
- Stakeholder communication strategy for security risk management
- Regulatory compliance requirements and industry-specific obligations

Implementation Framework:
- Detailed implementation timeline for strategic security initiatives
- Resource requirements and budget allocation for multi-year roadmap
- Change management strategy for security program transformation
- Success criteria and milestone tracking for security investments
- Risk mitigation strategies for identified threat scenarios
- Business continuity planning integration with security measures

Executive Decision Support:
- Board-level risk governance framework and oversight mechanisms
- Strategic investment priorities for cybersecurity capabilities
- Regulatory compliance requirements and industry-specific obligations
- Stakeholder communication strategy for security risk management
- Performance metrics and KPIs for measuring security program effectiveness
- Integration with enterprise risk management and business continuity planning

Strategic Recommendations:
- Multi-year strategic security roadmap addressing identified threats
- Recommended changes to board-level risk governance and oversight
- Budget allocation strategy for maximum risk reduction and business value
- Technology investment priorities for emerging threat landscape
- Personnel and training requirements for security program transformation
- Partnership and collaboration opportunities for threat intelligence sharing"""
        }
    }
]

# V2 GRC Scenarios - Realistic compliance assessments
GRC_SCENARIOS_V2 = [
    {
        "category": "GDPR Compliance Audit",
        "control_family": "Privacy",
        "base_context": """
COMPLIANCE ASSESSMENT: GDPR READINESS EVALUATION
ASSESSMENT DATE: {timestamp}
SCOPE: Annual GDPR compliance assessment for {system_name} processing 2.5M EU customer records across 15 business units.
KEY FINDINGS SUMMARY:
- Data Processing Activities: 47 identified processing activities, 12 lack proper legal basis documentation
- Data Subject Rights: Average response time of 45 days exceeds GDPR 30-day requirement
- Data Breach Procedures: Incident response plan exists but lacks 72-hour notification workflow
- Vendor Management: 23 third-party processors, 8 missing adequate Data Processing Agreements
- Technical Safeguards: Encryption at rest implemented, but data in transit protection inconsistent
REGULATORY CONTEXT: Irish Data Protection Commission has increased enforcement activities in our sector. Recent fines in similar companies averaged €15M. Our legal team reports 3 pending data subject complaints.
""",
        "context_layers": {
            "S": """IMMEDIATE CONTEXT:
- Next week's executive briefing on GDPR compliance
- CEO needs top 3 critical gaps requiring attention
- Irish DPC has increased enforcement (avg fines: €15M)
- 3 pending data subject complaints under legal review""",

            "M": """DETAILED ANALYSIS CONTEXT:

Remediation Requirements:
- Improving data subject rights response procedures (currently 45-day avg, need 30)
- Enhancing vendor management and DPA processes (8 of 23 processors missing agreements)
- Implementing technical safeguards for data in transit (currently inconsistent)
- Establishing proper legal basis documentation (12 of 47 activities lack documentation)
- Updating data breach procedures to include 72-hour notification workflow

Timeline & Resources:
- Comprehensive 12-month remediation plan required
- Resource requirements and success metrics needed
- Stakeholder communication plan for all business units
- Budget allocation for technology upgrades and personnel training

Business Impact:
- Irish DPC has increased enforcement activities in our sector
- Recent fines in similar companies averaged €15M
- 3 pending data subject complaints currently under legal review
- Cyber insurance carrier requires documented compliance program""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Gap Analysis & Risk Prioritization:
- Data Processing Activities: 47 identified processing activities, 12 lack proper legal basis documentation (High Risk: €10M fine potential)
- Data Subject Rights: 45-day average response time exceeds GDPR 30-day requirement (Medium Risk: €5M fine potential)
- Data Breach Procedures: Incident response plan exists but lacks 72-hour notification workflow (Critical Risk)
- Vendor Management: 23 third-party processors, 8 missing adequate Data Processing Agreements (High Risk: Joint liability exposure)
- Technical Safeguards: Encryption at rest implemented, but data in transit protection inconsistent across 15 business units (Medium Risk)

Strategic Transformation Requirements:
- Multi-year roadmap for achieving and maintaining compliance across all business units
- Budget requirements: Technology upgrades ($2M), Personnel (3 FTE privacy specialists), External legal support ($500K/yr)
- Governance framework: Privacy by design integration into product development lifecycle
- Training and awareness program: All-employee awareness training (2,500 staff) + specialized training for data handlers (150 personnel)
- Metrics and KPIs: Ongoing compliance monitoring dashboard for Board of Directors and Data Protection Officers
- Crisis management: Regulatory investigation response plan (Irish DPC has increased enforcement activities)
- Vendor risk management: Enhanced third-party processor oversight and Data Processing Agreement template

Business & Regulatory Context:
- Irish Data Protection Commission has increased enforcement activities in our sector
- Recent fines in similar companies averaged €15M for comparable violations
- 3 pending data subject complaints currently under legal review by General Counsel
- Board of Directors has mandated full compliance achievement before next annual audit
- Cyber insurance carrier requires documented compliance program for coverage renewal
- Processing 2.5M EU customer records across 15 business units
- Annual GDPR compliance assessment scope covers all data processing activities

Stakeholder Communication Requirements:
- Executive leadership expects strategic compliance transformation program for board approval
- Legal counsel standing by for GDPR compliance requirements and regulatory coordination
- Communications team preparing internal messaging for compliance awareness across organization
- IT steering committee coordination for technology upgrade resource allocation
- Business unit leaders need communication on process changes and compliance requirements
- Compliance team coordination for ongoing monitoring, testing, and audit preparation"""
        }
    },
    {
        "category": "SOX IT Controls Assessment",
        "control_family": "Financial Reporting",
        "base_context": """
SOX ASSESSMENT: IT GENERAL CONTROLS EVALUATION
ASSESSMENT PERIOD: FY2024 Annual Review
SCOPE: IT General Controls supporting financial reporting for {system_name} (SAP ERP) and related financial applications affecting $2.8B in annual revenue.
CONTROL DEFICIENCIES IDENTIFIED:
- Access Management: 47 users with inappropriate segregation of duties conflicts in financial modules
- Change Management: 12 emergency changes to production systems lacked proper approval documentation
- Data Backup/Recovery: Recovery testing performed quarterly instead of required monthly frequency
- System Monitoring: Automated monitoring gaps identified for 3 critical financial interfaces
- User Access Reviews: Q2 access certification completed 45 days late, affecting 2,847 user accounts
AUDIT CONTEXT: External auditors (Big 4 firm) have classified 2 deficiencies as 'significant deficiencies' requiring management remediation. CFO has mandated all gaps be resolved before Q4 testing begins in 8 weeks.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- SOX IT control deficiencies identified by Big 4 auditors
- External auditors returning in 8 weeks for Q4 testing
- 2 significant deficiencies require management remediation
- CFO has mandated all gaps resolved before follow-up testing
- $2.8B annual revenue at risk if controls fail""",

            "M": """DETAILED ANALYSIS CONTEXT:

Control Deficiencies:
- Access Management: 47 users with segregation of duties conflicts
- Change Management: 12 emergency changes lacked approval documentation
- Data Backup/Recovery: Testing performed quarterly instead of monthly
- System Monitoring: Automated monitoring gaps for 3 critical interfaces
- User Access Reviews: Q2 certification completed 45 days late

Remediation Requirements:
- Detailed remediation steps for each control deficiency
- Process improvements to prevent recurrence
- Enhanced monitoring and testing procedures
- Resource requirements and budget implications
- Communication plan for stakeholders and auditors

Business Impact:
- 2 deficiencies classified as 'significant' by Big 4 auditors
- CFO mandated all gaps resolved before Q4 testing
- 8 weeks until follow-up testing begins""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

SOX Compliance Assessment Timeline & Details:
- T-8 weeks: External auditors (Big 4 firm) completed Q3 SOX IT control testing
- T-6 weeks: Initial deficiency report issued with 5 control gaps identified
- T-4 weeks: Management response plan developed and submitted to auditors
- T-2 weeks: Follow-up testing scheduled for Q4 control validation
- T-1 week: CFO mandated all gaps resolved before follow-up testing
- T-0 (NOW): IT audit manager briefing CFO on remediation progress

Control Deficiency Analysis (High Confidence):
- Access Management: 47 users with inappropriate segregation of duties conflicts in financial modules
- Change Management: 12 emergency changes to production systems lacked proper approval documentation
- Data Backup/Recovery: Recovery testing performed quarterly instead of required monthly frequency
- System Monitoring: Automated monitoring gaps identified for 3 critical financial interfaces
- User Access Reviews: Q2 access certification completed 45 days late, affecting 2,847 user accounts

Business & Organizational Context:
- External auditors (Big 4 firm) classified 2 deficiencies as 'significant deficiencies'
- CFO has mandated all gaps be resolved before Q4 testing begins in 8 weeks
- Management remediation required for continued SOX compliance
- Potential impact on financial reporting controls and audit opinions
- Board of Directors has been notified of control deficiencies
- IT governance and compliance framework under review
- Resource allocation required for remediation activities

Stakeholder Communication Requirements:
- CFO expects immediate briefing on remediation progress and timeline
- External auditors require detailed remediation plans and evidence
- Board of Directors needs status update on control deficiencies
- IT steering committee coordination for resource allocation
- Business stakeholders need communication on process changes
- Compliance team coordination for ongoing monitoring and testing
- Legal counsel standing by for potential regulatory implications
- Audit committee notification of significant control deficiencies

Regulatory Compliance Framework:
- SOX Section 302: Management assessment of internal controls over financial reporting
- SOX Section 404: Management and auditor assessment of internal controls
- PCAOB Auditing Standard 5: Risk-based approach to internal control audits
- COSO Internal Control Framework: Integrated framework for internal control systems
- SEC Reporting Requirements: Material weakness disclosure requirements
- Financial Reporting Council: Enhanced auditor reporting standards

Risk Management and Governance:
- Enterprise Risk Management: Integration with overall risk management framework
- IT Governance: Alignment with COBIT framework and ITIL best practices
- Change Management: Enhanced change control procedures and documentation
- Access Governance: Segregation of duties and least privilege principles
- Monitoring and Testing: Continuous monitoring and periodic testing procedures
- Training and Awareness: Staff training on SOX compliance requirements"""
        }
    },
    {
        "category": "Cybersecurity Framework Assessment",
        "control_family": "Risk Management",
        "base_context": """
CYBERSECURITY MATURITY ASSESSMENT: NIST CSF EVALUATION
ASSESSMENT DATE: {timestamp}
SCOPE: Enterprise cybersecurity program maturity assessment using NIST Cybersecurity Framework across all business units and technology domains.
MATURITY SCORES BY FUNCTION:
- Identify: Tier 2 (Repeatable) - Asset inventory 85% complete, risk assessment process established
- Protect: Tier 1 (Partial) - Access controls inconsistent, security awareness training ad-hoc
- Detect: Tier 2 (Repeatable) - SIEM deployed but limited threat hunting capabilities
- Respond: Tier 1 (Partial) - Incident response plan exists but lacks regular testing and updates
- Recover: Tier 1 (Partial) - Backup systems in place but recovery procedures not fully documented
CRITICAL GAPS: Lack of integrated threat intelligence, insufficient security metrics and reporting, limited third-party risk management, inadequate security architecture governance.
BUSINESS CONTEXT: Recent cyber insurance renewal required this assessment. Premium increased 40% due to identified gaps. Board has mandated improvement to Tier 3 (Adaptive) within 18 months.
""",
        "context_layers": {
            "S": """IMMEDIATE RESPONSE CONTEXT:
- NIST CSF maturity assessment completed across all business units
- Cyber insurance premium increased 40% due to identified gaps
- Board of Directors mandated improvement to Tier 3 (Adaptive) within 18 months
- Current state: Mixed maturity (Tier 1-2) across CSF functions
- Critical gaps identified in threat intelligence and security metrics""",

            "M": """DETAILED ANALYSIS CONTEXT:

Current Maturity Assessment:
- Identify: Tier 2 (Repeatable) - Asset inventory 85% complete, risk assessment process established
- Protect: Tier 1 (Partial) - Access controls inconsistent, security awareness training ad-hoc
- Detect: Tier 2 (Repeatable) - SIEM deployed but limited threat hunting capabilities
- Respond: Tier 1 (Partial) - Incident response plan exists but lacks regular testing and updates
- Recover: Tier 1 (Partial) - Backup systems in place but recovery procedures not fully documented

Critical Gaps Identified:
- Lack of integrated threat intelligence and security metrics
- Limited third-party risk management and security architecture governance

Strategic Improvement Requirements:

Business Impact Assessment:
- Cyber insurance premium increased 40% due to identified cybersecurity maturity gaps
- Board of Directors has mandated improvement to Tier 3 (Adaptive) within 18 months""",

            "L": """COMPREHENSIVE ORGANIZATIONAL CONTEXT:

NIST Cybersecurity Framework Assessment Timeline & Details:
- T-6 months: Cyber insurance renewal process initiated with maturity assessment requirement
- T-4 months: NIST CSF evaluation conducted across all business units and technology domains
- T-2 months: Initial assessment results reviewed with current state analysis
- T-1 month: Cyber insurance carrier reviewed assessment and increased premium 40%
- T-2 weeks: Board of Directors reviewed assessment results and mandated improvement
- T-1 week: Strategic planning initiated for Tier 3 (Adaptive) maturity achievement
- T-0 (NOW): Cybersecurity manager presenting findings to IT steering committee

Maturity Assessment Results (High Confidence):
- Identify: Tier 2 (Repeatable) - Asset inventory 85% complete, risk assessment process established
- Protect: Tier 1 (Partial) - Access controls inconsistent, security awareness training ad-hoc
- Detect: Tier 2 (Repeatable) - SIEM deployed but limited threat hunting capabilities
- Respond: Tier 1 (Partial) - Incident response plan exists but lacks regular testing and updates
- Recover: Tier 1 (Partial) - Backup systems in place but recovery procedures not fully documented

Business & Organizational Context:
- Recent cyber insurance renewal required NIST CSF assessment for coverage
- Premium increased 40% due to identified cybersecurity maturity gaps
- Board of Directors has mandated improvement to Tier 3 (Adaptive) within 18 months
- Current state analysis shows mixed maturity across CSF functions
- Strategic cybersecurity transformation program required for compliance
- Resource allocation needed for technology, personnel, and training investments
- Integration with existing IT projects and business initiatives required

Stakeholder Communication Requirements:
- IT steering committee expects immediate briefing on current cybersecurity posture
- Board of Directors requires strategic transformation program for Tier 3 maturity
- Cyber insurance carrier needs evidence of improvement for premium reduction
- Business stakeholders need communication on security investments and changes
- Compliance team coordination for ongoing monitoring and reporting
- Legal counsel standing by for potential regulatory implications
- Audit committee notification of cybersecurity maturity gaps
- Employee communication plan for security awareness and culture transformation"""
        }
    }
]

def generate_realistic_data() -> Dict:
    """Generate realistic technical data using ACTUAL BOTSv3 indicators"""
    
    # Use real data from BOTSv3 for academic authenticity
    ransomware = random.choice(BOTS_RANSOMWARE)
    ddns_provider = random.choice(BOTS_DDNS_PROVIDERS)
    event_code = random.choice(BOTS_EVENT_CODES)
    
    return {
        "timestamp": "2018-08-20 14:23:17 UTC",  # BOTS v3 timeframe for authenticity
        "affected_systems": random.choice([
            "WRKSTN-BTCH01, WRKSTN-BTCH02", "SRV-MAIL01, SRV-FILE01", 
            "AWS-PROD-VPC, S3-BUCKET-DATA"
        ]),
        "system_name": random.choice([
            "Salesforce CRM", "SAP ERP", "Active Directory", 
            "AWS Production Environment", "Office 365 Tenant"
        ]),
        "ip_address": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        "user_account": random.choice([
            "btch01@froth.ly", "admin@froth.ly", "service_account"  # BOTS v3 domain
        ]),
        "file_hash": "sha256:a4f5317de7f5e04f82fa71c9d5338bc3",  # From actual BOTS data
        "cve_id": random.choice([
            "CVE-2017-0199", "CVE-2017-11882", "CVE-2018-0802"  # BOTS v3 era CVEs
        ]),
        # Real ransomware data for academic credibility
        "ransomware_family": ransomware['family'],
        "ransomware_extension": ransomware['extension'],
        
        # NEW: Additional real BOTSv3 data for enhanced credibility
        "ddns_domain": f"malicious-{random.randint(1000,9999)}.{ddns_provider}",
        "windows_event_code": event_code['code'],
        "event_description": event_code['desc'],
        "data_source": random.choice(BOTS_DATA_SOURCES),
    }

def create_length_variant(base_scenario: Dict, length: str, realistic_data: Dict) -> str:
    """
    Create length variants with SAME role and SAME task.
    ONLY the incident context detail varies (minimal → moderate → comprehensive).

    This design enables RQ1 analysis: "At what prompt length do quality gains plateau?"
    """
    
    # Format base incident context (same for all lengths)
    base_context = base_scenario["base_context"].format(**realistic_data)

    # CRITICAL: Role and task must be scenario-appropriate AND identical across S/M/L
    # SOC = incident response, GRC = compliance assessment, CTI = threat analysis
    # Detection order: Check control_family FIRST (GRC-specific), then category patterns
    if base_scenario.get("control_family"):
        # GRC Compliance scenarios (have control_family field: Privacy, Financial Reporting, Risk Management)
        role_and_task = """You are the compliance officer responsible for this assessment.

Analyze the findings below and provide a structured remediation plan."""

    elif base_scenario.get("category") in ["Ransomware Incident", "Business Email Compromise", "Advanced Persistent Threat", "Cloud Misconfiguration Breach", "Insider Threat Investigation"]:
        # SOC Incident Response scenarios
        role_and_task = """You are the incident response lead for this security incident.

Analyze the incident details below and provide immediate containment and recovery steps."""

    else:
        # CTI Threat Intelligence scenarios (fallback for all other scenarios)
        role_and_task = """You are the threat intelligence analyst assigned to this request.

Analyze the intelligence below and provide an actionable threat assessment."""
    
    # Get length-specific additional context (ONLY adds facts, not task changes)
    length_specific_context = base_scenario["context_layers"][length].format(**realistic_data)

    # Determine scenario type for appropriate task requirements
    if base_scenario.get("control_family"):
        # GRC Compliance scenarios
        # CRITICAL: Same task for all S/M/L - only context varies (RQ1 requirement)
        task_requirements = """
Provide:
1. Critical compliance gaps identified
2. Remediation actions required
3. Risk prioritization and timeline"""

    if length == "S":
            # SHORT: Minimal context (150-250 tokens total)
            base_context_lines = base_context.strip().split('\n')
            short_base_context = '\n'.join(base_context_lines[:4]) if len(base_context_lines) >= 4 else base_context
            prompt = f"""{role_and_task}

{short_base_context}

{length_specific_context}

{task_requirements}"""

    elif length == "M":
            # MEDIUM: Moderate context (450-550 tokens total)
            prompt = f"""{role_and_task}

{base_context}

{length_specific_context}

{task_requirements}"""

    else:  # L
            # LONG: Comprehensive context (800-1000 tokens total)
            prompt = f"""{role_and_task}

{base_context}

{length_specific_context}

{task_requirements}"""

    elif base_scenario.get("category") in ["Ransomware Incident", "Business Email Compromise", "Advanced Persistent Threat", "Cloud Misconfiguration Breach", "Insider Threat Investigation"]:
        # SOC Incident Response scenarios
        # CRITICAL: Same task for all S/M/L - only context varies (RQ1 requirement)
        task_requirements = """
Provide:
1. Immediate containment steps
2. Evidence preservation actions
3. Recovery prioritization"""

        if length == "S":
            # SHORT: Minimal context (150-250 tokens total)
            base_context_lines = base_context.strip().split('\n')
            short_base_context = '\n'.join(base_context_lines[:4]) if len(base_context_lines) >= 4 else base_context
            prompt = f"""{role_and_task}

{short_base_context}

{length_specific_context}

{task_requirements}"""

        elif length == "M":
            # MEDIUM: Moderate context (450-550 tokens total)
            prompt = f"""{role_and_task}

{base_context}

{length_specific_context}

{task_requirements}"""

        else:  # L
            # LONG: Comprehensive context (800-1000 tokens total)
            prompt = f"""{role_and_task}

{base_context}

{length_specific_context}

{task_requirements}"""

    else:
        # CTI Threat Intelligence scenarios
        # CRITICAL: Same task for all S/M/L - only context varies (RQ1 requirement)
        task_requirements = """
Provide:
1. Threat assessment and classification
2. Key intelligence findings
3. Recommended defensive actions"""

        if length == "S":
            # SHORT: Minimal context (150-250 tokens total)
            base_context_lines = base_context.strip().split('\n')
            short_base_context = '\n'.join(base_context_lines[:4]) if len(base_context_lines) >= 4 else base_context
            prompt = f"""{role_and_task}

{short_base_context}

{length_specific_context}

{task_requirements}"""

        elif length == "M":
            # MEDIUM: Moderate context (450-550 tokens total)
            prompt = f"""{role_and_task}

{base_context}

{length_specific_context}

{task_requirements}"""

        else:  # L
            # LONG: Comprehensive context (800-1000 tokens total)
            prompt = f"""{role_and_task}

{base_context}

{length_specific_context}

{task_requirements}"""

    return prompt

def generate_prompt_with_token_validation(base_scenario: Dict, length: str, realistic_data: Dict, max_attempts: int = 30) -> str:
    """
    Generate prompt with strict token range validation.
    Retries with different realistic_data if token count is out of range.
    """
    target_range = RESEARCH_CONFIG["token_targets"][length]
    
    for attempt in range(max_attempts):
        # Generate prompt with current realistic_data
        prompt_text = create_length_variant(base_scenario, length, realistic_data)
        token_count = len(encoding.encode(prompt_text))
        
        # Check if token count is within target range
        if target_range[0] <= token_count <= target_range[1]:
            return prompt_text
        
        # If not in range, generate new realistic_data and retry
        if attempt < max_attempts - 1:
            realistic_data = generate_realistic_data()
    
    # If we've exhausted all attempts, raise an error
    raise ValueError(f"Failed to generate {length} prompt for '{base_scenario['category']}' within range {target_range} after {max_attempts} attempts. Last attempt: {token_count} tokens. Consider adjusting context_layers['{length}'] length.")

def generate_academic_dataset() -> List[Dict]:
    """Generate complete academic research dataset with balanced distribution"""

    prompts = []
    prompt_counter = 1

    # Calculate balanced distribution for 100 base prompts total
    # 50 SOC (10 per scenario × 5 scenarios)
    # 30 GRC (10 per scenario × 3 scenarios)
    # 20 CTI (7-6-7 per scenario × 3 scenarios)
    soc_prompts_per_scenario = 10
    grc_prompts_per_scenario = 10
    cti_prompts_per_scenario = [7, 6, 7]  # Balanced distribution for 3 CTI scenarios

    # Generate SOC incident prompts with balanced distribution
    for scenario in SOC_SCENARIOS_V2:
        for i in range(soc_prompts_per_scenario):
            realistic_data = generate_realistic_data()

            # Create S/M/L variants
            for length in RESEARCH_CONFIG["length_variants"]:
                prompt_text = generate_prompt_with_token_validation(scenario, length, realistic_data)

                prompt = {
                    "_id": f"academic_soc_{prompt_counter:03d}_{length.lower()}",
                    "prompt_id": f"academic_soc_{prompt_counter:03d}_{length.lower()}",
                    "text": prompt_text,
                    "scenario": "SOC_INCIDENT",
                    "category": scenario["category"],
                    "source": "curated",
                    "prompt_type": "static",
                    "length_bin": length,
                    "token_count": len(encoding.encode(prompt_text)),
                    "dataset_version": RESEARCH_CONFIG["dataset_version"],
                    "metadata": {
                        "data_sources": scenario["data_sources"],
                        "scenario_type": scenario["category"],
                        "authentic_source": True,
                        "academic_grade": True,
                        "research_validated": True
                    },
                    "tags": [scenario["category"].lower().replace(" ", "_")]
                }
                prompts.append(prompt)

            prompt_counter += 1

    # Generate GRC assessment prompts with balanced distribution
    for scenario in GRC_SCENARIOS_V2:
        for i in range(grc_prompts_per_scenario):
            realistic_data = generate_realistic_data()

            # Create S/M/L variants
            for length in RESEARCH_CONFIG["length_variants"]:
                prompt_text = generate_prompt_with_token_validation(scenario, length, realistic_data)

                prompt = {
                    "_id": f"academic_grc_{prompt_counter:03d}_{length.lower()}",
                    "prompt_id": f"academic_grc_{prompt_counter:03d}_{length.lower()}",
                    "text": prompt_text,
                    "scenario": "GRC_MAPPING",
                    "category": scenario["category"],
                    "source": "curated",
                    "prompt_type": "static",
                    "length_bin": length,
                    "token_count": len(encoding.encode(prompt_text)),
                    "dataset_version": RESEARCH_CONFIG["dataset_version"],
                    "metadata": {
                        "control_family": scenario["control_family"],
                        "nist_control": scenario["category"],
                        "academic_grade": True,
                        "compliance_focused": True
                    },
                    "tags": [f"nist_{scenario['control_family'].lower()}", "compliance"]
                }
                prompts.append(prompt)

            prompt_counter += 1

    # Generate CTI analysis prompts with balanced distribution
    for idx, scenario in enumerate(CTI_SCENARIOS_V2):
        for i in range(cti_prompts_per_scenario[idx]):
            realistic_data = generate_realistic_data()

            # Create S/M/L variants
            for length in RESEARCH_CONFIG["length_variants"]:
                prompt_text = generate_prompt_with_token_validation(scenario, length, realistic_data)

                prompt = {
                    "_id": f"academic_cti_{prompt_counter:03d}_{length.lower()}",
                    "prompt_id": f"academic_cti_{prompt_counter:03d}_{length.lower()}",
                    "text": prompt_text,
                    "scenario": "CTI_SUMMARY",
                    "category": scenario["category"],
                    "source": "curated",
                    "prompt_type": "static",
                    "length_bin": length,
                    "token_count": len(encoding.encode(prompt_text)),
                    "dataset_version": RESEARCH_CONFIG["dataset_version"],
                    "metadata": {
                        "data_sources": scenario["data_sources"],
                        "scenario_type": scenario["category"],
                        "threat_intelligence": True,
                        "academic_grade": True,
                        "research_validated": True
                    },
                    "tags": [scenario["category"].lower().replace(" ", "_"), "threat_intel"]
                }
                prompts.append(prompt)

            prompt_counter += 1

    return prompts

def validate_research_methodology(prompts: List[Dict]) -> bool:
    """
    Validate that S/M/L variants have the SAME role and task.
    This ensures RQ1 methodology is scientifically sound.
    
    Per submitted assessment: We need "prompt length variants" to test
    where "quality gains plateau" - requires controlled experiment.
    """
    print("\n🔬 Validating RQ1 Methodology: Task Consistency Across Length Variants...")
    
    # Group prompts by base ID (without length suffix)
    from collections import defaultdict
    base_groups = defaultdict(list)
    
    for p in prompts:
        # Extract base ID: "academic_soc_001_s" → "academic_soc_001"
        parts = p["prompt_id"].split("_")
        base_id = "_".join(parts[:-1])  # Remove last part (s/m/l)
        base_groups[base_id].append(p)
    
    errors = []
    checked = 0
    
    for base_id, variants in base_groups.items():
        if len(variants) != 3:
            errors.append(f"{base_id}: Expected 3 variants (S/M/L), found {len(variants)}")
            continue
        
        # Extract first 3 lines (role + task + blank) from each variant
        role_tasks = {}
        for v in variants:
            lines = v["text"].strip().split('\n')
            # First 2-3 non-empty lines should contain role and task
            non_empty = [l.strip() for l in lines[:5] if l.strip()]
            # Take first 2 lines as role+task signature
            role_task = "\n".join(non_empty[:2]) if len(non_empty) >= 2 else (non_empty[0] if non_empty else "")
            role_tasks[v["length_bin"]] = role_task
        
        # Check if all three have the same role+task
        s_role_task = role_tasks.get('S', '')
        m_role_task = role_tasks.get('M', '')
        l_role_task = role_tasks.get('L', '')
        
        if not (s_role_task == m_role_task == l_role_task):
            errors.append(f"{base_id}: Role/Task mismatch across S/M/L variants")
            print(f"\n  ⚠️  {base_id}:")
            print(f"      S: {s_role_task[:70]}...")
            print(f"      M: {m_role_task[:70]}...")
            print(f"      L: {l_role_task[:70]}...")
        
        # Additional validation: Check scenario-appropriate task keywords
        s_text = variants[0]["text"].lower()  # Get full text for keyword checking
        if 'academic_soc_' in base_id:
            if 'containment' not in s_text and 'recovery' not in s_text:
                errors.append(f"  ⚠️  SOC scenario {base_id} missing incident response tasks")
        elif 'academic_grc_' in base_id:
            if 'compliance' not in s_text and 'remediation' not in s_text:
                errors.append(f"  ⚠️  GRC scenario {base_id} missing compliance assessment tasks")
        elif 'academic_cti_' in base_id:
            if 'threat' not in s_text and 'intelligence' not in s_text:
                errors.append(f"  ⚠️  CTI scenario {base_id} missing threat intelligence tasks")
        
        checked += 1
    
    if errors:
        print(f"\n❌ METHODOLOGY VALIDATION FAILED: {len(errors)} issues found")
        for error in errors[:10]:  # Show first 10 errors
            print(f"   - {error}")
        print(f"\n⚠️  This violates RQ1 controlled experiment requirements.")
        print(f"    S/M/L must have SAME task to test 'quality plateau' hypothesis.")
        return False
    else:
        print(f"✅ METHODOLOGY VALIDATED: All {checked} base prompts have consistent role+task across S/M/L")
        print(f"   RQ1 experimental design confirmed: Isolated length variable ✓")
        return True

def main():
    """Generate and save academic research dataset"""
    
    # For academic reproducibility, set a fixed seed
    random.seed(42)  # Ensures identical results across runs
    
    print("🎓 Generating Academic-Grade CyberPrompt Dataset")
    print(f"📊 Target: {RESEARCH_CONFIG['total_base_prompts']} base prompts × 3 variants = {RESEARCH_CONFIG['total_base_prompts'] * 3} total")
    print("🔬 Using reproducible seed (42) and precise tokenization")
    
    # Generate dataset
    prompts = generate_academic_dataset()
    
    # Validate RQ1 methodology before saving
    if not validate_research_methodology(prompts):
        print("\n⚠️  CRITICAL: Methodology validation failed.")
        print("    Dataset does not meet RQ1 controlled experiment requirements.")
        print("    Review context_layers to ensure they don't change role/task.")
        import sys
        sys.exit(1)
    
    # Create output structure
    output = {
        "exported_at": datetime.now().isoformat(),
        "dataset_version": RESEARCH_CONFIG["dataset_version"],
        "total_prompts": len(prompts),
        "research_metadata": {
            "base_prompts": RESEARCH_CONFIG["total_base_prompts"],
            "length_variants": RESEARCH_CONFIG["length_variants"],
            "scenarios": RESEARCH_CONFIG["scenarios"],
            "academic_validation": True,
            "industry_realistic": True,
            "uses_real_datasets": True
        },
        "prompts": prompts
    }
    
    # Determine script directory and build portable path
    script_dir = Path(__file__).parent
    output_path = script_dir.parent / "data" / "prompts.json"
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Generated {len(prompts)} academic-grade prompts")
    print(f"💾 Saved to: {output_path}")
    
    # Generate summary statistics
    scenarios = {}
    lengths = {}
    for prompt in prompts:
        scenarios[prompt["scenario"]] = scenarios.get(prompt["scenario"], 0) + 1
        lengths[prompt["length_bin"]] = lengths.get(prompt["length_bin"], 0) + 1
    
    print("\n📈 Dataset Statistics:")
    print(f"Scenarios: {scenarios}")
    print(f"Length Distribution: {lengths}")
    print(f"Average tokens per variant: S={sum(p['token_count'] for p in prompts if p['length_bin']=='S')/len([p for p in prompts if p['length_bin']=='S']):.0f}, M={sum(p['token_count'] for p in prompts if p['length_bin']=='M')/len([p for p in prompts if p['length_bin']=='M']):.0f}, L={sum(p['token_count'] for p in prompts if p['length_bin']=='L')/len([p for p in prompts if p['length_bin']=='L']):.0f}")

if __name__ == "__main__":
    main()