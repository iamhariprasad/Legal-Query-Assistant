"""Audit, metric, search, and evaluation persistence."""

from collections.abc import Sequence

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import GuardrailLog, Metric
from app.models.evaluation import EvaluationResult
from app.models.search import SearchLog
from app.repositories.base import Repository


class SearchLogRepository(Repository[SearchLog]):
    """Repository for search logs."""

    model = SearchLog


class MetricRepository(Repository[Metric]):
    """Repository for operational metrics."""

    model = Metric

    async def latest(self, limit: int = 100) -> Sequence[Metric]:
        """Return recent metrics."""
        result = await self.session.execute(select(Metric).order_by(desc(Metric.created_at)).limit(limit))
        return result.scalars().all()


class GuardrailLogRepository(Repository[GuardrailLog]):
    """Repository for guardrail logs."""

    model = GuardrailLog

    async def latest(self, limit: int = 100) -> Sequence[GuardrailLog]:
        """Return recent guardrail logs."""
        result = await self.session.execute(
            select(GuardrailLog).order_by(desc(GuardrailLog.created_at)).limit(limit)
        )
        return result.scalars().all()


class EvaluationRepository(Repository[EvaluationResult]):
    """Repository for evaluation results."""

    model = EvaluationResult

    async def latest(self, limit: int = 100) -> Sequence[EvaluationResult]:
        """Return recent evaluation rows."""
        result = await self.session.execute(
            select(EvaluationResult).order_by(desc(EvaluationResult.created_at)).limit(limit)
        )
        return result.scalars().all()

