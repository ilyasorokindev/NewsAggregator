from news_aggregator.api.schemas.errors import ErrorDetail, ErrorResponse
from news_aggregator.api.schemas.health import HealthResponse
from news_aggregator.api.schemas.search import SearchResultSchema
from news_aggregator.api.schemas.setup import (
    CreateSourceRequest,
    CreateSourceResponse,
    DeleteSourceRequest,
    SourceSchema,
    SuccessResponse,
    UpdateSourceRequest,
)

__all__ = [
    "CreateSourceRequest",
    "CreateSourceResponse",
    "DeleteSourceRequest",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "SearchResultSchema",
    "SourceSchema",
    "SuccessResponse",
    "UpdateSourceRequest",
]
