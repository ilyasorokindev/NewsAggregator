from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from news_aggregator.infrastructure.config.settings import Settings, get_settings
from news_aggregator.infrastructure.database.session_manager import DatabaseSessionManager

_session_manager: DatabaseSessionManager | None = None


def create_engine(settings: Settings) -> AsyncEngine:
    """Create an async SQLAlchemy engine."""
    return create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the given engine."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


def init_session_manager(settings: Settings | None = None) -> DatabaseSessionManager:
    """Initialize the global database session manager."""
    global _session_manager
    _session_manager = DatabaseSessionManager(settings or get_settings())
    return _session_manager


def get_session_manager() -> DatabaseSessionManager:
    """Return the initialized database session manager."""
    if _session_manager is None:
        return init_session_manager()
    return _session_manager


async def dispose_session_manager() -> None:
    """Dispose of the global database session manager."""
    global _session_manager
    if _session_manager is not None:
        await _session_manager.dispose()
        _session_manager = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for dependency injection."""
    manager = get_session_manager()
    async with manager.session() as session:
        yield session
