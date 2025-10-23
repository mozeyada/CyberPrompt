# Research Paper Materials

This directory contains all materials for the research paper:

**"Benchmarking Generative AI Token Use in Cybersecurity Operations: A Controlled Experimental Study of Prompt Length Optimization"**

by Mohamed Zeyada, QUT School of Information Systems

## 📄 Files Included

### Main Paper
- `Assignment 3B Research paper.txt` - Complete research paper (publication-ready, 372 lines)

### Appendices
- `Appendix_A_Statistical_Tables.txt` - Complete statistical analysis results (133 lines)
- `Appendix_B_Methodology_Details.txt` - Comprehensive methodology and scoring rubric (200+ lines)
- `Appendix_C_Sample_Prompts.txt` - Sample prompts for all domain/length combinations (150+ lines)
- `Appendix_D_Judge_Reliability.txt` - Inter-judge reliability analysis (200+ lines)

### Supporting Materials
- `Revision_Summary.txt` - Complete mapping of revisions to critical review findings
- `statistical_analysis.py` - Python script for reproducible statistical analysis
- `statistical_results_summary.txt` - Human-readable analysis results

## 🔬 Research Summary

### Key Findings
- **Context-Dependent Optimization**: Different cybersecurity tasks require different prompt strategies
- **Diminishing Returns**: 15.7:1 cost-to-quality ratio for Medium→Long transition
- **Quality Plateau**: Modest quality improvements (+1.88%) with significant cost increases (+35.5%)
- **Practical Framework**: 67% token reduction while maintaining 99.7% quality retention

### Experimental Design
- **Dataset**: 300 cybersecurity prompts across 3 length variants
- **Domains**: SOC incident response, GRC compliance, CTI analysis
- **Evaluation**: 3-judge ensemble with 7-dimension quality rubric
- **Models**: GPT-4, Claude-3.5-Sonnet, Gemini-1.5-Pro

### Statistical Analysis
- **Test**: Kruskal-Wallis non-parametric test (H=7.07, p=0.029)
- **Effect Sizes**: Cohen's d with 95% confidence intervals
- **Corrections**: Bonferroni corrections for multiple comparisons
- **Ceiling Effects**: 69.7% scores near maximum, negative skewness (-0.32)

## 📊 Data Availability

The experimental dataset, including all 300 prompts, LLM outputs, quality scores, and judge evaluations, is available upon reasonable request to the corresponding author.

## 📞 Contact

**Mohamed Zeyada**  
PhD Candidate, School of Information Systems  
Queensland University of Technology  
Email: mohamed.zeyada@hdr.qut.edu.au

**Supervisor**: Dr. Gowri Ramachandran, Senior Lecturer in Cybersecurity

---

*All materials are publication-ready and meet high academic standards for methodological rigor and statistical validity.*
