# 🚀 **TRIPLE-JUDGE ENSEMBLE IMPLEMENTATION PLAN**
## CyberCQBench Research Enhancement

### **🎯 OBJECTIVE**
Implement cross-vendor ensemble evaluation using:
- **GPT-4o-mini** (OpenAI) - Primary judge
- **Clause-3.5-Sonnet** (Anthropic) - Secondary judge  
- **Llama-3.1-70B** (Meta via Groq) - Tertiary judge

### **📋 IMPLEMENTATION PHASES**

## **PHASE 1: DATABASE SCHEMA EXTENSION** (15 minutes)
### **Modified Models**
```python
# Extend existing Run model
class RunV2(BaseModel):
    run_id: str
    prompt_id: str
    model: str
    output_blob_id: str
    
    # CURRENT: Single judge evaluation
    judge: JudgeConfig
    scores: RubricScores
    
    # NEW: Multi-judge ensemble evaluation
    ensemble_evaluation: EnsembleEvaluation | None = None

class EnsembleEvaluation(BaseModel):
    evaluation_id: str  # ULID for ensemble
    primary_judge: JudgeResult   # GPT-4o-mini
    secondary_judge: JudgeResult # Claude-3.5-Sonnet
    tertiary_judge: JudgeResult  # Llama-3.1-70B
    aggregated: AggregatedScores
    reliability_metrics: ReliabilityMetrics

class JudgeResult(BaseModel):
    judge_model: str
    scores: RubricScores
    raw_response: str  # Judge's reasoning
    evaluation_time: datetime
    tokens_used: int
    cost_usd: float
    fsp_used: bool

class AggregatedScores(BaseModel):
    mean_scores: RubricScores
    median_scores: RubricScores  
    std_scores: RubricScores
    confidence_95_ci: Dict[str, Tuple[float, float]]

class ReliabilityMetrics(BaseModel):
    pearson_correlations: Dict[str, float]
    fleiss_kappa: float
    inter_judge_agreement: str  # "substantial", "moderate", etc.
```

