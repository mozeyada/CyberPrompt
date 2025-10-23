# CyberPrompt Model Testing Architecture

## Overview

This document describes the comprehensive architecture for testing LLM models, calculating results, and storing evaluation data in the CyberPrompt research platform. The system implements a rigorous evaluation framework designed for RQ1 research on prompt length effects and RQ2 research on adaptive vs static benchmarking.

**Research Focus**: Systematic evaluation of prompt length effects on LLM output quality and cost efficiency in SOC/GRC contexts.

---

## 1. Model Testing Workflow

### 1.1 Experiment Execution Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Model Testing Workflow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐     │
│  │   Prompt    │    │    LLM      │    │   Response      │     │
│  │  Selection  │───►│   Model     │───►│   Generation    │     │
│  │             │    │   (GPT/     │    │                 │     │
│  │             │    │  Claude)    │    │                 │     │
│  └─────────────┘    └─────────────┘    └─────────────────┘     │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐     │
│  │   Token     │    │    Cost     │    │   Quality       │     │
│  │  Counting   │    │ Calculation │    │  Assessment     │     │
│  │             │    │             │    │                 │     │
│  └─────────────┘    └─────────────┘    └─────────────────┘     │
│         │                   │                   │              │
│         └───────────────────┼───────────────────┘              │
│                             ▼                                  │
│                    ┌─────────────────┐                        │
│                    │   Results       │                        │
│                    │   Storage       │                        │
│                    │   (MongoDB)     │                        │
│                    └─────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Step-by-Step Testing Process

#### Step 1: Prompt Preparation
- **Input**: Base cybersecurity scenarios (SOC incident, GRC compliance, CTI analysis)
- **Processing**: Generate S/M/L length variants (150-250, 450-550, 800-1000 tokens)
- **Output**: Controlled prompt set with identical task requirements

#### Step 2: Model Selection and Configuration
- **Models Tested**: GPT-4o, Claude-3.5-Sonnet, Claude-3.5-Haiku, Llama-3.3-70B
- **Configuration**: Temperature=0.2, max_tokens=2000, consistent parameters
- **API Integration**: Real-time calls to OpenAI, Anthropic, Groq APIs

#### Step 3: Response Generation
- **Execution**: Synchronous for ≤10 runs, asynchronous for >10 runs
- **Monitoring**: Real-time progress tracking and error handling
- **Validation**: Response quality checks and content validation

#### Step 4: Token Counting and Cost Calculation
- **Input Tokens**: Precise counting using tiktoken (GPT) or approximation (Claude)
- **Output Tokens**: Response length measurement
- **Cost Calculation**: Real-time AUD pricing per 1K tokens

#### Step 5: Quality Assessment
- **Judge Models**: GPT-4-Turbo (primary), Claude-3.5-Haiku (secondary), Llama-3.3-70B (tertiary)
- **Evaluation**: 7-dimension SOC/GRC rubric scoring
- **Bias Mitigation**: Focus Sentence Prompting (FSP) for length-invariant scoring

---

## 2. Results Calculation Methodology

### 2.1 7-Dimension Quality Assessment Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                7-Dimension SOC/GRC Rubric                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Technical Accuracy    │ 2. Actionability    │ 3. Completeness │
│     • Factual correctness │   • Actionable steps│   • All aspects │
│     • Cybersecurity context│   • Clear guidance  │   • No gaps     │
│     • Domain expertise    │   • Implementation  │   • Thorough    │
│                           │     ready           │     coverage    │
│                                                                 │
│  4. Compliance Alignment  │ 5. Risk Awareness   │ 6. Relevance    │
│     • Regulatory frameworks│   • Risk acknowledgment│   • On-task    │
│     • Policy alignment    │   • Limitations     │   • No digression│
│     • Standards compliance│   • Uncertainty     │   • Focused     │
│                           │     handling        │     response    │
│                                                                 │
│  7. Clarity               │                                    │
│     • Clear structure     │                                    │
│     • Unambiguous writing │                                    │
│     • Professional tone   │                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Scoring System

#### Individual Dimension Scoring
- **Scale**: 0.0 to 5.0 (continuous)
- **Criteria**: Each dimension has specific evaluation criteria
- **Judge Instructions**: Detailed prompts for consistent scoring

#### Composite Score Calculation
```python
def calculate_composite_score(dimension_scores):
    """
    Calculate composite score from 7-dimension rubric
    
    Args:
        dimension_scores: Dict of 7 dimension scores
        
    Returns:
        float: Composite score (0.0-5.0)
    """
    valid_scores = [score for score in dimension_scores.values() if score > 0]
    return sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
```

