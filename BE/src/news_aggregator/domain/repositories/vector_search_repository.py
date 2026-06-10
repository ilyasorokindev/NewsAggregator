from abc import ABC, abstractmethod

from news_aggregator.domain.entities.news_chunk import SearchResult


class VectorSearchRepository(ABC):
    """Contract for semantic vector similarity search."""

    @abstractmethod
    async def search(
        self,
        query_embedding: list[float],
        limit: int,
        similarity_threshold: float,
    ) -> list[SearchResult]:
        """Return chunks ordered by relevance to the query embedding."""
        raise NotImplementedError
