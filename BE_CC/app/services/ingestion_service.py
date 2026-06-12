import asyncio
import logging
import uuid
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

from app.config import settings
from app.database import SessionLocal
from app.infrastructure.embedder import embed
from app.infrastructure.qdrant_client import get_qdrant_client
from app.models.source import NewsSource

logger = logging.getLogger(__name__)

_STRIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "form"}
_KEEP_TAGS = {"p", "article", "section", "main"}
_SEMAPHORE = asyncio.Semaphore(5)

UUID5_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if len(chunk) >= 50:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(_STRIP_TAGS):
        tag.decompose()
    parts: list[str] = []
    for tag in soup.find_all(_KEEP_TAGS):
        text = tag.get_text(separator=" ", strip=True)
        if text:
            parts.append(text)
    if not parts:
        parts = [soup.get_text(separator=" ", strip=True)]
    return " ".join(parts)


def _deterministic_id(source_url: str, chunk_text: str) -> str:
    return str(uuid.uuid5(UUID5_NAMESPACE, source_url + chunk_text))


async def _scrape_source(source: NewsSource) -> None:
    async with _SEMAPHORE:
        logger.info("Scraping %s", source.url)
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                response = await client.get(source.url)
                response.raise_for_status()
                html = response.text
        except Exception as exc:
            logger.warning("Fetch failed for %s: %s", source.url, exc)
            return

        text = _extract_text(html)
        if not text.strip():
            logger.warning("Empty text for %s", source.url)
            return

        chunks = _chunk_text(text, settings.chunk_size, settings.chunk_overlap)
        if not chunks:
            logger.warning("No valid chunks for %s", source.url)
            return

        chunk_ids = [_deterministic_id(source.url, c) for c in chunks]

        qdrant = get_qdrant_client()
        existing = {
            str(p.id)
            for p in qdrant.retrieve(
                collection_name=settings.qdrant_collection,
                ids=chunk_ids,
                with_payload=False,
                with_vectors=False,
            )
        }

        new_chunks = [(cid, c) for cid, c in zip(chunk_ids, chunks) if cid not in existing]
        if not new_chunks:
            logger.info("No new chunks for %s", source.url)
            return

        new_ids, new_texts = zip(*new_chunks)
        loop = asyncio.get_running_loop()
        vectors = await loop.run_in_executor(None, embed, list(new_texts))

        date_added = datetime.now(timezone.utc).isoformat()
        points = [
            PointStruct(
                id=cid,
                vector=vec,
                payload={
                    "guid": cid,
                    "text": text,
                    "date_added": date_added,
                    "source_guid": source.guid,
                    "source_url": source.url,
                },
            )
            for cid, vec, text in zip(new_ids, vectors, new_texts)
        ]

        qdrant.upsert(collection_name=settings.qdrant_collection, points=points)
        logger.info("Upserted %d chunks for %s", len(points), source.url)


async def run_ingestion() -> None:
    with SessionLocal() as db:
        sources = db.query(NewsSource).all()

    logger.info("Ingestion started — %d sources", len(sources))
    start = datetime.now(timezone.utc)

    await asyncio.gather(*[_scrape_source(s) for s in sources], return_exceptions=True)

    duration = (datetime.now(timezone.utc) - start).total_seconds()
    logger.info("Ingestion finished in %.1fs", duration)


def delete_source_chunks(source_guid: str) -> None:
    qdrant = get_qdrant_client()
    qdrant.delete(
        collection_name=settings.qdrant_collection,
        points_selector=Filter(
            must=[FieldCondition(key="source_guid", match=MatchValue(value=source_guid))]
        ),
    )
    logger.info("Deleted chunks for source %s", source_guid)
