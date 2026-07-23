"""Typed application exceptions and HTTP error mapping."""

from dataclasses import dataclass, field
from typing import Any

from fastapi import Request
from fastapi.responses import ORJSONResponse


@dataclass(slots=True)
class AppError(Exception):
    """Base error carrying a public code and details."""

    message: str
    code: str = "legal_assistant_error"
    status_code: int = 400
    details: dict[str, Any] = field(default_factory=dict)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found", **details: Any) -> None:
        super().__init__(message=message, code="not_found", status_code=404, details=details)


class UnauthorizedError(AppError):
    """Raised when authentication is missing or invalid."""

    def __init__(self, message: str = "Authentication failed", **details: Any) -> None:
        super().__init__(message=message, code="unauthorized", status_code=401, details=details)


class ExternalServiceError(AppError):
    """Raised when a dependency such as Indian Kanoon or Ollama fails."""

    def __init__(self, message: str, **details: Any) -> None:
        super().__init__(message=message, code="external_service_error", status_code=502, details=details)


async def app_error_handler(_: Request, exc: AppError) -> ORJSONResponse:
    """Render application errors as structured JSON."""
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "details": exc.details},
    )


async def unhandled_error_handler(_: Request, exc: Exception) -> ORJSONResponse:
    """Hide internal details while returning a stable error shape."""
    return ORJSONResponse(
        status_code=500,
        content={
            "code": "internal_server_error",
            "message": "An unexpected server error occurred.",
            "details": {"type": exc.__class__.__name__},
        },
    )