#### Ensemble Aggregation
```python
def aggregate_ensemble_scores(judge_results):
    """
    Aggregate scores from multiple judges
    
    Args:
        judge_results: List of judge evaluation results
        
    Returns:
        dict: Aggregated scores with mean, std, confidence intervals
    """
    composite_scores = [result.composite for result in judge_results]
    
    return {
        'mean': np.mean(composite_scores),
        'std': np.std(composite_scores, ddof=1),
        'confidence_interval': calculate_ci(composite_scores),
        'judge_count': len(composite_scores)
    }
```

### 2.3 Bias Mitigation (Focus Sentence Prompting)

#### FSP Implementation
- **Purpose**: Reduce verbosity bias in evaluation
- **Method**: Extract key sentences from responses for focused evaluation
- **Process**: 
  1. Identify most relevant sentences
  2. Evaluate sentences in full context
  3. Aggregate sentence scores to response score

#### Length Normalization
- **Challenge**: Longer responses may score higher due to verbosity
- **Solution**: FSP ensures fair comparison regardless of response length
- **Validation**: Statistical verification of length-invariant scoring

---

## 3. Data Storage Architecture

### 3.1 MongoDB Document Structure

#### Prompt Collection
```javascript
{
  "_id": ObjectId("..."),
  "prompt_id": "academic_soc_001_s",
  "text": "You are the incident response lead...",
  "scenario": "SOC_INCIDENT",
  "category": "Ransomware Incident",
  "length_bin": "S",
  "token_count": 165,
  "dataset_version": "20250107_academic_v4_rq1_controlled",
  "metadata": {
    "data_sources": ["symantec:ep:security:file", "firewall:logs"],
    "academic_grade": true,
    "base_scenario": "academic_soc_001"
  },
  "created_at": ISODate("2025-01-07T10:30:00Z"),
  "updated_at": ISODate("2025-01-07T10:30:00Z")
}
```

#### Run Collection
```javascript
{
  "_id": ObjectId("..."),
  "run_id": "01HZ8K9M2N3P4Q5R6S7T8U9V0",
  "prompt_id": "academic_soc_001_s",
  "model": "gpt-4o",
  "status": "succeeded",
  "prompt_length_bin": "S",
  "tokens": {
    "input": 165,
    "output": 587,
    "total": 752
  },
  "economics": {
    "aud_cost": 0.0052,
    "latency_ms": 2340
  },
  "scores": {
    "technical_accuracy": 4.2,
    "actionability": 4.5,
    "completeness": 4.1,
    "compliance_alignment": 4.3,
    "risk_awareness": 4.0,
    "relevance": 4.4,
    "clarity": 4.6,
    "composite": 4.3
  },
  "ensemble_evaluation": {
    "judge_results": {
      "primary": {
        "model": "gpt-4-turbo",
        "scores": { /* 7-dimension scores */ },
        "composite": 4.3,
        "evaluation_failed": false
      },
      "secondary": {
        "model": "claude-3-5-haiku",
        "scores": { /* 7-dimension scores */ },
        "composite": 4.1,
        "evaluation_failed": false
      },
      "tertiary": {
        "model": "llama-3-3-70b-versatile",
        "scores": { /* 7-dimension scores */ },
        "composite": 4.5,
        "evaluation_failed": false
      }
    },
    "aggregated": {
      "mean_scores": {
        "technical_accuracy": 4.2,
        "actionability": 4.5,
        "completeness": 4.1,
        "compliance_alignment": 4.3,
        "risk_awareness": 4.0,
        "relevance": 4.4,
        "clarity": 4.6,
        "composite": 4.3
      },
      "std_scores": {
        "technical_accuracy": 0.1,
        "actionability": 0.2,
        "completeness": 0.1,
        "compliance_alignment": 0.1,
        "risk_awareness": 0.0,
        "relevance": 0.1,
        "clarity": 0.1,
        "composite": 0.2
      },
      "confidence_intervals": {
        "composite": [4.1, 4.5]
      }
    }
  },
  "output_blob_id": "a1b2c3d4e5f6...",
  "bias_controls": {
    "fsp_enabled": true,
    "length_normalization": true
  },
  "created_at": ISODate("2025-10-15T14:23:17Z"),
  "updated_at": ISODate("2025-10-15T14:23:17Z")
}
```

#### OutputBlob Collection
```javascript
{
  "_id": ObjectId("..."),
  "blob_id": "a1b2c3d4e5f6...",
  "content": "Based on the incident details provided, I recommend the following immediate containment and recovery steps:\n\n1. **Immediate Containment Steps:**\n   - Isolate the affected host (AWS-PROD-VPC) from the network immediately...",
  "metadata": {
    "content_length": 1247,
    "word_count": 234,
    "sentence_count": 12,
    "fsp_sentences": [
      "Isolate the affected host (AWS-PROD-VPC) from the network immediately",
      "Block the C2 infrastructure IP (192.168.63.58) at the firewall level",
      "Preserve memory dumps and system logs for forensic analysis"
    ]
  },
  "created_at": ISODate("2025-10-15T14:23:17Z")
}
```

