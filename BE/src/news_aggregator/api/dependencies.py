from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from news_aggregator.application.interfaces.embedding_provider import EmbeddingProvider
from news_aggregator.application.interfaces.ingestion_pipeline import IngestionPipeline
from news_aggregator.application.services.ingestion_service import IngestionService
from news_aggregator.application.services.search_service import SearchService
from news_aggregator.application.services.source_service import SourceService
from news_aggregator.domain.repositories.news_chunk_repository import NewsChunkRepository
from news_aggregator.domain.repositories.source_repository import SourceRepository
from news_aggregator.domain.repositories.vector_search_repository import VectorSearchRepository
from news_aggregator.infrastructure.config.settings import Settings, get_settings
from news_aggregator.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from news_aggregator.infrastructure.ingestion.factory import create_ingestion_pipeline
from news_aggregator.infrastructure.repositories.pgvector_search_repository import (
    PgVectorSearchRepository,
)
from news_aggregator.infrastructure.repositories.sqlalchemy_news_chunk_repository import (
    SqlAlchemyNewsChunkRepository,
)
from news_aggregator.infrastructure.repositories.sqlalchemy_source_repository import (
    SqlAlchemySourceRepository,
)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped database session bound to the application engine."""
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_session(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AsyncSession:
    """Provide a database session."""
    return session


def get_app_settings() -> Settings:
    """Provide application settings."""
    return get_settings()


def get_embedding_provider(request: Request) -> EmbeddingProvider:
    """Provide the shared embedding provider from application state."""
    return request.app.state.embedding_provider


def get_source_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SourceRepository:
    """Provide the source repository implementation."""
    return SqlAlchemySourceRepository(session)


def get_news_chunk_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> NewsChunkRepository:
    """Provide the news chunk repository implementation."""
    return SqlAlchemyNewsChunkRepository(session)


def get_vector_search_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VectorSearchRepository:
    """Provide the vector search repository implementation."""
    return PgVectorSearchRepository(session)


def get_ingestion_pipeline(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_app_settings)],
    embedding_provider: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
) -> IngestionPipeline:
    """Provide the ingestion pipeline implementation."""
    return create_ingestion_pipeline(
        session=session,
        settings=settings,
        embedding_provider=embedding_provider,
    )


def get_search_service(
    embedding_provider: Annotated[EmbeddingProvider, Depends(get_embedding_provider)],
    vector_search_repository: Annotated[
        VectorSearchRepository, Depends(get_vector_search_repository)
    ],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> SearchService:
    """Provide the search application service."""
    return SearchService(
        embedding_provider=embedding_provider,
        vector_search_repository=vector_search_repository,
        max_results=settings.search_max_results,
        similarity_threshold=settings.search_similarity_threshold,
    )


def get_source_service(
    source_repository: Annotated[SourceRepository, Depends(get_source_repository)],
) -> SourceService:
    """Provide the source management application service."""
    return SourceService(source_repository)


def get_ingestion_service(
    ingestion_pipeline: Annotated[IngestionPipeline, Depends(get_ingestion_pipeline)],
) -> IngestionService:
    """Provide the ingestion application service."""
    return IngestionService(ingestion_pipeline)
