from abc import ABC, abstractmethod


class TextChunker(ABC):
    """Contract for splitting text into overlapping chunks."""

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Split text into chunks according to configured size and overlap."""
        raise NotImplementedError
