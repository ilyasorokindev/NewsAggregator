# Project Structure

```
news-aggregator/
├── pyproject.toml
├── .env.example
├── docker-compose.yml
│
├── app/
│   ├── main.py                  # FastAPI app factory, scheduler startup
│   ├── config.py                # Settings from env vars (pydantic-settings)
│   ├── database.py              # SQLAlchemy engine + session factory
│   │
│   ├── models/
│   │   └── source.py            # SQLAlchemy ORM model: NewsSource
│   │
│   ├── schemas/
│   │   ├── source.py            # Pydantic request/response schemas for /setup
│   │   └── search.py            # Pydantic response schema for /search
│   │
│   ├── routers/
│   │   ├── search.py            # GET /search
│   │   └── setup.py             # GET /setup/items, POST/PUT/DELETE /setup/item
│   │
│   ├── services/
│   │   ├── source_service.py    # CRUD logic for news_sources table
│   │   ├── search_service.py    # Embed query + query Qdrant
│   │   └── ingestion_service.py # Scrape → chunk → embed → upsert pipeline
│   │
│   └── infrastructure/
│       ├── qdrant_client.py     # Qdrant client singleton + collection init
│       └── embedder.py          # sentence-transformers model wrapper
│
└── spec/                        # This specification
    ├── 01-overview.md
    ├── 02-architecture.md
    ├── 03-data-model.md
    ├── 04-api.md
    ├── 05-ingestion.md
    └── 06-project-structure.md
```

## Key Module Responsibilities

### `app/main.py`
- Creates the FastAPI instance.
- Registers routers (`/search`, `/setup`).
- On startup: initialises SQLite tables, verifies Qdrant collection exists (creates if absent), starts APScheduler.
- On shutdown: stops APScheduler gracefully.

### `app/config.py`
- Single `Settings` class using `pydantic-settings`.
- Reads all environment variables listed in [02-architecture.md](02-architecture.md).
- Exported as a module-level singleton `settings`.

### `app/infrastructure/qdrant_client.py`
- Lazily initialised `QdrantClient` singleton.
- `ensure_collection()` — idempotent collection creation with correct vector config.

### `app/infrastructure/embedder.py`
- Loads `SentenceTransformer` model once at process start.
- Exposes `embed(texts: list[str]) -> list[list[float]]`.

### `app/services/ingestion_service.py`
- `run_ingestion()` — full pipeline; called by scheduler and on-demand after URL update.
- `delete_source_chunks(source_guid: str)` — removes all Qdrant points for a source.

## Dependencies (`pyproject.toml`)

```toml
[project]
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic-settings>=2.3",
    "sqlalchemy>=2.0",
    "qdrant-client>=1.10",
    "sentence-transformers>=3.0",
    "httpx>=0.27",
    "beautifulsoup4>=4.12",
    "apscheduler>=3.10",
    "lxml>=5.2",         # faster BS4 parser
]
```