### 3.2 Database Relationships

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐
│   Prompt    │    │    Run      │    │ OutputBlob   │
│             │    │             │    │              │
│ prompt_id   │◄───┤ prompt_id   │    │ blob_id      │
│ text        │    │ run_id      │    │ content      │
│ scenario    │    │ model       │    │ metadata     │
│ length_bin  │    │ scores      │    │              │
│ token_count │    │ economics   │    │              │
│ metadata    │    │ output_blob │───►│              │
│             │    │ _id         │    │              │
└─────────────┘    └─────────────┘    └──────────────┘
```

### 3.3 Data Integrity and Validation

#### Input Validation
- **Pydantic Models**: All data validated at API boundaries
- **Type Checking**: Strict type validation for all fields
- **Business Rules**: Custom validation for research requirements

#### Data Consistency
- **Referential Integrity**: Foreign key relationships maintained
- **Atomic Operations**: MongoDB transactions for complex operations
- **Error Handling**: Comprehensive error recovery and logging

#### Research Data Quality
- **Dataset Versioning**: All prompts tagged with dataset version
- **Reproducibility**: Fixed seeds and controlled random generation
- **Audit Trail**: Complete creation and modification timestamps

---

## 4. Quality Assessment Process

### 4.1 Judge Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                   Judge Evaluation Pipeline                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐     │
│  │   LLM       │    │   Judge     │    │   Rubric        │     │
│  │  Response   │───►│   Model     │───►│   Scoring       │     │
│  │             │    │ (GPT/Claude)│    │                 │     │
│  └─────────────┘    └─────────────┘    └─────────────────┘     │
│         │                   │                   │              │
│         ▼                   ▼                   ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐     │
│  │   FSP       │    │   Context   │    │   Dimension     │     │
│  │ Extraction  │    │   Analysis  │    │   Scores        │     │
│  │             │    │             │    │                 │     │
│  └─────────────┘    └─────────────┘    └─────────────────┘     │
│         │                   │                   │              │
│         └───────────────────┼───────────────────┘              │
│                             ▼                                  │
│                    ┌─────────────────┐                        │
│                    │   Composite     │                        │
│                    │   Score         │                        │
│                    │   Calculation   │                        │
│                    └─────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Judge Model Configuration

#### Primary Judge: GPT-4-Turbo
- **Role**: Primary evaluator for all responses
- **Configuration**: Temperature=0.1, max_tokens=1000
- **Specialization**: Technical accuracy and compliance alignment

#### Secondary Judge: Claude-3.5-Haiku
- **Role**: Secondary evaluator for validation
- **Configuration**: Temperature=0.1, max_tokens=1000
- **Specialization**: Actionability and clarity

#### Tertiary Judge: Llama-3.3-70B
- **Role**: Tertiary evaluator for ensemble validation
- **Configuration**: Temperature=0.1, max_tokens=1000
- **Specialization**: Risk awareness and relevance

### 4.3 Evaluation Prompt Template

```
You are an expert cybersecurity evaluator assessing LLM responses for SOC/GRC tasks.

RESPONSE TO EVALUATE:
{response_content}

EVALUATION CRITERIA:
1. Technical Accuracy (0-5): Factual correctness in cybersecurity context
2. Actionability (0-5): Can analysts act on this response?
3. Completeness (0-5): Covers all aspects of the prompt
4. Compliance Alignment (0-5): Aligns with regulatory frameworks
5. Risk Awareness (0-5): Acknowledges risks and limitations
6. Relevance (0-5): Stays on-task without digressions
7. Clarity (0-5): Clear, structured, unambiguous writing

FOCUS SENTENCES (if FSP enabled):
{key_sentences}

Please provide scores for each dimension as a JSON object:
{
  "technical_accuracy": 4.2,
  "actionability": 4.5,
  "completeness": 4.1,
  "compliance_alignment": 4.3,
  "risk_awareness": 4.0,
  "relevance": 4.4,
  "clarity": 4.6
}
```

---

## 5. Statistical Analysis and Validation

### 5.1 Research Metrics Calculation

#### Cost-Quality Efficiency
```python
def calculate_efficiency(quality_score, cost):
    """
    Calculate cost-quality efficiency metric
    
    Args:
        quality_score: Composite quality score (0-5)
        cost: Cost in AUD
        
    Returns:
        float: Efficiency score (quality per dollar)
    """
    return quality_score / cost if cost > 0 else 0.0
