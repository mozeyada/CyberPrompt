#!/usr/bin/env python3
"""
Test FSP for length invariance as per the research paper
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.base import LLMJudge
from app.services.llm_client import ModelRunner
from app.models import ScenarioType, LengthBin
from app.core.config import settings

async def test_length_invariance():
    """Test that FSP achieves length invariance across different text lengths"""
    
    # Short response (should be similar quality to long response)
    short_response = """
    Implement immediate containment measures to isolate affected systems. Document all actions taken for compliance reporting.
    """
    
    # Long response (same content but more verbose)
    long_response = """
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
    
    print("Testing FSP Length Invariance...")
    print(f"Short response: {len(short_response)} chars, {len(short_response.split())} words")
    print(f"Long response: {len(long_response)} chars, {len(long_response.split())} words")
    print()
    
    # Test short response without FSP
    print("1. Short Response - Standard Evaluation")
    short_standard = await judge.evaluate(
        output=short_response,
        scenario=ScenarioType.GRC_MAPPING,
        length_bin=LengthBin.S,
        bias_controls={"fsp": False}
    )
    print(f"   Score: {short_standard['scores']['composite']:.3f}")
    print()
    
    # Test long response without FSP
    print("2. Long Response - Standard Evaluation")
    long_standard = await judge.evaluate(
        output=long_response,
        scenario=ScenarioType.GRC_MAPPING,
        length_bin=LengthBin.L,
        bias_controls={"fsp": False}
    )
    print(f"   Score: {long_standard['scores']['composite']:.3f}")
    print()
    
    # Test long response with FSP
    print("3. Long Response - FSP Evaluation")
    long_fsp = await judge.evaluate(
        output=long_response,
        scenario=ScenarioType.GRC_MAPPING,
        length_bin=LengthBin.L,
        bias_controls={"fsp": True}
    )
    print(f"   Score: {long_fsp['scores']['composite']:.3f}")
    print(f"   Sentences Evaluated: {long_fsp.get('sentences_evaluated', 0)}")
    print()
    
    # Analysis
    standard_diff = abs(long_standard['scores']['composite'] - short_standard['scores']['composite'])
    fsp_diff = abs(long_fsp['scores']['composite'] - short_standard['scores']['composite'])
    
    print("4. Length Invariance Analysis:")
    print(f"   Standard evaluation difference: {standard_diff:.3f}")
    print(f"   FSP evaluation difference: {fsp_diff:.3f}")
    
    if fsp_diff < standard_diff:
        print("   ✅ FSP improved length invariance (smaller difference)")
        print("   This indicates FSP is working as intended per the research paper.")
    else:
        print("   ❌ FSP did not improve length invariance")
        print("   The implementation may need further refinement.")
    
    print()
    print("5. Expected Behavior (per research paper):")
    print("   - FSP should make scores more consistent across different text lengths")
    print("   - The goal is length invariance, not necessarily score reduction")
    print("   - FSP prevents missing errors in longer documents")

if __name__ == "__main__":
    asyncio.run(test_length_invariance())