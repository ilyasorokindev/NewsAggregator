import logging
from uuid import UUID

import httpx

from news_aggregator.application.interfaces.content_extractor import ContentExtractor
from news_aggregator.application.interfaces.embedding_provider import EmbeddingProvider
from news_aggregator.application.interfaces.feed_discovery import FeedDiscovery
from news_aggregator.application.interfaces.feed_parser import FeedEntry, FeedParser
from news_aggregator.application.interfaces.ingestion_pipeline import IngestionPipeline
from news_aggregator.application.interfaces.text_chunker import TextChunker
from news_aggregator.domain.repositories.news_chunk_repository import NewsChunkRepository
from news_aggregator.domain.repositories.source_repository import SourceRepository
from news_aggregator.infrastructure.database.text_hash import compute_text_hash

logger = logging.getLogger(__name__)


class DefaultIngestionPipeline(IngestionPipeline):
    """Default end-to-end ingestion pipeline implementation."""

    def __init__(
        self,
        source_repository: SourceRepository,
        news_chunk_repository: NewsChunkRepository,
        feed_discovery: FeedDiscovery,
        feed_parser: FeedParser,
        content_extractor: ContentExtractor,
        text_chunker: TextChunker,
        embedding_provider: EmbeddingProvider,
        http_client: httpx.AsyncClient,
    ) -> None:
        self._source_repository = source_repository
        self._news_chunk_repository = news_chunk_repository
        self._feed_discovery = feed_discovery
        self._feed_parser = feed_parser
        self._content_extractor = content_extractor
        self._text_chunker = text_chunker
        self._embedding_provider = embedding_provider
        self._http_client = http_client

    async def close(self) -> None:
        """Close resources owned by the pipeline."""
        await self._http_client.aclose()

    async def ingest_source(self, source_guid: UUID, feed_url: str) -> None:
        """Ingest all articles from a single configured source."""
        logger.info(
            "Ingesting source",
            extra={"source_guid": str(source_guid), "feed_url": feed_url},
        )

        try:
            discovered_feed_url = await self._feed_discovery.discover_feed_url(feed_url)
            entries = await self._feed_parser.parse(discovered_feed_url)
        except Exception:
            logger.exception(
                "Failed to discover or parse feed",
                extra={"source_guid": str(source_guid), "feed_url": feed_url},
            )
            return

        for entry in entries:
            try:
                await self._ingest_article(source_guid, entry)
            except Exception:
                logger.exception(
                    "Failed to ingest article",
                    extra={"source_guid": str(source_guid), "article_url": entry.url},
                )

    async def ingest_all_sources(self) -> None:
        """Ingest articles from all configured sources."""
        logger.info("Ingesting all configured sources")
        sources = await self._source_repository.list_all()

        for source in sources:
            try:
                await self.ingest_source(source.guid, source.url)
            except Exception:
                logger.exception(
                    "Failed to ingest source",
                    extra={"source_guid": str(source.guid), "feed_url": source.url},
                )

    async def _ingest_article(self, source_guid: UUID, entry: FeedEntry) -> None:
        article_text = await self._content_extractor.extract(entry.url)
        if not article_text.strip():
            logger.warning(
                "Skipping article with empty extracted text",
                extra={"source_guid": str(source_guid), "article_url": entry.url},
            )
            return

        chunks = self._text_chunker.chunk(article_text)
        new_chunks: list[str] = []

        for chunk in chunks:
            text_hash = compute_text_hash(chunk)
            if await self._news_chunk_repository.exists_by_text_hash(text_hash):
                logger.debug(
                    "Skipping duplicate chunk",
                    extra={"source_guid": str(source_guid), "text_hash": text_hash},
                )
                continue
            new_chunks.append(chunk)

        if not new_chunks:
            logger.info(
                "No new chunks to store for article",
                extra={"source_guid": str(source_guid), "article_url": entry.url},
            )
            return

        embeddings = await self._embedding_provider.embed_batch(new_chunks)
        if len(embeddings) != len(new_chunks):
            msg = "Embedding provider returned unexpected number of vectors"
            raise ValueError(msg)

        for chunk, embedding in zip(new_chunks, embeddings, strict=True):
            await self._news_chunk_repository.create(
                source_guid=source_guid,
                text=chunk,
                embedding=embedding,
            )

        logger.info(
            "Article ingested",
            extra={
                "source_guid": str(source_guid),
                "article_url": entry.url,
                "chunk_count": len(new_chunks),
            },
        )
