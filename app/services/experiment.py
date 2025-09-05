import asyncio
import logging
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.db.repositories import OutputBlobRepository, PromptRepository, RunRepository
from app.services.risk import risk_heuristics
from app.services.base import create_judge
from app.models import EconomicsMetrics, RiskMetrics, Run, RunPlanRequest, RunStatus, TokenMetrics
from app.services.llm_client import ModelRunner
from app.utils.token_meter import CostCalculator
from app.utils.ulid_gen import generate_blob_id, generate_ulid

logger = logging.getLogger(__name__)


class ExperimentService:
    """Service for planning and executing LLM evaluation runs"""

    def __init__(self):
        self.run_repo = RunRepository()
        self.prompt_repo = PromptRepository()
        self.blob_repo = OutputBlobRepository()
        self.model_runner = ModelRunner(
            openai_key=settings.openai_api_key,
            anthropic_key=settings.anthropic_api_key,
            google_key=settings.google_api_key,
        )
        # Initialize cost calculator with current pricing
        pricing_config = settings.get_pricing()
        self.cost_calculator = CostCalculator(pricing_config) if pricing_config else None

    async def plan_runs(self, plan_request: RunPlanRequest) -> list[str]:
        """
        Plan experiment runs based on request
        Returns list of run_ids that were created
        """
        run_ids = []

        try:
            # Validate prompts exist
            prompts = []
            for prompt_id in plan_request.prompts:
                prompt = await self.prompt_repo.get_by_id(prompt_id)
                if not prompt:
                    msg = f"Prompt not found: {prompt_id}"
                    raise ValueError(msg)
                prompts.append(prompt)

            # Create run matrix
            for prompt in prompts:
                for model in plan_request.models:
                    for _repeat in range(plan_request.repeats):
                        run_id = generate_ulid()

                        run = Run(
                            run_id=run_id,
                            prompt_id=prompt.prompt_id,
                            model=model,
                            settings=plan_request.settings,
                            judge=plan_request.judge,
                            bias_controls=plan_request.bias_controls,
                            status=RunStatus.QUEUED,
                        )

                        await self.run_repo.create(run)
                        run_ids.append(run_id)

            logger.info(f"Planned {len(run_ids)} runs")
            return run_ids

        except Exception as e:
            logger.error(f"Error planning runs: {e}")
            raise

    async def execute_run(self, run_id: str) -> dict[str, Any]:
        """Execute a single run"""
        try:
            # Get run details
            run = await self.run_repo.get_by_id(run_id)
            if not run:
                msg = f"Run not found: {run_id}"
                raise ValueError(msg)

            if run.status != RunStatus.QUEUED:
                return {"run_id": run_id, "status": run.status, "message": "Run already processed"}

            # Update status to running
            await self.run_repo.update(run_id, {"status": RunStatus.RUNNING})

            # Get prompt
            prompt = await self.prompt_repo.get_by_id(run.prompt_id)
            if not prompt:
                msg = f"Prompt not found: {run.prompt_id}"
                raise ValueError(msg)

            # Execute real LLM model
            execution_result = await self.model_runner.execute_run(
                model=run.model,
                prompt=prompt.text,
                settings=run.settings.model_dump(),
            )

            if not execution_result["success"]:
                await self.run_repo.update(run_id, {
                    "status": RunStatus.FAILED,
                    "updated_at": datetime.utcnow(),
                })
                return {"run_id": run_id, "status": "failed", "error": execution_result.get("error")}

            # Store output blob
            blob_id = generate_blob_id(execution_result["response"], run_id)
            from app.models import OutputBlob
            blob = OutputBlob(
                blob_id=blob_id,
                content=execution_result["response"],
                metadata={
                    "run_id": run_id,
                    "model": run.model,
                    "created_at": datetime.utcnow().isoformat(),
                },
            )
            await self.blob_repo.store(blob)

            # Calculate costs
            tokens = TokenMetrics(**execution_result["tokens"])
            pricing = settings.get_pricing()
            if self.cost_calculator and pricing and run.model in pricing:
                aud_cost, unit_price_in, unit_price_out = self.cost_calculator.calculate_cost(
                    tokens.input, tokens.output, run.model,
                )
                economics = EconomicsMetrics(
                    aud_cost=aud_cost,
                    unit_price_in=unit_price_in,
                    unit_price_out=unit_price_out,
                    latency_ms=execution_result["latency_ms"],
                )
            else:
                logger.warning(f"Cost calculation unavailable for model {run.model}")
                economics = EconomicsMetrics(
                    aud_cost=0.0,
                    unit_price_in=0.0,
                    unit_price_out=0.0,
                    latency_ms=execution_result["latency_ms"],
                )

            # Risk metrics
            risk_flags = risk_heuristics.hallucination_flags(
                execution_result["response"],
                prompt.text,
            )
            risk_metrics = RiskMetrics(hallucination_flags=risk_flags)

            # Real LLM Judge evaluation
            scores = None
            if run.judge.type.value == "llm":
                try:
                    # Get the appropriate LLM client for the judge model
                    judge_model = run.judge.judge_model or "gpt-4o-mini"
                    judge_client = self.model_runner._get_client(judge_model)

                    judge = create_judge(run.judge.model_dump(), judge_client)

                    # Standard evaluation
                    judge_result = await judge.evaluate(
                        output=execution_result["response"],
                        scenario=prompt.scenario,
                        length_bin=prompt.length_bin,
                        bias_controls=run.bias_controls.model_dump(),
                        context=prompt.text,
                    )

                    if "scores" in judge_result:
                        scores = judge_result["scores"]

                except Exception as e:
                    logger.error(f"Judge evaluation failed for run {run_id}: {e}")
                    # Continue without scores rather than failing
                    scores = None

            # Update run with results
            from app.models import RubricScores
            update_data = {
                "status": RunStatus.SUCCEEDED,
                "tokens": tokens.model_dump(),
                "economics": economics.model_dump(),
                "output_ref": blob_id,
                "risk_metrics": risk_metrics.model_dump(),
                "updated_at": datetime.utcnow(),
            }

            if scores:
                update_data["scores"] = RubricScores(**scores).model_dump()

            await self.run_repo.update(run_id, update_data)

            return {
                "run_id": run_id,
                "status": "succeeded",
                "tokens": tokens.model_dump(),
                "economics": economics.model_dump(),
                "scores": scores,
            }

        except Exception as e:
            logger.error(f"Error executing run {run_id}: {e}")
            await self.run_repo.update(run_id, {
                "status": RunStatus.FAILED,
                "updated_at": datetime.utcnow(),
            })
            return {"run_id": run_id, "status": "failed", "error": str(e)}

    async def execute_batch(self, run_ids: list[str], max_concurrent: int = 5) -> list[dict[str, Any]]:
        """Execute multiple runs concurrently"""
        logger.info(f"Executing batch with run_ids: {run_ids}")
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_semaphore(run_id: str):
            async with semaphore:
                return await self.execute_run(run_id)

        tasks = [execute_with_semaphore(run_id) for run_id in run_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "run_id": run_ids[i],
                    "status": "failed",
                    "error": str(result),
                })
            else:
                processed_results.append(result)

        return processed_results


# Global service instance - initialized lazily
experiment_service = None

def get_experiment_service():
    """Get or create the experiment service instance"""
    global experiment_service
    if experiment_service is None:
        experiment_service = ExperimentService()
    return experiment_service
