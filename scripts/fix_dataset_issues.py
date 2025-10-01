#!/usr/bin/env python3
"""
Dataset Validation and Fix Script for CyberCQBench Academic Research

Addresses critical issues identified in the dataset generation:
1. Token length distribution alignment
2. Content diversity improvement
3. Realistic data source integration
4. Statistical significance requirements
"""

import json
import random
import tiktoken
from pathlib import Path
from typing import List, Dict

# Initialize tokenizer
encoding = tiktoken.get_encoding("cl100k_base")

def validate_token_distribution(prompts: List[Dict]) -> Dict:
    """Validate that token counts match research requirements"""
    
    target_ranges = {
        "S": (150, 300),
        "M": (400, 700), 
        "L": (800, 1200)
    }
    
    actual_stats = {"S": [], "M": [], "L": []}
    issues = []
    
    for prompt in prompts:
        length_bin = prompt["length_bin"]
        token_count = prompt["token_count"]
        actual_stats[length_bin].append(token_count)
        
        min_tokens, max_tokens = target_ranges[length_bin]
        if not (min_tokens <= token_count <= max_tokens):
            issues.append({
                "prompt_id": prompt["prompt_id"],
                "length_bin": length_bin,
                "actual_tokens": token_count,
                "target_range": f"{min_tokens}-{max_tokens}"
            })
    
    # Calculate statistics
    stats = {}
    for length_bin in ["S", "M", "L"]:
        tokens = actual_stats[length_bin]
        if tokens:
            stats[length_bin] = {
                "count": len(tokens),
                "min": min(tokens),
                "max": max(tokens),
                "avg": sum(tokens) / len(tokens),
                "target_range": target_ranges[length_bin],
                "compliance_rate": len([t for t in tokens if target_ranges[length_bin][0] <= t <= target_ranges[length_bin][1]]) / len(tokens)
            }
    
    return {
        "stats": stats,
        "issues": issues,
        "total_issues": len(issues)
    }

def check_content_diversity(prompts: List[Dict]) -> Dict:
    """Check for content diversity and repetition issues"""
    
    # Check for identical base contexts
    base_contexts = {}
    scenario_distribution = {}
    
    for prompt in prompts:
        scenario = prompt["scenario"]
        category = prompt["category"]
        
        # Count scenario distribution
        key = f"{scenario}_{category}"
        scenario_distribution[key] = scenario_distribution.get(key, 0) + 1
        
        # Check for repeated content patterns
        text_start = prompt["text"][:200]  # First 200 chars
        if text_start in base_contexts:
            base_contexts[text_start].append(prompt["prompt_id"])
        else:
            base_contexts[text_start] = [prompt["prompt_id"]]
    
    # Find duplicates
    duplicates = {k: v for k, v in base_contexts.items() if len(v) > 3}  # More than 3 similar starts
    
    return {
        "scenario_distribution": scenario_distribution,
        "duplicate_patterns": len(duplicates),
        "total_unique_starts": len(base_contexts)
    }

def validate_research_alignment(prompts: List[Dict], research_requirements: Dict) -> Dict:
    """Validate alignment with research project requirements"""
    
    issues = []
    
    # Check minimum dataset size for statistical significance
    total_prompts = len(prompts)
    min_required = research_requirements.get("min_prompts_per_length", 200)
    
    length_counts = {"S": 0, "M": 0, "L": 0}
    for prompt in prompts:
        length_counts[prompt["length_bin"]] += 1
    
    for length_bin, count in length_counts.items():
        if count < min_required:
            issues.append(f"Insufficient {length_bin} prompts: {count} < {min_required} required")
    
    # Check scenario coverage
    required_scenarios = research_requirements.get("required_scenarios", [])
    actual_scenarios = set(prompt["scenario"] for prompt in prompts)
    missing_scenarios = set(required_scenarios) - actual_scenarios
    
    if missing_scenarios:
        issues.append(f"Missing required scenarios: {missing_scenarios}")
    
    # Check for realistic data sources
    realistic_sources = 0
    for prompt in prompts:
        if "data_sources" in prompt.get("metadata", {}):
            sources = prompt["metadata"]["data_sources"]
            if any("bots" in str(source).lower() or "real" in str(source).lower() for source in sources):
                realistic_sources += 1
    
    realistic_ratio = realistic_sources / total_prompts if total_prompts > 0 else 0
    
    return {
        "total_prompts": total_prompts,
        "length_distribution": length_counts,
        "issues": issues,
        "realistic_data_ratio": realistic_ratio,
        "scenario_coverage": len(actual_scenarios),
        "alignment_score": max(0, 100 - len(issues) * 10)  # Simple scoring
    }

