from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from news_aggregator.domain.entities.source import Source
from news_aggregator.domain.exceptions.source import DuplicateSourceError, SourceNotFoundError
from news_aggregator.domain.repositories.source_repository import SourceRepository
from news_aggregator.infrastructure.database.mappers import source_to_entity
from news_aggregator.infrastructure.database.models.source import SourceModel


class SqlAlchemySourceRepository(SourceRepository):
    """PostgreSQL implementation of SourceRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[Source]:
        stmt = select(SourceModel).order_by(SourceModel.created_at)
        result = await self._session.scalars(stmt)
        return [source_to_entity(model) for model in result.all()]

    async def get_by_guid(self, guid: UUID) -> Source | None:
        stmt = select(SourceModel).where(SourceModel.guid == guid)
        model = await self._session.scalar(stmt)
        if model is None:
            return None
        return source_to_entity(model)

    async def get_by_url(self, url: str) -> Source | None:
        stmt = select(SourceModel).where(SourceModel.url == url)
        model = await self._session.scalar(stmt)
        if model is None:
            return None
        return source_to_entity(model)

    async def create(self, url: str) -> Source:
        model = SourceModel(url=url)
        self._session.add(model)
        try:
            await self._session.flush()
            await self._session.refresh(model)
        except IntegrityError as exc:
            raise DuplicateSourceError(f"Source URL already exists: {url}") from exc
        return source_to_entity(model)

    async def update(self, guid: UUID, url: str) -> Source:
        stmt = select(SourceModel).where(SourceModel.guid == guid)
        model = await self._session.scalar(stmt)
        if model is None:
            raise SourceNotFoundError(f"Source not found: {guid}")

        model.url = url
        try:
            await self._session.flush()
            await self._session.refresh(model)
        except IntegrityError as exc:
            raise DuplicateSourceError(f"Source URL already exists: {url}") from exc
        return source_to_entity(model)

    async def delete(self, guid: UUID) -> None:
        stmt = select(SourceModel).where(SourceModel.guid == guid)
        model = await self._session.scalar(stmt)
        if model is None:
            raise SourceNotFoundError(f"Source not found: {guid}")

        await self._session.delete(model)
        await self._session.flush()
