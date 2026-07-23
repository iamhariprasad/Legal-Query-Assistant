"""BM25 sparse retrieval."""

import re
from dataclasses import replace

from rank_bm25 import BM25Okapi

from app.ai.types import LegalChunk


def tokenize(text: str) -> list[str]:
    """Tokenize text for sparse retrieval."""
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


class BM25Retriever:
    """In-memory BM25 retriever over candidate chunks."""

    def retrieve(self, query: str, chunks: list[LegalChunk], limit: int = 10) -> list[LegalChunk]:
        """Score chunks with BM25 and return top results."""
        if not chunks:
            return []
        corpus = [tokenize(chunk.text) for chunk in chunks]
        bm25 = BM25Okapi(corpus)
        scores = bm25.get_scores(tokenize(query))
        ranked = sorted(zip(chunks, scores, strict=False), key=lambda pair: pair[1], reverse=True)
        results: list[LegalChunk] = []
        max_score = float(max(scores)) if len(scores) else 1.0
        for chunk, score in ranked[:limit]:
            normalized = float(score) / max(max_score, 1.0)
            results.append(replace(chunk, score=max(chunk.score, normalized)))
        return results
