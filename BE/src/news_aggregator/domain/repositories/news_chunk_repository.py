from abc import ABC, abstractmethod
from uuid import UUID

from news_aggregator.domain.entities.news_chunk import NewsChunk


class NewsChunkRepository(ABC):
    """Contract for persisting and retrieving news chunks."""

    @abstractmethod
    async def create(
        self,
        source_guid: UUID,
        text: str,
        embedding: list[float],
    ) -> NewsChunk:
        """Persist a new news chunk with its embedding."""
        raise NotImplementedError

    @abstractmethod
    async def exists_by_text_hash(self, text_hash: str) -> bool:
        """Check whether a chunk with the given text hash already exists."""
        raise NotImplementedError

    @abstractmethod
    async def delete_by_source_guid(self, source_guid: UUID) -> None:
        """Delete all chunks associated with a source."""
        raise NotImplementedError
