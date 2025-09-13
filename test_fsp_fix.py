#!/usr/bin/env python3
"""
Test script to verify FSP bias mitigation fix
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.base import LLMJudge
from app.services.llm_client import ModelRunner
from app.models import ScenarioType, LengthBin
from app.core.config import settings

async def test_fsp_bias_mitigation():
    """Test that FSP reduces scores for verbose responses"""
    
    # Sample verbose response (similar to the ones in the database)
    verbose_output = """
    By following the outlined phases and recommendations, our organization can effectively respond to the current cloud attack incident, mitigate risks, and strengthen our cybersecurity posture for the future. It is crucial to prioritize proactive measures, continuous monitoring, and ongoing training to ensure our organization remains resilient against evolving cyber threats.

    The incident response process should include immediate containment measures, thorough investigation procedures, and comprehensive recovery protocols. We must also ensure proper documentation throughout the process to support forensic analysis and compliance requirements.

    Additionally, we should implement enhanced monitoring capabilities, update our security policies and procedures, and conduct regular security awareness training for all personnel. This multi-layered approach will help prevent similar incidents in the future and improve our overall security posture.

    Furthermore, it is essential to establish clear communication channels during incident response, maintain regular backups of critical data, and ensure that all security tools and systems are properly configured and maintained. Regular testing of our incident response procedures through tabletop exercises and simulations will help identify areas for improvement.
    """
    
    # Initialize model runner and judge
    model_runner = ModelRunner(
        openai_key=settings.openai_api_key,
        anthropic_key=settings.anthropic_api_key,
        google_key=settings.google_api_key,
    )
    
    judge_client = model_runner._get_client("gpt-4o-mini")
    judge = LLMJudge("gpt-4o-mini", judge_client, "v2")
    
    print("Testing FSP bias mitigation...")
    print(f"Output length: {len(verbose_output)} chars, {len(verbose_output.split())} words")
    print()
    
    # Test without FSP
    print("1. Evaluating WITHOUT FSP (standard evaluation)...")
    standard_result = await judge.evaluate(
        output=verbose_output,
        scenario=ScenarioType.GRC_MAPPING,
        length_bin=LengthBin.L,
        bias_controls={"fsp": False, "granularity_demo": False}
    )
    
    standard_score = standard_result["scores"]["composite"]
    print(f"   Standard Score: {standard_score:.3f}")
    print(f"   FSP Used: {standard_result.get('fsp_used', False)}")
    print()
    
    # Test with FSP
    print("2. Evaluating WITH FSP (bias mitigation)...")
    fsp_result = await judge.evaluate(
        output=verbose_output,
        scenario=ScenarioType.GRC_MAPPING,
        length_bin=LengthBin.L,
        bias_controls={"fsp": True, "granularity_demo": False}
    )
    
    fsp_score = fsp_result["scores"]["composite"]
    print(f"   FSP Score: {fsp_score:.3f}")
    print(f"   FSP Used: {fsp_result.get('fsp_used', False)}")
    print(f"   Sentences Evaluated: {fsp_result.get('sentences_evaluated', 0)}")
    print()
    
    # Analysis
    score_difference = fsp_score - standard_score
    print("3. Analysis:")
    print(f"   Score Difference: {score_difference:.3f}")
    
    if score_difference < 0:
        print("   ✅ CORRECT: FSP reduced the score (mitigating verbosity bias)")
        print("   This indicates the fix is working properly.")
    elif score_difference > 0:
        print("   ❌ INCORRECT: FSP increased the score (not mitigating bias)")
        print("   This suggests the implementation still has issues.")
    else:
        print("   ⚠️  NEUTRAL: FSP had no effect on the score")
        print("   This might indicate FSP wasn't triggered or had no impact.")
    
    print()
    print("4. Detailed Scores:")
    print("   Standard Scores:")
    for dim, score in standard_result["scores"].items():
        if dim != "composite":
            print(f"     {dim}: {score}")
    
    print("   FSP Scores:")
    for dim, score in fsp_result["scores"].items():
        if dim != "composite":
            print(f"     {dim}: {score}")

if __name__ == "__main__":
    asyncio.run(test_fsp_bias_mitigation())