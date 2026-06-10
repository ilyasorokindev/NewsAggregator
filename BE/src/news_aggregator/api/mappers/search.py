from news_aggregator.api.schemas.search import SearchResultSchema
from news_aggregator.domain.entities.news_chunk import SearchResult


def to_search_result_schema(result: SearchResult) -> SearchResultSchema:
    """Map a domain search result to an API response schema."""
    return SearchResultSchema(guid=result.guid, text=result.text)


def to_search_result_schemas(results: list[SearchResult]) -> list[SearchResultSchema]:
    """Map domain search results to API response schemas."""
    return [to_search_result_schema(result) for result in results]
