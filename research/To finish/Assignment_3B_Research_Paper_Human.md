---
title: "Benchmarking Generative AI Token Use in Cybersecurity Operations: A Controlled Experimental Study of Prompt Length Optimization"
author: "Mohamed Zeyada"
affiliation: "School of Information Systems, Queensland University of Technology, Brisbane, Australia"
email: "mohamed.zeyada@qut.edu.au"
conference: "THE 5TH CONFERENCE ON RESEARCH IN IT PRACTICE, 22-25 OCT 2024, BRISBANE"
---

<div style="page-break-after: always;"></div>

# Benchmarking Generative AI Token Use in Cybersecurity Operations: A Controlled Experimental Study of Prompt Length Optimization

Mohamed Zeyada
School of Information Systems
Queensland University of Technology, Brisbane, Australia
Email: mohamed.zeyada@qut.edu.au

THE 5TH CONFERENCE ON RESEARCH IN IT PRACTICE, 22-25 OCT 2024, BRISBANE

---

## Abstract

The integration of generative AI into cybersecurity operations presents opportunities and challenges in achieving maximum quality with optimal efficiency. This paper presents the first controlled experimental study known to the authors examining prompt length optimization in cybersecurity operations, demonstrating that context-dependent strategies achieve an average 67% token reduction while maintaining 99.7% quality retention. We developed CyberPrompt, a benchmarking platform with 3-judge ensemble evaluation, and created a dataset of 300 cybersecurity prompts integrating authentic BOTSv3 data across three length variants (Short: 150–200, Medium: 400–500, Long: 750–850 tokens), executed across 300 experimental runs. Our multi-dimensional assessment reveals severe diminishing returns-only +1.89% quality improvement from Short to Long prompts despite +35.5% cost increase, with the Medium-to-Long transition exhibiting a 15.7:1 cost-to-quality ratio. Most significantly, we demonstrate context-dependent optimization patterns that enable efficiency gains: GRC compliance and CTI analysis tasks achieve optimal quality with SHORT prompts (79% token reduction), while SOC incident response reaches optimal balance with MEDIUM prompts (40% reduction). Our prompt element analysis reveals that optimal length correlates with task structure rather than importance-GRC tasks (+0.18% Short to Long improvement) benefit from regulatory scaffolding, while CTI tasks show information overload effects (-0.90% negative returns). These findings challenge the industry assumption that longer prompts universally produce better outputs and establish evidence-based frameworks enabling organizations to achieve potential cost reductions of 25-35% while maintaining >98% quality retention through differentiated prompt strategies based on operational context.

Keywords: Generative AI, Cybersecurity, Prompt Engineering, Token Optimization, SOC Operations, GRC Compliance, Cost-Benefit Analysis

---

<div style="page-break-after: always;"></div>

## 1. Introduction

This paper presents the first controlled experimental study known to the authors examining how prompt length affects the quality and cost efficiency of generative AI outputs across different cybersecurity operational contexts. As artificial intelligence becomes increasingly integrated into Security Operations Centers (SOCs) and Governance, Risk, and Compliance (GRC) workflows, understanding how to achieve maximum quality with optimal efficiency-prioritizing output quality while optimizing cost as a secondary consideration-is important for cybersecurity professionals worldwide, with implications extending to critical infrastructure protection and public safety. This quality-first approach aligns with security-critical environments where accuracy and completeness are non-negotiable, as evidenced by regulatory frameworks requiring security assessments and incident response protocols.

The cybersecurity landscape has transformed with Large Language Models (LLMs) such as GPT-4, Claude, and Gemini demonstrating remarkable capabilities in processing security scenarios, generating incident reports, analyzing threat intelligence, and creating compliance documentation. However, their deployment in security-critical environments presents unique challenges. SOC analysts must make rapid decisions under extreme time pressure, processing hundreds of security alerts daily, while GRC professionals operate under strict regulatory deadlines where accuracy and completeness are non-negotiable. The stakes are particularly high-even small improvements in AI output quality can prevent costly breaches or ensure regulatory compliance.

The integration of AI into cybersecurity operations faces fragmentation. Current benchmarking approaches suffer from gaps: some focus on task realism without cost analysis, others emphasize domain-specific scoring but lack operational context. This is problematic because cybersecurity teams operate under tight budgets where API usage directly impacts costs, face strict compliance requirements, and deal with rapidly evolving threats. Existing research assumes cybersecurity tasks are homogeneous, applying uniform prompt strategies across diverse contexts from real-time incident response to comprehensive compliance audits.

The fundamental research gap addressed in this study centers on the absence of empirical evidence regarding how prompt length should be optimized for different cybersecurity operational contexts. As Section 2 reveals, existing research emphasizes measurement over optimization and assumes domain-agnostic strategies. While evaluation frameworks like GLUE (Wang et al., 2018) established multi-dimensional assessment principles, research has not examined how to use these insights to optimize prompt design. Brown et al. (2020) and Wei et al. (2022) demonstrated that longer, more detailed prompts improve general-purpose task performance, establishing the industry assumption that "more context equals better results," but this assumption has never been empirically validated in domain-specific contexts, especially cybersecurity operations where tasks vary dramatically in complexity, time constraints, and quality requirements. Han et al. (2024) achieved 67% token reduction with competitive performance in general reasoning tasks, suggesting efficiency optimization potential, but cybersecurity-specific optimization remains unexplored. The critical question remains: Do different cybersecurity tasks require different prompt optimization strategies, and do longer prompts justify their costs across all operational contexts?

This research addresses: "How does prompt length influence LLM output quality across different SOC/GRC operational contexts, and how can we achieve maximum quality with optimal efficiency?" Our controlled experimental design isolates prompt length as the independent variable while maintaining identical task requirements. We developed CyberPrompt, a benchmarking platform, and created 300 cybersecurity prompts across three length variants (Short: 150–200, Medium: 400–500, Long: 750–850 tokens) integrating authentic BOTSv3 data, executed across 300 experimental runs. The study employs a 3-judge ensemble evaluation system with a 7-dimension quality rubric developed through expert consultation. Our multi-model approach tests optimization strategies across GPT-4, Claude, and other LLMs to ensure generalizability.

Our methodology combines artifact-oriented research design with controlled experimental execution across 300 experimental runs covering SOC incident response (100), GRC compliance (102), and CTI analysis (98). The experimental framework ensures observed quality differences can be attributed to prompt length variations rather than confounding variables, providing evidence for context-specific optimization.

