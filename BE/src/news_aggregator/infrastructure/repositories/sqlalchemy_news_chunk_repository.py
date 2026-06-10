from uuid import UUID

from sqlalchemy import delete, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from news_aggregator.domain.entities.news_chunk import NewsChunk
from news_aggregator.domain.repositories.news_chunk_repository import NewsChunkRepository
from news_aggregator.infrastructure.database.mappers import news_chunk_to_entity
from news_aggregator.infrastructure.database.models.news_chunk import NewsChunkModel


class SqlAlchemyNewsChunkRepository(NewsChunkRepository):
    """PostgreSQL implementation of NewsChunkRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        source_guid: UUID,
        text: str,
        embedding: list[float],
    ) -> NewsChunk:
        model = NewsChunkModel(
            source_guid=source_guid,
            text=text,
            embedding=embedding,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return news_chunk_to_entity(model)

    async def exists_by_text_hash(self, text_hash: str) -> bool:
        text_hash_expr = func.encode(func.digest(NewsChunkModel.text, "sha256"), "hex")
        stmt = select(exists().where(text_hash_expr == text_hash))
        result = await self._session.scalar(stmt)
        return bool(result)

    async def delete_by_source_guid(self, source_guid: UUID) -> None:
        stmt = delete(NewsChunkModel).where(NewsChunkModel.source_guid == source_guid)
        await self._session.execute(stmt)
        await self._session.flush()
