"""Search log ORM model."""

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class SearchLog(IdMixin, TimestampMixin, Base):
    """Audit record for Indian Kanoon search calls."""

    __tablename__ = "search_logs"

    query: Mapped[str] = mapped_column(Text, nullable=False)
    pagenum: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ok", nullable=False)

