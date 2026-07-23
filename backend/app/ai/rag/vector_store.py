"""ChromaDB vector store integration."""

import chromadb

from app.ai.rag.embeddings import EmbeddingModel
from app.ai.types import LegalChunk


class ChromaVectorStore:
    """Persistent ChromaDB collection for legal evidence chunks."""

    def __init__(self, persist_dir: str, embedding_model: EmbeddingModel) -> None:
        self.embedding_model = embedding_model
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="legal_chunks",
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[LegalChunk]) -> None:
        """Insert or update chunks and their embeddings."""
        if not chunks:
            return
        embeddings = self.embedding_model.embed([chunk.text for chunk in chunks])
        self.collection.upsert(
            ids=[chunk.id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[
                {
                    "document_id": chunk.document_id,
                    "title": chunk.title,
                    "source": chunk.source,
                    "url": chunk.url,
                    "citation": chunk.citation,
                }
                for chunk in chunks
            ],
        )

    def search(self, query: str, limit: int = 10) -> list[LegalChunk]:
        """Return dense nearest-neighbor chunks."""
        query_embedding = self.embedding_model.embed([query])[0]
        result = self.collection.query(query_embeddings=[query_embedding], n_results=limit)
        chunks: list[LegalChunk] = []
        ids = result.get("ids", [[]])[0]
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for chunk_id, text, meta, distance in zip(ids, docs, metas, distances, strict=False):
            score = max(0.0, 1.0 - float(distance))
            chunks.append(
                LegalChunk(
                    id=str(chunk_id),
                    document_id=str(meta.get("document_id", "")),
                    title=str(meta.get("title", "")),
                    source=str(meta.get("source", "")),
                    url=str(meta.get("url", "")),
                    text=str(text),
                    citation=str(meta.get("citation", "")),
                    score=score,
                    metadata=dict(meta),
                )
            )
        return chunks

