"""Admin endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import admin_user, current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.admin import FeedbackCreate, FeedbackRead, GuardrailLogRead, MetricRead
from app.services.admin_service import AdminService

router = APIRouter()


@router.post("/feedback", response_model=FeedbackRead)
async def feedback(
    payload: FeedbackCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
) -> object:
    """Record user feedback."""
    return await AdminService(session).add_feedback(user.id, payload)


@router.get("/metrics", response_model=list[MetricRead])
async def metrics(
    _: User = Depends(admin_user),
    session: AsyncSession = Depends(get_db_session),
) -> list:
    """Return recent operational metrics."""
    return list(await AdminService(session).latest_metrics())


@router.get("/guardrails", response_model=list[GuardrailLogRead])
async def guardrails(
    _: User = Depends(admin_user),
    session: AsyncSession = Depends(get_db_session),
) -> list:
    """Return recent guardrail logs."""
    return list(await AdminService(session).latest_guardrails())

