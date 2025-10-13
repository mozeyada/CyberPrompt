# Remove Legacy Single-Judge Scoring - Use ONLY 3-Judge Ensemble

## Root Cause Identified

**The Problem**: Two parallel scoring systems exist:
1. **Legacy single-judge**: Stores `run.scores` from primary judge only (4.714)
2. **3-judge ensemble**: Stores `run.ensemble_evaluation.aggregated.mean_scores` (4.476)

**Current Flow** (BROKEN):
```
1. execute_run(run_id, use_ensemble=False) ← ALWAYS False!
2. Primary judge evaluates → scores = 4.714
3. Update DB: run.scores = 4.714
4. SEPARATELY: Ensemble evaluates all 3 judges → mean = 4.476
5. Update DB: run.ensemble_evaluation = {...}
6. Result: TWO DIFFERENT SCORES in same run!
```

**Evidence from Logs**:
```
[SCORE-DEBUG] run_001 update_data['scores'] set: composite=4.714
[SCORE-DEBUG] run_001 update sent to DB with fields: ['scores', ...]  ← No ensemble_evaluation!
[Ensemble runs LATER in separate process]
```

## Solution: Remove Legacy, Use ONLY Ensemble

### Phase 1: Remove Single-Judge Scoring Path

**File**: `app/services/experiment.py`

**Lines 240-283**: Remove the entire `use_ensemble` conditional logic

**Current Code**:
```python
# Line 240-283
if use_ensemble:
    # Ensemble evaluation (NEVER EXECUTES because use_ensemble=False)
    scores = ensemble_eval.aggregated.mean_scores.model_dump()
elif run.judge.type.value == "llm":
    # Single judge (THIS is what actually runs)
    scores = await self._evaluate_single_judge(...)
```

**NEW Code**:
```python
# ALWAYS use ensemble, no conditional
ensemble_evaluation = None
scores = None

try:
    from app.services.ensemble import EnsembleJudgeService
    ensemble_service = EnsembleJudgeService()
    
    ensemble_eval = await ensemble_service.evaluate_with_ensemble(
        output=execution_result["response"],
        scenario=prompt.scenario,
        length_bin=prompt.length_bin,
        bias_controls=run.bias_controls.model_dump(),
        run_id=run_id,
        context=prompt.text
    )
    
    # Use ONLY ensemble aggregated scores
    if ensemble_eval.aggregated and ensemble_eval.aggregated.mean_scores:
        scores = ensemble_eval.aggregated.mean_scores.model_dump()
        ensemble_evaluation = ensemble_eval
        logger.info(f"[ENSEMBLE] {run_id} scores: composite={scores.get('composite'):.3f}")
    else:
        logger.error(f"[ENSEMBLE] {run_id} failed - no aggregated scores!")
        raise Exception("Ensemble evaluation failed to produce aggregated scores")
        
except Exception as e:
    logger.error(f"[ENSEMBLE] {run_id} evaluation failed: {e}")
    # Mark run as FAILED if ensemble fails
    await self.run_repo.update(run_id, {
        "status": RunStatus.FAILED,
        "error": f"Ensemble evaluation failed: {e}",
        "updated_at": datetime.utcnow()
    })
    raise
```

### Phase 2: Remove Redundant Ensemble Evaluation in API

**File**: `app/api/runs.py`

**Lines 157-195**: DELETE this entire block

**Current**: Runs ensemble SEPARATELY after execute_run()
**Problem**: Creates duplicate ensemble evaluation and doesn't update scores

**This entire section needs to be DELETED** because ensemble now runs INSIDE execute_run().

### Phase 3: Remove Single-Judge Fallback Method

**File**: `app/services/experiment.py`

**Lines ~380-415**: Remove `_evaluate_single_judge()` method entirely

**Reason**: We ONLY use ensemble now, no single-judge fallback.

### Phase 4: Remove use_ensemble Parameter

**File**: `app/services/experiment.py`

**Line 153**: Change function signature

**Current**:
```python
async def execute_run(self, run_id: str, use_ensemble: bool = False) -> dict[str, Any]:
```

