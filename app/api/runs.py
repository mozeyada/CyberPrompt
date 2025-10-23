import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query

from app.core.security import validate_api_key_header
from app.models import LengthBin, RunPlanRequest, RunStatus, ScenarioType
from app.services.experiment import get_experiment_service
from app.services.ensemble import EnsembleJudgeService
import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("/plan")
async def plan_runs(
    plan_request: RunPlanRequest,
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Plan experiment runs"""
    validate_api_key_header(x_api_key)

    try:
        run_ids = await get_experiment_service().plan_runs(plan_request)
        return {
            "message": f"Planned {len(run_ids)} runs",
            "run_ids": run_ids,
            "total_runs": len(run_ids),
        }
    except Exception as e:
        logger.error(f"Error planning runs: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/execute/batch")
async def execute_batch(
    request: dict,
    background_tasks: BackgroundTasks,
    max_concurrent: int = Query(5, ge=1, le=10),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Execute multiple runs in background"""
    validate_api_key_header(x_api_key)

    try:
        # Handle both formats: run_ids (planned) or prompt_ids + model_names (direct)
        run_ids = request.get("run_ids", [])
        prompt_ids = request.get("prompt_ids", [])
        model_names = request.get("model_names", [])

        logger.info(f"Received batch execute request with run_ids: {run_ids}, prompt_ids: {prompt_ids}, model_names: {model_names}")

        if run_ids:
            # Planned execution
            final_run_ids = run_ids
        elif prompt_ids and model_names:
            # Direct execution - plan first
            from app.models import BiasControls, JudgeConfig, JudgeType, RunPlanRequest, RunSettings
            
            # Extract configuration from request
            bias_controls_data = request.get("bias_controls", {})
            settings_data = request.get("settings", {})
            repeats = request.get("repeats", 1)
            
            plan_request = RunPlanRequest(
                prompts=prompt_ids,
                models=model_names,
                repeats=repeats,
                settings=RunSettings(
                    temperature=settings_data.get("temperature", 0.2),
                    max_tokens=settings_data.get("max_tokens", 2000),
                    seed=settings_data.get("seed", 42)
                ),
                judge=JudgeConfig(type=JudgeType.LLM),
                bias_controls=BiasControls(
                    fsp=bias_controls_data.get("fsp", True),
                    granularity_demo=bias_controls_data.get("granularity_demo", False)
                ),
            )
            include_variants = request.get("include_variants", False)
            final_run_ids = await get_experiment_service().plan_runs(plan_request, include_variants)
        else:
            raise HTTPException(status_code=400, detail="No run_ids or prompt_ids+model_names provided")

        # Execute in background for large batches
        if len(final_run_ids) > 10:
            from app.services.background_jobs import execute_batch_background
            
            # Get experiment_id from first run for frontend polling
            from app.db.repositories import RunRepository
            run_repo = RunRepository()
            first_run = await run_repo.get_by_id(final_run_ids[0]) if final_run_ids else None
            experiment_id = first_run.experiment_id if first_run else None
            
            background_tasks.add_task(execute_batch_background, final_run_ids, max_concurrent)
            return {
                "message": f"Started background execution of {len(final_run_ids)} runs",
                "status": "accepted",
                "run_ids": final_run_ids,
                "total_runs": len(final_run_ids),
                "experiment_id": experiment_id
            }
        else:
            # Execute synchronously for small batches
            results = await get_experiment_service().execute_batch(final_run_ids, max_concurrent)
            success_count = sum(1 for r in results if r.get("status") == "succeeded")
            failed_count = len(results) - success_count
            return {
                "results": results,
                "summary": {
                    "total": len(results),
                    "succeeded": success_count,
                    "failed": failed_count,
                },
            }
    except Exception as e:
        logger.error(f"Error executing batch: {e}")
        return {
            "results": [{"run_id": "error", "status": "failed", "error": str(e)}],
            "summary": {"total": 0, "succeeded": 0, "failed": 1},
        }


@router.post("/execute/batch-ensemble")
async def execute_batch_ensemble(
    request: dict,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Execute runs with ensemble evaluation"""
    validate_api_key_header(x_api_key)
    
    try:
        # Extract configuration
        prompt_ids = request.get("prompt_ids", [])
        model_names = request.get("model_names", [])
        ensemble_enabled = request.get("ensemble", True)
        include_variants = request.get("include_variants", False)
        
        if not prompt_ids or not model_names:
            raise HTTPException(status_code=400, detail="prompt_ids and model_names are required")
        
        # Plan runs as normal
        from app.models import BiasControls, JudgeConfig, JudgeType, RunPlanRequest, RunSettings
        
        bias_controls_data = request.get("bias_controls", {})
        settings_data = request.get("settings", {})
        repeats = request.get("repeats", 1)
        
        plan_request = RunPlanRequest(
            prompts=prompt_ids,
            models=model_names,
            repeats=repeats,
            settings=RunSettings(
                temperature=settings_data.get("temperature", 0.2),
                max_tokens=settings_data.get("max_tokens", 2000),
                seed=settings_data.get("seed", 42)
            ),
            judge=JudgeConfig(type=JudgeType.LLM),
            bias_controls=BiasControls(
                fsp=bias_controls_data.get("fsp", True),
                granularity_demo=bias_controls_data.get("granularity_demo", False)
            ),
        )
        
        run_ids = await get_experiment_service().plan_runs(plan_request, include_variants)
        
        # Execute batch (ensemble evaluation now happens INSIDE execute_run, not separately)
        # Note: ensemble_enabled parameter is now ignored - system ALWAYS uses 3-judge ensemble
        if not ensemble_enabled:
            logger.warning("ensemble_enabled=False ignored - system ALWAYS uses 3-judge ensemble")
        
        results = await get_experiment_service().execute_batch(run_ids)
        
        success_count = sum(1 for r in results if r.get("status") == "succeeded")
        failed_count = len(results) - success_count
        
        # Get experiment_id from first run for frontend polling
        from app.db.repositories import RunRepository
        run_repo = RunRepository()
        first_run = await run_repo.get_by_id(run_ids[0]) if run_ids else None
        experiment_id = first_run.experiment_id if first_run else None
        
        return {
            "message": f"Executed {len(run_ids)} runs with ensemble evaluation",
            "results": results,
            "ensemble_enabled": ensemble_enabled,
            "experiment_id": experiment_id,
            "summary": {
                "total": len(results),
                "succeeded": success_count,
                "failed": failed_count,
            }
        }
        
    except Exception as e:
        logger.error(f"Error executing batch ensemble: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/execute/{run_id}")
async def execute_run(
    run_id: str,
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Execute a single run"""
    validate_api_key_header(x_api_key)

    try:
        return await get_experiment_service().execute_run(run_id)
    except Exception as e:
        logger.error(f"Error executing run {run_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/experiments")
async def list_experiments(
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """List all experiments with summary statistics"""
    validate_api_key_header(x_api_key)
    
    try:
        from app.db.connection import get_database
        db = get_database()
        
        # Aggregate experiments with stats
        pipeline = [
            {"$match": {"experiment_id": {"$ne": None}}},
            {"$group": {
                "_id": "$experiment_id",
                "run_count": {"$sum": 1},
                "models": {"$addToSet": "$model"},
                "dataset_version": {"$first": "$dataset_version"},
                "created_at": {"$min": "$created_at"},
                "completed_runs": {"$sum": {"$cond": [{"$eq": ["$status", "succeeded"]}, 1, 0]}},
                "avg_cost": {"$avg": "$economics.aud_cost"}
            }},
            {"$sort": {"created_at": -1}}
        ]
        
        cursor = db.runs.aggregate(pipeline)
        experiments = await cursor.to_list(length=None)
        
        return {
            "experiments": [{
                "experiment_id": exp["_id"],
                "run_count": exp["run_count"],
                "models": exp["models"],
                "dataset_version": exp["dataset_version"],
                "created_at": exp["created_at"],
                "completed_runs": exp["completed_runs"],
                "avg_cost": exp["avg_cost"] or 0.0
            } for exp in experiments]
        }
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experiments/{experiment_id}/ensemble-evaluate")
async def add_ensemble_to_existing_runs(
    experiment_id: str,
    x_api_key: str = Header(..., description="API key")
) -> dict:
    """Add ensemble evaluation to existing runs in an experiment"""
    validate_api_key_header(x_api_key)
    
    try:
        # Get experiment service
        exp_service = get_experiment_service()
        ensemble_service = EnsembleJudgeService()
        
        # Get existing runs from experiment
        from app.db.repositories import RunRepository
        run_repo = RunRepository()
        runs = await run_repo.get_runs_by_experiment(experiment_id)
        
        if not runs:
            raise HTTPException(status_code=404, detail=f"No runs found for experiment {experiment_id}")
        
        results = []
        successful = 0
        failed = 0
        
        for run in runs:
            try:
                if run.output_blob_id:
                    # Get output content
                    from app.db.repositories import OutputBlobRepository, PromptRepository
                    blob_repo = OutputBlobRepository()
                    output_blob = await blob_repo.get_by_id(run.output_blob_id)
                    
                    # Get prompt for context
                    prompt_repo = PromptRepository()
                    prompt = await prompt_repo.get_by_id(run.prompt_id)
                    prompt_context = prompt.text if prompt else None
                    
                    if output_blob:
                        # Perform ensemble evaluation
                        ensemble_eval = await ensemble_service.evaluate_with_ensemble(
                            output=output_blob.content,
                            scenario=run.scenario,
                            length_bin=run.prompt_length_bin,
                            bias_controls=run.bias_controls.model_dump(),
                            run_id=run.run_id,
                            context=prompt_context  # Add context
                        )
                        
                        # Update run with ensemble results
                        await run_repo.update(run.run_id, {
                            "ensemble_evaluation": ensemble_eval.model_dump()
                        })
                        
                        # Extract correlation data
                        avg_correlation = 0
                        if ensemble_eval.reliability_metrics and ensemble_eval.reliability_metrics.pearson_correlations:
                            correlations = list(ensemble_eval.reliability_metrics.pearson_correlations.values())
                            avg_correlation = np.mean(correlations) if correlations else 0
                        
                        results.append({
                            "run_id": run.run_id,
                            "ensemble_scores": ensemble_eval.aggregated.mean_scores.model_dump(),
                            "reliability": ensemble_eval.reliability_metrics.inter_judge_agreement if ensemble_eval.reliability_metrics else "unknown",
                            "avg_correlation": avg_correlation
                        })
                        successful += 1
                    else:
                        logger.warning(f"No output blob found for run {run.run_id}")
                        failed += 1
                else:
                    logger.warning(f"No output blob ID for run {run.run_id}")
                    failed += 1
                    
            except Exception as e:
                logger.error(f"Ensemble evaluation failed for run {run.run_id}: {e}")
                results.append({"run_id": run.run_id, "error": str(e)})
                failed += 1
        
        return {
            "message": f"Ensemble evaluation completed for {successful} runs, {failed} failed",
            "experiment_id": experiment_id,
            "results": results,
            "summary": {
                "total_runs": len(runs),
                "successful": successful,
                "failed": failed
            }
        }
        
    except Exception as e:
        logger.error(f"Ensemble evaluation batch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{run_id}")
async def get_run(
    run_id: str,
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Get run details by ID with proper validation"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.repositories import OutputBlobRepository, PromptRepository, RunRepository

        run_repo = RunRepository()
        blob_repo = OutputBlobRepository()
        prompt_repo = PromptRepository()

        run = await run_repo.get_by_id(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Run with id {run_id} not found")

        # Get output if available - check both old and new field names
        output_content = None
        blob_id = run.output_blob_id or getattr(run, 'output_ref', None)
        
        logger.info(f"Debug run {run_id}: output_blob_id={run.output_blob_id}, output_ref={getattr(run, 'output_ref', None)}")
        
        if blob_id:
            blob = await blob_repo.get_by_id(blob_id)
            if blob:
                output_content = blob.content
                logger.info(f"Debug run {run_id}: Found blob with content length {len(output_content)}")
            else:
                logger.warning(f"Debug run {run_id}: Blob {blob_id} not found")
        else:
            logger.warning(f"Debug run {run_id}: No blob_id found")

        # Get prompt text if available
        prompt_text = None
        if run.prompt_id:
            prompt = await prompt_repo.get_by_id(run.prompt_id)
            if prompt:
                prompt_text = prompt.text

        # Add prompt_text to run data
        run_data = run.model_dump()
        run_data["prompt_text"] = prompt_text

        return {
            "run": run_data,
            "output": output_content,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting run {run_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Data validation error: {e!s}")


@router.get("/")
async def list_runs(
    status: RunStatus | None = None,
    prompt_id: str | None = None,
    model: str | None = None,
    scenario: ScenarioType | None = None,
    length_bin: LengthBin | None = None,
    experiment_id: str | None = None,
    dataset_version: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """List runs with filters and prompt_text included"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.connection import get_database
        
        db = get_database()
        
        # Build filter query
        filter_query = {}
        if status:
            filter_query["status"] = status
        if prompt_id:
            filter_query["prompt_id"] = prompt_id
        if model:
            filter_query["model"] = model
        if scenario:
            filter_query["scenario"] = scenario
        if length_bin:
            filter_query["length_bin"] = length_bin
        if experiment_id:
            filter_query["experiment_id"] = experiment_id
        if dataset_version:
            filter_query["dataset_version"] = dataset_version
        
            
        # Aggregation pipeline to join with prompts
        pipeline = [
            {"$match": filter_query},
            {"$lookup": {
                "from": "prompts",
                "localField": "prompt_id",
                "foreignField": "prompt_id",
                "as": "prompt"
            }},
            {"$unwind": {"path": "$prompt", "preserveNullAndEmptyArrays": True}},
            {"$addFields": {
                "prompt_text": "$prompt.text",
                "prompt_length_bin": "$prompt.length_bin",
                "prompt_dataset_version": "$prompt.dataset_version",
                "length_bin": "$prompt.length_bin"  # Add this for easier access
            }},
            {"$sort": {"created_at": -1}},
            {"$skip": (page - 1) * limit},
            {"$limit": limit}
        ]
        
        cursor = db.runs.aggregate(pipeline)
        docs = await cursor.to_list(length=limit)
        
        # Convert ObjectIds to strings
        from app.utils.mongodb import convert_objectid_list
        docs = convert_objectid_list(docs)
        
        return {
            "runs": docs,
            "page": page,
            "limit": limit,
            "count": len(docs),
        }
    except Exception as e:
        logger.error(f"Error listing runs: {e}")
        raise HTTPException(status_code=500, detail=f"Data validation error: {e!s}")


@router.delete("/delete/{run_id}")
async def delete_run(
    run_id: str,
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Delete a specific run"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.repositories import RunRepository
        run_repo = RunRepository()
        
        # Check if run exists
        run = await run_repo.get_by_id(run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run not found")
        
        # Delete the run
        success = await run_repo.delete_by_id(run_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete run")
        
        return {"message": f"Run {run_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting run {run_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete run: {e}")