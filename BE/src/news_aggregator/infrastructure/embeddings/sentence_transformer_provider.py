import asyncio
import logging
from typing import Any

from news_aggregator.application.interfaces.embedding_provider import EmbeddingProvider
from news_aggregator.infrastructure.config.settings import Settings

logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """Sentence Transformers implementation of EmbeddingProvider."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model: Any = None

    def _load_model(self) -> Any:
        """Load the SentenceTransformer model lazily."""
        if self._model is not None:
            return self._model

        # TODO: Configure device selection, model cache directory, and batching strategy.
        from sentence_transformers import SentenceTransformer

        logger.info(
            "Loading embedding model",
            extra={"model_name": self._settings.embedding_model},
        )
        self._model = SentenceTransformer(self._settings.embedding_model)
        return self._model

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text."""
        embeddings = await self.embed_batch([text])
        return embeddings[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts."""
        if not texts:
            return []

        def _encode() -> list[list[float]]:
            model = self._load_model()
            vectors = model.encode(texts, convert_to_numpy=True)
            return [vector.tolist() for vector in vectors]

        return await asyncio.to_thread(_encode)