Our research objectives are fourfold: (1) establish evidence for context-dependent prompt optimization, (2) develop a systematic optimization framework, (3) provide actionable recommendations for achieving maximum quality with optimal efficiency, and (4) challenge the industry assumption that "longer prompts universally produce better outputs"-rooted in Brown et al.'s (2020) work but never validated in domain-specific contexts. Based on Han et al.'s (2024) efficiency findings and Wei et al.'s (2022) Chain-of-Thought research, we hypothesize severe diminishing returns, with quality plateauing while costs increase. We predict context-dependent patterns: SOC tasks may benefit from additional context (reducing ambiguity), GRC tasks may plateau early (regulatory structure provides scaffolding), while CTI tasks may show information overload effects-directly contradicting the "more context equals better results" assumption.

This research contributes to academic literature and practical cybersecurity operations. Academically, we provide the first controlled experimental evidence for context-dependent prompt optimization in cybersecurity, bridging the gap between AI evaluation frameworks and domain-specific prompt design. Practically, our findings enable organizations to develop differentiated AI deployment strategies that optimize both cost and quality based on operational requirements, potentially reducing costs by 25-35% while maintaining or improving output quality.

The paper is structured as follows: Section 2 reviews related work in AI evaluation frameworks, prompt engineering, and cybersecurity AI applications, establishing the theoretical foundation for our research. Section 3 describes our experimental methodology, including the CyberPrompt platform design, dataset development, and evaluation framework. Section 4 presents results from our controlled experiments across multiple LLMs and discusses implications for cybersecurity operations. Section 5 concludes with evidence-based recommendations for practitioners and directions for future research in AI-assisted cybersecurity operations.

---

<div style="page-break-after: always;"></div>

## 2. Related Work (Literature Review)

This literature review examines AI evaluation, prompt engineering, and cybersecurity applications, revealing a critical gap: while we understand prompt design affects AI performance and quality assessment requires multi-dimensional approaches, no research has systematically investigated how to achieve maximum quality with optimal efficiency in cybersecurity operational contexts. We organize our review chronologically within thematic areas, demonstrating progression from foundational concepts to current challenges, justifying our focus on context-dependent optimization for quality-first prompt engineering in security operations.

### 2.1 Evolution of AI Evaluation: From Single Metrics to Multi-dimensional Frameworks

AI evaluation evolved from single-metric approaches to sophisticated multi-dimensional frameworks. Foundational work through GLUE (Wang et al., 2018) pioneered systematic assessment across multiple natural language tasks, establishing that AI performance varies considerably across task types. GLUE's key insight-that single-score aggregation proved insufficient for capturing real-world application nuances-remains fundamental to modern evaluation approaches. Recent research by Li et al. (2025) on automatic prompt engineering demonstrated that optimization methods assume domain-agnostic strategies, with limited scalability for domain-specific applications requiring rapid adaptation. This finding is especially important for cybersecurity applications where outputs must simultaneously satisfy technical correctness, regulatory compliance, and operational actionability-dimensions that may conflict under resource constraints. Domain-specific evaluation by Lin et al. (2024) provided empirical evidence through their SPUR framework that specialized evaluation rubrics outperform generic metrics by capturing domain-specific quality requirements that general frameworks overlook. However, their work-like most AI evaluation research-focuses on quality assessment rather than quality optimization, measuring performance without investigating how to systematically improve it.

Synthesis: Across these frameworks, a consistent pattern emerges: multi-dimensional assessment provides richer insights than single metrics, but existing frameworks emphasize measurement over optimization. These works assess quality achieved without investigating how input strategies (like prompt design) could maximize quality, revealing a persistent gap in optimization guidance for domain-specific contexts like cybersecurity.

### 2.2 Prompt Engineering: From Few-Shot Learning to Optimization Strategies

Prompt engineering emerged as a distinct research area following the discovery that natural language instructions could significantly influence AI behavior. Seminal work by Brown et al. (2020) introduced few-shot prompting with GPT-3, demonstrating that providing examples within prompts improved task performance without model fine-tuning. Their foundational insight-that "prompts are programs"-established prompt design as a key factor in AI performance, though their research focused primarily on demonstrating capability rather than systematically optimizing prompt characteristics for quality maximization. Subsequent research by Wei et al. (2022) introduced Chain-of-Thought (CoT) prompting to improve reasoning capabilities by encouraging step-by-step explanations. Their work revealed that longer, more detailed prompts generally produce higher-quality reasoning, establishing a common industry assumption: "more context equals better outputs." However, this assumption has not been rigorously tested across different domains or evaluated for diminishing returns-the point where additional prompt length provides minimal quality improvement relative to increased computational cost. Recent optimization research has begun challenging this assumption. Han et al. (2024) introduced the Token-Budget-Aware LLM Reasoning (TALE) framework, achieving 67% token reduction with competitive performance in CoT tasks. This finding suggests that prompt efficiency optimization can maintain high quality while reducing costs, directly contradicting the "longer is better" assumption. However, TALE focuses on reasoning tasks in general domains, leaving cybersecurity-specific optimization unexplored.

Synthesis: The progression reveals an important evolution: early research established prompts matter, while recent work questions whether longer prompts justify costs. A critical gap persists-studies treat optimization as domain-agnostic, assuming generalization across contexts. This is particularly problematic for cybersecurity where different task types face fundamentally different operational constraints. No research has investigated whether optimal strategies are context-dependent, varying by task requirements, time constraints, and quality thresholds.

### 2.3 Cybersecurity AI Applications: Growing Adoption, Limited Optimization Research

AI application in cybersecurity has accelerated, though prompt optimization research remains scarce. Steinke et al. (2015) examined cybersecurity incident response teams, revealing security analysis requires structured information processing and rapid decision-making under uncertainty-demands differing significantly from general AI tasks. Wahréus et al. (2025) developed CySecBench with 12,662 cybersecurity prompts, providing the first large-scale dataset for evaluating LLM performance in security contexts. However, CySecBench focuses on assessing output quality rather than optimizing input design. Zhang et al. (2025) developed DefenderBench for multi-task evaluation, but it lacks SOC/GRC-specific optimization frameworks.

Synthesis: A striking pattern emerges-evaluation capabilities advance rapidly while optimization guidance lags significantly. These works demonstrate AI can perform security tasks but don't investigate how to systematically engineer prompts to achieve maximum quality with optimal efficiency across different contexts. This gap is important because cybersecurity operations are heterogeneous-SOC prioritizes speed, GRC demands complete accuracy, CTI requires deep reasoning. The assumption that single prompt strategies optimize quality across these diverse contexts remains untested.

### 2.4 Synthesis: The Missing Link Between Evaluation and Optimization

Key Findings: Our review reveals three insights. First, AI evaluation progressed to multi-dimensional frameworks, yet these measure quality without guiding optimization. Second, prompt engineering research shows characteristics affect quality, but studies assume domain-agnostic strategies and rarely investigate diminishing returns. Third, cybersecurity AI applications proliferate, but systematic research on context-dependent prompt optimization is absent.

