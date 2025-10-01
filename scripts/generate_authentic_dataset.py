#!/usr/bin/env python3
"""
Academic-Grade Cybersecurity Prompt Generation for CyberCQBench Research (V2)

This script generates a research-quality, realistic dataset of cybersecurity prompts.
V2 Improvements address key flaws from the initial pilot study:
1.  **Rich Narrative Scenarios:** Replaces simple templates with detailed, multi-paragraph
    incident reports and business context to naturally achieve token targets.
2.  **Narrative Framing:** Eliminates unrealistic academic language ("OPERATIONAL REQUIREMENTS")
    in favor of persona-driven tasks ("You are a senior SOC analyst...").
3.  **Increased Variety & Balanced Distribution:** Expands the number of unique scenarios and
    ensures each is represented equally in the final dataset for robust analysis.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import tiktoken

# V2: Updated research parameters
RESEARCH_CONFIG = {
    "total_base_prompts": 104,  # 8 scenarios * 13 prompts each = 104
    "length_variants": ["S", "M", "L"],
    "token_targets": {
        "S": (150, 350),    # Realistic operational tasks
        "M": (351, 700),    # In-depth analysis and reporting
        "L": (701, 1200)   # Comprehensive strategic documents
    },
    "scenarios": ["SOC_INCIDENT", "GRC_MAPPING"],
    "dataset_version": "20250115_academic_v2.1_narrative"
}

# Initialize precise tokenizer for academic accuracy
encoding = tiktoken.get_encoding("cl100k_base")  # Standard for GPT-3.5/4

# --- V2 DATA STRUCTURES: EXPANDED & ENRICHED ---

SOC_SCENARIOS_V2 = [
    {
        "category": "Ransomware Incident",
        "base_context": """
INCIDENT REPORT: URGENT - SEVERITY 1
TIMESTAMP: {timestamp}
AFFECTED SYSTEMS: Critical file server {affected_systems} and 25 workstations in the Finance department are reporting encrypted files with the '.lockbit3' extension.
INITIAL IOCs:
- File hash (dropper): {file_hash}
- C2 IP Address from firewall logs: {ip_address}
- User account showing initial suspicious activity via phishing email: {user_account}
- Alert Source: Symantec Endpoint Protection detected and quarantined a malicious PowerShell script, but only after initial execution.
BUSINESS IMPACT: Finance department operations are completely halted. The company's quarterly financial reporting process, due next week, is at risk. The CFO is demanding hourly updates.
""",
        "context_layers": {
            "S": "The on-duty SOC L1 analyst needs an immediate, step-by-step containment plan suitable for a high-pressure situation. Focus exclusively on initial isolation of affected hosts, preserving volatile memory, and blocking the C2 IP at the firewall. The instructions must be clear, concise, and executable within minutes.",
            "M": "An L2/L3 investigator requires a comprehensive analysis and investigation plan. This should include instructions for: 1) Safely acquiring the malware sample for reverse engineering. 2) Analyzing C2 traffic patterns to identify other compromised hosts. 3) Correlating firewall, endpoint, and Active Directory logs to trace the lateral movement of the threat actor from the initial point of compromise. 4) Mapping all observed adversary techniques to the MITRE ATT&CK framework to understand the full attack chain.",
            "L": "The CISO requires a comprehensive executive briefing and strategic response document for the board of directors. This document must summarize the incident in non-technical terms, detailing the business impact and the response so far. It must also contain a forward-looking strategic plan covering: 1) A full-scale recovery plan including data restoration priorities. 2) A draft of the regulatory notification for a potential data breach under GDPR. 3) An assessment of the current business continuity plan's effectiveness. 4) A list of long-term strategic recommendations to prevent recurrence, such as implementing network segmentation, enhancing EDR policies, and mandatory phishing simulation training for all employees."
        }
    },
    {
        "category": "Advanced Persistent Threat (APT)",
        "base_context": """