## **PHASE 2: CORE ENSEMBLE SERVICE** (20 minutes)
### **New EnsembleService Class**
```python
class EnsembleJudgeService:
    """Triple-judge ensemble evaluation service"""
    
    def __init__(self):
        self.model_runner = ModelRunner(
            openai_key=settings.openai_api_key,
            anthropic_key=settings.anthropic_api_key,
            groq_key=settings.groq_api_key
        )
    
    async def evaluate_with_ensemble(
        self, 
        output: str, 
        scenario: ScenarioType,
        length_bin: LengthBin,
        bias_controls: dict,
        run_id: str
    ) -> EnsembleEvaluation:
        """Execute ensemble evaluation with all three judges"""
        
        # Define judge configurations
        judge_configs = [
            {"model": "gpt-4o-mini", "type": "primary"},
            {"model": "claude-3-5-sonnet-20241022", "type": "secondary"},
            {"model": "llama-3.3-70b-versatile", "type": "tertiary"}
        ]
        
        # Execute parallel evaluations
        evaluation_tasks = [
            self.evaluate_single_judge(output, config, scenario, length_bin, bias_controls, run_id)
            for config in judge_configs
        ]
        
        results = await asyncio.gather(*evaluation_tasks)
        
        # Convert to structured results
        judge_results = {
            "primary": self.process_judge_result(results[0], "primary"),
            "secondary": self.process_judge_result(results[1], "secondary"), 
            "tertiary": self.process_judge_result(results[2], "tertiary")
        }
        
        # Calculate aggregated scores
        aggregated = self.calculate_ensemble_metrics(judge_results)
        
        # Calculate reliability metrics
        reliability = self.calculate_reliability_metrics(judge_results)
        
        return EnsembleEvaluation(
            evaluation_id=generate_ulid(),
            primary_judge=judge_results["primary"],
            secondary_judge=judge_results["secondary"],
            tertiary_judge=judge_results["tertiary"],
            aggregated=aggregated,
            reliability_metrics=reliability
        )
    
    async def evaluate_single_judge(
        self, output, config, scenario, length_bin, bias_controls, run_id
    ) -> dict:
        """Evaluate with a single judge model"""
        
        try:
            client = self.model_runner._get_client(config["model"])
            judge = create_judge({
                "type": "llm",
                "judge_model": config["model"]
            }, client)
            
            start_time = time.time()
            
            result = await judge.evaluate(
                output=output,
                scenario=scenario,
                length_bin=length_bin,
                bias_controls=bias_controls
            )
            
            eval_time = time.time() - start_time
            
            return {
                "judge_model": config["model"],
                "scores": result["scores"],
                "raw_response": result.get("raw_response", ""),
                "evaluation_time": datetime.utcnow(),
                "evaluation_duration": eval_time,
                "success": True,
                "type": config["type"]
            }
            
        except Exception as e:
            logger.error(f"Judge {config['model']} failed: {e}")
            return self.create_fallback_result(config["model"], str(e), config["type"])
    
    def calculate_ensemble_metrics(self, judge_results) -> AggregatedScores:
        """Calculate mean, median, std, and confidence intervals"""
        
        dimensions = ["technical_accuracy", "actionability", "completeness",
                     "compliance_alignment", "risk_awareness", "relevance", "clarity"]
        
        mean_scores = {}
        median_scores = {}
        std_scores = {}
        ci_95 = {}
        
        for dim in dimensions:
            scores = [
                judge_results["primary"].scores[dim],
                judge_results["secondary"].scores[dim],
                judge_results["tertiary"].scores[dim]
            ]
            
            mean_scores[dim] = np.mean(scores)
            median_scores[dim] = np.median(scores)
            std_scores[dim] = np.std(scores)
            
            # 95% confidence interval
            ci_95[dim] = (
                mean_scores[dim] - 1.96 * std_scores[dim],
                mean_scores[dim] + 1.96 * std_scores[dim]
            )
        
        # Composite score aggregation
        mean_scores["composite"] = np.mean(list(mean_scores.values())[:-1])
        median_scores["composite"] = np.median(list(median_scores.values())[:-1])
        std_scores["composite"] = np.std(list(std_scores.values())[:-1])
        
        ci_95["composite"] = (
            mean_scores["composite"] - 1.96 * std_scores["composite"],
            mean_scores["composite"] + 1.96 * std_scores["composite"]
        )
        
        return AggregatedScores(
            mean_scores=RubricScores(**mean_scores),
            median_scores=RubricScores(**median_scores),
            std_scores=RubricScores(**std_scores),
            confidence_95_ci=ci_95
        )
    
    def calculate_reliability_metrics(self, judge_results) -> ReliabilityMetrics:
        """Calculate Pearson correlations and Fleiss' Kappa"""
        
        # Extract scores for correlation analysis
        dimensions = ["technical_accuracy", "actionability", "completeness",
                     "compliance_alignment", "risk_awareness", "relevance", "clarity"]
        
        correlations = {}
        
        # Calculate pairwise correlations
        pairs = [("primary", "secondary"), ("primary", "tertiary"), ("secondary", "tertiary")]
        
        for (judge1_name, judge2_name) in pairs:
            judge1_results = judge_results[judge1_name].scores
            judge2_results = judge_results[judge2_name].scores
            
            pair_scores = np.array([
                [judge1_results[dim], judge2_results[dim]] for dim in dimensions
            ])
            
            corr_coef, _ = pearsonr(pair_scores[:, 0], pair_scores[:, 1])
            correlations[f"{judge1_name}_{judge2_name}"] = corr_coef
        
        # Calculate average correlation
        avg_correlation = np.mean(list(correlations.values()))
        
        # Fleiss' Kappa placeholder (would need multiple evaluations to calculate)
        fleiss_kappa = avg_correlation  # Simplified for now
        
        # Determine agreement level
        if avg_correlation > 0.8:
            agreement_level = "substantial"
        elif avg_correlation > 0.6:
            agreement_level = "moderate"  
        else:
            agreement_level = "fair"
        
        return ReliabilityMetrics(
            pearson_correlations=correlations,
            fleiss_kappa=fleiss_kappa,
            inter_judge_agreement=agreement_level
        )
```

## **PHASE 3: EXPERIMENT SERVICE INTEGRATION** (10 minutes)
### **Modify ExperimentService**
```python
# In app/services/experiment.py - update execute_run method

async def execute_run(self, run_id: str, use_ensemble: bool = False) -> dict[str, Any]:
    """Execute run with optional ensemble evaluation"""
    
    # Existing execution logic...
    execution_result = await self.model_runner.execute_run(...)
    
    if execution_result["success"]:
        # NEW: Ensemble evaluation option
        if use_ensemble:
            ensemble_service = EnsembleJudgeService()
            ensemble_eval = await ensemble_service.evaluate_with_ensemble(
                output=execution_result["response"],
                scenario=prompt.scenario,
                length_bin=prompt.length_bin,
                bias_controls=run.bias_controls.model_big_dump(),
                run_id=run_id
            )
            
            # Store ensemble evaluation
            await self.store_ensemble_evaluation(run_id, ensemble_eval)
            
            # Use ensemble scores as primary scores
            scores = ensemble_eval.aggregated.mean_scores
        else:
            # Original single judge evaluation
            scores = await self.evaluate_single_judge(...)
        
        # Update run with results
        update_data = {
            "status": RunStatus.SUCCEEDED,
            "scores": scores,
            "ensemble_evaluation": ensemble_eval if use_ensemble else None,
            # ... other fields
        }
```

