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
from app.utils.ulid_gen import generate_blob_id
from app.utils.simple_ids import get_next_run_id, get_next_experiment_id

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

    async def plan_runs(self, plan_request: RunPlanRequest, include_variants: bool = False) -> list[str]:
        """
        Plan experiment runs based on request
        Returns list of run_ids that were created
        """
        run_ids = []

        try:
            # Generate simple experiment ID
            experiment_id = await get_next_experiment_id()
            current_dataset_version = datetime.now().strftime("%Y%m%d")
            
            # Validate prompts exist and expand variants if needed
            prompts = []
            invalid_prompt_ids = []
            
            for prompt_id in plan_request.prompts:
                if not prompt_id or not isinstance(prompt_id, str):
                    invalid_prompt_ids.append(f"Invalid prompt ID format: {prompt_id}")
                    continue
                    
                prompt = await self.prompt_repo.get_by_id(prompt_id)
                if not prompt:
                    invalid_prompt_ids.append(prompt_id)
                    continue
                    
                prompts.append(prompt)
                
                # If include_variants is True, add the M and L variants for this prompt
                if include_variants:
                    # Find variants by matching the base prompt ID (remove length suffix)
                    import re
                    base_prompt_id = re.sub(r'_[slm]$', '', prompt_id, flags=re.IGNORECASE)
                    
                    # Find medium and long variants using the naming pattern
                    from app.db.connection import get_database
                    db = get_database()
                    
                    # Create the variant IDs based on naming pattern
                    variant_ids = [
                        f"{base_prompt_id}_m",  # Medium variant
                        f"{base_prompt_id}_l"   # Long variant
                    ]
                    
                    variant_docs = await db.prompts.find({
                        'prompt_id': {'$in': variant_ids},
                        'scenario': prompt.scenario  # Ensure same scenario
                    }).to_list(None)
                    
                    for variant_doc in variant_docs:
                        try:
                            from app.models import Prompt
                            variant_prompt = Prompt(**variant_doc)
                            prompts.append(variant_prompt)
                            logger.info(f"Added variant: {variant_prompt.prompt_id} ({variant_prompt.length_bin})")
                        except Exception as e:
                            logger.warning(f"Skipping invalid variant: {e}")
                            continue
            
            if invalid_prompt_ids:
                msg = f"Invalid prompt IDs: {', '.join(invalid_prompt_ids[:5])}" + (" (and more)" if len(invalid_prompt_ids) > 5 else "")
                raise ValueError(msg)

            # Create run matrix
            for prompt in prompts:
                for model in plan_request.models:
                    for _repeat in range(plan_request.repeats):
                        run_id = await get_next_run_id()

                        # Ensure judge has a valid model
                        judge_config = plan_request.judge.model_copy()
                        if not judge_config.judge_model:
                            judge_config.judge_model = "gpt-4o-mini"
                        
                        # Map prompt source to run source
                        run_source = "adaptive" if prompt.source == "adaptive" else "static"
                        
                        run = Run(
                            run_id=run_id,
                            prompt_id=prompt.prompt_id,
                            model=model,
                            settings=plan_request.settings,
                            judge=judge_config,
                            bias_controls=plan_request.bias_controls,
                            status=RunStatus.QUEUED,
                            dataset_version=current_dataset_version,
                            experiment_id=experiment_id,
                            prompt_length_bin=prompt.length_bin,
                            scenario=prompt.scenario,
                            source=run_source,
                            fsp_enabled=plan_request.bias_controls.fsp,
                        )

                        await self.run_repo.create(run)
                        run_ids.append(run_id)

            logger.info(f"Planned {len(run_ids)} runs")
            return run_ids

        except Exception as e:
            logger.error(f"Error planning runs: {e}")
            raise

    async def execute_run(self, run_id: str, use_ensemble: bool = False) -> dict[str, Any]:
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

            # Evaluation logic - either ensemble or single judge
            scores = None
            ensemble_evaluation = None
            
            if use_ensemble:
                # Ensemble evaluation
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
                    
                    # Use ensemble aggregated scores
                    if ensemble_eval.aggregated and ensemble_eval.aggregated.mean_scores:
                        scores = ensemble_eval.aggregated.mean_scores.model_dump()
                        ensemble_evaluation = ensemble_eval
                        logger.info(f"Ensemble evaluation completed for run {run_id}")
                    else:
                        logger.warning(f"Ensemble evaluation failed to produce scores for run {run_id}")
                        
                except Exception as e:
                    logger.error(f"Ensemble evaluation failed for run {run_id}: {e}")
                    # Fall back to single judge
                    scores = await self._evaluate_single_judge(
                        execution_result["response"], prompt, run, run_id
                    )
            elif run.judge.type.value == "llm":
                # Single judge evaluation (original logic)
                scores = await self._evaluate_single_judge(
                    execution_result["response"], prompt, run, run_id
                )

            # Update run with results
            from app.models import RubricScores
            update_data = {
                "status": RunStatus.SUCCEEDED,
                "tokens": tokens.model_dump(),
                "economics": economics.model_dump(),
                "output_blob_id": blob_id,
                "risk_metrics": risk_metrics.model_dump(),
                "updated_at": datetime.utcnow(),
            }

            if scores:
                update_data["scores"] = RubricScores(**scores).model_dump()
            
            if ensemble_evaluation:
                update_data["ensemble_evaluation"] = ensemble_evaluation.model_dump()

            await self.run_repo.update(run_id, update_data)

            return {
                "run_id": run_id,
                "experiment_id": run.experiment_id,
                "status": "succeeded",
                "model": run.model,
                "tokens": tokens.model_dump(),
                "economics": economics.model_dump(),
                "scores": scores,
            }

        except Exception as e:
            logger.error(f"Error executing run {run_id}: {e}")
            # Get run for experiment_id even on failure
            try:
                run = await self.run_repo.get_by_id(run_id)
                exp_id = run.experiment_id if run else None
            except:
                exp_id = None
            await self.run_repo.update(run_id, {
                "status": RunStatus.FAILED,
                "updated_at": datetime.utcnow(),
            })
            return {
                "run_id": run_id, 
                "experiment_id": exp_id, 
                "status": "failed", 
                "model": run.model if run else "unknown",
                "error": str(e)
            }

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
                # Try to get model info for failed runs
                try:
                    run = await self.run_repo.get_by_id(run_ids[i])
                    model = run.model if run else "unknown"
                except:
                    model = "unknown"
                    
                processed_results.append({
                    "run_id": run_ids[i],
                    "status": "failed",
                    "model": model,
                    "error": str(result),
                })
            else:
                processed_results.append(result)

        return processed_results

    async def _evaluate_single_judge(self, response: str, prompt, run, run_id: str) -> dict:
        """Evaluate using single judge model"""
        try:
            # Get the appropriate LLM client for the judge model
            judge_model = run.judge.judge_model or "gpt-4o-mini"
            # Ensure we have a valid model name
            if not judge_model or judge_model == "":
                judge_model = "gpt-4o-mini"
            judge_client = self.model_runner._get_client(judge_model)

            judge = create_judge(run.judge.model_dump(), judge_client)

            # Standard evaluation
            judge_result = await judge.evaluate(
                output=response,
                scenario=prompt.scenario,
                length_bin=prompt.length_bin,
                bias_controls=run.bias_controls.model_dump(),
                context=prompt.text,
            )

            if "scores" in judge_result and "error" not in judge_result:
                scores = judge_result["scores"]
                # Only save scores if they're valid (not all zeros)
                if scores.get("composite", 0) > 0:
                    return scores
                else:
                    logger.warning(f"Judge returned zero scores for run {run_id}, not saving")
                    return None
            else:
                logger.warning(f"Judge failed for run {run_id}: {judge_result.get('error', 'Unknown error')}")
                return None

        except Exception as e:
            logger.error(f"Judge evaluation failed for run {run_id}: {e}")
            # Continue without scores rather than failing
            return None


# Global service instance - initialized lazily
experiment_service = None

def get_experiment_service():
    """Get or create the experiment service instance"""
    global experiment_service
    if experiment_service is None:
        experiment_service = ExperimentService()
    return experiment_service
