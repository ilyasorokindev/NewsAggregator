from abc import ABC, abstractmethod
from uuid import UUID


class IngestionPipeline(ABC):
    """Contract for the end-to-end news ingestion pipeline."""

    @abstractmethod
    async def ingest_source(self, source_guid: UUID, feed_url: str) -> None:
        """Ingest all articles from a single configured source."""
        raise NotImplementedError

    @abstractmethod
    async def ingest_all_sources(self) -> None:
        """Ingest articles from all configured sources."""
        raise NotImplementedError