## **PHASE 4: API ENDPOINTS** (15 minutes)
### **Enhanced Runs API**
```python
# In app/api/runs.py

@router.post("/execute/batch-ensemble")
async def execute_batch_ensemble(
    request: dict,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., description="API key")
) -> dict:
    """Execute experiments with ensemble evaluation"""
    
    validate_api_key_header(x_api_key)
    
    # Extract configuration
    prompt_ids = request.get("prompt_ids", [])
    model_names = request.get("model_names", [])
    ensemble_enabled = request.get("ensemble", True)
    
    # Plan runs as normal
    plan_request = RunPlanRequest(...)
    run_ids = await get_experiment_service().plan_runs(plan_request)
    
    # Execute with ensemble evaluation
    results = []
    for run_id in run_ids:
        result = await get_experiment_service().execute_run(run_id, use_ensemble=ensemble_enabled)
        results.append(result)
    
    return {
        "message": f"Executed {len(run_ids)} runs with ensemble evaluation",
        "results": results,
        "ensemble_enabled": ensemble_enabled
    }

@router.post("/experiments/{experiment_id}/dual-evaluate")
async def add_judges_to_existing_runs(
    experiment_id: str,
    judges_to_add: List[str] = ["claude-3-5-sonnet-20241022", "llama-3.3-70b-versatile"],
    x_api_key: str = Header(..., description="API key")
) -> dict:
    """Add additional judges to existing single-judge runs"""
    
    validate_api_key_header(x_api_key)
    
    # Get existing runs from experiment
    runs = await run_repo.get_runs_by_experiment(experiment_id)
    
    ensemble_service = EnsembleJudgeService()
    results = []
    
    for run in runs:
        if run.output_blob_id:
            # Get output content. Add judges
            ensemble_eval = await ensemble_service.evaluate_with_ensemble(
                output=await blob_repo.get_content(run.output_blob_id),
                scenario=run.scenario,
                length_bin=run.prompt_length_bin,
                bias_controls=run.bias_controls.model_big_dump(),
                run_id=run.run_id
            )
            
            # Update run with ensemble results
            await run_repo.update(run.run_id, {
                "ensemble_evaluation": ensemble_eval
            })
            
            results.append({
                "run_id": run.run_id,
                "ensemble_scores": ensemble_eval.aggregated.mean_scores,
                "reliability": ensemble_eval.reliability_metrics.inter_judge_agreement
            })
    
    return {
        "message": f"Added ensemble evaluation to {len(runs)} runs",
        "results": results
    }
```

