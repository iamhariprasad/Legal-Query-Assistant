"""Metrics endpoint."""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from fastapi import APIRouter, Response

REQUEST_COUNTER = Counter("legal_assistant_requests_total", "Total HTTP requests", ["method", "path"])
REQUEST_LATENCY = Histogram("legal_assistant_request_latency_seconds", "HTTP request latency", ["path"])

router = APIRouter()


@router.get("/metrics")
async def metrics() -> Response:
    """Return Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

