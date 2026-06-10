from uuid import UUID

from news_aggregator.domain.entities.news_chunk import NewsChunk, SearchResult
from news_aggregator.domain.entities.source import Source
from news_aggregator.infrastructure.database.models.news_chunk import NewsChunkModel
from news_aggregator.infrastructure.database.models.source import SourceModel


def source_to_entity(model: SourceModel) -> Source:
    """Map a Source ORM model to a domain entity."""
    return Source(
        guid=model.guid,
        url=model.url,
        created_at=model.created_at,
    )


def news_chunk_to_entity(model: NewsChunkModel) -> NewsChunk:
    """Map a NewsChunk ORM model to a domain entity."""
    return NewsChunk(
        guid=model.guid,
        source_guid=model.source_guid,
        text=model.text,
        created_at=model.created_at,
    )


def search_result_from_row(guid: UUID, text: str) -> SearchResult:
    """Map a database row to a search result domain entity."""
    return SearchResult(guid=guid, text=text)


def search_results_from_rows(rows: list[tuple[UUID, str]]) -> list[SearchResult]:
    """Map database rows to search result domain entities."""
    return [search_result_from_row(guid, text) for guid, text in rows]
