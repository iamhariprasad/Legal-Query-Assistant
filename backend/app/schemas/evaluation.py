"""Evaluation schemas."""

from pydantic import BaseModel, Field


class EvaluationRunRequest(BaseModel):
    """Request to run the benchmark evaluation."""

    limit: int | None = Field(default=None, ge=1, le=100)


class EvaluationResultRead(BaseModel):
    """Evaluation result returned to dashboards."""

    id: str
    query: str
    expected_issue: str
    expected_citations: list[str]
    answer: str
    refused: bool
    citation_accuracy: float
    precision: float
    recall: float
    faithfulness: float
    hallucination_rate: float
    context_recall: float
    latency_ms: int

    model_config = {"from_attributes": True}


class EvaluationSummary(BaseModel):
    """Aggregated evaluation metrics."""

    total: int
    citation_accuracy: float
    precision: float
    recall: float
    faithfulness: float
    hallucination_rate: float
    context_recall: float
    avg_latency_ms: float

class EvaluationResultsResponse(BaseModel):
    """Dashboard-ready evaluation payload."""

    summary: EvaluationSummary
    results: list[EvaluationResultRead]

