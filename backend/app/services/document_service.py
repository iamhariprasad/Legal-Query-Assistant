"""Document indexing service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag.chunker import LegalChunker
from app.ai.rag.vector_store import ChromaVectorStore
from app.integrations.indian_kanoon import IndianKanoonClient
from app.models.document import Document, EmbeddingMetadata
from app.repositories.document_repository import DocumentRepository, EmbeddingRepository
from app.schemas.search import DocumentRead, IndexDocumentResponse


class DocumentService:
    """Fetch, persist, and index Indian Kanoon documents."""

    def __init__(
        self,
        session: AsyncSession,
        indian_kanoon: IndianKanoonClient,
        chunker: LegalChunker,
        vector_store: ChromaVectorStore,
    ) -> None:
        self.documents = DocumentRepository(session)
        self.embeddings = EmbeddingRepository(session)
        self.indian_kanoon = indian_kanoon
        self.chunker = chunker
        self.vector_store = vector_store

    async def fetch(self, external_id: str) -> DocumentRead:
        """Fetch a document from storage or Indian Kanoon."""
        existing = await self.documents.get_by_external_id(external_id)
        if existing:
            return DocumentRead(
                id=existing.id,
                external_id=existing.external_id,
                title=existing.title,
                source=existing.source,
                url=existing.url,
                content=existing.content,
                metadata=existing.metadata_json,
            )
        legal_doc = await self.indian_kanoon.fetch_document(external_id)
        document = await self.documents.add(
            Document(
                external_id=legal_doc.document_id,
                title=legal_doc.title,
                source=legal_doc.source,
                url=legal_doc.url,
                content=legal_doc.content,
                metadata_json=legal_doc.metadata,
            )
        )
        return DocumentRead(
            id=document.id,
            external_id=document.external_id,
            title=document.title,
            source=document.source,
            url=document.url,
            content=document.content,
            metadata=document.metadata_json,
        )

    async def index(self, external_id: str) -> IndexDocumentResponse:
        """Fetch a document, chunk it, and upsert vectors."""
        document_read = await self.fetch(external_id)
        legal_doc = await self.indian_kanoon.fetch_document(external_id)
        chunks = self.chunker.chunk(legal_doc)
        self.vector_store.upsert_chunks(chunks)
        document = await self.documents.get_by_external_id(external_id)
        if document:
            existing = await self.embeddings.list_for_document(document.id)
            existing_keys = {item.chunk_index for item in existing}
            for chunk in chunks:
                index = int(chunk.metadata.get("chunk_index", 0))
                if index in existing_keys:
                    continue
                await self.embeddings.add(
                    EmbeddingMetadata(
                        document_id=document.id,
                        chunk_index=index,
                        vector_id=chunk.id,
                        chunk_text=chunk.text,
                        citation=chunk.citation,
                        metadata_json=chunk.metadata,
                    )
                )
        return IndexDocumentResponse(document_id=document_read.external_id, chunks_indexed=len(chunks))

