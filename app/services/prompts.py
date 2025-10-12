# app/judges/prompts.py

# Balanced judge prompt - concise with clear Low/High anchors for calibration
JUDGE_PROMPT = """You are an expert evaluator for cybersecurity outputs.

PROMPT:
{context}

RESPONSE:
{model_output}

TASK: Evaluate how well the response addresses the prompt for {scenario}.

Score each dimension (0-5):

1. TECHNICAL_ACCURACY: Factual correctness, terminology, real-world alignment
   Low: Hallucinated threats/tools, misused concepts (hashing vs encryption)
   High: Verified claims with MITRE, CVE, or NIST references

2. ACTIONABILITY: Step-by-step, operationally usable security guidance
   Low: Generic summaries without task guidance
   High: Detailed instructions (containment, triage, ISO/NIST controls)

3. COMPLETENESS: Fulfills all prompt requirements and security context
   Low: Omits prompt tasks or partial information
   High: Every aspect addressed with contextual security details

4. COMPLIANCE_ALIGNMENT: Adherence to regulatory frameworks and policies
   Low: Policy-violating suggestions
   High: Explicitly maps to NIST 800-53, ISO 27001, GDPR

5. RISK_AWARENESS: Identifies, analyzes, and mitigates risks
   Low: Ignores threat implications, impact, likelihood
   High: Threat modeling, risk matrices, control strategies

6. RELEVANCE: Alignment with specific prompt context and goal
   Low: Drifts from prompt intent or unrelated content
   High: Directly addresses task with domain-relevant terminology

7. CLARITY: Structural clarity for practitioners
   Low: Ambiguous, jargon-heavy, convoluted language
   High: Clear, concise, readable; proper formatting

Return JSON only:
{{
 "technical_accuracy": int,
 "actionability": int,
 "completeness": int,
 "compliance_alignment": int,
 "risk_awareness": int,
 "relevance": int,
 "clarity": int,
 "notes": "brief rationale"
}}

{granularity_demos}"""


def get_judge_prompt(version: str = "default") -> str:
    """Get judge prompt - version parameter kept for backward compatibility"""
    return JUDGE_PROMPT
