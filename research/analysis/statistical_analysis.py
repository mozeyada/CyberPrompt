#!/usr/bin/env python3
"""
Statistical Analysis Script for CyberPrompt Research Paper
Performs comprehensive statistical reanalysis of experimental data
"""

import json
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import shapiro, levene, kruskal, pearsonr
import pymongo
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def connect_to_mongodb():
    """Connect to MongoDB and return database object"""
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['genai_bench']
        print("✓ Connected to MongoDB successfully")
        return db
    except Exception as e:
        print(f"✗ Failed to connect to MongoDB: {e}")
        return None

def load_data_from_files():
    """Load data from exported JSON files"""
    try:
        with open('/app/runs_export.json', 'r') as f:
            runs_data = json.load(f)
        with open('/app/prompts_export.json', 'r') as f:
            prompts_data = json.load(f)
        with open('/app/output_blobs_export.json', 'r') as f:
            output_blobs_data = json.load(f)
        
        print(f"✓ Loaded data: {len(runs_data)} runs, {len(prompts_data)} prompts, {len(output_blobs_data)} output blobs")
        return runs_data, prompts_data, output_blobs_data
    except Exception as e:
        print(f"✗ Failed to load data files: {e}")
        return None, None, None

def extract_runs_data(runs_data):
    """Extract and clean runs data"""
    df_runs = pd.DataFrame(runs_data)
    
    # Convert ObjectId to string for JSON serialization
    df_runs['_id'] = df_runs['_id'].astype(str)
    
    # Extract quality scores from the composite score
    df_runs['quality_score'] = df_runs['scores'].apply(lambda x: x['composite'] if isinstance(x, dict) and 'composite' in x else None)
    
    # Extract prompt length (convert S/M/L to numeric for analysis)
    length_mapping = {'S': 1, 'M': 2, 'L': 3}
    df_runs['prompt_length_numeric'] = df_runs['prompt_length_bin'].map(length_mapping)
    
    # Extract domain from scenario
    df_runs['domain'] = df_runs['scenario'].apply(lambda x: x.split('_')[0] if isinstance(x, str) else None)
    
    # Extract token counts
    df_runs['input_tokens'] = df_runs['tokens'].apply(lambda x: x['input'] if isinstance(x, dict) and 'input' in x else None)
    df_runs['output_tokens'] = df_runs['tokens'].apply(lambda x: x['output'] if isinstance(x, dict) and 'output' in x else None)
    df_runs['total_tokens'] = df_runs['tokens'].apply(lambda x: x['total'] if isinstance(x, dict) and 'total' in x else None)
    
    # Extract costs
    df_runs['cost_usd'] = df_runs['economics'].apply(lambda x: x['aud_cost'] if isinstance(x, dict) and 'aud_cost' in x else None)
    
    print("Runs data columns:", df_runs.columns.tolist())
    print("Quality score range:", df_runs['quality_score'].min(), "to", df_runs['quality_score'].max())
    print("Prompt length bins:", df_runs['prompt_length_bin'].value_counts().to_dict())
    print("Domains:", df_runs['domain'].value_counts().to_dict())
    
    return df_runs

def verify_paper_claims(df_runs):
    """Verify claims made in the paper against actual data"""
    verification_report = []
    
    # Check total number of runs
    total_runs = len(df_runs)
    verification_report.append(f"Total runs in database: {total_runs}")
    
    # Check if we have the expected 300 runs
    if total_runs == 300:
        verification_report.append("✓ Paper claim of 300 runs VERIFIED")
    else:
        verification_report.append(f"✗ Paper claims 300 runs, but database has {total_runs}")
    
    # Check prompt length distribution
    if 'prompt_length_bin' in df_runs.columns:
        length_counts = df_runs['prompt_length_bin'].value_counts()
        verification_report.append(f"Prompt length distribution: {length_counts.to_dict()}")
    
    # Check domain distribution
    if 'domain' in df_runs.columns:
        domain_counts = df_runs['domain'].value_counts()
        verification_report.append(f"Domain distribution: {domain_counts.to_dict()}")
    
    # Check quality scores
    if 'quality_score' in df_runs.columns:
        quality_stats = df_runs['quality_score'].describe()
        verification_report.append(f"Quality score statistics: mean={quality_stats['mean']:.3f}, std={quality_stats['std']:.3f}")
        
        # Check if means match paper claims
        paper_claims = {
            'S': 4.538,  # Short prompts
            'M': 4.599,  # Medium prompts  
            'L': 4.624   # Long prompts
        }
        
        for length_bin, expected_mean in paper_claims.items():
            actual_mean = df_runs[df_runs['prompt_length_bin'] == length_bin]['quality_score'].mean()
            verification_report.append(f"{length_bin} prompts: Paper claims {expected_mean}, Actual {actual_mean:.3f}")
            if abs(actual_mean - expected_mean) < 0.1:
                verification_report.append(f"✓ {length_bin} mean VERIFIED")
            else:
                verification_report.append(f"✗ {length_bin} mean MISMATCH")
    
    return verification_report

