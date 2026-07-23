"""Health endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheClient
from app.core.config import Settings
from app.db.session import get_db_session
from app.api.deps import cache_dep, settings_dep
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(
    session: AsyncSession = Depends(get_db_session),
    cache: CacheClient = Depends(cache_dep),
    settings: Settings = Depends(settings_dep),
) -> HealthResponse:
    """Return application health and dependency status."""
    dependencies: dict[str, str] = {}
    try:
        await session.execute(text("SELECT 1"))
        dependencies["postgres"] = "ok"
    except Exception:
        dependencies["postgres"] = "error"
    try:
        await cache.redis.ping()
        dependencies["redis"] = "ok"
    except Exception:
        dependencies["redis"] = "error"
    dependencies["ollama_model"] = settings.ollama_model
    return HealthResponse(status="ok", version="1.0.0", dependencies=dependencies)

