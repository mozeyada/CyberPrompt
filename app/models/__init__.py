from datetime import datetime
from enum import Enum
from typing import Any, Dict, Literal
import math

from pydantic import BaseModel, Field, field_validator, model_serializer


def safe_float_for_json(value: Any) -> Any:
    """Convert NaN and Infinity values to None for JSON serialization"""
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value


class SafeBaseModel(BaseModel):
    """Base model with safe JSON serialization for NaN/Infinity values"""
    
    @model_serializer
    def serialize_model(self):
        """Custom serializer that handles NaN and Infinity values"""
        data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, dict):
                data[key] = {k: safe_float_for_json(v) for k, v in value.items()}
            elif isinstance(value, list):
                data[key] = [safe_float_for_json(item) for item in value]
            else:
                data[key] = safe_float_for_json(value)
        return data


class SourceType(str, Enum):
    CYSECBENCH = "cysecbench"
    CURATED = "curated"
    CYBENCH = "CySecBench"  # Research data
    ADAPTIVE = "adaptive"  # Generated from SOC/GRC docs and CTI


class DocumentSourceType(str, Enum):
    GRC_POLICY = "GRC_POLICY"
    CTI_FEED = "CTI_FEED"


class ScenarioType(str, Enum):
    SOC_INCIDENT = "SOC_INCIDENT"
    CTI_SUMMARY = "CTI_SUMMARY"
    CTI_ANALYSIS = "CTI_ANALYSIS"
    GRC_MAPPING = "GRC_MAPPING"


class ContextType(str, Enum):
    SOC = "SOC"
    INCIDENT_RESPONSE = "IncidentResponse"
    GRC = "GRC"


class LengthBin(str, Enum):
    S = "S"    # ≤300 tokens (Short SOC/GRC prompts)
    M = "M"    # 301-800 tokens (Medium SOC/GRC prompts)
    L = "L"    # >800 tokens (Long SOC/GRC prompts)


class SafetyTag(str, Enum):
    SAFE_DOC = "SAFE_DOC"
    REDACTED = "REDACTED"
    BLOCKED = "BLOCKED"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JudgeType(str, Enum):
    LLM = "llm"
    HUMAN = "human"


class Prompt(BaseModel):
    prompt_id: str | None = Field(None, description="ULID identifier")
    text: str
    source: SourceType | None = None
    prompt_type: Literal["static", "adaptive"] = "static"  # Classification for research
    scenario: ScenarioType
    context: ContextType | None = None
    length_bin: LengthBin | None = None
    token_count: int | None = None  # Token count for classification
    complexity: int | None = Field(None, ge=1, le=5)
    safety_tag: SafetyTag | None = None
    category: str | None = None  # Research category
    metadata: dict[str, Any] | None = None  # Research metadata
    tags: list[str] | None = None
    dataset_version: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TokenMetrics(BaseModel):
    input: int
    output: int
    total: int


class EconomicsMetrics(SafeBaseModel):
    aud_cost: float
    unit_price_in: float
    unit_price_out: float
    latency_ms: int


class RunSettings(BaseModel):
    temperature: float = 0.2
    seed: int = 42


class JudgeConfig(BaseModel):
    type: JudgeType
    judge_model: str | None = None
    prompt_ver: str = "calibrated"  # Calibrated with 5-point scale


class RubricScores(SafeBaseModel):
    technical_accuracy: float = Field(..., ge=0, le=5)
    actionability: float = Field(..., ge=0, le=5)
    completeness: float = Field(..., ge=0, le=5)
    compliance_alignment: float = Field(..., ge=0, le=5)
    risk_awareness: float = Field(..., ge=0, le=5)
    relevance: float = Field(..., ge=0, le=5)
    clarity: float = Field(..., ge=0, le=5)
    composite: float = Field(..., ge=0, le=5)


class RiskMetrics(BaseModel):
    hallucination_flags: int = 0


class BiasControls(BaseModel):
    fsp: bool = True  # FSP ON by default
    granularity_demo: bool = False


class JudgeResult(BaseModel):
    """Result from a single judge evaluation"""
    judge_model: str
    scores: RubricScores
    raw_response: str = ""
    evaluation_time: datetime = Field(default_factory=datetime.utcnow)
    tokens_used: int = 0
    cost_usd: float = 0.0
    fsp_used: bool = False
    evaluation_failed: bool = False

