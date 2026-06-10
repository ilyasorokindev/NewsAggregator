from urllib.parse import urlparse

from news_aggregator.domain.exceptions.source import InvalidSourceError


def validate_source_url(url: str) -> str:
    """Validate and normalize a news source URL."""
    normalized = url.strip()
    if not normalized:
        raise InvalidSourceError("URL must not be empty")

    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        raise InvalidSourceError("URL must use http or https scheme")

    if not parsed.netloc:
        raise InvalidSourceError("URL must have a valid host")

    return normalized
