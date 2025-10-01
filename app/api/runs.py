import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Query

from app.core.security import validate_api_key_header
from app.models import LengthBin, RunPlanRequest, RunStatus, ScenarioType
from app.services.experiment import get_experiment_service

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
                    max_tokens=settings_data.get("max_tokens", 800)
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
            background_tasks.add_task(execute_batch_background, final_run_ids, max_concurrent)
            return {
                "message": f"Started background execution of {len(final_run_ids)} runs",
                "status": "accepted",
                "run_ids": final_run_ids,
                "total_runs": len(final_run_ids)
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
    limit: int = Query(50, ge=1, le=200),
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