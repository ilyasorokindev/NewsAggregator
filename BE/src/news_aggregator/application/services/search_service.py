import logging

from news_aggregator.application.interfaces.embedding_provider import EmbeddingProvider
from news_aggregator.domain.entities.news_chunk import SearchResult
from news_aggregator.domain.exceptions.search import SearchError
from news_aggregator.domain.repositories.vector_search_repository import VectorSearchRepository

logger = logging.getLogger(__name__)


class SearchService:
    """Application service orchestrating semantic news search."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_search_repository: VectorSearchRepository,
        max_results: int,
        similarity_threshold: float,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_search_repository = vector_search_repository
        self._max_results = max_results
        self._similarity_threshold = similarity_threshold

    async def search(self, query: str) -> list[SearchResult]:
        """Execute semantic search for the given query."""
        normalized_query = query.strip()
        if not normalized_query:
            raise SearchError("Search query must not be empty")

        logger.info("Search request received", extra={"query_length": len(normalized_query)})

        try:
            query_embedding = await self._embedding_provider.embed(normalized_query)
            results = await self._vector_search_repository.search(
                query_embedding=query_embedding,
                limit=self._max_results,
                similarity_threshold=self._similarity_threshold,
            )
        except SearchError:
            raise
        except Exception as exc:
            raise SearchError("Search operation failed") from exc

        logger.info(
            "Search completed",
            extra={
                "query_length": len(normalized_query),
                "result_count": len(results),
            },
        )
        return results
