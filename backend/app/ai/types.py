"""Typed AI pipeline objects."""

from dataclasses import dataclass, field
from typing import Any, TypedDict


REFUSAL_MESSAGE = (
    "I could not find sufficient citation-grounded legal evidence to answer reliably. "
    "Please consult a qualified lawyer."
)


@dataclass(slots=True)
class LegalDocument:
    """Normalized legal document."""

    document_id: str
    title: str
    source: str
    url: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LegalChunk:
    """Text chunk with citation metadata."""

    id: str
    document_id: str
    title: str
    source: str
    url: str
    text: str
    citation: str
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class GuardrailResult:
    """Guardrail decision."""

    allowed: bool
    trigger: str | None = None
    reason: str | None = None
    severity: str = "medium"


class GraphState(TypedDict, total=False):
    """LangGraph state exchanged between nodes."""

    user_id: str
    query: str
    search_results: list[dict[str, Any]]
    documents: list[LegalDocument]
    chunks: list[LegalChunk]
    ranked_chunks: list[LegalChunk]
    prompt: str
    answer: str
    confidence: float
    citations: list[dict[str, Any]]
    guardrail: GuardrailResult
    refused: bool
    refusal_reason: str | None
    latency_ms: int
    metadata: dict[str, Any]

