import logging

from fastapi import APIRouter, Header, HTTPException, Query

from app.services.analytics_service import analytics_service
from app.core.security import validate_api_key_header
from app.models import JudgeType, LengthBin, ScenarioType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/cost-quality-scatter")
async def cost_quality_scatter(
    x_api_key: str = Header(..., description="API key"),
) -> list[dict]:
    """Simple cost vs quality data for scatter plot"""
    validate_api_key_header(x_api_key)

    try:
        from app.db.repositories import RunRepository

        run_repo = RunRepository()

        # Get all succeeded runs with required data
        pipeline = [
            {
                "$match": {
                    "status": "succeeded",
                    "economics.aud_cost": {"$exists": True, "$gt": 0},
                    "scores.composite": {"$exists": True},
                },
            },
            {
                "$project": {
                    "run_id": 1,
                    "model": 1,
                    "aud_cost": "$economics.aud_cost",
                    "composite_score": "$scores.composite",
                },
            },
        ]

        cursor = run_repo.db.runs.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        # Convert ObjectIds to strings
        from app.utils.mongodb import convert_objectid_list
        return convert_objectid_list(results)


    except Exception as e:
        logger.error(f"Error in cost-quality scatter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost_quality")
async def cost_quality(
    scenario: ScenarioType | None = None,
    model: list[str] | None = Query(None),
    length_bin: list[LengthBin] | None = Query(None),
    judge_type: JudgeType | None = None,
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Cost vs Quality frontier analysis"""
    validate_api_key_header(x_api_key)

    try:
        results = await analytics_service.cost_quality_analysis(
            scenario=scenario,
            models=model,
            length_bins=length_bin,
            judge_type=judge_type,
        )

        return {
            "data": results,
            "filters": {
                "scenario": scenario.value if scenario else None,
                "models": model,
                "length_bins": [lb.value for lb in length_bin] if length_bin else None,
                "judge_type": judge_type.value if judge_type else None,
            },
        }

    except Exception as e:
        logger.error(f"Error in cost-quality analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/length_bias")
async def length_bias(
    scenario: ScenarioType | None = None,
    model: list[str] | None = Query(None),
    dimension: str = Query("composite", pattern="^(composite|technical_accuracy|actionability|completeness|compliance_alignment|risk_awareness|relevance|clarity)$"),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Length bias analysis per dimension"""
    validate_api_key_header(x_api_key)

    try:
        return await analytics_service.length_bias_analysis(
            scenario=scenario,
            models=model,
            dimension=dimension,
        )


    except Exception as e:
        logger.error(f"Error in length bias analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk_curves")
async def risk_curves(
    scenario: ScenarioType | None = None,
    model: list[str] | None = Query(None),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Risk curves analysis"""
    validate_api_key_header(x_api_key)

    try:
        return await analytics_service.risk_curves_analysis(
            scenario=scenario,
            models=model,
        )


    except Exception as e:
        logger.error(f"Error in risk curves analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk_cost")
async def risk_cost(
    scenario: ScenarioType | None = None,
    model: list[str] | None = Query(None),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Risk-cost frontier analysis"""
    validate_api_key_header(x_api_key)

    try:
        # Get cost-quality data
        cost_quality_data = await analytics_service.cost_quality_analysis(
            scenario=scenario,
            models=model,
        )

        # Get risk curves data
        risk_data = await analytics_service.risk_curves_analysis(
            scenario=scenario,
            models=model,
        )

        # Combine for risk-cost frontier
        risk_cost_points = []

        for cq_point in cost_quality_data:
            model_name = cq_point["model"]
            length_bin = cq_point["length_bin"]

            # Find corresponding risk data
            if model_name in risk_data.get("risk_curves", {}):
                risk_curves = risk_data["risk_curves"][model_name]

                # Find matching length bin
                risk_awareness = None
                hallucination_rate = None

                for ra_point in risk_curves.get("risk_awareness", []):
                    if ra_point["length_bin"] == length_bin:
                        risk_awareness = ra_point["value"]
                        break

                for hr_point in risk_curves.get("hallucination_rate", []):
                    if hr_point["length_bin"] == length_bin:
                        hallucination_rate = hr_point["value"]
                        break

                if risk_awareness is not None:
                    risk_cost_points.append({
                        "model": model_name,
                        "length_bin": length_bin,
                        "x": cq_point["x"],  # AUD cost per 1k tokens
                        "y": 1 - (risk_awareness / 5.0),  # Inverse risk (higher is riskier)
                        "risk_awareness": risk_awareness,
                        "hallucination_rate": hallucination_rate or 0,
                        "composite": cq_point["y"],
                    })

        return {
            "risk_cost_frontier": risk_cost_points,
            "filters": {
                "scenario": scenario.value if scenario else None,
                "models": model,
            },
        }

    except Exception as e:
        logger.error(f"Error in risk-cost analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/adaptive_relevance")
async def adaptive_relevance(
    scenario: ScenarioType | None = None,
    model: list[str] | None = Query(None),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Adaptive relevance analysis (derived metric)"""
    validate_api_key_header(x_api_key)

    try:
        return await analytics_service.adaptive_relevance_analysis(
            scenario=scenario,
            models=model,
        )


    except Exception as e:
        logger.error(f"Error in adaptive relevance analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/best_quality_per_aud")
async def best_quality_per_aud(
    scenario: ScenarioType | None = None,
    length_bin: list[LengthBin] | None = Query(None),
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Best quality per AUD leaderboard"""
    validate_api_key_header(x_api_key)

    try:
        results = await analytics_service.best_quality_per_aud(
            scenario=scenario,
            length_bins=length_bin,
        )

        return {
            "leaderboard": results,
            "filters": {
                "scenario": scenario.value if scenario else None,
                "length_bins": [lb.value for lb in length_bin] if length_bin else None,
            },
        }

    except Exception as e:
        logger.error(f"Error in best quality per AUD analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coverage")
async def prompt_coverage(
    x_api_key: str = Header(..., description="API key"),
) -> dict:
    """Prompt coverage tracking by source and scenario"""
    validate_api_key_header(x_api_key)
    
    try:
        return await analytics_service.get_prompt_coverage()
        
    except Exception as e:
        logger.error(f"Error in prompt coverage analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