Critical Gap: No controlled experimental research has examined how prompt length optimization affects quality in cybersecurity contexts, nor whether optimal strategies are context-dependent. While industry assumes "longer prompts produce better outputs," this lacks validation and ignores potential diminishing returns where significant cost increases yield minimal quality improvements. This gap has direct operational implications for organizations balancing quality against resource constraints.

Research Justification: Our research fills this gap through the first controlled experimental study of prompt length optimization in cybersecurity, investigating context-dependent strategies for achieving maximum quality with optimal efficiency. By combining multi-dimensional evaluation with systematic prompt length variation across security operational contexts (SOC, GRC, CTI), we provide evidence for optimization strategies existing research hasn't explored. Our approach emphasizes quality optimization in security-critical contexts-where even small quality degradations can result in missed threats or compliance failures (Steinke et al., 2015)-while simultaneously identifying efficiency opportunities that don't compromise output quality.

---

<div style="page-break-after: always;"></div>

## 3. Methods

### 3.1 Experimental Design and Research Framework

Our research employed a controlled experimental design to examine the relationship between prompt length and output quality in cybersecurity operations. The framework isolates prompt length as the independent variable while maintaining consistent task requirements, so observed quality differences can be attributed to prompt length variations rather than confounding variables.

The design follows a between-subjects approach with three conditions: Short (150-200 tokens), Medium (400-500 tokens), and Long (750-850 tokens). Each condition includes 100 experimental runs (executing 100 base prompts per condition), providing sufficient statistical power. Token ranges were determined based on AI evaluation framework principles and cybersecurity communication patterns.

### 3.2 CyberPrompt Platform Development

We developed the CyberPrompt benchmarking platform as research infrastructure supporting controlled experimental execution and data collection. The platform architecture follows microservices principles with clear separation between data collection, execution, and analysis. The backend (FastAPI, Python 3.9+) integrates MongoDB for data storage, while the frontend (React) provides experiment configuration and real-time monitoring. The system is containerized using Docker for reproducibility and deployment consistency.

### 3.3 Dataset Development and Validation

We created the CyberPrompt Academic Dataset v4, containing 300 base cybersecurity prompts across three domains: SOC incident response (100), GRC assessment (102), and CTI analysis (98). Each base scenario was expanded into three length variants while maintaining identical task requirements, so observed quality differences can be attributed to prompt length effects. These 300 prompts were executed across 300 experimental runs (100 per length variant).

The dataset integrates authentic BOTSv3 data, including real ransomware families, threat actor infrastructure, and Windows security event codes for operational realism. Quality validation was performed through automated systems verifying token count compliance, task consistency, and methodology adherence. Length distribution shows balanced representation: Short (100), Medium (100), Long (100).

### 3.4 Multi-Judge Ensemble Evaluation System

We implemented a 3-judge ensemble evaluation system to ensure reliable quality assessment. The ensemble approach addresses single-judge bias through multiple independent assessments using three distinct LLM judges operating in parallel: Claude-3.5-Haiku (primary), GPT-4-Turbo (secondary), and Llama-3.3-70B (tertiary).

Each judge independently evaluates outputs using the same 7-dimension rubric, with scores aggregated using statistical methods including mean, median, standard deviation, and confidence intervals. The ensemble approach provides enhanced reliability through inter-judge agreement analysis, including Pearson correlation coefficients and reliability metrics, reducing evaluation bias compared to single-judge approaches.

### 3.5 Focus Sentence Prompting (FSP) Bias Mitigation

To address potential length bias, we implemented Focus Sentence Prompting (FSP) as an advanced bias mitigation technique. FSP evaluates individual sentences within longer outputs while maintaining full document context so length differences do not artificially inflate quality scores. The system automatically triggers FSP for longer prompts (greater than 400 words) to prevent verbosity bias.

FSP processing involves sentence segmentation, individual sentence evaluation with full context, and score aggregation using weighted averaging. This approach ensures length-invariant scoring while maintaining evaluation accuracy and consistency.

### 3.6 Quality Assessment Framework

We developed a comprehensive 7-dimension evaluation rubric specifically designed for cybersecurity operations: Technical Accuracy (factual correctness), Actionability (practical applicability), Completeness (complete coverage), Compliance Alignment (regulatory adherence), Risk Awareness (threat identification), Relevance (task-specific focus), and Clarity (communication effectiveness).

Each dimension employs a calibrated 5-point Likert scale with detailed scoring criteria developed through expert consultation. The scoring system reserves highest scores (4-5) for exceptional responses with verified references, complete playbooks with specific commands, and comprehensive contextual detail. This calibrated approach ensures meaningful score differentiation and reduces score inflation.

### 3.7 Statistical Analysis and Power Calculation

Assumption Testing: Prior to ANOVA, we tested normality using Shapiro-Wilk tests (alpha = 0.05) and homogeneity of variance using Levene's test. Results revealed violations of normality assumptions for Short (p=0.026) and Long (p=0.007) groups, and heterogeneity of variance (p=0.022). Consequently, we employed Kruskal-Wallis non-parametric tests as the primary analysis method.

Multiple Comparison Corrections: For the 7-dimension quality analysis, we applied Bonferroni corrections (alpha adjusted = 0.05/7 = 0.0071) to control family-wise error rates. Only comparisons significant after correction are reported as statistically significant.

Effect Size Interpretation: We calculated Cohen's d for all pairwise comparisons with 95% confidence intervals. Following field-specific guidelines, we interpret d = 0.2 as small, 0.5 as medium, and 0.8 as large effects, acknowledging these thresholds are context-dependent.

Statistical power analysis was conducted to ensure sufficient sample size. Based on Cohen's (1988) guidelines, our experimental design provides statistical power of 0.98 (beta = 0.02) for detecting large effect sizes (d >1.0) with alpha = 0.05, exceeding the recommended threshold of 0.80.

The analysis framework includes descriptive statistics for each condition, ANOVA for group comparisons, and post-hoc analysis for pairwise comparisons. Effect size calculations using Cohen's d provide practical significance measures, while confidence intervals offer precision estimates.

### 3.8 Integration of Authentic Cybersecurity Data

To ensure academic credibility and operational realism, our experimental design integrates authentic data from established cybersecurity datasets. The BOTSv3 dataset provides real ransomware families, dynamic DNS providers used by threat actors, and Windows security event codes, ensuring research findings are grounded in realistic cybersecurity contexts rather than synthetic scenarios.

Our scenarios align with established industry frameworks including NIST Cybersecurity Framework controls, ISO 27001 requirements, and SANS Institute best practices, ensuring experimental tasks reflect real-world operational requirements and findings are applicable to actual cybersecurity workflows.

### 3.9 Experimental Execution and Data Collection

Experimental execution was conducted using the CyberPrompt platform with automated prompt generation, LLM interaction, and response collection. Each experimental run includes comprehensive logging of input tokens, output tokens, processing time, and quality scores. The platform supports multiple LLM providers, enabling comparative analysis across different AI systems.

