from abc import ABC, abstractmethod
from uuid import UUID

from news_aggregator.domain.entities.source import Source


class SourceRepository(ABC):
    """Contract for persisting and retrieving news sources."""

    @abstractmethod
    async def list_all(self) -> list[Source]:
        """Return all configured sources."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_guid(self, guid: UUID) -> Source | None:
        """Return a source by its identifier."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_url(self, url: str) -> Source | None:
        """Return a source by its URL."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, url: str) -> Source:
        """Create a new source."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, guid: UUID, url: str) -> Source:
        """Update an existing source."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, guid: UUID) -> None:
        """Delete a source by its identifier."""
        raise NotImplementedError
