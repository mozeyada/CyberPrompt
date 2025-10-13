# Variant Testing Verification Guide

## Overview

This document explains the comprehensive logging instrumentation added to verify that S/M/L prompt variants are being tested correctly and producing genuinely different scores, not artificially similar results due to bugs.

## What Was Implemented

Comprehensive logging has been added to all critical points in the evaluation pipeline with the prefix `[VARIANT-CHECK]` to make it easy to filter and analyze variant testing. The logging covers:

### 1. Prompt Execution & LLM Response (`app/services/experiment.py`)

**Location**: `execute_run()` method, lines 167-178, 201-202, 243-244, 260

**What is logged**:
- **Before LLM execution**: 
  - `prompt_id` - Which prompt variant is being used
  - `length_bin` - Should be S, M, or L
  - `prompt_length` - Character count of prompt text
  - `model` - LLM model being tested
  
- **After LLM execution**:
  - `response_length` - Character count of LLM response
  - `success` - Whether LLM call succeeded
  
- **After blob storage**:
  - `blob_id` - Should be unique per variant
  - `content_length` - Response character count
  
- **Before ensemble evaluation**:
  - `length_bin` - Confirm correct variant
  - `output_len` - Response being judged
  - `context_len` - Original prompt length

**Purpose**: Verify that different prompt texts are being sent to the LLM and producing different responses.

### 2. Ensemble Evaluation Coordination (`app/services/ensemble.py`)

**Location**: `evaluate_with_ensemble()` method, lines 45-46, 74-77, 111-112, 161-162, 210-211

**What is logged**:
- **Ensemble start**:
  - `length_bin` - Variant being evaluated
  - `output_len` - LLM response length
  - `context_len` - Original prompt length
  - `scenario` - Task type
  
- **Individual judge scores** (for each of 3 judges):
  - `judge_model` - Which judge (GPT-4o-mini, Claude, Llama)
  - `composite` - Overall score
  - `technical_accuracy` - First dimension
  - `completeness` - Second dimension
  
- **Before aggregation**:
  - Number of judges providing scores
  
- **After aggregation**:
  - `mean_composite` - Average across 3 judges
  - `std_composite` - Standard deviation (should be >0)
  - `mean_tech_acc` - Average technical accuracy

**Purpose**: Verify that all 3 judges receive the correct output and produce scores with some variance.

### 3. Individual Judge Evaluation (`app/services/base.py`)

**Location**: `_evaluate_standard()` method, lines 71-72, 103-104

**What is logged**:
- **Before judge evaluation**:
  - `judge_model` - Which judge is evaluating
  - `output_len` - Response being judged
  - `context_len` - Original prompt for reference
  - `length_bin` - Variant type
  - `scenario` - Task type
  
- **After judge scoring**:
  - `composite` - Overall score from this judge
  - `technical_accuracy` - Individual dimension
  - `completeness` - Individual dimension
  - `clarity` - Individual dimension

**Purpose**: Verify that each judge receives different content for S/M/L variants and produces different scores.

### 4. Score Normalization (`app/services/composite.py`)

**Location**: `normalize_rubric_scores()` function, lines 42-43, 56-57

**What is logged** (at DEBUG level):
- **Before normalization**:
  - Raw input scores dictionary
  
- **After normalization**:
  - Final composite score
  - Number of non-zero dimensions out of 7

**Purpose**: Verify that score calculation is correct and all dimensions are present.

## How to Use This Instrumentation

### Step 1: Enable INFO Logging

Ensure your logging configuration shows INFO level messages. In your `.env` or logging config:

```bash
LOG_LEVEL=INFO
```

### Step 2: Run a Controlled Test

Execute a minimal test experiment:
- **1 base prompt** (e.g., a prompt ending with `_s`)
- **Include variants enabled** (will automatically add `_m` and `_l` versions)
- **1 model** (e.g., gpt-4o-mini)
- **Ensemble evaluation enabled**

This will create **3 runs total** (one per variant).

### Step 3: Filter and Analyze Logs

Filter logs for the verification tags:

```bash
# View all variant verification logs
grep "\[VARIANT-CHECK\]" backend.log

# View only prompt and response details
grep "\[VARIANT-CHECK\].*Executing\|response_length" backend.log

# View only judge scores
grep "\[VARIANT-CHECK\].*scores:" backend.log

# View aggregation results
grep "\[VARIANT-CHECK\].*aggregation" backend.log
```

### Step 4: Verification Checklist

#### ✅ **Prompts Are Different**
Look for lines like:
```
[VARIANT-CHECK] Executing run_001: prompt_id=soc_001_s, length_bin=S, prompt_length=200, model=gpt-4o-mini
[VARIANT-CHECK] Executing run_002: prompt_id=soc_001_m, length_bin=M, prompt_length=500, model=gpt-4o-mini
[VARIANT-CHECK] Executing run_003: prompt_id=soc_001_l, length_bin=L, prompt_length=900, model=gpt-4o-mini
```

