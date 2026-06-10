from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from news_aggregator.api.dependencies import get_search_service
from news_aggregator.api.mappers.search import to_search_result_schemas
from news_aggregator.api.schemas.search import SearchResultSchema
from news_aggregator.application.services.search_service import SearchService

router = APIRouter(tags=["search"])


@router.get(
    "/search",
    response_model=list[SearchResultSchema],
    status_code=status.HTTP_200_OK,
    summary="Search news content",
)
async def search(
    service: Annotated[SearchService, Depends(get_search_service)],
    s: Annotated[str, Query(min_length=1, description="Search query")],
) -> list[SearchResultSchema]:
    """Search news content by semantic similarity."""
    results = await service.search(s)
    return to_search_result_schemas(results)
