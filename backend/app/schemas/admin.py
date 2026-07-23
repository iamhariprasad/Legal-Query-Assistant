"""Administrative schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    """Feedback submission payload."""

    chat_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackRead(BaseModel):
    """Feedback response."""

    id: str
    chat_id: str
    rating: int
    comment: str | None

    model_config = {"from_attributes": True}


class MetricRead(BaseModel):
    """Operational metric."""

    name: str
    value: float
    labels: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class GuardrailLogRead(BaseModel):
    """Guardrail audit log."""

    id: str
    chat_id: str | None
    query: str
    trigger: str
    reason: str
    severity: str
    metadata_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}

