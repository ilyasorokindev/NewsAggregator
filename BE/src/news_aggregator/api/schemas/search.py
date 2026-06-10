from uuid import UUID

from pydantic import BaseModel, Field


class SearchResultSchema(BaseModel):
    """Search result response item."""

    guid: UUID
    text: str = Field(..., min_length=1)
