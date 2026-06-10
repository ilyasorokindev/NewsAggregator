from typing import Annotated

from fastapi import APIRouter, Depends, status

from news_aggregator.api.dependencies import get_source_service
from news_aggregator.api.schemas.setup import (
    CreateSourceRequest,
    CreateSourceResponse,
    DeleteSourceRequest,
    SourceSchema,
    SuccessResponse,
    UpdateSourceRequest,
)
from news_aggregator.application.services.source_service import SourceService

router = APIRouter(prefix="/setup", tags=["setup"])


@router.get(
    "/items",
    response_model=list[SourceSchema],
    status_code=status.HTTP_200_OK,
    summary="List configured news sources",
)
async def list_sources(
    service: Annotated[SourceService, Depends(get_source_service)],
) -> list[SourceSchema]:
    """List all configured news sources."""
    sources = await service.list_sources()
    return [SourceSchema(guid=source.guid, url=source.url) for source in sources]


@router.post(
    "/item",
    response_model=CreateSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a news source",
)
async def create_source(
    request: CreateSourceRequest,
    service: Annotated[SourceService, Depends(get_source_service)],
) -> CreateSourceResponse:
    """Create a new news source."""
    source = await service.create_source(str(request.url))
    return CreateSourceResponse(guid=source.guid)


@router.put(
    "/item",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a news source",
)
async def update_source(
    request: UpdateSourceRequest,
    service: Annotated[SourceService, Depends(get_source_service)],
) -> SuccessResponse:
    """Update an existing news source."""
    await service.update_source(request.guid, str(request.url))
    return SuccessResponse()


@router.delete(
    "/item",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a news source",
)
async def delete_source(
    request: DeleteSourceRequest,
    service: Annotated[SourceService, Depends(get_source_service)],
) -> SuccessResponse:
    """Delete a news source."""
    await service.delete_source(request.guid)
    return SuccessResponse()
