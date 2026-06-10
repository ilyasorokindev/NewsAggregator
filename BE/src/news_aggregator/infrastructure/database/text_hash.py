import hashlib


def compute_text_hash(text: str) -> str:
    """Compute a SHA-256 hex digest for duplicate chunk detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