def perform_anova_analysis(df_runs):
    """Perform ANOVA with assumption testing"""
    results = {}
    
    if 'quality_score' not in df_runs.columns or 'prompt_length_bin' not in df_runs.columns:
        print("✗ Required columns (quality_score, prompt_length_bin) not found")
        return results
    
    # Group data by prompt length
    groups = []
    length_labels = []
    
    for length in df_runs['prompt_length_bin'].unique():
        group_data = df_runs[df_runs['prompt_length_bin'] == length]['quality_score'].dropna()
        if len(group_data) > 0:
            groups.append(group_data)
            length_labels.append(str(length))
    
    if len(groups) < 2:
        print("✗ Insufficient groups for ANOVA")
        return results
    
    # Test normality assumption
    normality_results = {}
    for i, group in enumerate(groups):
        if len(group) >= 3:  # Minimum for Shapiro-Wilk
            stat, p_value = shapiro(group)
            normality_results[length_labels[i]] = {
                'statistic': stat,
                'p_value': p_value,
                'normal': p_value > 0.05
            }
    
    results['normality'] = normality_results
    
    # Test homogeneity of variance
    if len(groups) >= 2:
        stat, p_value = levene(*groups)
        results['homogeneity'] = {
            'statistic': stat,
            'p_value': p_value,
            'homogeneous': p_value > 0.05
        }
    
    # Perform ANOVA or Kruskal-Wallis based on assumptions
    if all(normality_results.values()) and results['homogeneity']['homogeneous']:
        # Use ANOVA
        f_stat, p_value = stats.f_oneway(*groups)
        results['test_type'] = 'ANOVA'
        results['f_statistic'] = f_stat
        results['p_value'] = p_value
    else:
        # Use Kruskal-Wallis
        h_stat, p_value = kruskal(*groups)
        results['test_type'] = 'Kruskal-Wallis'
        results['h_statistic'] = h_stat
        results['p_value'] = p_value
    
    # Calculate effect size (eta-squared)
    if results['test_type'] == 'ANOVA':
        # Calculate eta-squared
        ss_between = sum(len(group) * (group.mean() - df_runs['quality_score'].mean())**2 for group in groups)
        ss_total = sum((df_runs['quality_score'] - df_runs['quality_score'].mean())**2)
        eta_squared = ss_between / ss_total
        results['eta_squared'] = eta_squared
    
    return results

def calculate_effect_sizes(df_runs):
    """Calculate Cohen's d for pairwise comparisons"""
    effect_sizes = {}
    
    if 'quality_score' not in df_runs.columns or 'prompt_length_bin' not in df_runs.columns:
        return effect_sizes
    
    lengths = sorted(df_runs['prompt_length_bin'].unique())
    
    for i in range(len(lengths)):
        for j in range(i+1, len(lengths)):
            group1 = df_runs[df_runs['prompt_length_bin'] == lengths[i]]['quality_score'].dropna()
            group2 = df_runs[df_runs['prompt_length_bin'] == lengths[j]]['quality_score'].dropna()
            
            if len(group1) > 0 and len(group2) > 0:
                # Calculate Cohen's d
                pooled_std = np.sqrt(((len(group1)-1)*group1.var() + (len(group2)-1)*group2.var()) / (len(group1)+len(group2)-2))
                cohens_d = (group1.mean() - group2.mean()) / pooled_std
                
                # Calculate 95% confidence interval for Cohen's d
                se_d = np.sqrt((len(group1) + len(group2)) / (len(group1) * len(group2)) + cohens_d**2 / (2 * (len(group1) + len(group2))))
                ci_lower = cohens_d - 1.96 * se_d
                ci_upper = cohens_d + 1.96 * se_d
                
                comparison_key = f"{lengths[i]}_vs_{lengths[j]}"
                effect_sizes[comparison_key] = {
                    'cohens_d': cohens_d,
                    'ci_lower': ci_lower,
                    'ci_upper': ci_upper,
                    'group1_mean': group1.mean(),
                    'group2_mean': group2.mean(),
                    'group1_n': len(group1),
                    'group2_n': len(group2)
                }
    
    return effect_sizes

