"""Audit and operational metric ORM models."""

from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Metric(IdMixin, TimestampMixin, Base):
    """Operational metric sample."""

    __tablename__ = "metrics"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    labels: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class GuardrailLog(IdMixin, TimestampMixin, Base):
    """Audit log for guardrail decisions."""

    __tablename__ = "guardrail_logs"

    chat_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    trigger: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

