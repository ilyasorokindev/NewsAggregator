from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Source:
    """Domain entity representing a configured news source."""

    guid: UUID
    url: str
    created_at: datetime
