import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from news_aggregator.api.exception_handlers import register_exception_handlers
from news_aggregator.api.routers import health_router, search_router, setup_router
from news_aggregator.application.services.ingestion_service import IngestionService
from news_aggregator.infrastructure.config.settings import get_settings
from news_aggregator.infrastructure.database.session import create_engine, create_session_factory
from news_aggregator.infrastructure.embeddings.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from news_aggregator.infrastructure.ingestion.factory import create_ingestion_pipeline
from news_aggregator.infrastructure.ingestion.ingestion_pipeline import DefaultIngestionPipeline
from news_aggregator.infrastructure.scheduler.scheduler import SchedulerBootstrap


def configure_logging(log_level: str) -> None:
    """Configure structured application logging."""
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle."""
    settings = get_settings()
    configure_logging(settings.log_level)

    engine: AsyncEngine = create_engine(settings)
    session_factory: async_sessionmaker[AsyncSession] = create_session_factory(engine)
    embedding_provider = SentenceTransformerEmbeddingProvider(settings)

    app.state.engine = engine
    app.state.session_factory = session_factory
    app.state.embedding_provider = embedding_provider

    async def sync_all_sources_job() -> None:
        async with session_factory() as session:
            pipeline = create_ingestion_pipeline(
                session=session,
                settings=settings,
                embedding_provider=embedding_provider,
            )
            try:
                ingestion_service = IngestionService(pipeline)
                await ingestion_service.sync_all_sources()
                await session.commit()
            except Exception:
                await session.rollback()
                logging.getLogger(__name__).exception("Scheduled feed synchronization failed")
            finally:
                if isinstance(pipeline, DefaultIngestionPipeline):
                    await pipeline.close()

    scheduler = SchedulerBootstrap(settings)
    scheduler.register_sync_job(sync_all_sources_job)
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown()
        await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="News Aggregator API",
        description="Backend API for news ingestion and semantic search",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(search_router)
    app.include_router(setup_router)

    return app
