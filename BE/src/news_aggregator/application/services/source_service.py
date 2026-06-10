import logging
from uuid import UUID

from news_aggregator.domain.entities.source import Source
from news_aggregator.domain.exceptions.source import DuplicateSourceError, SourceNotFoundError
from news_aggregator.domain.repositories.source_repository import SourceRepository
from news_aggregator.domain.validation.source_url import validate_source_url

logger = logging.getLogger(__name__)


class SourceService:
    """Application service for news source management."""

    def __init__(self, source_repository: SourceRepository) -> None:
        self._source_repository = source_repository

    async def list_sources(self) -> list[Source]:
        """Return all configured sources."""
        return await self._source_repository.list_all()

    async def create_source(self, url: str) -> Source:
        """Create a new news source."""
        normalized_url = validate_source_url(url)
        logger.info("Creating source", extra={"url": normalized_url})

        existing = await self._source_repository.get_by_url(normalized_url)
        if existing is not None:
            raise DuplicateSourceError(f"Source URL already exists: {normalized_url}")

        return await self._source_repository.create(normalized_url)

    async def update_source(self, guid: UUID, url: str) -> Source:
        """Update an existing news source."""
        normalized_url = validate_source_url(url)
        logger.info("Updating source", extra={"guid": str(guid), "url": normalized_url})

        existing_source = await self._source_repository.get_by_guid(guid)
        if existing_source is None:
            raise SourceNotFoundError(f"Source not found: {guid}")

        duplicate = await self._source_repository.get_by_url(normalized_url)
        if duplicate is not None and duplicate.guid != guid:
            raise DuplicateSourceError(f"Source URL already exists: {normalized_url}")

        return await self._source_repository.update(guid, normalized_url)

    async def delete_source(self, guid: UUID) -> None:
        """Delete a news source."""
        logger.info("Deleting source", extra={"guid": str(guid)})

        existing_source = await self._source_repository.get_by_guid(guid)
        if existing_source is None:
            raise SourceNotFoundError(f"Source not found: {guid}")

        await self._source_repository.delete(guid)