def generate_improvement_recommendations(validation_results: Dict) -> List[str]:
    """Generate specific recommendations for dataset improvement"""
    
    recommendations = []
    
    # Token distribution issues
    token_issues = validation_results["token_validation"]["total_issues"]
    if token_issues > 0:
        recommendations.append(
            f"🔧 Fix {token_issues} token distribution issues - adjust prompt templates to meet target ranges"
        )
    
    # Content diversity
    diversity = validation_results["diversity_check"]
    if diversity["duplicate_patterns"] > 5:
        recommendations.append(
            "🎯 Improve content diversity - reduce template repetition and add more scenario variations"
        )
    
    # Research alignment
    alignment = validation_results["research_alignment"]
    if alignment["alignment_score"] < 80:
        recommendations.append(
            f"📊 Address research alignment issues: {alignment['issues']}"
        )
    
    # Statistical significance
    min_prompts = min(alignment["length_distribution"].values())
    if min_prompts < 200:
        recommendations.append(
            f"📈 Increase dataset size - current minimum {min_prompts} prompts per length, need 200+ for statistical significance"
        )
    
    # Data realism
    if alignment["realistic_data_ratio"] < 0.5:
        recommendations.append(
            "🔍 Integrate more realistic data sources from actual BOTS v3 dataset"
        )
    
    return recommendations

def main():
    """Main validation function"""
    
    # Load current dataset
    data_path = Path(__file__).parent.parent / "data" / "prompts.json"
    
    if not data_path.exists():
        print("❌ Dataset file not found. Run generate_academic_prompts.py first.")
        return
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    prompts = data["prompts"]
    
    print("🔍 CYBERCQBENCH DATASET VALIDATION")
    print("=" * 50)
    print(f"Dataset: {data['dataset_version']}")
    print(f"Total prompts: {len(prompts)}")
    print()
    
    # Research requirements based on your project
    research_requirements = {
        "min_prompts_per_length": 200,  # For statistical significance
        "required_scenarios": ["SOC_INCIDENT", "GRC_MAPPING", "CTI_ANALYSIS"],
        "target_token_ranges": {
            "S": (150, 300),
            "M": (400, 700),
            "L": (800, 1200)
        }
    }
    
    # Run validations
    print("1️⃣ Validating token distribution...")
    token_validation = validate_token_distribution(prompts)
    
    print("2️⃣ Checking content diversity...")
    diversity_check = check_content_diversity(prompts)
    
    print("3️⃣ Validating research alignment...")
    research_alignment = validate_research_alignment(prompts, research_requirements)
    
    # Compile results
    validation_results = {
        "token_validation": token_validation,
        "diversity_check": diversity_check,
        "research_alignment": research_alignment
    }
    
    # Display results
    print("\n📊 VALIDATION RESULTS")
    print("=" * 30)
    
    # Token distribution
    print("Token Distribution:")
    for length_bin, stats in token_validation["stats"].items():
        compliance = stats["compliance_rate"] * 100
        print(f"  {length_bin}: {stats['min']}-{stats['max']} tokens (avg: {stats['avg']:.1f}) - {compliance:.1f}% compliant")
    
    print(f"\nContent Diversity:")
    print(f"  Scenario distribution: {diversity_check['scenario_distribution']}")
    print(f"  Duplicate patterns: {diversity_check['duplicate_patterns']}")
    print(f"  Unique content starts: {diversity_check['total_unique_starts']}")
    
    print(f"\nResearch Alignment:")
    print(f"  Alignment score: {research_alignment['alignment_score']}/100")
    print(f"  Realistic data ratio: {research_alignment['realistic_data_ratio']:.2f}")
    
    # Generate recommendations
    print("\n💡 IMPROVEMENT RECOMMENDATIONS")
    print("=" * 35)
    recommendations = generate_improvement_recommendations(validation_results)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    if not recommendations:
        print("✅ Dataset meets all validation criteria!")
    
    # Save validation report
    report_path = Path(__file__).parent.parent / "data" / "validation_report.json"
    with open(report_path, 'w') as f:
        json.dump({
            "validation_date": "2025-01-15",
            "dataset_version": data["dataset_version"],
            "results": validation_results,
            "recommendations": recommendations
        }, f, indent=2)
    
    print(f"\n📄 Validation report saved to: {report_path}")

if __name__ == "__main__":
    main()