from abc import ABC, abstractmethod


class ContentExtractor(ABC):
    """Contract for extracting readable text from article HTML."""

    @abstractmethod
    async def extract(self, article_url: str) -> str:
        """Download and extract readable text from an article page."""
        raise NotImplementedError
