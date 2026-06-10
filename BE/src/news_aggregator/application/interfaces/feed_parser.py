from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FeedEntry:
    """Parsed feed entry containing an article URL."""

    url: str


class FeedParser(ABC):
    """Contract for parsing RSS/Atom feeds."""

    @abstractmethod
    async def parse(self, feed_url: str) -> list[FeedEntry]:
        """Parse a feed and return article URLs."""
        raise NotImplementedError
