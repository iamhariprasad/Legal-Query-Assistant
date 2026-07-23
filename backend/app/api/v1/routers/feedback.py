"""Feedback endpoint alias."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.admin import FeedbackCreate, FeedbackRead
from app.services.admin_service import AdminService

router = APIRouter()


@router.post("", response_model=FeedbackRead)
async def feedback(
    payload: FeedbackCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
) -> object:
    """Record user feedback."""
    return await AdminService(session).add_feedback(user.id, payload)

