"""Background job processing for long-running tasks"""

import logging
from typing import Any

from app.services.experiment import get_experiment_service

logger = logging.getLogger(__name__)


async def execute_batch_background(
    run_ids: list[str], 
    max_concurrent: int = 5
) -> dict[str, Any]:
    """Execute batch of runs in background"""
    try:
        logger.info(f"Starting background execution of {len(run_ids)} runs")
        results = await get_experiment_service().execute_batch(run_ids, max_concurrent)
        
        success_count = sum(1 for r in results if r.get("status") == "succeeded")
        failed_count = len(results) - success_count
        
        logger.info(f"Background batch completed: {success_count} succeeded, {failed_count} failed")
        
        return {
            "results": results,
            "summary": {
                "total": len(results),
                "succeeded": success_count,
                "failed": failed_count,
            },
        }
    except Exception as e:
        logger.error(f"Background batch execution failed: {e}")
        return {
            "results": [{"run_id": "error", "status": "failed", "error": str(e)}],
            "summary": {"total": 0, "succeeded": 0, "failed": 1},
        }