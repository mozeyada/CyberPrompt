# CyberPrompt Research Repository

## Research Paper: "Benchmarking Generative AI Token Use in Cybersecurity Operations"

This repository contains the complete research materials for the study "Benchmarking Generative AI Token Use in Cybersecurity Operations: A Controlled Experimental Study of Prompt Length Optimization" by Mohamed Zeyada (QUT School of Information Systems).

## 📄 Research Paper Files

### Main Paper
- `Assignment 3B Research paper.txt` - Complete research paper (publication-ready)

### Supporting Materials
- `Appendix_A_Statistical_Tables.txt` - Complete statistical analysis results
- `Appendix_B_Methodology_Details.txt` - Comprehensive methodology and scoring rubric
- `Appendix_C_Sample_Prompts.txt` - Sample prompts for all domain/length combinations
- `Appendix_D_Judge_Reliability.txt` - Inter-judge reliability analysis
- `Revision_Summary.txt` - Complete mapping of revisions to critical review findings

### Analysis Materials
- `statistical_analysis.py` - Python script for reproducible statistical analysis
- `statistical_results_summary.txt` - Human-readable analysis results
- `statistical_results_detailed.json` - Detailed statistical results in JSON format

## 🔬 Research Overview

### Key Findings
- **Context-Dependent Optimization**: Different cybersecurity tasks require different prompt strategies
- **Diminishing Returns**: 15.7:1 cost-to-quality ratio for Medium→Long transition
- **Quality Plateau**: Modest quality improvements (+1.88%) with significant cost increases (+35.5%)
- **Multi-Model Validation**: Consistent patterns across GPT-4, Claude, and Gemini
- **Practical Framework**: 67% token reduction while maintaining 99.7% quality retention

### Experimental Design
- **Dataset**: 300 cybersecurity prompts across 3 length variants (Short: 150-200, Medium: 400-500, Long: 750-850 tokens)
- **Domains**: SOC incident response, GRC compliance, CTI analysis
- **Evaluation**: 3-judge ensemble with 7-dimension quality rubric
- **Models**: GPT-4, Claude-3.5-Sonnet, Gemini-1.5-Pro

### Statistical Analysis
- **Test**: Kruskal-Wallis non-parametric test (H=7.07, p=0.029)
- **Effect Sizes**: Cohen's d with 95% confidence intervals
- **Corrections**: Bonferroni corrections for multiple comparisons
- **Ceiling Effects**: 69.7% scores near maximum, negative skewness (-0.32)

## 📊 Data Availability

The experimental dataset, including all 300 prompts, LLM outputs, quality scores, and judge evaluations, is available upon reasonable request to the corresponding author (mohamed.zeyada@hdr.qut.edu.au).

### Available Data
- Complete experimental runs (300 prompts × 3 length variants)
- Quality scores from 3-judge ensemble evaluation
- Token counts and cost analysis
- Domain-specific performance metrics
- Inter-judge reliability statistics

### Analysis Code
- `statistical_analysis.py` - Complete statistical analysis script
- MongoDB export scripts for data extraction
- Reproducible analysis pipeline

## 🏗️ CyberPrompt Platform

This research is based on the CyberPrompt benchmarking platform, which includes:

### Platform Components
- **Backend**: FastAPI with MongoDB database
- **Frontend**: React-based user interface
- **Evaluation**: 3-judge ensemble system
- **Analysis**: Real-time statistical analysis

### Key Features
- Controlled experimental design
- Multi-model LLM evaluation
- Real-time cost tracking
- Bias mitigation techniques (Focus Sentence Prompting)
- Comprehensive quality assessment

## 📚 Citation

If you use this research or the CyberPrompt platform, please cite:

```
Zeyada, M. (2024). Benchmarking Generative AI Token Use in Cybersecurity Operations: 
A Controlled Experimental Study of Prompt Length Optimization. 
Proceedings of the 5th Conference on Research in IT Practice, Brisbane, Australia.
```

## 📞 Contact

**Mohamed Zeyada**  
PhD Candidate, School of Information Systems  
Queensland University of Technology  
Email: mohamed.zeyada@hdr.qut.edu.au

**Supervisor**: Dr. Gowri Ramachandran, Senior Lecturer in Cybersecurity

## 📄 License

This research is licensed under the MIT License. See LICENSE file for details.

## 🔗 Related Work

- CyberPrompt Platform: [GitHub Repository URL]
- BOTSv3 Dataset: SANS Institute cybersecurity scenarios
- NIST SP 800-53: Cybersecurity framework controls
- ISO 27001: Information security management systems

---

*This repository contains all materials necessary to reproduce the research findings and understand the methodology employed in the study.*
