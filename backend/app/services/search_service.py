"""Search service coordinating Indian Kanoon and audit logs."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.indian_kanoon import IndianKanoonClient
from app.models.search import SearchLog
from app.repositories.audit_repository import SearchLogRepository
from app.schemas.search import LegalSearchRequest, LegalSearchResponse


class SearchService:
    """Search legal sources and log the request."""

    def __init__(self, session: AsyncSession, indian_kanoon: IndianKanoonClient) -> None:
        self.logs = SearchLogRepository(session)
        self.indian_kanoon = indian_kanoon

    async def search(self, payload: LegalSearchRequest) -> LegalSearchResponse:
        """Run a legal search and persist audit metadata."""
        response = await self.indian_kanoon.search(
            payload.query,
            pagenum=payload.pagenum,
            maxpages=payload.maxpages,
            maxcites=payload.maxcites,
        )
        await self.logs.add(
            SearchLog(
                query=payload.query,
                pagenum=payload.pagenum,
                result_count=len(response.results),
                cache_hit=response.cache_hit,
                latency_ms=response.latency_ms,
                status="ok",
            )
        )
        return response

