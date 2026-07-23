"""Document persistence operations."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, EmbeddingMetadata
from app.repositories.base import Repository


class DocumentRepository(Repository[Document]):
    """Repository for legal documents."""

    model = Document

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_external_id(self, external_id: str) -> Document | None:
        """Fetch a document using its Indian Kanoon ID."""
        result = await self.session.execute(select(Document).where(Document.external_id == external_id))
        return result.scalar_one_or_none()


class EmbeddingRepository(Repository[EmbeddingMetadata]):
    """Repository for chunk metadata."""

    model = EmbeddingMetadata

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_for_document(self, document_id: str) -> Sequence[EmbeddingMetadata]:
        """Return indexed chunks for a document."""
        result = await self.session.execute(
            select(EmbeddingMetadata)
            .where(EmbeddingMetadata.document_id == document_id)
            .order_by(EmbeddingMetadata.chunk_index)
        )
        return result.scalars().all()

