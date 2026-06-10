import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from news_aggregator.api.schemas.errors import ErrorDetail, ErrorResponse
from news_aggregator.domain.exceptions.search import SearchError
from news_aggregator.domain.exceptions.source import (
    DuplicateSourceError,
    InvalidSourceError,
    SourceNotFoundError,
)

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register domain exception to HTTP response mappings."""

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        message = _format_validation_message(exc)
        return _error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="validation_error",
            message=message,
        )

    @app.exception_handler(SourceNotFoundError)
    async def handle_source_not_found(
        _request: Request,
        exc: SourceNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="source_not_found",
            message=str(exc),
        )

    @app.exception_handler(InvalidSourceError)
    async def handle_invalid_source(
        _request: Request,
        exc: InvalidSourceError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="invalid_source",
            message=str(exc),
        )

    @app.exception_handler(DuplicateSourceError)
    async def handle_duplicate_source(
        _request: Request,
        exc: DuplicateSourceError,
    ) -> JSONResponse:
        return _error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="duplicate_source",
            message=str(exc),
        )

    @app.exception_handler(SearchError)
    async def handle_search_error(
        _request: Request,
        exc: SearchError,
    ) -> JSONResponse:
        logger.exception("Search error")
        return _error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="search_error",
            message=str(exc),
        )


def _format_validation_message(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "Request validation failed"

    first_error = errors[0]
    location = ".".join(str(part) for part in first_error.get("loc", ()))
    message = first_error.get("msg", "Invalid request")
    if location:
        return f"{location}: {message}"
    return message


def _error_response(
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(status_code=status_code, content=body.model_dump())