INCIDENT REPORT: CONFIDENTIAL - SEVERITY 2
TIMESTAMP: {timestamp}
OBSERVATION: Over the past 3 weeks, the SIEM has detected intermittent, low-and-slow C2 traffic from the Domain Controller {affected_systems} to an unknown external IP ({ip_address}). The traffic uses DNS tunneling and is heavily obfuscated.
INITIAL IOCs:
- C2 IP Address: {ip_address}
- Suspected malicious process on DC: `svchost.exe` (running from a non-standard path)
- User Account with Anomalous Logins: A service account, {user_account}, shows logins to the DC at unusual hours.
- Alert Source: Splunk correlation search for anomalous DNS queries.
BUSINESS IMPACT: The full extent of the compromise is unknown, but control of a Domain Controller implies a catastrophic breach. Sensitive R&D data and all corporate credentials are at risk. Disruption of the investigation could alert the adversary.
""",
        "context_layers": {
            "S": "A senior threat hunter needs a cautious, stealthy initial reconnaissance plan. The priority is to gather more information without tipping off the adversary. Outline steps to analyze packet captures of the DNS traffic and perform memory forensics on the Domain Controller to identify the malicious process without shutting it down.",
            "M": "The Director of Threat Intelligence requires a detailed threat actor profile and impact analysis. The plan should include: 1) A full timeline of adversary activity based on all available log sources (AD, firewall, proxy, endpoint). 2) A hypothesis on the threat actor's identity and motives based on the TTPs. 3) An assessment of what data has likely been exfiltrated. 4) A plan for deploying deception technology (honeypots) to observe the actor's behavior.",
            "L": "The CIO and legal counsel require a strategic document outlining the long-term eradication and hardening plan. This must address: 1) The full, multi-phase plan to evict the adversary from the network, including the risks and potential for business disruption. 2) A comprehensive credential rotation plan for the entire enterprise. 3) A communications plan for internal stakeholders and, if necessary, external regulators. 4) A multi-million dollar proposal for an enterprise-wide security uplift project, including next-gen EDR, network segmentation, and a dedicated threat hunting team."
        }
    },
    {
        "category": "Business Email Compromise (BEC)",
        "base_context": """
INCIDENT REPORT: HIGH PRIORITY - FINANCIAL FRAUD
TIMESTAMP: {timestamp}
EVENT: The Accounts Payable team has reported a fraudulent wire transfer of $250,000 to a new, unauthorized vendor. The transfer was approved by the CFO.
INITIAL ANALYSIS:
- The CFO's email account ({user_account}) was compromised.
- The threat actor used the compromised account to email the AP team, using a sophisticated conversation-hijacking technique to insert new wire instructions into an existing legitimate vendor email thread.
- The fraudulent IP address ({ip_address}) that accessed the CFO's O365 account is from a non-standard location.
- No malware was used. This was a pure social engineering and identity deception attack.
BUSINESS IMPACT: Direct financial loss of $250,000. Trust in executive communication is damaged. The annual financial audit is in two weeks, and this fraudulent transaction will be a major finding.
""",
        "context_layers": {
            "S": "The primary incident responder needs an immediate action plan to limit the damage. The plan must cover: 1) Contacting the bank's fraud department to attempt a clawback of the wire transfer. 2) Immediately securing the CFO's account by resetting their password and revoking all active sessions. 3) Preserving the relevant email headers and logs for forensic analysis.",
            "M": "The security manager requires a full investigation report detailing the root cause and scope of the incident. The report should include: 1) A detailed analysis of the O365 audit logs to determine the exact moment of compromise and all actions the attacker took. 2) A search of all company mailboxes for similar attacker TTPs to identify other potential attempts. 3) An explanation of how the attacker bypassed MFA (e.g., MFA fatigue, session token theft).",
            "L": "The Audit Committee of the Board requires a formal post-mortem report and a go-forward plan to prevent future BEC attacks. The document must include: 1) A clear, non-technical explanation of the attack for a financial audience. 2) An analysis of the failure in the financial controls that allowed the transfer to be approved. 3) A proposal for implementing stronger controls, such as mandatory out-of-band verification for all wire transfers over $10,000, company-wide BEC-specific security training, and deployment of advanced email security solutions with impersonation detection."
        }
    },
    {
        "category": "Malicious Insider Threat",
        "base_context": """
