from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from news_aggregator.infrastructure.config.settings import Settings
from news_aggregator.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class DatabaseSessionManager:
    """Manages the database engine, session factory, and unit of work lifecycle."""

    def __init__(self, settings: Settings) -> None:
        self._engine: AsyncEngine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True,
        )
        self._session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        """Return the async SQLAlchemy engine."""
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Return the async session factory."""
        return self._session_factory

    def unit_of_work(self) -> SqlAlchemyUnitOfWork:
        """Create a new unit of work bound to this session manager."""
        return SqlAlchemyUnitOfWork(self._session_factory)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a database session with automatic commit or rollback."""
        async with self._session_factory() as db_session:
            try:
                yield db_session
                await db_session.commit()
            except Exception:
                await db_session.rollback()
                raise

    async def dispose(self) -> None:
        """Dispose of the database engine and connection pool."""
        await self._engine.dispose()
