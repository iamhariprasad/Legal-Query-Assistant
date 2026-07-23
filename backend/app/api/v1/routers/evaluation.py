"""Evaluation endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import admin_user, current_user
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.evaluation import EvaluationResultsResponse, EvaluationRunRequest
from app.services.evaluation_service import EvaluationService

router = APIRouter()


@router.get("/results", response_model=EvaluationResultsResponse)
async def results(
    _: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
) -> EvaluationResultsResponse:
    """Return evaluation dashboard data."""
    return await EvaluationService(session).latest()


@router.post("/run", response_model=EvaluationResultsResponse)
async def run_evaluation(
    payload: EvaluationRunRequest,
    _: User = Depends(admin_user),
    session: AsyncSession = Depends(get_db_session),
) -> EvaluationResultsResponse:
    """Run the benchmark evaluation seeding pipeline."""
    return await EvaluationService(session).seed_static_results(limit=payload.limit)