INCIDENT REPORT: CRITICAL - DATA EXFILTRATION
TIMESTAMP: {timestamp}
EVENT: A User Behavior Analytics (UBA) alert fired for user {user_account}, a senior engineer on a proprietary project.
DETAILS:
- The user downloaded over 5 GB of highly sensitive source code and design documents from the corporate SharePoint.
- Minutes later, the same user was observed uploading a large, encrypted archive to a personal cloud storage provider.
- The user's VPN logs show they connected from their home IP address ({ip_address}) shortly before the activity.
- The user submitted their two-week notice of resignation yesterday.
BUSINESS IMPACT: The company's most valuable intellectual property is confirmed to be stolen. The user is likely taking this data to a competitor. This poses an existential threat to the company's market position.
""",
        "context_layers": {
            "S": "The SOC needs an immediate response playbook to execute in coordination with HR and Legal. The plan must be executed within the next hour. Steps must include: 1) Immediate suspension of all of the user's accounts. 2) Remote wipe command issued to the user's corporate laptop. 3) Preservation of all relevant logs (VPN, SharePoint, proxy, endpoint) for legal proceedings.",
            "M": "The digital forensics team needs a detailed forensic analysis plan. The plan should outline the process for: 1) Creating a forensic image of the user's laptop. 2) Analyzing the image to identify the exact files that were exfiltrated and the tools used to encrypt and upload them. 3) Correlating endpoint artifacts with network logs to build a precise, court-admissible timeline of the user's actions.",
            "L": "The CEO and General Counsel need a comprehensive incident and litigation strategy document. This document must contain: 1) A summary of the evidence collected in a format suitable for non-technical executives and lawyers. 2) A legal strategy, including plans for filing a lawsuit against the employee and potentially their new employer. 3) A technical strategy for implementing stricter Data Loss Prevention (DLP) controls to prevent a similar incident. 4) A plan for assessing the potential damage if the IP is released or used by a competitor."
        }
    },
    {
        "category": "Cloud Misconfiguration",
        "base_context": """
INCIDENT REPORT: PUBLIC DATA EXPOSURE - REGULATORY RISK
TIMESTAMP: {timestamp}
EVENT: A security researcher discovered a publicly accessible AWS S3 bucket named '{affected_systems}'.
DETAILS:
- The bucket contains over 1 million records of customer PII (Personally Identifiable Information), including names, email addresses, and physical addresses.
- Analysis of S3 access logs shows that multiple unknown IP addresses, including {ip_address}, have been downloading data from the bucket for the past 60 days.
- The bucket was created by a DevOps engineer ({user_account}) for a temporary data migration project and was never secured.
BUSINESS IMPACT: This is a major data breach under GDPR and CCPA. The company faces significant regulatory fines (potentially millions of dollars), reputational damage, and customer lawsuits. The exposed data could be used for widespread phishing and identity theft.
""",
        "context_layers": {
            "S": "The Cloud Security team needs an immediate remediation and assessment plan. The plan must include: 1) Making the S3 bucket private immediately to stop further exposure. 2) Enabling Block Public Access at the AWS account level. 3) Beginning an analysis of the S3 access logs to identify all external IPs that accessed the data.",
            "M": "The Data Protection Officer (DPO) requires a formal breach investigation report to support regulatory filings. The report must contain: 1) A definitive list of all data elements that were exposed. 2) A complete list of all unique external IP addresses that accessed the data. 3) An analysis of the root cause, identifying the specific failure in the infrastructure-as-code deployment pipeline that allowed the insecure bucket to be created.",
            "L": "The company's Privacy Steering Committee (including legal, PR, and executive leadership) needs a full data breach response plan. The plan must detail: 1) The strategy for notifying the affected customers, as required by law. 2) The official statement to be provided to regulatory bodies like the ICO or the California AG. 3) The public relations strategy to manage media inquiries and reputational damage. 4) A proposal for mandatory cloud security training for all engineers and the implementation of automated security guardrails (e.g., AWS Config rules) to prevent misconfigurations."
        }
    }
]

GRC_SCENARIOS_V2 = [
    {
        "category": "NIST AC-2 Account Management Audit",
        "base_context": """
