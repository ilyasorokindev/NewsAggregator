from news_aggregator.application.interfaces.text_chunker import TextChunker
from news_aggregator.infrastructure.config.settings import Settings


class ConfigurableTextChunker(TextChunker):
    """Settings-driven implementation of TextChunker."""

    def __init__(self, settings: Settings) -> None:
        self._chunk_size = settings.chunk_size
        self._chunk_overlap = settings.chunk_overlap

    def chunk(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        normalized = " ".join(text.split())
        if not normalized:
            return []

        if len(normalized) <= self._chunk_size:
            return [normalized]

        if self._chunk_overlap >= self._chunk_size:
            msg = "Chunk overlap must be smaller than chunk size"
            raise ValueError(msg)

        chunks: list[str] = []
        start = 0
        text_length = len(normalized)

        while start < text_length:
            end = start + self._chunk_size
            chunks.append(normalized[start:end])
            if end >= text_length:
                break
            start = end - self._chunk_overlap

        return chunks