def analyze_ceiling_effects(df_runs):
    """Analyze potential ceiling effects in quality scores"""
    ceiling_analysis = {}
    
    if 'quality_score' not in df_runs.columns:
        return ceiling_analysis
    
    scores = df_runs['quality_score'].dropna()
    
    # Calculate skewness and kurtosis
    skewness = stats.skew(scores)
    kurtosis = stats.kurtosis(scores)
    
    # Count scores near maximum
    max_score = scores.max()
    near_max = scores[scores >= max_score - 0.5]
    ceiling_percentage = len(near_max) / len(scores) * 100
    
    ceiling_analysis = {
        'mean_score': scores.mean(),
        'max_score': max_score,
        'skewness': skewness,
        'kurtosis': kurtosis,
        'ceiling_percentage': ceiling_percentage,
        'scores_near_max': len(near_max),
        'total_scores': len(scores),
        'potential_ceiling_effect': ceiling_percentage > 20  # Threshold for ceiling effects
    }
    
    return ceiling_analysis

def calculate_inter_judge_reliability(output_blobs_data):
    """Calculate inter-judge reliability metrics"""
    reliability_results = {}
    
    if not output_blobs_data:
        return reliability_results
    
    # This will need to be adjusted based on actual output_blobs structure
    print("Output blobs sample:", output_blobs_data[0] if output_blobs_data else "No data")
    
    # Placeholder for reliability calculations
    # In practice, this would extract individual judge scores and calculate:
    # - Intraclass Correlation Coefficient (ICC)
    # - Cronbach's alpha
    # - Pearson correlations between judges
    
    reliability_results = {
        'icc': 'TO_BE_CALCULATED',
        'cronbach_alpha': 'TO_BE_CALCULATED',
        'mean_correlation': 'TO_BE_CALCULATED',
        'note': 'Requires detailed output_blobs structure analysis'
    }
    
    return reliability_results