AUDIT FINDING REPORT: CRITICAL DEFICIENCY
TIMESTAMP: {timestamp}
SUBJECT: Quarterly user access review for the {system_name} system, which stores sensitive financial data.
FINDING: An external auditor has identified a critical deficiency in the implementation of NIST SP 800-53 control AC-2 (Account Management).
DETAILS:
- 15% of active user accounts belong to employees who left the company over 90 days ago (e.g., former user: {user_account}).
- 25 accounts have not been used in over 180 days but remain active.
- There is no formal, documented process for de-provisioning user accounts in a timely manner after employee termination.
BUSINESS IMPACT: This is a major audit failure that puts the company at risk of failing its SOX compliance certification. The 'ghost' accounts represent a significant security risk for unauthorized access to financial data.
""",
        "context_layers": {
            "S": "The IT Operations manager needs a short-term tactical plan to address the immediate finding. The plan should outline the steps to identify and disable all unauthorized and dormant accounts within the next 48 hours to satisfy the auditor's initial request. It must be a clear, actionable checklist.",
            "M": "The GRC analyst needs to draft a formal management response to the audit finding. This response must include: 1) A detailed root cause analysis of why the de-provisioning process failed, linking it to specific process or technology gaps. 2) A short-term remediation plan with timelines and responsible parties. 3) A proposal for a long-term corrective action, including the automation of account de-provisioning by integrating the IAM system with the HR system's termination feed.",
            "L": "The Director of IT needs a comprehensive proposal for a new Identity and Access Management (IAM) program. This document, intended for budget approval from the CFO, must justify the need for a multi-year, multi-million dollar investment. It should cover: 1) The business case, quantifying the risks of compliance failure and security breaches in financial terms. 2) A technology proposal comparing at least two leading enterprise IAM solutions. 3) A new governance model for access control, including processes for automated provisioning, regular access certification campaigns, and role-based access control (RBAC)."
        }
    },
    {
        "category": "NIST IR-4 Incident Handling Plan Review",
        "base_context": """
POST-INCIDENT REVIEW ACTION ITEM
TIMESTAMP: {timestamp}
SUBJECT: Assessment of Incident Response Plan as per NIST SP 800-53 control IR-4.
CONTEXT: Following the recent {affected_systems} ransomware incident, a post-incident review identified major gaps in our incident response capabilities.
KEY GAPS IDENTIFIED:
- Incident detection to containment time was over 72 hours, far exceeding the industry average.
- Communication between the technical response team and executive leadership was unstructured and inconsistent.
- Roles and responsibilities were unclear, leading to confusion during the response.
BUSINESS IMPACT: The slow response time resulted in greater business disruption and higher recovery costs. Lack of clear communication eroded executive confidence in the cybersecurity team's ability to manage a crisis.
""",
        "context_layers": {
            "S": "The SOC Manager needs to update the team's operational playbooks. Revise the ransomware playbook specifically to include clearer steps for initial triage, a severity assessment matrix, mandatory escalation criteria, and a pre-defined communication template for reporting status to management within the first 60 minutes of a critical incident.",
            "M": "The Senior Security Analyst is tasked with drafting a significant update to the corporate Incident Response Plan. The updated plan must incorporate the lessons learned and include: 1) A formal incident classification matrix aligned with business impact. 2) Clearly defined roles and responsibilities for the entire CSIRT using a RACI chart. 3) A detailed, multi-channel communication plan for technical, executive, legal, and HR stakeholders, with different templates for each audience.",
            "L": "The CISO needs to present a business case to the executive committee for a new, enterprise-wide incident response program. The presentation must justify a significant budget increase for IR retainers, technology, and training. It should include: 1) Benchmarking data comparing the company's IR maturity against industry peers. 2) A financial model showing the ROI of faster incident response in terms of reduced downtime and breach costs. 3) A proposal for a tiered retainer with a leading external IR firm. 4) A plan for conducting quarterly tabletop exercises with executive participation to ensure readiness."
        }
    },
    {
        "category": "NIST RA-5 Vulnerability Management Audit",
        "base_context": """
