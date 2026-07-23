"""Legal document and embedding metadata ORM models."""

from sqlalchemy import ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Document(IdMixin, TimestampMixin, Base):
    """Normalized legal document fetched from Indian Kanoon."""

    __tablename__ = "documents"

    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    embeddings = relationship("EmbeddingMetadata", back_populates="document", cascade="all, delete-orphan")


class EmbeddingMetadata(IdMixin, TimestampMixin, Base):
    """Chunk metadata corresponding to a vector stored in ChromaDB."""

    __tablename__ = "embeddings_metadata"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk"),)

    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    citation: Mapped[str] = mapped_column(String(500), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    document = relationship("Document", back_populates="embeddings")