## **PHASE 5: ANALYTICS SERVICE** (15 minutes)
### **Enhanced Analytics**
```python
# In app/services/analytics_service.py

async def get_ensemble_analytics(
    self,
    scenario: str | None = None,
    length_bin: str | None = None,
    experiment_id: str | None = None
) -> dict:
    """Get ensemble evaluation analytics"""
    
    # Build aggregation pipeline
    pipeline = [
        {"$match": {"ensemble_evaluation": {"$exists": True}}},
        {"$unwind": "$ensemble_evaluation"},
        {"$project": {
            "run_id": 1,
            "scenario": 1,
            "prompt_length_bin": 1,
            "ensemble_mean": "$ensemble_evaluation.aggregated.mean_scores",
            "reliability": "$ensemble_evaluation.reliability_metrics",
            "individual_judges": {
                "primary": "$ensemble_evaluation.primary_judge.scores",
                "secondary": "$ensemble_evaluation.secondary_judge.scores", 
                "tertiary": "$ensemble_evaluation.tertiary_judge.scores"
            }
        }}
    ]
    
    if scenario:
        pipeline.insert(0, {"$match": {"scenario": scenario}})
    
    db = get_database()
    results = list(db.runs.aggregate(pipeline))
    
    if not results:
        return {"message": "No ensemble evaluations found"}
    
    # Calculate overall reliability metrics
    avg_correlations = []
    agreement_levels = []
    
    for result in results:
        avg_correlations.append(np.mean(list(result["reliability"]["pearson_correlations"].values())))
        agreement_levels.append(result["reliability"]["inter_judge_agreement"])
    
    # Judge comparison analysis
    judge_performance = {}
    for dimension in ["technical_accuracy", "actionability", "completeness", 
                     "compliance_alignment", "risk_awareness", "relevance", "clarity", "composite"]:
        
        primary_scores = [r["individual_judges"]["primary"][dimension] for r in results]
        secondary_scores = [r["individual_judges"For secondary_scores = [r["individual_judges"]["secondary"][dimension] for r in results]
        tertiary_scores = [r["individual_judges"]["tertiary"][dimension] for r in results]
        
        judge_performance[dimension] = {
            "primary_avg": np.mean(primary_scores),
            "secondary_avg": np.mean(secondary_scores),
            "tertiary_avg": np.mean(tertiary_scores),
            "primary_std": np.std(primary_scores),
            "secondary_std": np.std(secondary_scores),
            "tertiary_std": np.std(tertiary_scores)
        }
    
    return {
        "total_ensemble_evaluations": len(results),
        "overall_reliability": {
            "average_correlation": np.mean(avg_correlations),
            "agreement_distribution": Counter(agreement_levels)
        },
        "judge_performance_by_dimension": judge_performance,
        "scenario": scenario,
        "length_bin": length_bin
    }

async def get_inter_judge_correlation(
    self,
    scenario: str | None = None,
    min_evaluations: int = 10
) -> dict:
    """Detailed correlation analysis between judges"""
    
    pipeline = [
        {"$match": {
            "ensemble_evaluation": {"$exists": True},
            "scores.composite": {"$exists": True}
        }},
        {"$unwind": "$ensemble_evaluation"},
        {"$project": {
            "scenario": 1,
            "prompt_length_bin": 1,
            "correlations": "$ensemble_evaluation.reliability_metrics.pearson_correlations"
        }}
    ]
    
    if scenario:
        pipeline.insert(0, {"$match": {"scenario": scenario}})
    
    db = get_database()
    results = list(db.runs.aggregate(pipeline))
    
    if len(results) < min_evaluations:
        return {"error": f"Insufficient data ({len(results)} evaluations, need {min_evaluations}+)"}
    
    # Aggregate correlations across evaluations
    correlation_pairs = {}
    
    for result in results:
        for pair, correlation in result["correlations"].items():
            if pair not in correlation_pairs:
                correlation_pairs[pair] = []
            correlation_pairs[pair].append(correlation)
    
    # Calculate statistics
    correlation_stats = {}
    for pair, correlations in correlation_pairs.items():
        correlation_stats[pair] = {
            "mean": np.mean(correlations),
            "std": np.std(correlations),
            "min": np.min(correlations),
            "max": np.max(correlations),
            "count": len(correlations)
        }
    
    return {
        "total_evaluations": len(results),
        "correlation_statistics": correlation_stats,
        "overall_mean_correlation": np.mean([
            stats["mean"] for stats in correlation_stats.values()
        ])
    }
```

## **PHASE 6: UI INTEGRATION** (15 minutes)
### **Enhanced Frontend Components**
```typescript
// New React component for ensemble evaluation
interface EnsembleEvaluationProps {
  runId: string;
  ensembleData: {
    primary_judge: JudgeResult;
    secondary_judge: JudgeResult;  
    tertiary_judge: JudgeResult;
    aggregated: AggregatedScores;
    reliability_metrics: ReliabilityMetrics;
  };
}

export function EnsembleEvaluationView({ runId, ensembleData }: EnsembleEvaluationProps) {
  const [activeView, setActiveView] = useState<'individual' | 'aggregated'>('aggregated');
  
  return (
    <div className="ensemble-evaluation">
      <div className="view-toggle">
        <button 
          className={activeView === 'aggregated' ? 'active' : ''}
          onClick={() => setActiveView('aggregated')}
        >
          Ensemble Summary
        </button>
        <button 
          className={activeView === 'individual' ? 'active' : ''}
          onClick={() => setActiveView('individual')}
        >
          Individual Scores
        </button>
      </div>
      
      {activeView === 'aggregated' ? (
        <div className="aggregated-scores">
          <h3>Ensemble Scores (Mean ± 95% CI)</h3>
          <ScoreTable 
            scores={ensembleData.aggregated.mean_scores}
            confidenceIntervals={ensembleData.aggregated.confidence_95_ci}
            showUncertainty={true}
          />
          
          <div className="reliability-metrics">
            <h4>Inter-Judge Reliability</h4>
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-value">{ensembleData.reliability_metrics.inter_judge_agreement}</div>
                <div className="metric-label">Overall Agreement</div>
              </div>
              <div className="metric-card">
                <div className="metric-value">{Object.values(ensembleData.reliability_metrics.pearson_correlations)[0]?.toFixed(3)}</div>
                <div className="metric-label">Avg Correlation</div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="individual-scores">
          <h3>Individual Judge Scores</h3>
          <div className="judges-comparison">
            <JudgeComparisonItem 
              title="GPT-4o-mini (Primary)"
              scores={ensembleData.primary_judge.scores}
              model="gpt-4o-mini"
            />
            <JudgeComparisonItem 
              title="Claude-3.5-Sonnet (Secondary)"
              scores={ensembleData.secondary_judge.scores}
              model="claude-3.5-sonnet"
            />
            <JudgeComparisonItem 
              title="Llama-3.1-70B (Tertiary)"
              scores={ensembleData.tertiary_judge.scores}
              model="llama-3.1-70b"
            />
          </div>
        </div>
      )}
    </div>
  );
}
```