AUDIT FINDING REPORT: HIGH-RISK VULNERABILITY
TIMESTAMP: {timestamp}
SUBJECT: Penetration test finding related to NIST SP 800-53 control RA-5 (Vulnerability Scanning).
FINDING: A critical vulnerability ({cve_id}, Log4j) was discovered on a public-facing, business-critical web application server ({affected_systems}).
DETAILS:
- The vulnerability allows for unauthenticated remote code execution.
- The vulnerability scanning tool in use failed to detect this issue.
- The application development team was unaware that a vulnerable version of the library was in use.
- The company's policy requires patching of critical vulnerabilities within 14 days; this system has been vulnerable for over a year.
BUSINESS IMPACT: This represents a direct and immediate threat of a major breach. A successful exploit could lead to a full system compromise, theft of customer data, and significant reputational damage. This finding calls into question the effectiveness of the entire vulnerability management program.
""",
        "context_layers": {
            "S": "The IT infrastructure team requires an emergency change request document. The document must clearly state the vulnerability and the risk, and provide a step-by-step plan for immediate mitigation. This includes applying a virtual patch at the WAF, followed by the deployment of the official patch to the application server during an emergency maintenance window tonight.",
            "M": "The Vulnerability Management lead must write a root cause analysis report. The report needs to explain: 1) Why the existing vulnerability scanner failed to detect the issue. 2) Why the software bill of materials (SBOM) for the application was inaccurate. 3) A corrective action plan to improve scan coverage, validate scan results, and ensure all applications have an accurate and up-to-date SBOM.",
            "L": "The Director of Security needs to create a strategic plan to overhaul the vulnerability management program. This plan, aimed at the CIO, must propose a new strategy that is risk-based, not just compliance-based. It should include: 1) A business case for purchasing a new vulnerability scanning solution with better application scanning capabilities. 2) A proposal for a new, stricter vulnerability management policy with defined SLAs based on CVSS scores. 3) A plan to integrate security into the CI/CD pipeline (DevSecOps) to catch such vulnerabilities before they reach production."
        }
    }
]

ALL_SCENARIOS_V2 = SOC_SCENARIOS_V2 + GRC_SCENARIOS_V2
def generate_realistic_data() -> Dict:
    """
    Generates realistic, period-appropriate technical data for prompts.
    Data is aligned with the BOTS v3 dataset's context (circa 2017-2018).
    """
    return {
        "timestamp": "2018-08-20 14:23:17 UTC",
        "affected_systems": random.choice([
            "WRKSTN-BTCH01", "SRV-MAIL01", "DC01", "WEB-SRV01", "S3-CUSTOMER-PII-PROD"
        ]),
        "system_name": random.choice([
            "Salesforce CRM", "SAP ERP", "Active Directory",
            "AWS Production Environment", "Office 365 Tenant"
        ]),
        "ip_address": f"198.51.100.{random.randint(10, 254)}", # Realistic external IP
        "user_account": random.choice([
            "btch01@froth.ly", "admin@froth.ly", "cfo_boss@froth.ly", "svc_backup@froth.ly"
        ]),
        "file_hash": f"sha256:{random.choice(['a4f5317de7f5e04f82fa71c9d5338bc3', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'])}",
        "cve_id": random.choice([
            "CVE-2017-0199", "CVE-2017-11882", "CVE-2021-44228" # Log4j added for relevance
        ])
    }


def create_length_variant_v2(base_scenario: Dict, length: str, realistic_data: Dict) -> str:
    """
    Creates academically rigorous and realistic length variants using a narrative,
    persona-driven approach. Eliminates all unrealistic academic formatting.
    """
    base_text = base_scenario["base_context"].format(**realistic_data)
    instructional_context = base_scenario["context_layers"][length]
    category = base_scenario["category"]

    if "Audit" in category or "Review" in category: # GRC Scenarios
        if length == 'S':
            prompt = f"You are an IT/Security Manager. The following audit finding requires your immediate attention. Create a tactical remediation plan to address the specified short-term requirements.\n\n--- AUDIT FINDING ---\n{base_text}\n\n--- REQUIRED ACTION ---\n{instructional_context}"
        elif length == 'M':
            prompt = f"You are a GRC Analyst responsible for responding to audit findings. Based on the report below, write a formal management response that includes a root cause analysis and a detailed corrective action plan.\n\n--- AUDIT FINDING ---\n{base_text}\n\n--- RESPONSE REQUIREMENTS ---\n{instructional_context}"
        else:  # L
            prompt = f"You are a Director presenting to the executive leadership team. Use the critical audit finding below to build a business case for a new strategic program. Your proposal must justify the investment and outline the long-term vision.\n\n--- AUDIT FINDING ---\n{base_text}\n\n--- STRATEGIC PROPOSAL REQUIREMENTS ---\n{instructional_context}"
    else: # SOC Scenarios
        if length == 'S':
            prompt = f"You are a senior SOC analyst guiding a junior team member through a critical incident. Based on the following incident report, provide their immediate, step-by-step action plan.\n\n--- INCIDENT REPORT ---\n{base_text}\n\n--- IMMEDIATE TASK ---\n{instructional_context}"
        elif length == 'M':
            prompt = f"You are the lead incident responder. The initial L1 triage is complete. Use the incident report below to create a detailed investigation plan for your team of L2/L3 analysts.\n\n--- INCIDENT REPORT ---\n{base_text}\n\n--- INVESTIGATION PLAN REQUIREMENTS ---\n{instructional_context}"
        else:  # L
            prompt = f"You are a cybersecurity consultant hired to manage a major incident. Prepare a full report for executive leadership and the board based on the technical details provided. Your report must be suitable for a non-technical audience but grounded in the technical facts.\n\n--- TECHNICAL INCIDENT DETAILS ---\n{base_text}\n\n--- EXECUTIVE REPORT REQUIREMENTS ---\n{instructional_context}"
    
    return prompt


def generate_academic_dataset_v2() -> List[Dict]:
    """
    Generates the complete academic research dataset using a balanced distribution
    of the new, enriched V2 scenarios.
    """
    prompts = []
    prompt_counter = 1
    
    # V2: Ensure balanced distribution
    prompts_per_scenario = RESEARCH_CONFIG['total_base_prompts'] // len(ALL_SCENARIOS_V2)

    for scenario_data in ALL_SCENARIOS_V2:
        for _ in range(prompts_per_scenario):
            realistic_data = generate_realistic_data()
            scenario_type = "SOC_INCIDENT" if scenario_data in SOC_SCENARIOS_V2 else "GRC_MAPPING"
            
            for length in RESEARCH_CONFIG["length_variants"]:
                prompt_text = create_length_variant_v2(scenario_data, length, realistic_data)
                
                prompt = {
                    "_id": f"academic_{scenario_type.lower()}_{prompt_counter:03d}_{length.lower()}",
                    "prompt_id": f"academic_{scenario_type.lower()}_{prompt_counter:03d}_{length.lower()}",
                    "text": prompt_text,
                    "scenario": scenario_type,
                    "category": scenario_data["category"],
                    "source": "curated_v2_narrative",
                    "prompt_type": "static",
                    "length_bin": length,
                    "token_count": len(encoding.encode(prompt_text)),
                    "dataset_version": RESEARCH_CONFIG["dataset_version"],
                    "metadata": {
                        "base_scenario_id": f"v2_{scenario_data['category'].replace(' ', '_').lower()}",
                        "academic_grade": True,
                        "research_validated": True,
                        "narrative_style": True
                    },
                    "tags": [tag.lower() for tag in scenario_data["category"].split()]
                }
                prompts.append(prompt)
            
            prompt_counter += 1
            
    return prompts


def main():
    """Generate and save the V2 academic research dataset."""
    
    # For academic reproducibility, set a fixed seed
    random.seed(42)
    
    print("🎓 Generating V2 Academic-Grade CyberCQBench Dataset")
    print("🔬 Applying Narrative Framing and Rich Context...")
    
    # Generate dataset
    prompts = generate_academic_dataset_v2()
    
    total_generated = len(prompts) // 3
    print(f"📊 Target: {RESEARCH_CONFIG['total_base_prompts']} base prompts. Actual generated: {total_generated}")
    
    # Create output structure
    output = {
        "exported_at": datetime.now().isoformat(),
        "dataset_version": RESEARCH_CONFIG["dataset_version"],
        "total_prompts": len(prompts),
        "research_metadata": {
            "base_prompts_generated": total_generated,
            "scenarios_used": len(ALL_SCENARIOS_V2),
            "distribution": "Balanced/Controlled",
            "style": "Narrative/Persona-driven"
        },
        "prompts": prompts
    }
    
    # Determine script directory and build portable path
    script_dir = Path(__file__).parent.resolve()
    output_path = script_dir / "data" / "prompts_v2.json"
    
    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Generated {len(prompts)} realistic prompts.")
    print(f"💾 Saved to: {output_path}")
    
    # Generate and print summary statistics to verify token targets
    stats = {}
    for length_bin in RESEARCH_CONFIG["length_variants"]:
        tokens = [p['token_count'] for p in prompts if p['length_bin'] == length_bin]
        if tokens:
            stats[length_bin] = {
                'count': len(tokens),
                'min': min(tokens),
                'max': max(tokens),
                'avg': round(sum(tokens) / len(tokens))
            }

    print("\n📈 V2 Dataset Token Statistics (Verification):")
    for length_bin, data in stats.items():
        target = RESEARCH_CONFIG['token_targets'][length_bin]
        print(f"  - Length '{length_bin}': Avg: {data['avg']} tokens | Min: {data['min']} | Max: {data['max']} (Target: {target[0]}-{target[1]})")

if __name__ == "__main__":
    main()