**NEW**:
```python
async def execute_run(self, run_id: str) -> dict[str, Any]:
    # Always uses 3-judge ensemble evaluation
```

### Phase 5: Update All Callers

**File**: `app/services/experiment.py`

**Line 344**: Remove parameter from batch execution

**Current**:
```python
return await self.execute_run(run_id)
```

**NEW**: (Already correct - no parameter)

**File**: `app/api/runs.py`

**Line 165 & 264**: Already correct - no parameter passed

### Phase 6: Clean Up Database Fields

**Current Run Document**:
```json
{
  "scores": {...},              // Legacy single-judge scores
  "ensemble_evaluation": {...}  // Real ensemble scores
}
```

**NEW Run Document**:
```json
{
  "scores": {...},              // NOW contains ensemble aggregated scores
  "ensemble_evaluation": {...}  // Full ensemble details (for analysis)
}
```

**Action**: Both fields should have IDENTICAL composite scores.

### Phase 7: Update Run Model to Enforce This

**File**: `app/models/__init__.py`

Add validation to Run model:

```python
@model_validator(mode='after')
def validate_scores_match_ensemble(self):
    """Ensure scores field matches ensemble aggregated scores if ensemble exists"""
    if self.ensemble_evaluation and self.ensemble_evaluation.aggregated:
        ensemble_composite = self.ensemble_evaluation.aggregated.mean_scores.composite
        scores_composite = self.scores.composite if self.scores else None
        
        if scores_composite and abs(ensemble_composite - scores_composite) > 0.01:
            logger.warning(f"Score mismatch: scores={scores_composite}, ensemble={ensemble_composite}")
            # Force scores to match ensemble
            self.scores = self.ensemble_evaluation.aggregated.mean_scores
    
    return self
```

## Implementation Order

### Step 1: Backup Current State
```bash
docker exec cyberprompt-mongo-1 mongodump --db genai_bench --out /tmp/backup
```

### Step 2: Modify experiment.py

1. Remove use_ensemble parameter (line 153)
2. Replace lines 240-283 with ALWAYS ensemble logic
3. Remove _evaluate_single_judge method

### Step 3: Modify runs.py

1. Delete lines 157-195 (redundant ensemble evaluation)
2. Simplify execute_batch endpoint

### Step 4: Test with Single Run

```bash
# Delete all runs
# Execute 1 test run
# Check: run.scores.composite == run.ensemble_evaluation.aggregated.mean_scores.composite
```

### Step 5: Run Full Experiment

Execute 12 runs (4 prompts × 3 lengths) and verify ALL scores match.

## Success Criteria

- [ ] ZERO calls to single-judge evaluation
- [ ] ALL runs have ensemble_evaluation
- [ ] run.scores.composite ALWAYS equals run.ensemble_evaluation.aggregated.mean_scores.composite
- [ ] Logs show ONLY ensemble evaluation, never single-judge
- [ ] Code has ZERO legacy single-judge paths
- [ ] Can't accidentally run single-judge mode

## Expected Database After Fix

```json
{
  "run_id": "run_001",
  "scores": {
    "composite": 4.476,  // ← From ensemble mean
    "technical_accuracy": 5.0,
    // ... all from ensemble aggregated
  },
  "ensemble_evaluation": {
    "primary_judge": {scores: {composite: 4.714}},
    "secondary_judge": {scores: {composite: 4.286}},
    "tertiary_judge": {scores: {composite: 4.429}},
    "aggregated": {
      "mean_scores": {
        "composite": 4.476  // ← SAME as run.scores!
      }
    }
  }
}
```

## Code Changes Summary

**Delete**:
- use_ensemble parameter and all conditionals
- Lines 157-195 in app/api/runs.py (duplicate ensemble)
- _evaluate_single_judge() method
- All single-judge logic paths

**Add**:
- Mandatory ensemble evaluation in execute_run()
- Fail run if ensemble fails (no fallback)
- Validation to ensure scores match ensemble

**Result**: Single source of truth - ensemble aggregated scores stored in BOTH places for compatibility.

