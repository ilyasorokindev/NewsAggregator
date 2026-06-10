from abc import ABC, abstractmethod


class FeedDiscovery(ABC):
    """Contract for discovering RSS/Atom feed URLs from source URLs."""

    @abstractmethod
    async def discover_feed_url(self, source_url: str) -> str:
        """Return a feed URL for the given source URL."""
        raise NotImplementedError
