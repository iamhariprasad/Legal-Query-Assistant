"""Shared API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Structured API error response."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Service health response."""

    status: str
    version: str
    dependencies: dict[str, str]


class TimestampedResponse(BaseModel):
    """Base response with timestamps."""

    id: str
    created_at: datetime
    updated_at: datetime

