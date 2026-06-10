from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator


class SourceSchema(BaseModel):
    """Source response item."""

    guid: UUID
    url: str


class CreateSourceRequest(BaseModel):
    """Request body for creating a source."""

    url: HttpUrl

    @field_validator("url", mode="before")
    @classmethod
    def strip_url(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                msg = "URL must not be empty"
                raise ValueError(msg)
            return stripped
        return value


class CreateSourceResponse(BaseModel):
    """Response body for creating a source."""

    guid: UUID


class UpdateSourceRequest(BaseModel):
    """Request body for updating a source."""

    guid: UUID
    url: HttpUrl

    @field_validator("url", mode="before")
    @classmethod
    def strip_url(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                msg = "URL must not be empty"
                raise ValueError(msg)
            return stripped
        return value


class SuccessResponse(BaseModel):
    """Generic success response."""

    success: bool = True


class DeleteSourceRequest(BaseModel):
    """Request body for deleting a source."""

    guid: UUID = Field(..., description="Identifier of the source to delete")