**Expected**: `prompt_length` should increase significantly (2-5x) from S→M→L

**Suspicious**: All three prompts have similar lengths (within 10%)

#### ✅ **LLM Responses Are Different**
Look for lines like:
```
[VARIANT-CHECK] LLM response for run_001: response_length=350, success=True
[VARIANT-CHECK] LLM response for run_002: response_length=650, success=True
[VARIANT-CHECK] LLM response for run_003: response_length=1100, success=True
```

**Expected**: `response_length` should increase with prompt length

**Suspicious**: All responses are identical or very similar lengths

#### ✅ **Blob IDs Are Unique**
Look for lines like:
```
[VARIANT-CHECK] Stored blob for run_001: blob_id=a1b2c3d4e5f6..., content_length=350
[VARIANT-CHECK] Stored blob for run_002: blob_id=x9y8z7w6v5u4..., content_length=650
[VARIANT-CHECK] Stored blob for run_003: blob_id=m3n2o1p0q9r8..., content_length=1100
```

**Expected**: Each run has a **different** `blob_id`

**Suspicious**: Same `blob_id` appears for multiple runs (indicates overwrites)

#### ✅ **Ensemble Receives Correct Inputs**
Look for lines like:
```
[VARIANT-CHECK] Ensemble evaluation start for run_001: length_bin=S, output_len=350, context_len=200
[VARIANT-CHECK] Ensemble evaluation start for run_002: length_bin=M, output_len=650, context_len=500
[VARIANT-CHECK] Ensemble evaluation start for run_003: length_bin=L, output_len=1100, context_len=900
```

**Expected**: `length_bin` correct (S/M/L), `output_len` and `context_len` differ

**Suspicious**: `length_bin` is null or incorrect, lengths are identical

#### ✅ **Judges Produce Different Scores**
Look for lines like:
```
[VARIANT-CHECK] Judge gpt-4o-mini (primary) scores for run_001: composite=3.100, technical_accuracy=3.0, completeness=3.0
[VARIANT-CHECK] Judge gpt-4o-mini (primary) scores for run_002: composite=3.600, technical_accuracy=3.5, completeness=3.8
[VARIANT-CHECK] Judge gpt-4o-mini (primary) scores for run_003: composite=4.100, technical_accuracy=4.0, completeness=4.3
```

**Expected**: Scores increase for longer prompts (S < M < L) by at least 0.3-0.5 points

**Suspicious**: All scores within 0.1 points (suspiciously close)

#### ✅ **Judges Show Variance**
Look for the same run across different judges:
```
[VARIANT-CHECK] Judge gpt-4o-mini (primary) scores for run_001: composite=3.100
[VARIANT-CHECK] Judge claude-3-5-sonnet (secondary) scores for run_001: composite=3.300
[VARIANT-CHECK] Judge llama-3.3-70b (tertiary) scores for run_001: composite=2.900
```

**Expected**: Judges disagree by 0.2-0.5 points (healthy variance)

**Suspicious**: All three judges return **identical** scores (std = 0.0)

#### ✅ **Aggregation Shows Standard Deviation**
Look for lines like:
```
[VARIANT-CHECK] Ensemble aggregation complete: mean_composite=3.100, std_composite=0.200, mean_tech_acc=3.067
[VARIANT-CHECK] Ensemble aggregation complete: mean_composite=3.600, std_composite=0.233, mean_tech_acc=3.567
[VARIANT-CHECK] Ensemble aggregation complete: mean_composite=4.100, std_composite=0.200, mean_tech_acc=4.067
```

**Expected**: `std_composite` > 0.15 (judges have some disagreement)

**Suspicious**: `std_composite` = 0.0 (all judges identical)

## Expected Results vs. Bugs

### ✅ Healthy System (Expected)

```
Prompt Lengths:
- S: 200-250 chars
- M: 450-550 chars  (2-2.5x longer than S)
- L: 800-1000 chars (4-5x longer than S)

Response Lengths:
- S: 300-500 chars
- M: 500-800 chars
- L: 800-1200 chars

Scores (example):
- S: composite=3.1, technical_accuracy=3.0, completeness=3.0
- M: composite=3.6, technical_accuracy=3.5, completeness=3.8
- L: composite=4.1, technical_accuracy=4.0, completeness=4.3

Judge Variance (per run):
- std_composite: 0.15-0.35

Score Progression:
- S→M improvement: +0.5 points (16%)
- M→L improvement: +0.5 points (14%)
- S→L improvement: +1.0 points (32%)
```

