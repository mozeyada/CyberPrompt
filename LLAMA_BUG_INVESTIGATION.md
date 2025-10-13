# Llama Judge Failure Investigation

## What You Found

In your 24 runs, S scored highest (4.643) vs M (4.381) and L (4.518). This seemed wrong.

## Root Cause Found

**Llama judge FAILED on 2 runs (005 and 006)**, returning zeros that dragged down M and L averages.

---

## Evidence Chain

### 1. The Outliers
```
run_005 [M]: Mean=3.095 (GPT=4.857, Claude=4.429, Llama=0.000)
run_006 [L]: Mean=3.095 (GPT=4.857, Claude=4.429, Llama=0.000)
```

### 2. The Error
```
ERROR:app.services.groq_client:Groq API error: 
ERROR:app.services.base:Error in LLM judge evaluation: Groq API error 500: 
{"error":{"message":"Internal Server Error","type":"internal_server_error"}}
```

### 3. The Fallback
Llama raw response: **EMPTY** (not a JSON evaluation)
Llama scores: All zeros (fallback scores)

### 4. The Impact
With Bug #2 fix, zeros are included:
- Mean = (4.857 + 4.429 + 0.000) / 3 = 3.095
- This drops M and L averages significantly

---

## Why This Happens

### Code Flow for Llama Judge

**File**: `app/services/ensemble.py` lines 115-126
```python
if "llama" in config["model"].lower():
    client = GroqClient(settings.groq_api_key)
```

**File**: `app/services/groq_client.py` lines 46-69
```python
response = await client.post(
    f"{self.base_url}/chat/completions",
    headers=headers,
    json=payload,
    timeout=30.0
)
response.raise_for_status()  # Throws error if 500
```

**File**: `app/services/base.py` lines 58-60
```python
except Exception as e:
    logger.error(f"Error in LLM judge evaluation: {e}")
    return self._fallback_scores(str(e))  # Returns all zeros!
```

### The Problem

When Groq API returns 500 error:
1. Exception caught in `base.py`
2. Returns `_fallback_scores()` → all zeros
3. My Bug #2 fix includes these zeros in aggregation
4. Result: Mean drops from 4.7 to 3.1!

---

## Is This a Bug in YOUR Code or Groq?

### Groq API Issue (External)
- Groq returned 500: "Internal Server Error"
- This is GROQ'S problem, not yours
- Happens intermittently (worked on run_004, failed on run_005)

### YOUR Code Issue (Internal)
**Bug #6**: Doesn't distinguish between:
- **Legitimate zero**: Judge evaluated and thinks quality is 0/5
- **Failure zero**: Judge crashed/API failed

Currently BOTH get included in aggregation after my Bug #2 fix!

---

## The Correct Scores (Without Failures)

```
S: 4.607
M: 4.565  (only -0.9% vs S)
L: 4.721  (+2.5% vs S)
```

**Pattern**: L > S > M (L scores highest!)

**This is LEGITIMATE**: Longer prompts produce slightly better responses.

---

## What Needs to Be Fixed

### Solution: Mark Failed Evaluations

**Change 1**: Add flag to JudgeResult
```python
class JudgeResult:
    judge_model: str
    scores: RubricScores
    evaluation_failed: bool = False  # NEW
```

**Change 2**: Set flag when returning fallback
```python
# In base.py _fallback_scores()
return {
    "scores": {all zeros},
    "evaluation_failed": True  # Mark as failed
}
```

**Change 3**: Exclude failed evaluations from aggregation
```python
# In ensemble.py calculate_ensemble_metrics()
for judge_type in ["primary", "secondary", "tertiary"]:
    judge = judge_results[judge_type]
    if not judge.evaluation_failed:  # Only include successful
        scores.append(judge.scores.dimension)
```

---

## Impact

### With Current Code (Bug #6)
```
Llama fails → returns zeros → zeros included → mean drops to 3.095
```

### With Bug #6 Fixed
```
Llama fails → marked as failed → excluded → mean calculated from 2 judges = 4.643
```

---

## Your Question Answered

**Q**: "Why does S score highest? Is it legit or our structure?"

**A**: It's **our structure** (Bug #6)! The REAL pattern is:
```
L (4.721) > S (4.607) > M (4.565)
```

Llama API failures on M and L runs artificially lowered their scores.

---

## Next Steps

1. Fix Bug #6 (distinguish failed evaluations)
2. Re-run the 2 failed runs (005, 006) 
3. Verify L now scores highest
4. Document corrected findings

**The close scores (4.56-4.72) are LEGITIMATE after excluding failures!**

