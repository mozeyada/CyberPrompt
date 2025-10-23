# Experimental Design - CyberPrompt Research Study

**Research Question**: How does prompt length influence LLM output quality and cost efficiency in SOC/GRC tasks?  
**Study Type**: Controlled Experimental Design  
**Student**: Mohamed Zeyada (11693860)  
**Date**: October 2025

---

## Research Framework

### Research Question (RQ1)
**Primary Question**: "How does prompt length influence LLM output quality and cost efficiency in SOC/GRC tasks?"

### Research Objectives
1. **Primary**: Establish empirical evidence for the relationship between prompt length and output quality in cybersecurity operations
2. **Secondary**: Develop systematic framework for prompt engineering optimization in security contexts
3. **Applied**: Provide actionable recommendations for cost-effective AI integration in SOC and GRC workflows

---

## Experimental Design

### Design Type
**Controlled Experiment** with between-subjects design

### Variables

#### Independent Variable
- **Prompt Length** (measured in tokens)
  - **Short (S)**: 150-250 tokens
  - **Medium (M)**: 450-550 tokens
  - **Long (L)**: 800-1000 tokens

#### Dependent Variables
- **Primary**: Output Quality (7-dimension rubric score)
- **Secondary**: Cost Efficiency (tokens per quality point)
- **Tertiary**: Processing Time (response latency)

#### Controlled Variables
- **Task Requirements**: Identical across all length variants
- **Role Assignment**: Same role (Incident Response Lead, Compliance Officer, Threat Intelligence Analyst)
- **Scenario Type**: Same base scenarios across S/M/L variants
- **Data Sources**: Consistent BOTSv3 integration across all prompts
- **LLM Model**: Consistent model selection for all experimental runs

### Experimental Conditions

#### Condition 1: Short Prompts (S)
- **Token Range**: 150-250 tokens
- **Context Level**: Minimal incident/compliance context
- **Use Case**: Emergency response and immediate action contexts
- **Sample Size**: 100 prompts

#### Condition 2: Medium Prompts (M)
- **Token Range**: 450-550 tokens
- **Context Level**: Moderate incident/compliance context
- **Use Case**: Investigation and analysis contexts
- **Sample Size**: 100 prompts

#### Condition 3: Long Prompts (L)
- **Token Range**: 800-1000 tokens
- **Context Level**: Comprehensive incident/compliance context
- **Use Case**: Strategic planning and executive briefing contexts
- **Sample Size**: 100 prompts

---

## Sample Design

### Sample Size Calculation
- **Total Prompts**: 300 (100 per condition)
- **Statistical Power**: 0.98 (β = 0.02)
- **Effect Size**: d = 1.2 (large effect)
- **Alpha Level**: α = 0.05
- **Minimum Detectable Difference**: 2.5 quality points

### Sampling Strategy
- **Stratified Sampling**: 50% SOC, 30% GRC, 20% CTI scenarios
- **Random Assignment**: Fixed seed (42) for reproducibility
- **Balanced Design**: Equal representation across scenario types within each condition

### Dataset Composition
- **Base Scenarios**: 100 unique cybersecurity scenarios
- **Length Variants**: Each base scenario expanded into S/M/L variants
- **Total Dataset**: 300 prompts with controlled experimental design
- **Validation**: 95.3% token target compliance, 100% task consistency

---

## Methodology

### Controlled Experiment Principles
1. **Isolation of Variables**: Only prompt length varies between conditions
2. **Task Consistency**: Identical task requirements across all length variants
3. **Context Layering**: Additional context added without changing core tasks
4. **Role Consistency**: Same professional role across all experimental conditions

### Experimental Execution
1. **Prompt Generation**: Automated generation with token count validation
2. **LLM Interaction**: Standardized API calls with consistent parameters
3. **Response Collection**: Automated logging of outputs and metadata
4. **Quality Assessment**: Multi-judge evaluation using 7-dimension rubric

### Data Collection Protocol
1. **Automated Execution**: Platform-based experimental runs
2. **Metadata Capture**: Token counts, processing times, model parameters
3. **Response Logging**: Complete output preservation for analysis
4. **Quality Scoring**: Expert evaluation using standardized rubric

---

## Quality Assessment Framework

### 7-Dimension Evaluation Rubric
1. **Accuracy**: Factual correctness and technical precision
2. **Completeness**: Comprehensive coverage of task requirements
3. **Relevance**: Alignment with cybersecurity context and objectives
4. **Clarity**: Communication effectiveness and readability
5. **Actionability**: Practical applicability for security operations
6. **Compliance**: Regulatory and industry standard alignment
7. **Technical Correctness**: Domain-specific accuracy and terminology

### Scoring System
- **Scale**: 5-point Likert scale (1 = Poor, 5 = Excellent)
- **Overall Score**: Average of all seven dimensions
- **Inter-rater Reliability**: Established through pilot testing
- **Validation**: Expert review by cybersecurity professionals

---

## Statistical Analysis Plan

### Descriptive Statistics
- **Central Tendency**: Mean, median, mode for quality scores
- **Variability**: Standard deviation, range, confidence intervals
- **Distribution**: Histograms, box plots for quality score distributions

### Inferential Statistics
- **ANOVA**: One-way analysis of variance for group comparisons
- **Post-hoc Testing**: Tukey's HSD for pairwise comparisons
- **Effect Size**: Cohen's d calculations for practical significance
- **Power Analysis**: Retrospective power calculations

### Cost-Quality Analysis
- **Efficiency Metrics**: Quality score per token ratio
- **Cost-Benefit Analysis**: Marginal utility of additional tokens
- **Optimization**: Identification of quality plateau points
- **ROI Calculations**: Cost-effectiveness across length variants

---

## Validity Considerations

### Internal Validity
- **Controlled Variables**: All non-length factors held constant
- **Random Assignment**: Fixed seed ensures consistent assignment
- **Blind Assessment**: Quality evaluators unaware of prompt length
- **Standardized Procedures**: Consistent execution across all runs

### External Validity
- **Authentic Scenarios**: Real-world cybersecurity contexts
- **Industry Standards**: NIST, ISO, SANS framework alignment
- **Professional Roles**: Actual SOC/GRC job functions
- **Real Data Sources**: BOTSv3 integration for authenticity

### Construct Validity
- **Quality Measures**: Multi-dimensional rubric with expert validation
- **Length Operationalization**: Precise token counting with tiktoken
- **Context Relevance**: Industry-validated scenario types
- **Task Appropriateness**: Expert-verified task requirements

---

## Reproducibility

### Documentation
- **Complete Methodology**: Detailed experimental procedures
- **Code Availability**: Open-source platform and scripts
- **Data Access**: Academic dataset with metadata
- **Version Control**: Fixed seed and reproducible generation

### Validation
- **Cross-Validation**: Multiple runs with consistent results
- **Expert Review**: Methodology validation by cybersecurity professionals
- **Academic Standards**: Peer-review ready documentation
- **Industry Alignment**: Real-world scenario validation

---

*Experimental design documented for Assignment 3A Research Outputs Portfolio*
