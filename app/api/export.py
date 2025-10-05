import csv
import io
import logging
from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from app.core.security import validate_api_key_header
from app.models import LengthBin, RunStatus, ScenarioType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["export"])


@router.get("/runs.csv")
async def export_runs_csv(
    status: RunStatus | None = None,
    model: str | None = None,
    scenario: ScenarioType | None = None,
    experiment_id: str | None = None,
    dataset_version: str | None = None,
    x_api_key: str = Header(..., description="API key"),
) -> StreamingResponse:
    """Export runs data as CSV with full research metadata"""
    validate_api_key_header(x_api_key)
    
    try:
        from app.db.connection import get_database
        db = get_database()
        
        # Build filter query
        filter_query = {}
        if status:
            filter_query["status"] = status
        if model:
            filter_query["model"] = model
        if scenario:
            filter_query["scenario"] = scenario
        if experiment_id:
            filter_query["experiment_id"] = experiment_id
        if dataset_version:
            filter_query["dataset_version"] = dataset_version
        
        # Aggregation pipeline with full metadata
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
                "prompt_scenario": "$prompt.scenario",
                "prompt_dataset_version": "$prompt.dataset_version"
            }},
            {"$sort": {"created_at": -1}}
        ]
        
        cursor = db.runs.aggregate(pipeline)
        runs = await cursor.to_list(length=None)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # CSV Headers with full research metadata
        headers = [
            "run_id", "experiment_id", "dataset_version", "prompt_id", "model",
            "prompt_scenario", "prompt_length_bin", "status", "created_at",
            "input_tokens", "output_tokens", "total_tokens", "aud_cost",
            "technical_accuracy", "actionability", "completeness", 
            "compliance_alignment", "risk_awareness", "relevance", "clarity", 
            "composite_score", "fsp_enabled", "temperature", "seed",
            "judge_model", "judge_prompt_ver", "latency_ms"
        ]
        writer.writerow(headers)
        
        # Write data rows
        for run in runs:
            scores = run.get("scores", {}) or {}
            economics = run.get("economics", {}) or {}
            tokens = run.get("tokens", {}) or {}
            settings = run.get("settings", {}) or {}
            bias_controls = run.get("bias_controls", {}) or {}
            judge = run.get("judge", {}) or {}
            
            row = [
                run.get("run_id", ""),
                run.get("experiment_id", ""),
                run.get("dataset_version", ""),
                run.get("prompt_id", ""),
                run.get("model", ""),
                run.get("prompt_scenario", ""),
                run.get("prompt_length_bin", ""),
                run.get("status", ""),
                run.get("created_at", ""),
                tokens.get("input", 0),
                tokens.get("output", 0),
                tokens.get("total", 0),
                economics.get("aud_cost", 0.0),
                scores.get("technical_accuracy", ""),
                scores.get("actionability", ""),
                scores.get("completeness", ""),
                scores.get("compliance_alignment", ""),
                scores.get("risk_awareness", ""),
                scores.get("relevance", ""),
                scores.get("clarity", ""),
                scores.get("composite", ""),
                bias_controls.get("fsp", False),
                settings.get("temperature", ""),
                settings.get("seed", ""),
                judge.get("judge_model", ""),
                judge.get("prompt_ver", ""),
                economics.get("latency_ms", "")
            ]
            writer.writerow(row)
        
        # Prepare response
        output.seek(0)
        filename = f"cyberprompt_runs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments.csv")
async def export_experiments_csv(
    x_api_key: str = Header(..., description="API key"),
) -> StreamingResponse:
    """Export experiments summary as CSV"""
    validate_api_key_header(x_api_key)
    
    try:
        from app.db.connection import get_database
        db = get_database()
        
        # Aggregate experiments with detailed stats
        pipeline = [
            {"$match": {"experiment_id": {"$ne": None}}},
            {"$group": {
                "_id": "$experiment_id",
                "run_count": {"$sum": 1},
                "models": {"$addToSet": "$model"},
                "dataset_version": {"$first": "$dataset_version"},
                "created_at": {"$min": "$created_at"},
                "completed_runs": {"$sum": {"$cond": [{"$eq": ["$status", "succeeded"]}, 1, 0]}},
                "failed_runs": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
                "avg_cost": {"$avg": "$economics.aud_cost"},
                "total_cost": {"$sum": "$economics.aud_cost"},
                "avg_tokens": {"$avg": "$tokens.total"},
                "avg_composite_score": {"$avg": "$scores.composite"}
            }},
            {"$sort": {"created_at": -1}}
        ]
        
        cursor = db.runs.aggregate(pipeline)
        experiments = await cursor.to_list(length=None)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = [
            "experiment_id", "dataset_version", "created_at", "run_count",
            "completed_runs", "failed_runs", "models", "avg_cost", "total_cost",
            "avg_tokens", "avg_composite_score"
        ]
        writer.writerow(headers)
        
        for exp in experiments:
            row = [
                exp["_id"],
                exp["dataset_version"] or "",
                exp["created_at"],
                exp["run_count"],
                exp["completed_runs"],
                exp["failed_runs"],
                "|".join(exp["models"]),
                exp["avg_cost"] or 0.0,
                exp["total_cost"] or 0.0,
                exp["avg_tokens"] or 0,
                exp["avg_composite_score"] or ""
            ]
            writer.writerow(row)
        
        output.seek(0)
        filename = f"cyberprompt_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))