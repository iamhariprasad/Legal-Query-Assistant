"""Legal document chunking utilities."""

import re

from app.ai.types import LegalChunk, LegalDocument


class LegalChunker:
    """Chunk Indian legal documents using paragraph-aware boundaries."""

    def __init__(self, chunk_size: int = 1200, overlap: int = 180) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: LegalDocument) -> list[LegalChunk]:
        """Split a document into overlapping evidence chunks."""
        text = re.sub(r"\s+", " ", document.content).strip()
        if not text:
            return []
        chunks: list[LegalChunk] = []
        start = 0
        index = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if end < len(text):
                boundary = text.rfind(". ", start, end)
                if boundary > start + self.chunk_size // 2:
                    end = boundary + 1
            snippet = text[start:end].strip()
            if snippet:
                chunk_id = f"{document.document_id}:{index}"
                citation = f"{document.title} ({document.source})"
                chunks.append(
                    LegalChunk(
                        id=chunk_id,
                        document_id=document.document_id,
                        title=document.title,
                        source=document.source,
                        url=document.url,
                        text=snippet,
                        citation=citation,
                        metadata={**document.metadata, "chunk_index": index},
                    )
                )
                index += 1
            if end == len(text):
                break
            start = max(end - self.overlap, start + 1)
        return chunks

