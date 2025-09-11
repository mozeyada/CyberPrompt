#!/usr/bin/env python3
"""
Validation script to verify token-based classification is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.token_classification import get_token_count_and_bin, classify_by_tokens


def test_classification_logic():
    """Test the token classification logic with known examples."""
    print("Testing token classification logic:")
    print("=" * 50)
    
    test_cases = [
        (149, None, "Below S range"),
        (150, "S", "S range start"),
        (175, "S", "S range middle"),
        (200, "S", "S range end"),
        (201, None, "Above S, below M"),
        (399, None, "Below M range"),
        (400, "M", "M range start"),
        (500, "M", "M range middle"),
        (600, "M", "M range end"),
        (601, None, "Above M, below L"),
        (999, None, "Below L range"),
        (1000, None, "At L threshold"),
        (1001, "L", "L range start"),
        (2000, "L", "L range high"),
    ]
    
    all_passed = True
    for token_count, expected_bin, description in test_cases:
        result = classify_by_tokens(token_count)
        result_str = result.value if result else None
        
        if result_str == expected_bin:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            all_passed = False
        
        print(f"{status} | {token_count:4d} tokens -> {result_str:>4} | {description}")
    
    print("=" * 50)
    if all_passed:
        print("✅ All classification tests passed!")
    else:
        print("❌ Some classification tests failed!")
    
    return all_passed


def test_sample_texts():
    """Test classification with sample text examples."""
    print("\nTesting with sample texts:")
    print("=" * 50)
    
    sample_texts = [
        ("Short prompt", "Analyze this malware sample."),
        ("Medium prompt", " ".join(["This is a longer cybersecurity prompt that should have enough tokens to fall into the medium category."] * 15)),
        ("Long prompt", " ".join(["This is a very long cybersecurity analysis prompt with extensive details about threat intelligence, incident response procedures, compliance requirements, and risk assessment methodologies."] * 25)),
    ]
    
    for description, text in sample_texts:
        token_count, length_bin = get_token_count_and_bin(text)
        bin_str = length_bin.value if length_bin else "unclassified"
        
        print(f"{description:15} | {token_count:4d} tokens -> {bin_str:>12}")
        print(f"                | Text: {text[:80]}{'...' if len(text) > 80 else ''}")
        print()


async def main():
    """Main validation function."""
    print("🔍 Validating Token-Based Classification System")
    print("=" * 60)
    
    # Test classification logic
    logic_passed = test_classification_logic()
    
    # Test with sample texts
    test_sample_texts()
    
    print("=" * 60)
    if logic_passed:
        print("✅ Token classification validation completed successfully!")
        print("\nNew classification system:")
        print("- Short (S): 150-200 tokens")
        print("- Medium (M): 400-600 tokens")
        print("- Long (L): >1000 tokens")
        print("- Unclassified: All other ranges")
    else:
        print("❌ Token classification validation failed!")
        return False
    
    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)