### 🐛 Bug Indicators (Suspicious)

```
❌ All prompt lengths identical: 200, 200, 200
   → Variant lookup is failing, only base prompt used

❌ All response lengths identical: 350, 350, 350
   → Same response stored for all variants (blob collision?)

❌ Same blob_id for multiple runs
   → Responses being overwritten, not stored separately

❌ All scores within 0.1 points: 3.5, 3.52, 3.51
   → Either variants not different OR judges too consistent

❌ Judge std = 0.0 for all runs
   → All judges returning identical scores (caching bug?)

❌ length_bin field is null or incorrect
   → Variant metadata not being stored correctly

❌ No correlation between prompt length and score
   → Quality doesn't improve with more context (unexpected)
```

## Statistical Analysis

After collecting logs from a full experiment, perform statistical analysis:

### 1. Extract Scores by Variant

```python
import re
import pandas as pd

# Parse logs
with open('backend.log', 'r') as f:
    logs = f.read()

# Extract ensemble scores
pattern = r'\[VARIANT-CHECK\] Ensemble scores for (run_\d+): composite=(\d+\.\d+)'
matches = re.findall(pattern, logs)

# Create DataFrame
df = pd.DataFrame(matches, columns=['run_id', 'composite_score'])
df['composite_score'] = df['composite_score'].astype(float)

# Map runs to variants (from earlier logs)
# ... add length_bin mapping ...

# Group by length_bin
summary = df.groupby('length_bin')['composite_score'].agg(['mean', 'std', 'count'])
print(summary)
```

### 2. Expected Statistical Properties

```python
# Effect size (Cohen's d) between S and L
mean_S = scores_S.mean()
mean_L = scores_L.mean()
pooled_std = np.sqrt((scores_S.std()**2 + scores_L.std()**2) / 2)
cohens_d = (mean_L - mean_S) / pooled_std

# Expected: Cohen's d > 0.5 (medium effect)
# Suspicious: Cohen's d < 0.2 (negligible effect)

# Statistical significance
from scipy.stats import ttest_ind
t_stat, p_value = ttest_ind(scores_S, scores_L)

# Expected: p < 0.05 (significant difference)
# Suspicious: p > 0.1 (no significant difference)
```

## Troubleshooting Guide

### Problem: Can't find `[VARIANT-CHECK]` logs

**Solution**: 
1. Check logging level is set to INFO
2. Ensure logs are being written to file
3. Verify backend is using latest code (restart if needed)

### Problem: Prompt lengths all identical

**Investigation**:
1. Check MongoDB prompts collection for variant prompts
2. Verify `prompt_id` pattern includes `_s`, `_m`, `_l` suffixes
3. Check `include_variants` flag is True in experiment request
4. Review variant expansion logic in `experiment.py:66-98`

### Problem: Scores suspiciously close

**Investigation**:
1. Check if LLM responses are actually different (compare `response_length`)
2. Verify judge temperature is 0.1 (correct for consistency)
3. Check if all judges return identical scores (indicates caching issue)
4. Review judge standard deviation - should be >0

### Problem: Same blob_id for different runs

**Investigation**:
1. Check `generate_blob_id()` function includes `run_id`
2. Verify each run has unique `run_id`
3. Check MongoDB output_blobs collection for duplicates
4. Review blob storage logic in `experiment.py:182-193`

## Next Steps

After verifying the logging output:

1. **If logs show variants are working correctly**:
   - The close scores might be legitimate (prompts naturally produce similar quality)
   - Analyze judge variance and statistical significance
   - Consider testing with more diverse prompts
   
2. **If logs reveal a bug**:
   - Document the specific issue found
   - Refer to the relevant code section in this guide
   - Fix the bug and re-run test
   
3. **For deeper analysis**:
   - Export full log file
   - Parse with Python scripts
   - Generate comparison charts
   - Calculate statistical metrics

## Log File Locations

- **Docker**: Check container logs with `docker logs backend`
- **Local**: Check `backend.log` or console output
- **Production**: Check configured log file path in `.env`

## Summary

This instrumentation provides comprehensive visibility into the variant testing pipeline. By examining the `[VARIANT-CHECK]` logs, you can definitively determine whether:

1. ✅ Prompts differ across S/M/L variants
2. ✅ LLM responses differ appropriately
3. ✅ Each run stores unique outputs
4. ✅ Ensemble judges receive correct inputs
5. ✅ Judges produce varying scores
6. ✅ Scores improve with prompt length
7. ✅ Standard deviation indicates healthy disagreement

If all checks pass but scores are still close, this indicates the LLMs genuinely produce similar-quality responses regardless of prompt length - a valid (if unexpected) research finding.


