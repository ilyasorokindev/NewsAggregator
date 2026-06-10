from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from news_aggregator.domain.entities.news_chunk import SearchResult
from news_aggregator.domain.repositories.vector_search_repository import VectorSearchRepository
from news_aggregator.infrastructure.database.mappers import search_result_from_row
from news_aggregator.infrastructure.database.models.news_chunk import NewsChunkModel


class PgVectorSearchRepository(VectorSearchRepository):
    """pgvector implementation of VectorSearchRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(
        self,
        query_embedding: list[float],
        limit: int,
        similarity_threshold: float,
    ) -> list[SearchResult]:
        """Return chunks ordered by cosine similarity to the query embedding."""
        distance = NewsChunkModel.embedding.cosine_distance(query_embedding)
        max_distance = 1.0 - similarity_threshold

        stmt = (
            select(NewsChunkModel.guid, NewsChunkModel.text)
            .where(distance <= max_distance)
            .order_by(distance)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [
            search_result_from_row(row.guid, row.text)
            for row in result.all()
        ]
