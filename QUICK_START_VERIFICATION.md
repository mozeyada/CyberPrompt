# Quick Start: Verify Variant Testing

## 🎯 Goal
Verify that S/M/L prompt variants are being tested correctly and determine why scores are suspiciously close.

## ⚡ Quick Test (5 minutes)

### Step 1: Start Backend with Logging
```bash
# If using Docker
docker-compose up -d

# Verify backend is running
curl http://localhost:8000/health
```

### Step 2: Open Two Terminals

**Terminal 1: Watch logs in real-time**
```bash
# Docker
docker logs -f backend 2>&1 | grep '\[VARIANT-CHECK\]'

# Or local
tail -f backend.log | grep '\[VARIANT-CHECK\]'
```

**Terminal 2: Run experiment via UI**
1. Open browser: http://localhost:3000
2. Go to **Benchmark Runner** or **RQ1 Flow**
3. Configure experiment:
   - **Prompts**: Select 1 prompt (e.g., any SOC_INCIDENT)
   - **✓ Include length variants** (enables S+M+L testing)
   - **Models**: Select 1 model (e.g., gpt-4o-mini)
   - **✓ Ensemble evaluation** (enables 3-judge scoring)
   - **Repeats**: 1
4. Click **Run Experiment**

### Step 3: Watch Logs Appear

You should immediately see logs like:

```
[VARIANT-CHECK] Executing run_001: prompt_id=soc_001_s, length_bin=S, prompt_length=234 chars, model=gpt-4o-mini
[VARIANT-CHECK] LLM response for run_001: response_length=412 chars, success=True
[VARIANT-CHECK] Stored blob for run_001: blob_id=a1b2c3d4e5f6..., content_length=412 chars
[VARIANT-CHECK] Triggering ensemble eval for run_001: length_bin=S, output_len=412, context_len=234
[VARIANT-CHECK] Ensemble evaluation start for run_001: length_bin=S, output_len=412, context_len=234, scenario=SOC_INCIDENT
[VARIANT-CHECK] Judge gpt-4o-mini evaluating run_001: output_len=412, length_bin=S
[VARIANT-CHECK] Judge gpt-4o-mini standard eval: output_len=412, context_len=234, length_bin=S, scenario=SOC_INCIDENT
[VARIANT-CHECK] Judge gpt-4o-mini scores: composite=3.214, technical_accuracy=3.0, completeness=3.5, clarity=3.0
[VARIANT-CHECK] Judge claude-3-5-sonnet-20241022 evaluating run_001: output_len=412, length_bin=S
[VARIANT-CHECK] Judge claude-3-5-sonnet-20241022 standard eval: output_len=412, context_len=234, length_bin=S, scenario=SOC_INCIDENT
[VARIANT-CHECK] Judge claude-3-5-sonnet-20241022 scores: composite=3.071, technical_accuracy=3.0, completeness=3.0, clarity=3.0
[VARIANT-CHECK] Judge llama-3.3-70b-versatile evaluating run_001: output_len=412, length_bin=S
[VARIANT-CHECK] Judge llama-3.3-70b-versatile standard eval: output_len=412, context_len=234, length_bin=S, scenario=SOC_INCIDENT
[VARIANT-CHECK] Judge llama-3.3-70b-versatile scores: composite=3.357, technical_accuracy=3.5, completeness=3.0, clarity=3.5
[VARIANT-CHECK] Judge gpt-4o-mini (primary) scores for run_001: composite=3.214, technical_accuracy=3.0, completeness=3.5
[VARIANT-CHECK] Judge claude-3-5-sonnet-20241022 (secondary) scores for run_001: composite=3.071, technical_accuracy=3.0, completeness=3.0
[VARIANT-CHECK] Judge llama-3.3-70b-versatile (tertiary) scores for run_001: composite=3.357, technical_accuracy=3.5, completeness=3.0
[VARIANT-CHECK] Calculating ensemble metrics from 3 judges
[VARIANT-CHECK] Ensemble aggregation complete: mean_composite=3.214, std_composite=0.143, mean_tech_acc=3.167
[VARIANT-CHECK] Ensemble scores for run_001: composite=3.214, technical_accuracy=3.167, completeness=3.167

... (Then runs for M and L variants) ...
```

### Step 4: Verify Results

#### ✅ Check 1: Prompt Lengths Increase
Look for these patterns:
```
prompt_length=234 chars   <- S variant
prompt_length=567 chars   <- M variant (2-3x longer)
prompt_length=945 chars   <- L variant (4-5x longer)
```

**Pass**: Lengths increase significantly (2-5x)  
**Fail**: All same length → **Bug in variant lookup**

#### ✅ Check 2: Response Lengths Vary
```
response_length=412 chars   <- S response
response_length=689 chars   <- M response
response_length=1123 chars  <- L response
```

**Pass**: Responses get longer with prompts  
**Fail**: All same length → **Bug in LLM execution or storage**

#### ✅ Check 3: Blob IDs Are Unique
```
blob_id=a1b2c3d4e5f6...   <- run_001
blob_id=x9y8z7w6v5u4...   <- run_002
blob_id=m3n2o1p0q9r8...   <- run_003
```

**Pass**: All different blob IDs  
**Fail**: Same blob_id repeated → **Bug in storage (overwrites)**

#### ✅ Check 4: Scores Improve with Length
```
composite=3.214   <- S score
composite=3.642   <- M score (↑0.43 points)
composite=4.071   <- L score (↑0.43 points)
```

**Pass**: Scores increase by 0.3-1.0 points  
**Fail**: All within 0.1 points → **Investigate further**

