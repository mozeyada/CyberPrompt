# app/judges/prompts.py

# Calibrated judge prompt with 5-point scale for better discrimination
JUDGE_PROMPT = """You are an expert evaluator for cybersecurity outputs.

PROMPT:
{context}

RESPONSE:
{model_output}

TASK: Evaluate how well the response addresses the prompt for {scenario}.

Score each dimension (0-5 scale, use FULL range):

1. TECHNICAL_ACCURACY: Factual correctness, terminology, real-world alignment
   0-2: Hallucinations, wrong concepts | 3: Basic facts correct | 4: Accurate with some citations | 5: Perfect with multiple verified references (CVE/MITRE/NIST)

2. ACTIONABILITY: Step-by-step, operationally usable security guidance
   0-2: Generic advice | 3: Some steps provided | 4: Clear process with tools | 5: Complete playbook with commands/configs

3. COMPLETENESS: Fulfills ALL prompt requirements including context nuances
   0-2: Missing key requirements | 3: Literal requirements met | 4: Requirements + some context | 5: Every requirement + ALL contextual details addressed

4. COMPLIANCE_ALIGNMENT: Adherence to regulatory frameworks
   0-2: No frameworks | 3: Generic mention (e.g., "follow GDPR") | 4: Specific framework cited | 5: Multiple frameworks with control mappings

5. RISK_AWARENESS: Identifies, analyzes, and mitigates risks
   0-2: No risk analysis | 3: Risk mentioned | 4: Risk with impact/likelihood | 5: Complete risk matrix with mitigation strategies

6. RELEVANCE: Alignment with specific prompt context and goal
   0-2: Off-topic | 3: Generally relevant | 4: On-target for prompt | 5: Perfectly tailored to specific context/scenario

7. CLARITY: Structural clarity for practitioners
   0-2: Confusing | 3: Readable | 4: Clear structure | 5: Professional formatting with visual aids

BE STRICT: Reserve 5 for truly exceptional responses. Most good responses should score 3-4.

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
