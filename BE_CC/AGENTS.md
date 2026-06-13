# AGENTS.md — News Aggregator Backend

Guide for AI coding agents working in this repository.

---

## What This Project Is

A Python 3.12 FastAPI backend that:
1. Accepts user-registered news site URLs via REST API.
2. Periodically scrapes those URLs, chunks the text, embeds it, and stores it in Qdrant.
3. Exposes a semantic (vector) search endpoint over the ingested content.

There is no auth, no frontend, no keyword search, no RSS.

---

## Running Locally

**Prerequisites:** Docker (for Qdrant), Python 3.12+, `uv`.

```bash
# 1. Start Qdrant
docker compose up -d

# 2. Install dependencies
uv sync

# 3. Copy env and adjust if needed
cp .env.example .env

# 4. Run the app
uv run uvicorn app.main:app --reload
```

API is available at `http://localhost:8000`.  
Swagger UI: `http://localhost:8000/docs`.

---

## Running Tests

```bash
uv run pytest
```

Tests live in `tests/`. They cover chunking logic and source service CRUD. No Qdrant or live network required — use fakes/mocks for infrastructure when adding tests.

---

## Architecture in One Paragraph

FastAPI app with two routers (`/search`, `/setup`). An in-process APScheduler fires `run_ingestion()` every `SCRAPE_INTERVAL_MINUTES` minutes (default 60). Ingestion reads source URLs from SQLite, scrapes HTML with httpx + BeautifulSoup4, chunks the text, embeds it with `sentence-transformers` (`all-MiniLM-L6-v2`), and upserts into Qdrant. The SQLite DB only stores source metadata; all article content lives in Qdrant.

---

## Project Structure

```
app/
  main.py               # App factory, lifespan: DB init, Qdrant init, scheduler start
  config.py             # pydantic-settings Settings singleton → settings
  database.py           # SQLAlchemy engine + SessionLocal + init_db()
  models/
    source.py           # ORM: NewsSource (guid, url, created_at, updated_at)
  schemas/
    source.py           # Pydantic: SourceCreate, SourceUpdate, SourceResponse
    search.py           # Pydantic: SearchResult
  routers/
    search.py           # GET /search?s=<query>&limit=<n>
    setup.py            # GET /setup/items | POST/PUT/DELETE /setup/item
  services/
    source_service.py   # CRUD on news_sources table
    search_service.py   # Embed query → query Qdrant → return results
    ingestion_service.py# Full scrape→chunk→embed→upsert pipeline
  infrastructure/
    qdrant_client.py    # QdrantClient singleton + ensure_collection()
    embedder.py         # SentenceTransformer singleton, embed(texts) -> list[list[float]]
spec/                   # Authoritative specs — read before changing behaviour
tests/
```

---

## Key Invariants — Do Not Break

### Deduplication
Chunk IDs are deterministic UUID v5: `uuid5(NAMESPACE, source_url + chunk_text)`.  
This means re-scraping the same content is idempotent — existing chunks are retrieved from Qdrant and skipped before embedding.  
**Do not change the ID generation logic without updating deduplication logic.**

### Qdrant payload fields
Every upserted point carries these payload fields:
- `guid` — same as the point ID (string)
- `text` — chunk text
- `date_added` — ISO 8601 UTC
- `source_guid` — FK to `news_sources.guid`
- `source_url` — denormalized URL

`source_guid` is required for cascade deletion when a source is deleted or its URL updated. Do not drop it.

### Source deletion cascade
`DELETE /setup/item` and `PUT /setup/item` (URL change) both call `delete_source_chunks(source_guid)` before modifying SQLite. Order matters — delete Qdrant data first, then update/delete the SQL row.

### Embedding model
The Qdrant collection is created with vector size `384` (matches `all-MiniLM-L6-v2`). Changing `EMBEDDING_MODEL` to a different-dimension model without recreating the collection will cause upsert failures.

### Scheduler: max_instances=1
The ingestion job is configured with `max_instances=1`. Do not remove this — a slow scrape run must not overlap with the next tick.

### Concurrency cap
`_SEMAPHORE = asyncio.Semaphore(5)` in `ingestion_service.py` limits concurrent source scrapes. The embedding step runs in `loop.run_in_executor(None, embed, ...)` to avoid blocking the event loop.

---

## API Summary

| Method | Path | Description |
|--------|------|-------------|
| GET | `/search` | Semantic search (`s` param required, `limit` optional, max 100) |
| GET | `/setup/items` | List all sources |
| POST | `/setup/item` | Add source (`{"url": "..."}`) → 201 |
| PUT | `/setup/item` | Update source URL (`{"guid": "...", "url": "..."}`) → triggers re-scrape |
| DELETE | `/setup/item` | Delete source + its chunks (`{"guid": "..."}`) → 204 |

All errors return `{"detail": "..."}`.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `QDRANT_COLLECTION` | `news` | Qdrant collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model |
| `SCRAPE_INTERVAL_MINUTES` | `60` | Scrape interval |
| `CHUNK_SIZE` | `500` | Words per chunk (sliding window) |
| `CHUNK_OVERLAP` | `50` | Word overlap between chunks |
| `DATABASE_URL` | `sqlite:///./news.db` | SQLAlchemy DB URL |
| `LOG_LEVEL` | `INFO` | Python log level |

All variables are read by `app/config.py` via `pydantic-settings` and can be set in `.env`.

---

## Chunking Logic

`_chunk_text(text, chunk_size, overlap)` in `ingestion_service.py`:
- Splits on whitespace (word-level, not token-level).
- Sliding window: step = `chunk_size - overlap`.
- Discards chunks shorter than 50 characters.

`CHUNK_SIZE` and `CHUNK_OVERLAP` are in **words**, not tokens.

---

## HTML Extraction Logic

`_extract_text(html)` in `ingestion_service.py`:
- Strips: `script`, `style`, `nav`, `footer`, `header`, `aside`, `form`.
- Collects text from: `p`, `article`, `section`, `main`.
- Falls back to full page `get_text()` if no semantic tags found.
- Parser: `lxml` (faster than `html.parser`).

---

## Startup Behaviour

On startup (`lifespan` in `main.py`):
1. `init_db()` — creates SQLite tables if absent.
2. `ensure_collection()` — creates Qdrant collection if absent (idempotent).
3. Scheduler starts; first periodic tick fires after `SCRAPE_INTERVAL_MINUTES`.
4. Background task: if Qdrant collection is empty, fires one ingestion run after 10 seconds.

---

## What to Avoid

- Do not add authentication — it is explicitly out of scope.
- Do not add keyword/full-text search — semantic search only.
- Do not introduce a task queue (Redis/Celery) — APScheduler in-process is intentional.
- Do not change `CHUNK_SIZE` semantics from words to tokens without updating tests and docs.
- Do not store article HTML or full page content — only extracted text chunks go into Qdrant.
