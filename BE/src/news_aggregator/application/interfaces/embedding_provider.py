from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Contract for generating vector embeddings from text."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text."""
        raise NotImplementedError

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for multiple texts."""
        raise NotImplementedError
