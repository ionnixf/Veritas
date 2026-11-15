"""Versioned HTTP response contracts; scores are never probabilities."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from auditlens.inference import DISCLAIMER


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ErrorDetail(StrictModel):
    code: str
    message: str


class ErrorResponse(StrictModel):
    error: ErrorDetail


class HealthResponse(StrictModel):
    status: Literal["ready", "unavailable"]
    model_available: bool
    model_id: str | None
    model_version: str | None
    device: Literal["cpu"] = "cpu"


class Transaction(StrictModel):
    record_id: str
    timestamp: str
    customer_id: str
    terminal_id: str
    amount: float = Field(ge=0)


class ReviewItem(Transaction):
    rank: int = Field(ge=1)
    score: float
    score_kind: Literal["uncalibrated_classifier_score"]
    reasons: list[str]
    explanation_kind: str
    warnings: list[str]
    review_required: bool
    model_version: str
    validation_status: str


class AnalyzeResponse(StrictModel):
    analyzed_count: int
    history_count: int
    top_k: int
    queue_count: int
    operations: list[ReviewItem]
    warnings: list[str]
    model_id: str
    model_version: str
    research_status: Literal["RESEARCH DEMO"] = "RESEARCH DEMO"
    score_kind: Literal["uncalibrated_classifier_score"] = "uncalibrated_classifier_score"
    processing_time_ms: float
    disclaimer: str = DISCLAIMER


class BenchmarkMetrics(StrictModel):
    n: int
    positives: int
    precision: float
    recall: float
    average_precision: float
    f1: float
    precision_at_1000: float
    positives_at_1000: float
    threshold: float


class ModelResponse(StrictModel):
    model_id: str
    name: str
    version: str
    available: bool
    research_status: str
    recommended_for_live_detection: bool
    score_kind: str
    input_schema: dict
    file_types: list[str]
    history_requirements: dict
    limits: dict
    limitations: list[str]
    benchmark: dict[str, BenchmarkMetrics]
    baselines: dict[str, BenchmarkMetrics]
    benchmark_provenance: dict
    disclaimer: str = DISCLAIMER


class DemoRequest(StrictModel):
    top_k: int = Field(default=5, gt=0, le=999999999999, strict=True)


class DemoResponse(StrictModel):
    id: str
    description: str
    provenance: str
    transactions: list[Transaction]
    history_count: int
    downloads: dict[str, str]
    analysis_url: str
    disclaimer: str = DISCLAIMER
