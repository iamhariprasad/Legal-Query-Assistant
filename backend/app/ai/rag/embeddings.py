"""Sentence Transformer embedding provider."""

import logging

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Lazy Sentence Transformers wrapper."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        """Load the embedding model on first use."""
        if self._model is None:
            logger.info("Loading embedding model %s", self.model_name, extra={"request_id": "-"})
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts as Python lists for vector stores."""
        if not texts:
            return []
        vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        array = np.asarray(vectors, dtype=float)
        return array.tolist()

