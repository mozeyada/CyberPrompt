# app/judges/prompts.py

JUDGE_V2 = """You are a strict evaluator for SOC/GRC documentation quality.

CONTEXT:
- Scenario: {scenario}
- Evaluation focus: {focus_desc}
- The model output to score is inside <output></output>.
- Score each dimension on an integer scale 0–5 (0=unacceptable, 5=excellent).
- IMPORTANT: Do NOT return a 'hallucination' field. That metric is computed separately.

SCORING DIMENSIONS:
- technical_accuracy: factual correctness in a SOC/GRC context
- actionability: can an analyst/auditor act on it without extra steps?
- completeness: covers all key aspects implied by the task
- compliance_alignment: aligns with policy/regulatory tone/structure
- risk_awareness: acknowledges risk, limitations, uncertainty
- relevance: stays on-task; no digressions
- clarity: clear, structured, unambiguous writing

Return strict JSON:
{{
 "technical_accuracy": int,
 "actionability": int,
 "completeness": int,
 "compliance_alignment": int,
 "risk_awareness": int,
 "relevance": int,
 "clarity": int,
 "notes": "one-paragraph rationale"
}}

{granularity_demos}

<output>
{model_output}
</output>
"""

JUDGE_V1 = """Evaluate this SOC/GRC output on a 0-5 scale for each dimension:

Output to evaluate:
{model_output}

Return JSON with scores for: technical_accuracy, actionability, completeness, compliance_alignment, risk_awareness, relevance, clarity, and notes.
"""

JUDGE_PROMPTS = {
    "v1": JUDGE_V1,
    "v2": JUDGE_V2,
}


def get_judge_prompt(version: str = "v2") -> str:
    """Get judge prompt by version"""
    return JUDGE_PROMPTS.get(version, JUDGE_V2)
