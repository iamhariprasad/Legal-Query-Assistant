"""Cross-encoder re-ranking."""

import logging
from dataclasses import replace

from sentence_transformers import CrossEncoder

from app.ai.types import LegalChunk

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Re-rank evidence chunks by query relevance."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: CrossEncoder | None = None

    @property
    def model(self) -> CrossEncoder:
        """Load the cross encoder on first use."""
        if self._model is None:
            logger.info("Loading reranker model %s", self.model_name, extra={"request_id": "-"})
            self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(self, query: str, chunks: list[LegalChunk], limit: int) -> list[LegalChunk]:
        """Return chunks sorted by cross-encoder score."""
        if not chunks:
            return []
        pairs = [(query, chunk.text) for chunk in chunks]
        raw_scores = self.model.predict(pairs)
        scored: list[LegalChunk] = []
        for chunk, raw_score in zip(chunks, raw_scores, strict=False):
            score = 1.0 / (1.0 + pow(2.718281828, -float(raw_score)))
            scored.append(replace(chunk, score=score))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit]
