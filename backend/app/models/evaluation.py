"""Evaluation result ORM model."""

from sqlalchemy import Boolean, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class EvaluationResult(IdMixin, TimestampMixin, Base):
    """Stored benchmark evaluation metrics for one legal query."""

    __tablename__ = "evaluation_results"

    query: Mapped[str] = mapped_column(Text, nullable=False)
    expected_issue: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_citations: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    refused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    citation_accuracy: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    precision: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    recall: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    faithfulness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    hallucination_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    context_recall: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