#### ✅ Check 5: Judges Show Variance
For each run, check std_composite:
```
std_composite=0.143   <- Healthy variance
std_composite=0.205   <- Healthy variance
std_composite=0.187   <- Healthy variance
```

**Pass**: std > 0.10 (judges disagree)  
**Fail**: std = 0.00 → **Bug (judges identical)**

## 📊 Save Results

After experiment completes:

```bash
# Save all variant check logs
docker logs backend 2>&1 | grep '\[VARIANT-CHECK\]' > variant_check_logs_$(date +%Y%m%d_%H%M%S).txt

# Or if local
cat backend.log | grep '\[VARIANT-CHECK\]' > variant_check_logs_$(date +%Y%m%d_%H%M%S).txt
```

## 🔍 Analyze Logs

### Quick Analysis (Manual)

```bash
# Count how many runs were executed
grep "Executing run_" variant_check_logs.txt | wc -l
# Expected: 3 (one per variant)

# Extract prompt lengths
grep "Executing run_" variant_check_logs.txt | grep -o "prompt_length=[0-9]*"
# Expected: Three different values

# Extract response lengths
grep "LLM response for" variant_check_logs.txt | grep -o "response_length=[0-9]*"
# Expected: Three different values

# Extract final ensemble scores
grep "Ensemble scores for run_" variant_check_logs.txt | grep -o "composite=[0-9.]*"
# Expected: Three different scores
```

### Detailed Analysis (Python)

```python
import re

# Load logs
with open('variant_check_logs.txt', 'r') as f:
    logs = f.read()

# Extract data
runs = {}
for line in logs.split('\n'):
    if 'Executing run_' in line:
        match = re.search(r'run_(\d+).*prompt_length=(\d+).*length_bin=(\w+)', line)
        if match:
            run_id, prompt_len, length_bin = match.groups()
            runs[run_id] = {'length_bin': length_bin, 'prompt_len': int(prompt_len)}
    
    if 'Ensemble scores for run_' in line:
        match = re.search(r'run_(\d+).*composite=([\d.]+)', line)
        if match:
            run_id, composite = match.groups()
            if run_id in runs:
                runs[run_id]['composite'] = float(composite)

# Display results
for run_id, data in sorted(runs.items()):
    print(f"Run {run_id}: {data['length_bin']} - Prompt: {data['prompt_len']} chars - Score: {data.get('composite', 'N/A'):.3f}")

# Calculate improvement
scores = sorted([r for r in runs.values() if 'composite' in r], key=lambda x: x['prompt_len'])
if len(scores) >= 2:
    improvement = scores[-1]['composite'] - scores[0]['composite']
    percent = (improvement / scores[0]['composite']) * 100
    print(f"\nImprovement S→L: {improvement:.3f} points ({percent:.1f}%)")
```

## 🎯 Decision Tree

Based on your log analysis:

### ✅ Scenario: All Checks Pass
- Prompts differ significantly
- Responses differ appropriately
- Unique blob IDs
- Scores improve (0.3-1.0 points)
- Judges show variance (std > 0.10)

**Conclusion**: Variants are working correctly. Close scores are a **valid research finding** - LLMs produce similar quality regardless of prompt detail.

**Next Steps**:
1. Accept finding as legitimate
2. Document in research report
3. Consider testing more diverse prompts
4. Analyze statistical significance

### ❌ Scenario: Bug in Variant Lookup
- All prompts same length
- Same prompt_id used

**Conclusion**: Variant expansion not working.

**Fix**: Check `app/services/experiment.py` lines 66-98, verify prompts in database.

### ❌ Scenario: Bug in Score Calculation
- Prompts/responses differ
- All judges return identical scores (std = 0)

**Conclusion**: Judge evaluation issue (possibly caching).

**Fix**: Check `app/services/base.py` lines 62-106, review judge calls.

### ❌ Scenario: Bug in Storage
- Prompts/responses differ
- Same blob_id for multiple runs

**Conclusion**: Storage overwrites.

**Fix**: Check `app/services/experiment.py` lines 182-193, review blob generation.

## 📚 Full Documentation

For comprehensive analysis:
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Complete Verification Guide**: `VARIANT_TESTING_VERIFICATION_GUIDE.md`
- **Original Plan**: `verify-llm-testing-methodology.plan.md`

## 🆘 Troubleshooting

### No logs appearing?

1. Check logging level:
   ```bash
   # In .env
   LOG_LEVEL=INFO
   ```

2. Restart backend:
   ```bash
   docker-compose restart backend
   ```

3. Verify code is updated:
   ```bash
   git status  # Check for uncommitted changes
   docker-compose build backend  # Rebuild if needed
   ```

### Logs appear but hard to read?

Use better filtering:
```bash
# Show only key metrics
docker logs backend 2>&1 | grep '\[VARIANT-CHECK\]' | grep -E 'Executing|Ensemble scores'

# Show only scores
docker logs backend 2>&1 | grep '\[VARIANT-CHECK\]' | grep 'composite='

# Show with timestamps
docker logs -t backend 2>&1 | grep '\[VARIANT-CHECK\]'
```

## ✅ Success Criteria

You're done when you can answer:

1. ❓ Do prompts differ across S/M/L? → Check `prompt_length`
2. ❓ Do responses differ? → Check `response_length`
3. ❓ Are runs stored separately? → Check `blob_id` uniqueness
4. ❓ Do scores improve with length? → Check `composite` progression
5. ❓ Do judges disagree slightly? → Check `std_composite > 0`

If **all yes**: System working, close scores are real.  
If **any no**: Bug found, refer to fix guides.

