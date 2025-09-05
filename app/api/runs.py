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
            plan_request = RunPlanRequest(
                prompts=prompt_ids,
                models=model_names,
                repeats=1,
                settings=RunSettings(),
                judge=JudgeConfig(type=JudgeType.LLM),
                bias_controls=BiasControls(),
            )
            final_run_ids = await get_experiment_service().plan_runs(plan_request)
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


@router.get("/{run_id}")
async def get_run(
    run_id: str,
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Get run details by ID with proper validation"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.repositories import OutputBlobRepository, RunRepository

        run_repo = RunRepository()
        blob_repo = OutputBlobRepository()

        run = await run_repo.get_by_id(run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Run with id {run_id} not found")

        # Get output if available
        output_content = None
        if run.output_blob_id:
            blob = await blob_repo.get_by_id(run.output_blob_id)
            if blob:
                output_content = blob.content

        return {
            "run": run.model_dump(),
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
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """List runs with filters and proper validation"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.repositories import RunRepository

        run_repo = RunRepository()
        runs = await run_repo.list_runs(
            status=status,
            prompt_id=prompt_id,
            model=model,
            scenario=scenario,
            length_bin=length_bin,
            page=page,
            limit=limit,
        )

        return {
            "runs": [run.model_dump() for run in runs],
            "page": page,
            "limit": limit,
            "count": len(runs),
        }
    except Exception as e:
        logger.error(f"Error listing runs: {e}")
        raise HTTPException(status_code=500, detail=f"Data validation error: {e!s}")
