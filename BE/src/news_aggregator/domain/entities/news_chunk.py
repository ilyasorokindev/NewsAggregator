from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class NewsChunk:
    """Domain entity representing a searchable text chunk."""

    guid: UUID
    source_guid: UUID
    text: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Domain entity representing a semantic search result."""

    guid: UUID
    text: str