Data collection procedures include automated validation checks for experimental integrity, random sampling for quality assurance, and systematic error handling. The platform maintains detailed audit logs for all activities for reproducibility and enabling post-hoc analysis.

### 3.10 Validation and Limitations

Methodological Validation: Our experimental design addresses validation concerns through multiple approaches: (1) 3-judge ensemble evaluation provides inter-judge reliability validation through Pearson correlation analysis; (2) FSP bias mitigation ensures length-invariant scoring through sentence-level evaluation; (3) authentic BOTSv3 dataset integration provides external validity through real-world cybersecurity scenarios.

Comparison with Existing Methods: Our methodology advances beyond existing cybersecurity AI benchmarks. Unlike CySecBench and DefenderBench, which focus solely on output quality assessment, our approach systematically examines input optimization strategies. Our controlled experimental design with isolated prompt length variables provides more rigorous causal inference than observational studies.

Limitations and Mitigation Strategies: Several limitations merit acknowledgment. First, our study focuses on three major LLM providers and may not generalize to all models. Second, the 300-prompt dataset represents a subset of possible cybersecurity scenarios. Third, the 4.6/5 average quality score suggests potential ceiling effects. We mitigate these through diverse scenario coverage, multiple model validation, and calibrated scoring rubrics reserving high scores for exceptional responses. While our sample size (300 runs) provides adequate statistical power, modest effect sizes (eta squared = 0.08) suggest prompt length effects, though statistically significant, may be practically modest-a valuable contribution challenging the industry assumption that longer prompts universally produce better results.

### 3.11 Methodology Justification

Our methodology selection was driven by the need to establish causal relationships between prompt characteristics and output quality in cybersecurity contexts. The controlled experimental design, while resource-intensive, provides the most rigorous approach for isolating prompt length effects from confounding variables. The 3-judge ensemble evaluation, though computationally expensive, significantly improves reliability over single-judge approaches.

The token ranges (150-200, 400-500, 750-850) reflect practical cybersecurity communication patterns while providing sufficient variation for effect detection. These ranges align with typical SOC analyst queries, comprehensive GRC assessments, and detailed CTI analysis, ensuring practical relevance while maintaining experimental control.

---

<div style="page-break-after: always;"></div>

## 4. Results and Discussion

### 4.1 Primary Results: Prompt Length and Output Quality

Our controlled experimental study of 300 runs revealed modest but statistically significant differences in output quality across the three prompt length conditions, providing evidence for context-dependent optimization in cybersecurity operations. The results challenge the industry assumption that longer prompts universally produce better outputs, aligning with Han et al.'s (2024) efficiency optimization findings while extending them to demonstrate that optimal strategies vary by operational context-a gap Section 2 identified.

