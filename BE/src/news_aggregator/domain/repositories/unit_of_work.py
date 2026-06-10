from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from news_aggregator.domain.repositories.news_chunk_repository import NewsChunkRepository
from news_aggregator.domain.repositories.source_repository import SourceRepository


class UnitOfWork(ABC):
    """Contract for coordinating repository access within a transaction."""

    @property
    @abstractmethod
    def sources(self) -> SourceRepository:
        """Return the source repository bound to the current unit of work."""
        raise NotImplementedError

    @property
    @abstractmethod
    def news_chunks(self) -> NewsChunkRepository:
        """Return the news chunk repository bound to the current unit of work."""
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Roll back the current transaction."""
        raise NotImplementedError

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
