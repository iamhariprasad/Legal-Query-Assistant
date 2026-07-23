"""Citation extraction and verification."""

import re

from app.ai.types import LegalChunk


class CitationVerifier:
    """Verify that generated citations refer to retrieved chunks."""

    citation_pattern = re.compile(r"\[(\d+)\]")

    def extract_indices(self, answer: str) -> set[int]:
        """Extract citation indices from model output."""
        return {int(match) for match in self.citation_pattern.findall(answer)}

    def to_citations(self, chunks: list[LegalChunk]) -> list[dict]:
        """Convert chunks into API citation dictionaries."""
        return [
            {
                "document_id": chunk.document_id,
                "title": chunk.title,
                "source": chunk.source,
                "url": chunk.url,
                "snippet": chunk.text[:500],
                "score": chunk.score,
            }
            for chunk in chunks
        ]

    def verify(self, answer: str, chunks: list[LegalChunk]) -> tuple[bool, list[dict]]:
        """Return whether answer citations map to available chunks."""
        indices = self.extract_indices(answer)
        if not indices:
            return False, []
        selected = [chunks[index - 1] for index in sorted(indices) if 1 <= index <= len(chunks)]
        return len(selected) == len(indices), self.to_citations(selected)

