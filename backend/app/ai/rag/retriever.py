"""Hybrid retrieval orchestration."""

from app.ai.rag.bm25 import BM25Retriever
from app.ai.rag.vector_store import ChromaVectorStore
from app.ai.types import LegalChunk


class HybridRetriever:
    """Combine dense Chroma retrieval with BM25 sparse retrieval."""

    def __init__(self, vector_store: ChromaVectorStore, bm25: BM25Retriever) -> None:
        self.vector_store = vector_store
        self.bm25 = bm25

    def retrieve(self, query: str, candidate_chunks: list[LegalChunk], limit: int = 12) -> list[LegalChunk]:
        """Return de-duplicated dense and sparse results."""
        dense = self.vector_store.search(query, limit=limit)
        sparse = self.bm25.retrieve(query, candidate_chunks, limit=limit)
        merged: dict[str, LegalChunk] = {}
        for chunk in dense + sparse:
            existing = merged.get(chunk.id)
            if existing is None or chunk.score > existing.score:
                merged[chunk.id] = chunk
        return sorted(merged.values(), key=lambda item: item.score, reverse=True)[:limit]

