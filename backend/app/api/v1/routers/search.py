"""Legal search endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user, indian_kanoon_dep
from app.db.session import get_db_session
from app.integrations.indian_kanoon import IndianKanoonClient
from app.models.user import User
from app.schemas.search import LegalSearchRequest, LegalSearchResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/legal", response_model=LegalSearchResponse)
async def legal_search(
    payload: LegalSearchRequest,
    _: User = Depends(current_user),
    session: AsyncSession = Depends(get_db_session),
    indian_kanoon: IndianKanoonClient = Depends(indian_kanoon_dep),
) -> LegalSearchResponse:
    """Search Indian Kanoon legal documents."""
    return await SearchService(session, indian_kanoon).search(payload)