## **📊 TESTING STRATEGY**

### **Phase 1: Unit Testing (5 minutes)**
```python
# test_ensemble_service.py
async def test_ensemble_evaluation():
    """Test ensemble evaluation with sample output"""
    
    ensemble_service = EnsembleJudgeService()
    
    sample_output = """Based on the incident report, immediate containment steps include:
    1. Isolate affected systems from network
    2. Preserve evidence by imaging drives
    3. Document all actions taken"""
    
    result = await ensemble_service.evaluate_with_ensemble(
        output=sample_output,
        scenario=ScenarioType.SOC_INCIDENT,
        length_bin=LengthBin.S,
        bias_controls={"fsp": True},
        run_id="test_run_001"
    )
    
    # Validations
    assert result.primary_judge.judge_model == "gpt-4o-mini"
    assert result.secondary_judge.judge_model == "claude-3-5-sonnet-20241022"
    assert result.tertiary_judge.judge_model == "llama-3.3-70b-versatile"
    assert result.aggregated.mean_scores.composite > 0
    assert result.reliability_metrics.inter_judge_agreement in ["fair", "moderate", "substantial"]
```

### **Phase 2: End-to-End Testing (10 minutes)**
```python
# test_ensemble_integration.py
async def test_full_ensemble_workflow():
    """Test complete ensemble evaluation workflow"""
    
    # Run small experiment with ensemble evaluation
    request = {
        "prompt_ids": ["academic_soc_001_s", "academic_soc_002_s"],
        "model_names": ["gpt-3.5-turbo"],
        "ensemble": True,
        "settings": {"temperature": 0.2, "max_tokens": 500}
    }
    
    response = await client.post("/runs/execute/batch-ensemble", json=request)
    assert response.status_code == 200
    
    data = response.json()
    assert data["ensemble_enabled"] == True
    assert len(data["results"]) == 2
    
    # Get analytics
    analytics_response = await client.get("/analytics/ensemble")
    analytics_data = analytics_response.json()
    
    assert analytics_data["total_ensemble_evaluations"] >= 2
    assert "overall_reliability" in analytics_data
```

## **🎯 IMPLEMENTATION CHECKLIST**

### **Pre-Implementation**
- [x] ✅ Prepare database schema extensions
- [x] ✅ Create ensemble service structure
- [x] ✅ Design API endpoints
- [x] ✅ Plan UI integration

### **Implementation (Ready when Claude API keys available)**
- [ ] 🔄 Extend database models
- [ ] 🔄 Implement EnsembleJudgeService
- [ ] 🔄 Add ensemble endpoints to Runs API
- [ ] 🔄 Enhance Analytics service  
- [ ] 🔄 Create UI components
- [ ] 🔄 Add comprehensive testing

### **Validation**
- [ ] 🔄 Run ensemble evaluation on 3 test prompts
- [ ] 🔄 Verify correlation calculations
- [ ] 🔄 Test UI displays
- [ ] 🔄 Validate analytics computations

### **Deployment**
- [ ] 🔄 Update environment variables with Claude API key
- [ ] 🔄 Test full workflow integration
- [ ] 🔄 Generate sample ensemble analytics

## **💰 COST ESTIMATION**

### **Estimated API Costs**
- **GPT-4o-mini**: ~$0.03 per evaluation × 100 experiments = $3
- **Claude-3.5-Sonnet**: ~$0.06 per evaluation × 100 experiments = $6  
- **Llama-3.1-70B (Groq)**: ~$0.01 per evaluation × 100 experiments = $1

### **Total Cost: ~$10-15 for comprehensive testing**

## **⏱️ TIMELINE SUMMARY**

- **Pre-Implementation**: ✅ Complete (this document)
- **Implementation**: 90 minutes (when Claude API key ready)
- **Testing**: 20 minutes
- **Total**: ~2 hours for complete ensemble evaluation system

Ready to begin implementation upon receipt of Claude API key! 🚀
