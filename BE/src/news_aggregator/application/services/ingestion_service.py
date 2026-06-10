import logging

from news_aggregator.application.interfaces.ingestion_pipeline import IngestionPipeline

logger = logging.getLogger(__name__)


class IngestionService:
    """Application service orchestrating background news ingestion."""

    def __init__(self, ingestion_pipeline: IngestionPipeline) -> None:
        self._ingestion_pipeline = ingestion_pipeline

    async def sync_all_sources(self) -> None:
        """Synchronize all configured sources."""
        logger.info("Starting feed synchronization")
        await self._ingestion_pipeline.ingest_all_sources()
        logger.info("Feed synchronization completed")
