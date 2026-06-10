from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Structured error detail."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard API error response envelope."""

    error: ErrorDetail = Field(...)
