# News Aggregator Backend

FastAPI backend: scrapes news sites → chunks text → embeds → stores in Qdrant → exposes semantic search API.

## Commands

```bash
# Start Qdrant (required before running app)
docker compose up -d

# Install dependencies
uv sync

# Run dev server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest
```

## Architecture

- **FastAPI** app with two routers: `/search` and `/setup`
- **SQLite** (via SQLAlchemy) — stores only source URLs (`news_sources` table)
- **Qdrant** — stores all article content as vector embeddings
- **APScheduler** (in-process) — fires `run_ingestion()` every `SCRAPE_INTERVAL_MINUTES` minutes
- **sentence-transformers** (`all-MiniLM-L6-v2`, vector size 384) — local embeddings, no API key needed

Ingestion pipeline per source: fetch HTML → strip boilerplate tags → extract text from semantic tags → chunk (sliding window, word-level) → deduplicate via UUID v5 → embed → upsert into Qdrant.

## Project Layout

```
app/
  main.py               # App factory + lifespan (DB init, Qdrant init, scheduler)
  config.py             # Settings singleton from env vars (pydantic-settings)
  database.py           # SQLAlchemy engine, SessionLocal, init_db()
  models/source.py      # ORM: NewsSource
  schemas/              # Pydantic schemas (source.py, search.py)
  routers/              # search.py → GET /search | setup.py → CRUD /setup/*
  services/
    source_service.py   # CRUD on news_sources
    search_service.py   # Embed query + query Qdrant
    ingestion_service.py# Full pipeline: scrape → chunk → embed → upsert
  infrastructure/
    qdrant_client.py    # QdrantClient singleton + ensure_collection()
    embedder.py         # SentenceTransformer singleton, embed() function
spec/                   # Authoritative specs — read before changing behaviour
```

## Critical Invariants

**Deduplication:** chunk IDs are `uuid5(NAMESPACE, source_url + chunk_text)` — changing this breaks idempotency.

**Qdrant payload** must always include: `guid`, `text`, `date_added`, `source_guid`, `source_url`. The `source_guid` field is required for cascade deletion.

**Cascade deletion order:** delete Qdrant chunks first (`delete_source_chunks()`), then update/delete the SQL row. This order is intentional.

**Vector size is fixed at 384.** Changing `EMBEDDING_MODEL` to a different-dimension model requires recreating the Qdrant collection.

**Scheduler:** `max_instances=1` — do not remove; prevents overlapping scrape runs.

**Embedding is CPU-bound** — runs in `loop.run_in_executor()` to avoid blocking the event loop.

## Environment Variables

| Variable | Default |
|---|---|
| `QDRANT_HOST` | `localhost` |
| `QDRANT_PORT` | `6333` |
| `QDRANT_COLLECTION` | `news` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` |
| `SCRAPE_INTERVAL_MINUTES` | `60` |
| `CHUNK_SIZE` | `500` (words) |
| `CHUNK_OVERLAP` | `50` (words) |
| `DATABASE_URL` | `sqlite:///./news.db` |
| `LOG_LEVEL` | `INFO` |

## Out of Scope — Do Not Add

- Authentication / authorization
- Keyword or full-text search
- RSS/Atom feed parsing
- External task queue (Redis, Celery)
- Frontend or UI
