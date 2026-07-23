"""Chunker tests."""

from app.ai.rag.chunker import LegalChunker
from app.ai.types import LegalDocument


def test_chunker_preserves_document_metadata() -> None:
    document = LegalDocument(
        document_id="42",
        title="Important Case",
        source="Supreme Court",
        url="https://indiankanoon.org/doc/42/",
        content="A sentence. " * 200,
        metadata={"court": "SC"},
    )
    chunks = LegalChunker(chunk_size=200, overlap=20).chunk(document)
    assert chunks
    assert chunks[0].document_id == "42"
    assert chunks[0].metadata["court"] == "SC"