class AggregatedScores(SafeBaseModel):
    """Aggregated scores from ensemble evaluation"""
    mean_scores: RubricScores
    median_scores: RubricScores | None = None
    std_scores: RubricScores | None = None
    confidence_95_ci: dict[str, tuple[float, float]] = {}

class ReliabilityMetrics(SafeBaseModel):
    """Inter-judge reliability metrics"""
    pearson_correlations: dict[str, float] = {}
    fleiss_kappa: float = 0.0
    inter_judge_agreement: str = "unknown"

class EnsembleEvaluation(SafeBaseModel):
    """Triple-judge ensemble evaluation result"""
    evaluation_id: str = Field(default_factory=lambda: f"ensemble_{int(datetime.utcnow().timestamp())}")
    primary_judge: JudgeResult | None = None    # GPT-4o-mini
    secondary_judge: JudgeResult | None = None  # Claude-3.5-Sonnet
    tertiary_judge: JudgeResult | None = None   # Llama-3.1-70B
    aggregated: AggregatedScores | None = None
    reliability_metrics: ReliabilityMetrics | None = None

class Run(SafeBaseModel):
    run_id: str = Field(..., description="ULID identifier")
    prompt_id: str
    model: str
    model_id: str | None = None  # Specific model version/ID
    settings: RunSettings
    status: RunStatus = RunStatus.QUEUED
    source: Literal["static", "adaptive"] = "static"
    prompt_length_bin: LengthBin | None = None  # Length bin from prompt
    scenario: ScenarioType | None = None  # Scenario from prompt
    tokens: TokenMetrics | None = None
    economics: EconomicsMetrics | None = None
    output_blob_id: str | None = Field(None, description="Reference to OutputBlob.blob_id")
    output_ref: str | None = None  # Alternative reference field
    judge: JudgeConfig
    scores: RubricScores | None = None
    risk_metrics: RiskMetrics | None = None
    bias_controls: BiasControls = BiasControls()
    fsp_enabled: bool = True  # Track which scoring path was used
    dataset_version: str | None = None
    experiment_id: str | None = None  # Group runs from same experiment
    seed: int | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # NEW: Ensemble evaluation support
    ensemble_evaluation: EnsembleEvaluation | None = None

    @field_validator("model_id", mode="before")
    @classmethod
    def set_model_id(cls, v, info):
        if v is None and info and hasattr(info, 'data') and info.data and "model" in info.data:
            return info.data["model"]
        return v


class OutputBlob(BaseModel):
    blob_id: str = Field(..., description="Hash identifier")
    content: str
    metadata: dict[str, Any]


class BaselineRun(BaseModel):
    baseline_id: str = Field(..., description="ULID identifier")
    source: str = Field(..., description="Source benchmark name")
    task_name: str | None = None
    model: str
    tokens: TokenMetrics
    aud_cost: float
    metric_name: str
    metric_value: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Request/Response models
class RunPlanRequest(BaseModel):
    prompts: list[str]
    models: list[str]
    repeats: int = 1
    settings: RunSettings = RunSettings()
    judge: JudgeConfig = JudgeConfig(type=JudgeType.LLM)
    bias_controls: BiasControls = BiasControls()


class RunExecuteResponse(BaseModel):
    run_id: str
    status: RunStatus


# New models for the refactor
class PricingConfig(BaseModel):
    model_id: str
    input_per_1k: float  # AUD per 1K input tokens
    output_per_1k: float  # AUD per 1K output tokens
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LastRunItem(BaseModel):
    run_id: str
    model_id: str
    scenario: str
    fsp_enabled: bool
    overall: float | None
    aud_cost: float
    created_at: str


class StatsOverview(BaseModel):
    total_runs: int
    available_prompts: int
    total_cost_aud: float
    avg_quality_overall: float | None
    last_runs: list[LastRunItem]


class CySecBenchImportRequest(BaseModel):
    dataset_version: str
    seed: int
    counts: dict[str, int]  # {"SOC": 50, "IncidentResponse": 30, "GRC": 20}


class RunsSummary(BaseModel):
    total_runs: int
    avg_overall: float | None
    avg_cost_per_1k: float | None
    avg_risk_awareness: float | None


class SourceDocument(BaseModel):
    doc_id: str | None = Field(None, description="ULID identifier")
    filename: str
    source_type: DocumentSourceType
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SourceDocumentCreate(BaseModel):
    filename: str
    source_type: DocumentSourceType
    content: str


class SourceDocumentList(BaseModel):
    doc_id: str
    filename: str
    source_type: DocumentSourceType
    created_at: datetime
