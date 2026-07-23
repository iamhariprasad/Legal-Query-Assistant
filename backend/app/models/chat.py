"""Chat history and feedback ORM models."""

from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class ChatHistory(IdMixin, TimestampMixin, Base):
    """Persisted legal query, generated answer, citations, and safety outcome."""

    __tablename__ = "chat_history"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    citations: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    refused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    refusal_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="chat_history")
    feedback = relationship("Feedback", back_populates="chat", cascade="all, delete-orphan")


class Feedback(IdMixin, TimestampMixin, Base):
    """Human feedback for a chat response."""

    __tablename__ = "feedback"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    chat_id: Mapped[str] = mapped_column(ForeignKey("chat_history.id"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="feedback")
    chat = relationship("ChatHistory", back_populates="feedback")