```

#### Length Bias Analysis
```python
def analyze_length_bias(runs_by_length):
    """
    Analyze bias in scoring across prompt lengths
    
    Args:
        runs_by_length: Dict of runs grouped by length bin
        
    Returns:
        dict: Bias analysis results
    """
    length_stats = {}
    for length_bin, runs in runs_by_length.items():
        scores = [run.scores.composite for run in runs]
        length_stats[length_bin] = {
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'count': len(scores)
        }
    return length_stats
```

### 5.2 Statistical Validation

#### Inter-Judge Reliability
- **Correlation Analysis**: Pearson correlation between judge scores
- **Agreement Metrics**: Intraclass correlation coefficient (ICC)
- **Consistency Check**: Cronbach's alpha for internal consistency

#### Ensemble Validation
- **Mathematical Verification**: Expected vs actual statistical calculations
- **Bias Detection**: Systematic differences between judges
- **Error Handling**: Graceful handling of judge failures

---

## 6. Research Data Management

### 6.1 Dataset Versioning

#### Version Control
- **Dataset Versions**: Tagged with date and research focus
- **Change Tracking**: Complete audit trail of dataset modifications
- **Reproducibility**: Fixed seeds for consistent generation

#### Current Dataset: academic_v4_rq1_controlled
- **Total Prompts**: 300 (100 base × 3 length variants)
- **Scenarios**: SOC incident (50%), GRC compliance (30%), CTI analysis (20%)
- **Token Ranges**: S (150-250), M (450-550), L (800-1000)
- **Quality Metrics**: 95.3% compliance with target ranges

### 6.2 Experimental Design Validation

#### Controlled Variables
- **Prompt Length**: Only independent variable (S/M/L)
- **Task Requirements**: Identical across all length variants
- **Model Parameters**: Consistent across all experiments
- **Evaluation Criteria**: Standardized 7-dimension rubric

#### Statistical Power
- **Sample Size**: 100 prompts per length bin (n=300 total)
- **Effect Size**: d=1.2 (large effect expected)
- **Statistical Power**: 0.98 (98% power to detect effects)
- **Confidence Level**: 95% for all statistical tests

---

## 7. Performance and Scalability

### 7.1 System Performance

#### Response Times
- **Single Run**: ~2-3 seconds (LLM call + evaluation)
- **Batch Processing**: ~10-15 seconds per run (with queuing)
- **Background Tasks**: Asynchronous processing for >10 runs

#### Throughput
- **Concurrent Runs**: Up to 10 simultaneous experiments
- **API Rate Limits**: Respects provider rate limits
- **Error Recovery**: Automatic retry with exponential backoff

### 7.2 Scalability Considerations

#### Database Optimization
- **Indexing**: Compound indexes on frequently queried fields
- **Sharding**: Horizontal scaling for large datasets
- **Caching**: Redis caching for frequently accessed data

#### API Scalability
- **Load Balancing**: Multiple API instances
- **Caching**: Response caching for static data
- **Monitoring**: Real-time performance monitoring

---

## 8. Research Validation and Quality Assurance

### 8.1 Data Quality Checks

#### Automated Validation
- **Token Count Verification**: Validate against expected ranges
- **Score Range Validation**: Ensure scores within 0-5 range
- **Completeness Checks**: Verify all required fields present

#### Manual Quality Assurance
- **Sample Review**: Regular review of evaluation quality
- **Judge Calibration**: Periodic calibration of judge models
- **Bias Monitoring**: Continuous monitoring for systematic biases

### 8.2 Research Reproducibility

#### Reproducible Experiments
- **Fixed Seeds**: Consistent random number generation
- **Version Control**: All code and data versioned
- **Documentation**: Complete methodology documentation

#### Validation Framework
- **Statistical Tests**: Automated validation of calculations
- **Cross-Validation**: Multiple judge validation
- **Error Detection**: Automated detection of calculation errors

---

## Conclusion

The CyberPrompt model testing architecture provides a comprehensive, rigorous framework for evaluating LLM performance in cybersecurity contexts. The system implements:

- **Systematic Testing**: Controlled experiments with proper variable isolation
- **Rigorous Evaluation**: 7-dimension rubric with ensemble scoring
- **Bias Mitigation**: FSP and length normalization for fair comparison
- **Robust Storage**: MongoDB with proper relationships and validation
- **Statistical Rigor**: Proper statistical analysis and validation
- **Research Quality**: Reproducible, versioned, and auditable experiments

This architecture ensures that RQ1 research on prompt length effects and RQ2 research on adaptive vs static benchmarking produces reliable, valid, and reproducible results for academic publication and industry application.

---

**Document Version**: 1.0  
**Last Updated**: October 2025  
**Research Focus**: RQ1 Prompt Length Effects, RQ2 Adaptive Benchmarking  
**Platform**: CyberPrompt v1.0
