# Sample Prompts - CyberPrompt Academic Dataset v4

**Dataset Version**: 20250107_academic_v4_rq1_controlled  
**Purpose**: Demonstration of S/M/L length variants with controlled experiment design

---

## Sample S (Short) - 150-250 Tokens

**Prompt ID**: academic_soc_001_s
**Token Count**: 152
**Scenario**: SOC_INCIDENT
**Category**: Ransomware Incident

### Prompt Text:
```
You are the incident response lead for this security incident.

Analyze the incident details below and provide immediate containment and recovery steps.

INCIDENT REPORT: URGENT - SEVERITY 1
TIMESTAMP: 2018-08-20 14:23:17 UTC
AFFECTED SYSTEMS: Critical file server AWS-PROD-VPC, S3-BUCKET-DATA and 25 workstations in the Finance department are reporting encrypted files with the '.korrektor' extension.
MALWARE TYPE: Rector ransomware

IMMEDIATE RESPONSE CONTEXT:
- Finance operations halted
- CFO demanding updates
- Quarterly reporting deadline next week

Provide:
1. Immediate containment steps
2. Evidence preservation actions
3. Recovery prioritization
```

---

## Sample M (Medium) - 450-550 Tokens

**Prompt ID**: academic_soc_001_m
**Token Count**: 501
**Scenario**: SOC_INCIDENT
**Category**: Ransomware Incident

### Prompt Text:
```
You are the incident response lead for this security incident.

Analyze the incident details below and provide immediate containment and recovery steps.

INCIDENT REPORT: URGENT - SEVERITY 1
TIMESTAMP: 2018-08-20 14:23:17 UTC
AFFECTED SYSTEMS: Critical file server AWS-PROD-VPC, S3-BUCKET-DATA and 25 workstations in the Finance department are reporting encrypted files with the '.korrektor' extension.
MALWARE TYPE: Rector ransomware

DETAILED ANALYSIS CONTEXT:

Threat Actor Details:
- Rector ransomware variant (known for targeting financial institutions)
- Finance department specifically targeted (25 workstations affected)
- Critical infrastructure compromised (file server and S3 bucket)
- Encryption extension: .korrektor (signature of Rector variant)

Investigation Requirements:
- Immediate containment to prevent lateral spread
- Evidence preservation for forensic analysis
- Recovery prioritization based on business impact
- Coordination with finance team for operational continuity

Business Impact:
- Finance operations completely halted
- Quarterly reporting deadline next week
- CFO demanding immediate updates and resolution timeline
- Potential regulatory compliance issues
- Customer financial data at risk

Technical Environment:
- AWS production environment (AWS-PROD-VPC)
- S3 bucket containing critical data
- 25 workstations in Finance department
- Network segmentation considerations

Provide:
1. Immediate containment steps
2. Evidence preservation actions
3. Recovery prioritization
```

---

## Sample L (Long) - 800-1000 Tokens

**Prompt ID**: academic_soc_001_l
**Token Count**: 891
**Scenario**: SOC_INCIDENT
**Category**: Ransomware Incident

### Prompt Text:
```
You are the incident response lead for this security incident.

Analyze the incident details below and provide immediate containment and recovery steps.

INCIDENT REPORT: URGENT - SEVERITY 1
TIMESTAMP: 2018-08-20 14:23:17 UTC
AFFECTED SYSTEMS: Critical file server AWS-PROD-VPC, S3-BUCKET-DATA and 25 workstations in the Finance department are reporting encrypted files with the '.korrektor' extension.
MALWARE TYPE: Rector ransomware

COMPREHENSIVE ORGANIZATIONAL CONTEXT:

Attack Timeline & Technical Details:
- T-0 (NOW): Finance team reports encrypted files with .korrektor extension
- T-15 minutes: Initial assessment shows 25 workstations affected
- T-30 minutes: Critical file server AWS-PROD-VPC compromised
- T-45 minutes: S3-BUCKET-DATA showing encryption activity
- T-60 minutes: Full scope assessment reveals Rector ransomware variant

Technical Indicators (High Confidence):
- Ransomware variant: Rector (known for targeting financial institutions)
- Encryption extension: .korrektor (signature of Rector variant)
- Affected systems: Critical file server, S3 bucket, 25 workstations
- Network scope: Finance department network segment
- Data at risk: Financial records, customer data, quarterly reports

Business & Organizational Context:
- Finance department operations completely halted
- Quarterly reporting deadline next week (regulatory requirement)
- CFO demanding immediate updates and resolution timeline
- Potential SEC filing delays and regulatory compliance issues
- Customer financial data and PII at risk
- Business continuity planning activated
- Legal counsel notified of potential data breach
- Cyber insurance carrier contacted
- Board of Directors briefed on incident severity

Stakeholder Communication Requirements:
- CFO and Finance team expect immediate containment and recovery timeline
- Legal team requires incident details for regulatory compliance assessment
- Customer service team needs communication templates for potential inquiries
- IT operations team coordinating with cloud providers for infrastructure support
- HR department preparing for potential employee impact and communication
- Public relations team standing by for potential media inquiries
- Board of Directors requiring detailed incident report and business impact assessment

Regulatory and Compliance Considerations:
- Potential GDPR/CCPA notification requirements if customer data compromised
- SOX compliance implications for quarterly reporting delays
- Financial services regulatory requirements for incident reporting
- Cyber insurance claim process initiation
- Legal discovery and evidence preservation requirements

Recovery and Business Continuity:
- Finance operations alternative procedures activation
- Customer service escalation procedures
- Vendor and partner notification requirements
- Supply chain impact assessment
- Operational continuity planning execution

Provide:
1. Immediate containment steps
2. Evidence preservation actions
3. Recovery prioritization
```

---

## Key Design Features

### Controlled Experiment Design
- **Identical Task Requirements**: All S/M/L variants request the same deliverables
- **Varying Context Only**: Length differences come from context detail, not task changes
- **Same Role Assignment**: Consistent role across all variants
- **Same Scenario Type**: Identical base scenario across length variants

### Token Range Validation
- **S (Short)**: Optimized for emergency response contexts (150-250 tokens)
- **M (Medium)**: Balanced for investigation and analysis (450-550 tokens)  
- **L (Long)**: Comprehensive for strategic planning (800-1000 tokens)

### Authentic Data Integration
- **BOTSv3 Dataset**: Real ransomware families, C2 infrastructure, Windows event codes
- **NIST Frameworks**: Authentic cybersecurity controls and compliance requirements
- **Industry Standards**: SANS, ISO 27001, and regulatory framework alignment

---

*Sample prompts extracted from actual dataset for Assignment 3A Research Outputs Portfolio*