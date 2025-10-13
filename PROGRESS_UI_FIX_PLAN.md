yes# Fix Progress UI "Processing run 13 of 12" Issue

## Current Problem

UI shows: "Processing run 13 of 12..."
- Total runs says 12
- Current run counter goes above 12
- Progress doesn't update until all runs complete

## Root Cause Analysis

**Backend Response** (line 87-92 in app/api/runs.py):
```python
return {
    "run_ids": final_run_ids,      # Array of run IDs
    "total_runs": len(final_run_ids)  # Count
}
```

**Frontend Polling** (line 97-100 in ui/src/pages/RQ1Flow.tsx):
```tsx
const runsData = await runsApi.list({ limit: data.total_runs })
const relevantRuns = runsData.runs.filter((r: any) => 
  data.run_ids.includes(r.run_id)  // Filter by run_ids array
)
```

**Problem**: If `runsApi.list()` returns runs from OTHER experiments, and some have matching IDs, it could count wrong.

## Best Fix: Add experiment_id to Response and Use for Filtering

### Solution 1: Backend Returns experiment_id (BEST)

**Step 1**: Modify backend to include experiment_id in response

File: `app/api/runs.py` line 87-92

```python
# Get experiment_id from first run
first_run = await run_repo.get_by_id(final_run_ids[0]) if final_run_ids else None
experiment_id = first_run.experiment_id if first_run else None

return {
    "message": f"Started background execution of {len(final_run_ids)} runs",
    "status": "accepted",
    "run_ids": final_run_ids,
    "total_runs": len(final_run_ids),
    "experiment_id": experiment_id  # ADD THIS
}
```

**Step 2**: Frontend uses experiment_id for polling

File: `ui/src/pages/RQ1Flow.tsx` line 97-100

```tsx
// Use experiment_id if available, otherwise fall back to run_ids
const queryParams = data.experiment_id 
  ? { experiment_id: data.experiment_id, limit: 200 }
  : { limit: data.total_runs }

const runsData = await runsApi.list(queryParams)

const relevantRuns = data.experiment_id
  ? runsData.runs  // All runs from this experiment
  : runsData.runs.filter((r: any) => data.run_ids.includes(r.run_id))
```

**Benefits**:
- ✅ More reliable (queries by experiment, not array matching)
- ✅ Handles any number of runs
- ✅ No array size limits
- ✅ Cleaner code

### Solution 2: Fix run_ids Array Matching (SIMPLER)

Just ensure the polling limit is high enough and array matching is correct.

File: `ui/src/pages/RQ1Flow.tsx` line 97

```tsx
// Increase limit to ensure we get all runs
const runsData = await runsApi.list({ limit: 200 })  // Was: data.total_runs
const relevantRuns = runsData.runs.filter((r: any) => 
  data.run_ids.includes(r.run_id)
)
```

**Benefits**:
- ✅ Minimal change
- ✅ Fixes immediate issue

**Drawbacks**:
- ⚠️ Less efficient (fetches more runs than needed)
- ⚠️ Doesn't scale well

## Recommendation: Solution 1 (Add experiment_id)

**Why**: More robust, scalable, and semantically correct. Experiments should be tracked by ID, not by array of run IDs.

## Implementation Steps

1. Add experiment_id to backend response (2 locations: line 87-92, line 166-175)
2. Update frontend to use experiment_id for polling
3. Test with 12-run experiment
4. Verify progress shows correctly (1/12, 2/12, ... 12/12)

