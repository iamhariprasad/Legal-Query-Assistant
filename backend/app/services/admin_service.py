"""Admin dashboard service — computes metrics from real database tables."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis
from app.models.audit import GuardrailLog
from app.models.chat import ChatHistory, Feedback
from app.models.search import SearchLog
from app.repositories.audit_repository import GuardrailLogRepository
from app.repositories.chat_repository import FeedbackRepository
from app.schemas.admin import FeedbackCreate, MetricRead


class AdminService:
    """Metrics, feedback, and guardrail read models."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.feedback = FeedbackRepository(session)
        self.guardrails = GuardrailLogRepository(session)

    async def add_feedback(self, user_id: str, payload: FeedbackCreate) -> Feedback:
        """Persist human feedback."""
        return await self.feedback.add(
            Feedback(user_id=user_id, chat_id=payload.chat_id, rating=payload.rating, comment=payload.comment)
        )

    async def latest_metrics(self) -> list[MetricRead]:
        """Compute operational metrics from real database tables + Redis."""
        now = datetime.now(timezone.utc)

        # --- Aggregate from chat_history ---
        chat_count = await self._scalar(select(func.count(ChatHistory.id)))
        refused_count = await self._scalar(
            select(func.count(ChatHistory.id)).where(ChatHistory.refused.is_(True))
        )
        avg_confidence = await self._scalar(select(func.avg(ChatHistory.confidence))) or 0.0
        avg_latency = await self._scalar(select(func.avg(ChatHistory.latency_ms))) or 0.0

        # --- Aggregate from search_logs ---
        search_log_count = await self._scalar(select(func.count(SearchLog.id)))
        cache_hits = await self._scalar(
            select(func.count(SearchLog.id)).where(SearchLog.cache_hit.is_(True))
        )
        cache_misses = await self._scalar(
            select(func.count(SearchLog.id)).where(SearchLog.cache_hit.is_(False))
        )

        # --- Aggregate from guardrail_logs ---
        guardrail_count = await self._scalar(select(func.count(GuardrailLog.id)))

        # --- Redis cache info ---
        redis_keys = 0
        try:
            redis_conn = get_redis()
            redis_keys = len(await redis_conn.keys("ik:*"))
        except Exception:
            pass

        # --- Build metric rows ---
        metrics = [
            MetricRead(name="total_chats", value=float(chat_count), labels={}, created_at=now),
            MetricRead(name="total_refusals", value=float(refused_count), labels={}, created_at=now),
            MetricRead(name="avg_confidence", value=float(avg_confidence), labels={}, created_at=now),
            MetricRead(name="avg_latency_ms", value=float(avg_latency), labels={}, created_at=now),
            MetricRead(name="cache_hits", value=float(cache_hits), labels={}, created_at=now),
            MetricRead(name="cache_misses", value=float(cache_misses), labels={}, created_at=now),
            MetricRead(name="total_search_logs", value=float(search_log_count), labels={}, created_at=now),
            MetricRead(name="total_guardrails", value=float(guardrail_count), labels={}, created_at=now),
            MetricRead(name="redis_cached_keys", value=float(redis_keys), labels={}, created_at=now),
        ]
        return metrics

    async def latest_guardrails(self):
        """Return recent guardrail events."""
        return await self.guardrails.latest()

    async def _scalar(self, stmt):
        """Execute a scalar query and return the result."""
        result = await self.session.execute(stmt)
        return result.scalar()
