class SourceError(Exception):
    """Base exception for source-related domain errors."""


class SourceNotFoundError(SourceError):
    """Raised when a requested source does not exist."""


class InvalidSourceError(SourceError):
    """Raised when a source URL is invalid."""


class DuplicateSourceError(SourceError):
    """Raised when a source URL already exists."""