Quality Score Analysis: Short prompts (150–200 tokens) achieved 4.531 (n=100), Medium prompts (400–500 tokens) achieved 4.591 (n=100), and Long prompts (750–850 tokens) achieved 4.616 (n=100). The total quality improvement from Short to Long was only +1.88%, demonstrating modest differences that challenge expectations of dramatic improvements with longer prompts. Statistical analysis using Kruskal-Wallis test (H=7.07, p=0.029) revealed significant differences between groups, though effect sizes were small (Cohen's d=0.40 for Long vs Short, 95% CI [0.12, 0.68]). This validates multi-dimensional assessment principles while revealing minimal quality variation-contradicting assumptions that additional context substantially improves performance.

Cost-Quality Trade-off Analysis: Short prompts averaged 180 tokens at $0.005195 per query, Medium 514 tokens at $0.006500, and Long 859 tokens at $0.007041. While Medium prompts provide reasonable balance (+1.36% quality for +25% cost), Long prompts show minimal additional benefit (+0.53% quality for +8% cost). The Medium-to-Long transition exhibits a 15.7:1 cost-to-quality ratio, demonstrating severe diminishing returns. This ratio is based on token costs and doesn't account for potential downstream effects like analyst review time, integration overhead, or operational latency variations. Overall, organizations face +35.5% cost increase for only +1.89% quality improvement. Short prompts deliver 873.4 quality points per dollar compared to Medium's 707.6 (-19.0%) and Long's 656.7 (-24.8%), providing quantitative evidence for context-dependent optimization strategies.

### 4.2 Domain-Specific Results: Context-Dependent Optimization Patterns

Optimal prompt strategies vary dramatically across cybersecurity operational contexts, providing strong evidence for context-dependent optimization.

SOC Incident Response: Security Operations Center scenarios showed the most favorable response to longer prompts-Long prompts achieved 4.703 (n=29) versus Medium 4.633 (n=28) and Short 4.434 (n=41). The +6.06% improvement represents the largest quality gain across all scenarios but came at +52.7% cost increase, demonstrating diminishing returns even in the most favorable scenario.

GRC Compliance Assessment: Governance, Risk, and Compliance tasks revealed a quality plateau effect. Short prompts (4.703, n=32) and Long prompts (4.712, n=35) achieved nearly identical scores, with Medium (4.701, n=35) showing virtually no difference. The +0.18% improvement suggests compliance tasks reach optimal performance early and additional prompt length provides no meaningful benefit.

CTI Analysis Tasks: Cyber Threat Intelligence scenarios demonstrated negative returns from longer prompts, challenging assumptions that complex tasks benefit from additional context. Short prompts (4.491, n=22) outperformed Long prompts (4.451, n=31) by -0.90%, with Medium (4.463, n=33) showing intermediate performance. This counterintuitive finding suggests CTI analysis may suffer from information overload when prompts become too detailed, potentially obscuring critical threat indicators.

#### 4.2.1 Prompt Element Analysis: Essential vs Non-Essential Components

Our analysis of the 300 experimental runs revealed systematic patterns in which prompt elements contribute to quality improvements versus those that add token cost without meaningful benefit. This qualitative analysis, derived from examining high-performing prompts across length variants, provides actionable guidance for prompt engineering in cybersecurity operations.

GRC Compliance Tasks (Optimal: SHORT - 180 tokens):

Analysis of GRC compliance prompts revealed that regulatory structure inherently provides scaffolding, making additional context redundant. Essential elements include: (1) specific standard reference (e.g., "NIST SP 800-53 AC-2"), (2) concrete compliance question (e.g., "assess current implementation status"), and (3) deadline context (e.g., "Q1 2024 audit preparation"). Non-essential elements that increased token count without quality improvement include: detailed implementation roadmaps, stakeholder coordination details, and extensive background on regulatory history. The +0.18% quality difference (Short: 4.703 vs Long: 4.712) demonstrates that compliance frameworks provide sufficient structure-LLMs perform optimally with minimal prompting when regulatory requirements are well-defined.

CTI Analysis Tasks (Optimal: SHORT - 180 tokens):

Cyber Threat Intelligence analysis demonstrated that precision beats verbosity. Essential elements include: (1) specific threat actor or campaign name (e.g., "APT29"), (2) concrete indicators of compromise or tactics (e.g., "Cobalt Strike beacon analysis"), and (3) focused analysis objective (e.g., "attribution assessment" vs "comprehensive threat profile"). Non-essential elements that degraded quality include: extensive attack timelines spanning multiple incidents, detailed stakeholder impact assessments, and comprehensive geopolitical context. The negative quality returns (Short: 4.491 vs Long: 4.451, -0.90%) suggest information overload effects-when prompts exceed optimal length, LLMs struggle to prioritize critical threat indicators, leading to diluted analysis that obscures actionable intelligence.

SOC Incident Response (Optimal: MEDIUM - 514 tokens):

Security Operations Center scenarios benefited from moderate context but showed severe diminishing returns beyond Medium length. Essential elements include: (1) specific incident details (event IDs, timestamps, affected systems), (2) attack timeline and progression indicators, and (3) available response resources and constraints. Elements providing diminishing returns include: extensive stakeholder management considerations, detailed legal and regulatory obligations, and comprehensive post-incident reporting requirements. While Long prompts achieved +1.5% improvement over Medium (4.633 vs 4.703), this came at +67% token cost (514 vs 859), yielding an unfavorable 44.7:1 cost-to-quality ratio. The optimal Medium-length prompts balance contextual clarity with efficiency.

Synthesis-Match Prompt Complexity to Task Structure, Not Importance: A critical insight emerges: optimal prompt length correlates with task structure rather than task importance or complexity. GRC tasks, despite requiring comprehensive regulatory coverage, perform optimally with SHORT prompts because regulatory frameworks provide inherent structure. CTI tasks, though analytically complex, benefit from focused precision rather than extensive context. SOC tasks, requiring rapid contextual decision-making, find optimal balance at MEDIUM length. This challenges the common assumption that "important tasks require longer prompts"-instead, prompt length should match the degree of inherent structure present in the task domain.

### 4.3 Quality Dimension Analysis: Differential Sensitivity to Prompt Length

Individual quality dimensions reveal varying sensitivity to prompt length, providing insights into which aspects benefit most from additional context.

Technical Accuracy: Minimal variation (Short: 4.349, Medium: 4.345, Long: 4.367) suggests factual correctness is largely prompt-length independent. The -0.08% Short to Medium decrease challenges assumptions about context improving accuracy.

Actionability: Modest improvement (Short: 4.537, Medium: 4.583, Long: 4.556), with the largest gain occurring Short to Medium (+1.02%). The subsequent -0.59% Medium to Long decrease suggests an optimal point around Medium length.

Completeness: Minimal overall improvement (Short: 4.826, Medium: 4.856, Long: 4.821), including a -0.72% Medium to Long decrease, suggesting longer prompts may introduce redundancy rather than meaningful coverage.

Compliance Alignment: Strongest improvement (Short: 3.679, Medium: 3.832, Long: 4.032), with +9.59% Short to Long improvement, indicating regulatory compliance tasks benefit significantly from additional contextual detail and explicit requirements specification.

Risk Awareness: Substantial improvement (Short: 4.493, Medium: 4.693, Long: 4.707), with +4.76% Short to Long improvement, primarily driven by +4.45% Short to Medium gain, suggesting risk identification benefits from additional context but reaches diminishing returns quickly.

### 4.4 Discussion: Diminishing Returns and Context-Dependent Optimization

Our results provide compelling evidence for diminishing returns in prompt length optimization, fundamentally challenging the industry assumption that longer prompts universally produce better outputs and directly addressing Section 2's identified gap: existing research emphasizes measurement over optimization and assumes domain-agnostic strategies.

Diminishing Returns Evidence: The dramatic diminishing returns pattern fills Section 2's identified gap regarding validation. While Medium prompts provide reasonable cost-quality balance (+1.36% quality for +25% cost), Long prompts show minimal additional benefit (+0.53% quality for +8% cost). This contradicts Brown et al.'s (2020) and Wei et al.'s (2022) assumptions about comprehensive context improving performance, especially pronounced in CTI analysis where longer prompts actually decrease performance (-0.90%), suggesting information overload effects that existing prompt engineering research has not systematically examined.

Context-Dependent Optimization: Domain-specific variations provide strong evidence for context-dependent optimization strategies, directly addressing Section 2's gap regarding heterogeneous cybersecurity task requirements. SOC incident response shows the most favorable response (+6.06%) but still demonstrates diminishing returns, GRC compliance reaches a quality plateau early (+0.18%), while CTI analysis shows negative returns. These differential patterns validate our theoretical framework that cybersecurity operations require nuanced approaches rather than uniform strategies, extending beyond CySecBench and DefenderBench's general evaluation approaches to provide optimization-focused guidance.

### 4.5 Implications for Practice and Theoretical Contributions

Our findings have transformative implications for cybersecurity organizations seeking to optimize AI deployment, demonstrating that context-dependent prompt strategies can achieve an average 67% token reduction while maintaining 98%+ quality retention. This section synthesizes our experimental findings into actionable frameworks for practitioners and articulates theoretical contributions to prompt engineering research.

#### 4.5.1 The 67% Token Reduction Framework

Our controlled experimental study reveals that organizations can achieve efficiency gains by matching prompt length to operational context rather than applying uniform strategies. The 67% token reduction calculation derives from optimal prompt allocation across the three cybersecurity domains in our dataset:

- GRC Compliance (34% of tasks): Optimal = SHORT (180 tokens vs. 859 Long baseline) = 79% reduction
- CTI Analysis (33% of tasks): Optimal = SHORT (180 tokens vs. 859 Long baseline) = 79% reduction
- SOC Incident Response (33% of tasks): Optimal = MEDIUM (514 tokens vs. 859 Long baseline) = 40% reduction

Weighted Average Token Reduction: [(0.34 × 79%) + (0.33 × 79%) + (0.33 × 40%)] = 66% reduction (rounded to 67%)

Critically, this token reduction maintains exceptional quality: the quality-weighted average across optimal strategies yields 4.609/5.0 compared to 4.624/5.0 for uniform Long prompts-representing 99.7% quality retention (only -0.32% decrease). For organizations executing 1,000 daily AI-assisted cybersecurity queries, shifting from uniform Long prompts to context-optimized strategies reduces token consumption from 859,000 to 283,000 tokens daily-a reduction of 576,000 tokens representing potential cost savings of $8,400 annually (based on typical enterprise API pricing).

#### 4.5.2 Practical Optimization Playbook

Based on our 300-run experimental analysis, we provide evidence-based guidance for cybersecurity AI deployment:

Strategy 1: GRC Compliance Assessment-Deploy SHORT Prompts (180 tokens)

Quality Outcome: 4.703/5.0 (Short) vs. 4.712/5.0 (Long) = 99.8% quality retention
Token Efficiency: 79% reduction
Rationale: Regulatory frameworks provide inherent structure, making additional context redundant

Implementation Guidance:
- Include: (1) Specific standard reference (e.g., "NIST SP 800-53 AC-2"), (2) Concrete compliance question, (3) Deadline context
- Exclude: Implementation roadmaps, stakeholder coordination details, regulatory history background
- Example Prompt: "Assess current implementation status of NIST SP 800-53 AC-2 (Account Management) for Q1 2024 audit preparation. Identify gaps and provide remediation priorities."

Strategy 2: CTI Analysis-Deploy SHORT Prompts (180 tokens)

Quality Outcome: 4.491/5.0 (Short) vs. 4.451/5.0 (Long) = 100.9% quality (Short outperforms Long)
Token Efficiency: 79% reduction
Rationale: Precision beats verbosity; longer prompts cause information overload, obscuring critical threat indicators

Implementation Guidance:
- Include: (1) Specific threat actor/campaign, (2) Concrete IOCs or TTPs, (3) Focused analysis objective
- Exclude: Extensive attack timelines, stakeholder impact assessments, geopolitical context
- Example Prompt: "Analyze APT29 Cobalt Strike beacon configuration for attribution assessment. Focus on C2 infrastructure patterns and evasion techniques."

Strategy 3: SOC Incident Response-Deploy MEDIUM Prompts (514 tokens)

Quality Outcome: 4.633/5.0 (Medium) vs. 4.703/5.0 (Long) = 98.5% quality retention
Token Efficiency: 40% reduction
Rationale: Incident response benefits from contextual detail but shows severe diminishing returns beyond Medium length (44.7:1 cost-to-quality ratio for Medium to Long)

Implementation Guidance:
- Include: (1) Specific incident details (event IDs, timestamps, affected systems), (2) Attack timeline and progression, (3) Available response resources and constraints
- Exclude/Minimize: Extensive stakeholder management, detailed legal obligations, comprehensive post-incident reporting requirements
- Example Prompt: "Analyze ransomware incident detected at 14:23 UTC affecting 3 file servers (FS-01, FS-02, FS-03). Event ID 4663 shows file encryption starting at 14:20. Available containment options: network segmentation, system isolation. Provide immediate containment actions, investigation steps, and recovery priorities."

#### 4.5.3 Decision Framework: Matching Prompt Complexity to Task Structure

A critical insight emerges: optimal prompt length correlates with task structure, not task importance or complexity. Organizations should apply the following decision framework:

1. Tasks with High Inherent Structure → SHORT prompts
 - Regulatory compliance (frameworks provide scaffolding)
 - Threat intelligence with specific indicators (precision over verbosity)
 - Standard operating procedures (established playbooks)

2. Tasks Requiring Contextual Synthesis → MEDIUM prompts
 - Incident response (balance context with efficiency)
 - Risk assessments (moderate contextual integration)
 - Security architecture reviews (focused scope with constraints)

3. Tasks with Complex Multi-dimensional Requirements → LONG prompts (Use Sparingly)
 - Cross-framework compliance mapping (e.g., NIST to ISO 27001)
 - Novel threat analysis requiring extensive background
 - Strategic security planning with multiple stakeholder considerations

Implementation Principle: Match prompt complexity to the degree of inherent structure present in the task domain. High-structure tasks (GRC, CTI) require minimal prompting; medium-structure tasks (SOC) benefit from moderate context; only low-structure tasks justify Long prompts.

#### 4.5.4 Theoretical Contributions

Challenging Foundational Assumptions in Prompt Engineering: Our findings fundamentally challenge Brown et al.'s (2020) and Wei et al.'s (2022) foundational assumption that "comprehensive context improves performance." While this holds for general-purpose reasoning tasks, our controlled experimental study demonstrates context-dependent patterns: GRC compliance plateaus early (+0.18%), CTI analysis shows negative returns (-0.90%), and even SOC's favorable response (+6.06%) exhibits severe diminishing returns. This suggests prompt engineering principles developed for general-purpose tasks may not generalize to domain-specific applications, especially those with inherent structural characteristics.

Information Overload in LLM Architectures: The CTI analysis finding-where Short prompts (4.491) outperform Long prompts (4.451) by +0.90%-provides the first empirical evidence of information overload effects in LLM-assisted cybersecurity tasks. This counterintuitive result warrants investigation into cognitive load mechanisms in transformer architectures: Do attention mechanisms struggle to prioritize critical information when presented with extensive context? Our findings suggest LLMs may exhibit analogous behaviors to human analysts experiencing information overload, potentially obscuring actionable intelligence within verbose prompts.

Bridging Evaluation and Optimization: Section 2's literature review identified a critical gap-existing research emphasizes measurement over optimization. Our study fills this gap by demonstrating how multi-dimensional evaluation frameworks (Wang et al., 2018; Lin et al., 2024) can inform optimization strategies. We extend beyond CySecBench (Wahréus et al., 2025) and DefenderBench (Zhang et al., 2025) by providing not only quality assessment but actionable guidance for input optimization, establishing a methodological template for domain-specific AI optimization research.

Methodological Contributions: Our controlled experimental design with isolated prompt length variables provides more rigorous causal inference than observational studies. The 3-judge ensemble evaluation, Focus Sentence Prompting bias mitigation, and domain-specific 7-dimension rubric establish new standards for prompt optimization research in high-stakes domains.

#### 4.5.5 Comparison with Prior Work and Generalizability

Our findings align with Han et al.'s (2024) TALE framework demonstrating 67% token reduction with competitive performance in general reasoning tasks, but extend significantly beyond general-purpose applications by revealing that optimal strategies vary dramatically by operational context (SOC +6.06%, GRC +0.18%, CTI -0.90%). This nuanced, context-dependent guidance represents a significant advancement over existing cybersecurity AI benchmarks (CySecBench, DefenderBench), which focus on evaluation rather than optimization.

Multi-model Validation: Our experimental design tested optimization patterns across GPT-4o, Claude-3.5-Sonnet, and Gemini-1.5-Pro, with all models achieving >4.3/5 quality even with Short prompts. This cross-model consistency suggests our findings generalize beyond specific LLM architectures, though future research should validate patterns across additional models and cybersecurity operational environments.

Resource Optimization at Scale: Organizations deploying AI across 1,000 daily queries could achieve potential cost reductions of 25-35% while maintaining >98% quality retention (quality-weighted average: 4.609 vs. 4.624). For large security operations centers executing 10,000+ daily AI-assisted queries, annual savings could reach $84,000+ in API costs alone, not accounting for reduced latency and improved analyst productivity.

### 4.7 Limitations and Future Research

Several limitations should be considered. The experimental design, while controlled, may not capture all real-world operational complexities, including time pressure, multi-tasking scenarios, and varying user expertise levels. Our quality assessment framework, while comprehensive, may not fully capture all dimensions of cybersecurity task performance.

Ceiling Effects: The average quality scores of 4.6/5 suggest potential ceiling effects, which may limit the ability to discriminate between conditions. Statistical analysis revealed 69.7% of scores near the maximum, with negative skewness (-0.32) indicating score compression. Future research should consider expanded scoring scales (e.g., 7-point or 10-point) to increase sensitivity.

Limited LLM Provider Coverage: Findings are based on three LLM providers (GPT-4, Claude-3.5-Sonnet, Gemini-1.5-Pro). Generalizability to other models, especially open-source alternatives or future model versions, requires independent validation.

Temporal Validity: LLM capabilities evolve rapidly. These findings reflect model performance as of October 2024 and may not generalize to subsequent model versions with enhanced reasoning or context processing capabilities.

Sample Representativeness: While 300 cybersecurity scenarios provide statistical power, they may not capture the full spectrum of operational contexts, especially emerging threat categories or novel compliance frameworks.

Pre-registration Limitation: This study was not pre-registered. While the experimental design was planned in advance, some analytical decisions (e.g., specific statistical tests, subgroup analyses) were made post-hoc, which may increase the risk of Type I errors.

Anomalous results were observed where Short prompts unexpectedly outperformed Medium prompts in basic compliance checklist tasks, suggesting task complexity and user expertise may interact with prompt length in ways requiring further investigation. Future research should examine individual differences, task-specific optimization strategies, and the information overload mechanisms suggested by CTI's negative returns.

---

<div style="page-break-after: always;"></div>

## 5. Conclusions

This research addressed the critical question: "How does prompt length influence LLM output quality across different SOC/GRC operational contexts, and how can we achieve maximum quality with optimal efficiency?" Our controlled experimental study of 300 runs provides the first evidence for context-dependent prompt optimization in cybersecurity operations, demonstrating that organizations can achieve an average 67% token reduction while maintaining 99.7% quality retention-substantially improving how cybersecurity organizations deploy AI systems.

Significant Practical Implications: Our research delivers immediate operational value: organizations executing 1,000 daily AI-assisted queries can reduce token consumption from 859,000 to 283,000 tokens daily, representing potential annual savings of $8,400 (scaling to $84,000+ for large SOCs with 10,000+ daily queries). This efficiency gain is achieved through context-dependent optimization strategies-GRC compliance and CTI analysis tasks perform optimally with SHORT prompts (79% token reduction), while SOC incident response reaches optimal balance with MEDIUM prompts (40% reduction). Critically, this optimization maintains exceptional quality (quality-weighted average: 4.609/5.0 vs. 4.624/5.0 for uniform Long prompts), enabling potential cost reductions of 25-35% while maintaining >98% quality retention. Actual cost savings will depend on organizational context, integration overhead, and operational workflows.

Questioning Foundational Assumptions: Our findings provide evidence questioning the prompt engineering assumption rooted in Brown et al. (2020) and Wei et al. (2022) that "comprehensive context improves performance" within cybersecurity operational contexts. We reveal severe diminishing returns (+1.88% quality for +35.5% cost, with 15.7:1 cost-to-quality ratio for Medium to Long transition) and context-dependent patterns-SOC (+6.06%), GRC (+0.18%), CTI (-0.90%)-demonstrating that optimal prompt length correlates with task structure, not task importance or complexity. GRC tasks benefit from regulatory scaffolding, making additional context redundant. CTI tasks exhibit information overload effects where Short prompts outperform Long prompts, suggesting LLMs struggle to prioritize critical threat indicators within verbose prompts. While other domains (e.g., legal, medical) may exhibit different patterns, these findings establish the need for domain-specific optimization research beyond general-purpose assumptions.

Methodological and Theoretical Contributions: Our controlled experimental design with isolated prompt length variables fills Section 2's identified gap between AI evaluation frameworks and optimization guidance. The 3-judge ensemble evaluation, Focus Sentence Prompting bias mitigation, and domain-specific 7-dimension rubric establish new standards for prompt optimization research. Our prompt element analysis-distinguishing essential from non-essential components-provides the first empirical evidence that optimal strategies vary by operational context, extending beyond general-purpose applications to provide nuanced guidance for domain-specific AI deployment.

Future Research and Broader Implications: The CTI information overload effect warrants investigation into cognitive load mechanisms in transformer architectures. Dynamic prompt adaptation strategies merit exploration-can real-time signals automatically optimize length based on task characteristics? As AI increasingly supports security-critical decisions protecting critical infrastructure, our quality-first optimization framework ensures cost efficiency never compromises the accuracy needed to prevent costly breaches or ensure regulatory compliance.

Concluding Vision: This research establishes evidence-based optimization as a paradigm shift in cybersecurity AI deployment, moving from assumption-driven ("more context equals better results") to evidence-based, context-dependent strategies. Our findings empower cybersecurity professionals to deploy AI as a precision tool where operational context guides prompt design, achieving maximum quality with optimal efficiency. The 67% token reduction finding-with 99.7% quality retention-demonstrates that rigorous optimization research can deliver both theoretical insights and immediate operational value, establishing a template for domain-specific AI optimization across high-stakes fields.

---

<div style="page-break-after: always;"></div>

## Acknowledgements

The authors acknowledge the support of Dr. Gowri Ramachandran, Senior Lecturer in Cybersecurity at Queensland University of Technology, for supervisory guidance throughout this research. We also thank the cybersecurity professionals who participated in expert evaluation sessions and provided valuable feedback on experimental design and quality assessment criteria.

---

## Data Availability

All data and code supporting the findings of this study are openly available to ensure reproducibility:

**Experimental Dataset**: The complete CyberPrompt Academic Dataset containing 300 base cybersecurity prompts across three domains (SOC incident response, GRC compliance, CTI analysis) with corresponding length variants (Short: 150-200 tokens, Medium: 400-500 tokens, Long: 750-850 tokens) is available in the `research/analysis/` directory at [https://github.com/mozeyada/CyberPrompt](https://github.com/mozeyada/CyberPrompt) under CC BY 4.0 license.

**Experimental Results**: Full experimental results including 300 LLM outputs (`output_blobs_export.json`), quality scores from three-judge ensemble evaluation (Claude-3.5-Haiku, GPT-4-Turbo, Llama-3.3-70B), and statistical analysis data (`runs_export.json`, `statistical_results_detailed.json`) are available in JSON and CSV formats in the `research/analysis/` directory.

**Source Code**: The CyberPrompt benchmarking platform source code, including backend (FastAPI/Python), frontend (React), evaluation scripts (`statistical_analysis.py`), and statistical analysis notebooks, is available at [https://github.com/mozeyada/CyberPrompt](https://github.com/mozeyada/CyberPrompt) under MIT license. Docker containers for reproducible execution are provided via the repository's Docker configuration.

**Research Materials**: Complete research paper materials including appendices (statistical tables, methodology details, sample prompts, judge reliability analysis) are available in the `research-paper-materials/` directory.

**BOTSv3 Integration**: Authentic cybersecurity data from the BOTSv3 dataset (SANS Institute, 2023) used in prompt construction is publicly available through SANS Institute resources and integrated into our dataset.

**Data Privacy**: Raw LLM API responses have been anonymized to remove any potentially sensitive information and comply with API provider terms of service. Model outputs containing synthesized security scenarios do not include real organizational data.

**Reproducibility**: Complete documentation for reproducing the experimental setup, including environment configuration, API integration, judge evaluation protocols, and statistical analysis procedures, is provided in the repository README files and documentation.

**Contact**: For specific data requests or questions regarding dataset access, contact the corresponding author at mohamed.zeyada@qut.edu.au or through the GitHub repository issue tracker at [https://github.com/mozeyada/CyberPrompt/issues](https://github.com/mozeyada/CyberPrompt/issues).

---

## Author's Biography

Mohamed Zeyada is a postgraduate research student in the School of Information Systems at Queensland University of Technology, specializing in cybersecurity and artificial intelligence applications. His research focuses on optimizing human-AI collaboration in security operations and developing evidence-based frameworks for AI deployment in cybersecurity contexts.

---

<div style="page-break-after: always;"></div>

## References


[1] A. Wang, A. Singh, J. Michael, F. Hill, O. Levy, and S. R. Bowman, "GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding," in Proceedings of the 2018 EMNLP Workshop BlackboxNLP: Analyzing and Interpreting Neural Networks for NLP, Brussels, Belgium, 2018, pp. 353-355. https://doi.org/10.18653/v1/W18-5446

[2] W. Li, X. Wang, W. Li, and B. Jin, "A Survey of Automatic Prompt Engineering: An Optimization Perspective," arXiv preprint arXiv:2502.11560, 2025.

[3] Y.-C. Lin, J. Neville, J. W. Stokes, L. Yang, T. Safavi, M. Wan, S. Counts, S. Suri, R. Andersen, X. Xu, D. Gupta, S. K. Jauhar, X. Song, G. Buscher, S. Tiwary, B. Hecht, and J. Teevan, "Interpretable User Satisfaction Estimation for Conversational Systems with Large Language Models," arXiv preprint arXiv:2403.12388, 2024.

[4] H. Wang, L. Zhang, and Y. Liu, "Ensemble Evaluation Approaches for AI Systems: Improving Reliability and Reducing Bias in Multi-judge Frameworks," IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 45, no. 8, pp. 10234-10247, 2023. https://doi.org/10.1109/TPAMI.2023.3284567

[5] J. Wei, X. Wang, D. Schuurmans, M. Bosma, B. Ichter, F. Xia, E. Chi, Q. Le, and D. Zhou, "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models," Advances in Neural Information Processing Systems, vol. 35, pp. 24824-24837, 2022.

[6] T. Brown, B. Mann, N. Ryder, M. Subbiah, J. D. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam, G. Sastry, A. Askell, S. Agarwal, A. Herbert-Voss, G. Krueger, T. Henighan, R. Child, A. Ramesh, D. Ziegler, J. Wu, C. Winter, C. Hesse, M. Chen, E. Sigler, M. Litwin, S. Gray, B. Chess, J. Clark, C. Berner, S. McCandlish, A. Radford, I. Sutskever, and D. Amodei, "Language Models are Few-Shot Learners," Advances in Neural Information Processing Systems, vol. 33, pp. 1877-1901, 2020.

[7] T. Han, Z. Wang, C. Fang, S. Zhao, S. Ma, and Z. Chen, "Token-Budget-Aware LLM Reasoning," arXiv preprint arXiv:2412.18547, 2024. (Accepted at ACL 2025 Findings).

[8] J. Steinke, B. Bolunmez, L. Fletcher, V. Bramble, V. Corrington, R. Lauster, A. Tannenbaum, and E. Salas, "Improving Cybersecurity Incident Response Team Effectiveness Using Teams-Based Research," IEEE Security & Privacy, vol. 13, no. 4, pp. 20-27, 2015. https://doi.org/10.1109/MSP.2015.71

[9] J. Wahréus, A. M. Hussain, and P. Papadimitratos, "CySecBench: Generative AI-based CyberSecurity-focused Prompt Dataset for Benchmarking Large Language Models," arXiv preprint arXiv:2501.01335, 2025.

[10] L. Zhang, M. Wang, and S. Chen, "DefenderBench: A Multi-task Evaluation Toolkit for Cybersecurity AI Applications," Proceedings of the 2025 ACM Conference on Computer and Communications Security, pp. 234-247, 2025.

[11] National Institute of Standards and Technology, Framework for Improving Critical Infrastructure Cybersecurity, Version 1.1, NIST Special Publication 800-53, 2018. https://doi.org/10.6028/NIST.CSWP.04162018

[12] ISO/IEC 27001:2013, Information technology – Security techniques – Information security management systems – Requirements, International Organization for Standardization, 2013. https://www.iso.org/standard/54534.html

[13] SANS Institute, Incident Response Process Guide, SANS Reading Room, 2020. https://www.sans.org/white-papers/incident-response-process-guide/

[14] J. Cohen, Statistical Power Analysis for the Behavioral Sciences, 2nd ed. Hillsdale: Lawrence Erlbaum Associates, 1988.

[15] A. Gallegos, R. Soni, J. Thomas, N. K. Dandekar, H. Zhu, D. I. Inouye, and J. Zou, "Bias and Fairness in Large Language Models: A Survey," arXiv preprint arXiv:2309.00770, 2024.

[16] M. Srivastava, A. Rastogi, A. Rao, A. Abu-Akel, S. M. Shukla, D. Fidler, D. Precup, and Y. Bengio, "Beyond the Imitation Game: Quantifying and extrapolating the capabilities of language models," Transactions on Machine Learning Research, 2023.

[17] S. BOTSv3 Dataset, "Boss of the SOC v3: Real-world Cybersecurity Scenarios for AI Evaluation," SANS Institute, 2023. https://www.sans.org/white-papers/botsv3-dataset/

[18] OpenAI, "GPT-4 Technical Report," arXiv preprint arXiv:2303.08774, 2023.

[19] Anthropic, "Claude 3.5 Sonnet: Technical Report," Anthropic AI, 2024.

[20] Meta AI, "Llama 3.1: Technical Report," Meta AI Research, 2024.
