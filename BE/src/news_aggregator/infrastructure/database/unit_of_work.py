from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from news_aggregator.domain.repositories.news_chunk_repository import NewsChunkRepository
from news_aggregator.domain.repositories.source_repository import SourceRepository
from news_aggregator.domain.repositories.unit_of_work import UnitOfWork
from news_aggregator.infrastructure.repositories.sqlalchemy_news_chunk_repository import (
    SqlAlchemyNewsChunkRepository,
)
from news_aggregator.infrastructure.repositories.sqlalchemy_source_repository import (
    SqlAlchemySourceRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of UnitOfWork."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._sources: SqlAlchemySourceRepository | None = None
        self._news_chunks: SqlAlchemyNewsChunkRepository | None = None

    @property
    def sources(self) -> SourceRepository:
        """Return the source repository for the active session."""
        if self._session is None or self._sources is None:
            msg = "Unit of work has not been started"
            raise RuntimeError(msg)
        return self._sources

    @property
    def news_chunks(self) -> NewsChunkRepository:
        """Return the news chunk repository for the active session."""
        if self._session is None or self._news_chunks is None:
            msg = "Unit of work has not been started"
            raise RuntimeError(msg)
        return self._news_chunks

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._session is None:
            msg = "Unit of work has not been started"
            raise RuntimeError(msg)
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction."""
        if self._session is None:
            msg = "Unit of work has not been started"
            raise RuntimeError(msg)
        await self._session.rollback()

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._sources = SqlAlchemySourceRepository(self._session)
        self._news_chunks = SqlAlchemyNewsChunkRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return

        try:
            if exc_type is not None:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self._session.close()
            self._session = None
            self._sources = None
            self._news_chunks = None