def generate_statistical_summary(df_runs, anova_results, effect_sizes, ceiling_analysis, reliability_results):
    """Generate comprehensive statistical summary"""
    summary = []
    
    summary.append("=" * 80)
    summary.append("STATISTICAL ANALYSIS SUMMARY")
    summary.append("=" * 80)
    summary.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    
    # Data verification
    summary.append("1. DATA VERIFICATION")
    summary.append("-" * 20)
    summary.append(f"Total experimental runs: {len(df_runs)}")
    if 'prompt_length' in df_runs.columns:
        length_counts = df_runs['prompt_length'].value_counts()
        summary.append(f"Prompt length distribution: {length_counts.to_dict()}")
    if 'domain' in df_runs.columns:
        domain_counts = df_runs['domain'].value_counts()
        summary.append(f"Domain distribution: {domain_counts.to_dict()}")
    summary.append("")
    
    # ANOVA results
    summary.append("2. ANOVA/KRUSKAL-WALLIS RESULTS")
    summary.append("-" * 30)
    if anova_results:
        summary.append(f"Test type: {anova_results.get('test_type', 'N/A')}")
        if 'f_statistic' in anova_results:
            summary.append(f"F-statistic: {anova_results['f_statistic']:.4f}")
        if 'h_statistic' in anova_results:
            summary.append(f"H-statistic: {anova_results['h_statistic']:.4f}")
        summary.append(f"P-value: {anova_results.get('p_value', 'N/A')}")
        if 'eta_squared' in anova_results:
            summary.append(f"Eta-squared: {anova_results['eta_squared']:.4f}")
        summary.append("")
        
        # Assumption testing
        summary.append("Assumption Testing:")
        if 'normality' in anova_results:
            for group, result in anova_results['normality'].items():
                status = "✓" if result['normal'] else "✗"
                summary.append(f"  {group}: {status} Normal (p={result['p_value']:.4f})")
        
        if 'homogeneity' in anova_results:
            status = "✓" if anova_results['homogeneity']['homogeneous'] else "✗"
            summary.append(f"  Homogeneity: {status} (p={anova_results['homogeneity']['p_value']:.4f})")
    summary.append("")
    
    # Effect sizes
    summary.append("3. EFFECT SIZES (COHEN'S D)")
    summary.append("-" * 25)
    if effect_sizes:
        for comparison, result in effect_sizes.items():
            summary.append(f"{comparison}:")
            summary.append(f"  Cohen's d: {result['cohens_d']:.4f}")
            summary.append(f"  95% CI: [{result['ci_lower']:.4f}, {result['ci_upper']:.4f}]")
            summary.append(f"  Group means: {result['group1_mean']:.4f} vs {result['group2_mean']:.4f}")
            summary.append(f"  Sample sizes: {result['group1_n']} vs {result['group2_n']}")
            summary.append("")
    else:
        summary.append("No effect sizes calculated (missing data)")
    summary.append("")
    
    # Ceiling effects
    summary.append("4. CEILING EFFECTS ANALYSIS")
    summary.append("-" * 25)
    if ceiling_analysis:
        summary.append(f"Mean quality score: {ceiling_analysis['mean_score']:.4f}")
        summary.append(f"Maximum score: {ceiling_analysis['max_score']:.4f}")
        summary.append(f"Skewness: {ceiling_analysis['skewness']:.4f}")
        summary.append(f"Kurtosis: {ceiling_analysis['kurtosis']:.4f}")
        summary.append(f"Scores near maximum: {ceiling_analysis['ceiling_percentage']:.1f}%")
        summary.append(f"Potential ceiling effect: {'Yes' if ceiling_analysis['potential_ceiling_effect'] else 'No'}")
    summary.append("")
    
    # Reliability
    summary.append("5. INTER-JUDGE RELIABILITY")
    summary.append("-" * 25)
    if reliability_results:
        summary.append(f"ICC: {reliability_results.get('icc', 'N/A')}")
        summary.append(f"Cronbach's alpha: {reliability_results.get('cronbach_alpha', 'N/A')}")
        summary.append(f"Mean correlation: {reliability_results.get('mean_correlation', 'N/A')}")
        if 'note' in reliability_results:
            summary.append(f"Note: {reliability_results['note']}")
    summary.append("")
    
    return "\n".join(summary)

def main():
    """Main analysis function"""
    print("Starting Statistical Analysis for CyberPrompt Research Paper")
    print("=" * 60)
    
    # Load data
    runs_data, prompts_data, output_blobs_data = load_data_from_files()
    if runs_data is None:
        print("✗ Failed to load data. Exiting.")
        return
    
    # Extract and clean data
    df_runs = extract_runs_data(runs_data)
    
    # Verify paper claims
    verification_report = verify_paper_claims(df_runs)
    print("\nData Verification:")
    for item in verification_report:
        print(f"  {item}")
    
    # Perform statistical analyses
    print("\nPerforming statistical analyses...")
    
    # ANOVA analysis
    anova_results = perform_anova_analysis(df_runs)
    
    # Effect sizes
    effect_sizes = calculate_effect_sizes(df_runs)
    
    # Ceiling effects
    ceiling_analysis = analyze_ceiling_effects(df_runs)
    
    # Inter-judge reliability
    reliability_results = calculate_inter_judge_reliability(output_blobs_data)
    
    # Generate summary
    summary = generate_statistical_summary(df_runs, anova_results, effect_sizes, ceiling_analysis, reliability_results)
    
    # Save results
    with open('/app/statistical_results_summary.txt', 'w') as f:
        f.write(summary)
    
    # Save detailed results as JSON
    detailed_results = {
        'anova_results': anova_results,
        'effect_sizes': effect_sizes,
        'ceiling_analysis': ceiling_analysis,
        'reliability_results': reliability_results,
        'verification_report': verification_report
    }
    
    with open('/app/statistical_results_detailed.json', 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print("\n✓ Analysis complete!")
    print("Results saved to:")
    print("  - statistical_results_summary.txt")
    print("  - statistical_results_detailed.json")
    
    # Print summary to console
    print("\n" + summary)

if __name__ == "__main__":
    main()
