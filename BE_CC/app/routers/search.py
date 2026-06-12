from fastapi import APIRouter, HTTPException, Query
from qdrant_client.http.exceptions import UnexpectedResponse

from app.schemas.search import SearchResult
from app.services import search_service

router = APIRouter()


@router.get("/search", response_model=list[SearchResult])
def search(
    s: str = Query(..., min_length=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    try:
        return search_service.search(s, limit)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).exception("Search failed: %s", exc)
        raise HTTPException(status_code=503, detail="Search service unavailable")
