"""Chat and citation schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation used to ground a response."""

    document_id: str
    title: str
    source: str
    url: str
    snippet: str
    score: float = 0.0


class ChatRequest(BaseModel):
    """Legal query request."""

    query: str = Field(min_length=3, max_length=2000)


class ChatResponse(BaseModel):
    """Citation-grounded answer response."""

    id: str | None = None
    answer: str
    confidence: float
    citations: list[Citation]
    refused: bool
    refusal_reason: str | None = None
    latency_ms: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatHistoryItem(BaseModel):
    """Persisted chat history item."""

    id: str
    query: str
    answer: str
    confidence: float
    citations: list[Citation]
    refused: bool
    refusal_reason: str | None
    latency_ms: int
    created_at: datetime

    model_config = {"from_attributes": True}

class StreamChunk(BaseModel):
    """Server-sent event chunk payload."""

    event: str
    data: dict[str, Any]

