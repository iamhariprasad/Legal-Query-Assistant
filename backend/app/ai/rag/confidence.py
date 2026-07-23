"""Confidence scoring for legal RAG answers."""

from app.ai.rag.citations import CitationVerifier
from app.ai.types import LegalChunk


class ConfidenceScorer:
    """Score confidence from retrieval strength, citation coverage, and answer quality."""

    def __init__(self, verifier: CitationVerifier) -> None:
        self.verifier = verifier

    def score(self, answer: str, chunks: list[LegalChunk]) -> float:
        """Return a bounded confidence score."""
        if not chunks or "insufficient evidence" in answer.lower():
            return 0.0
        citation_indices = self.verifier.extract_indices(answer)
        citation_ratio = 1.0 if citation_indices else 0.0
        retrieval_score = sum(chunk.score for chunk in chunks[:3]) / max(min(len(chunks), 3), 1)
        answer_score = 0.8 if len(answer.split()) >= 25 else 0.45
        confidence = (0.5 * retrieval_score) + (0.35 * citation_ratio) + (0.15 * answer_score)
        return round(max(0.0, min(confidence, 1.0)), 3)
