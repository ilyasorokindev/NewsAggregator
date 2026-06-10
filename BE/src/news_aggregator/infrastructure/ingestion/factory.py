import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from news_aggregator.application.interfaces.embedding_provider import EmbeddingProvider
from news_aggregator.application.interfaces.ingestion_pipeline import IngestionPipeline
from news_aggregator.infrastructure.config.settings import Settings
from news_aggregator.infrastructure.ingestion.content_extractor import BeautifulSoupContentExtractor
from news_aggregator.infrastructure.ingestion.feed_discovery import HtmlFeedDiscovery
from news_aggregator.infrastructure.ingestion.feed_parser import FeedparserFeedParser
from news_aggregator.infrastructure.ingestion.ingestion_pipeline import DefaultIngestionPipeline
from news_aggregator.infrastructure.ingestion.text_chunker import ConfigurableTextChunker
from news_aggregator.infrastructure.repositories.sqlalchemy_news_chunk_repository import (
    SqlAlchemyNewsChunkRepository,
)
from news_aggregator.infrastructure.repositories.sqlalchemy_source_repository import (
    SqlAlchemySourceRepository,
)

DEFAULT_HTTP_TIMEOUT_SECONDS = 30.0
USER_AGENT = "NewsAggregator/0.1.0"


def create_ingestion_pipeline(
    session: AsyncSession,
    settings: Settings,
    embedding_provider: EmbeddingProvider,
) -> IngestionPipeline:
    """Build an ingestion pipeline bound to the given database session."""
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(DEFAULT_HTTP_TIMEOUT_SECONDS),
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    )
    feed_parser = FeedparserFeedParser()

    return DefaultIngestionPipeline(
        source_repository=SqlAlchemySourceRepository(session),
        news_chunk_repository=SqlAlchemyNewsChunkRepository(session),
        feed_discovery=HtmlFeedDiscovery(http_client=http_client, feed_parser=feed_parser),
        feed_parser=feed_parser,
        content_extractor=BeautifulSoupContentExtractor(http_client=http_client),
        text_chunker=ConfigurableTextChunker(settings),
        embedding_provider=embedding_provider,
        http_client=http_client,
    )
