from app.config import settings
from app.infrastructure.embedder import embed
from app.infrastructure.qdrant_client import get_qdrant_client
from app.schemas.search import SearchResult


def search(query: str, limit: int = 10) -> list[SearchResult]:
    vector = embed([query])[0]
    client = get_qdrant_client()
    result = client.query_points(
        collection_name=settings.qdrant_collection,
        query=vector,
        limit=limit,
    )
    return [
        SearchResult(guid=hit.payload["guid"], text=hit.payload["text"])
        for hit in result.points
    ]
