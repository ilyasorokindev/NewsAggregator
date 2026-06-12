# Architecture

## Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| Web framework | **FastAPI** | Async-native, automatic OpenAPI docs, lightweight |
| Vector database | **Qdrant** | Fast ANN search, rich filtering, self-hostable |
| Source config store | **SQLite** (via SQLAlchemy) | Simple, no extra infra; stores URL list only |
| HTML scraping | **httpx** + **BeautifulSoup4** | Async HTTP + battle-tested HTML parser |
| Embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | Runs locally, no API key, good multilingual quality |
| Background scheduler | **APScheduler** | In-process periodic jobs, no Redis/Celery needed |
| Dependency management | **uv** + `pyproject.toml` | Fast resolver, PEP 517 compliant |

## System Components

```
┌──────────────────────────────────────────────────────┐
│                      FastAPI App                     │
│                                                      │
│  ┌─────────────────┐      ┌──────────────────────┐  │
│  │  Search Router  │      │   Setup Router       │  │
│  │  GET /search    │      │  GET  /setup/items   │  │
│  └────────┬────────┘      │  POST /setup/item    │  │
│           │               │  PUT  /setup/item    │  │
│           ▼               │  DELETE /setup/item  │  │
│  ┌─────────────────┐      └──────────┬───────────┘  │
│  │ Search Service  │                 │               │
│  │ (embed query,   │                 ▼               │
│  │  query Qdrant)  │      ┌──────────────────────┐  │
│  └────────┬────────┘      │   Source Service     │  │
│           │               │   (CRUD on SQLite)   │  │
│           ▼               └──────────────────────┘  │
│      ┌─────────┐                                     │
│      │  Qdrant │                                     │
│      └─────────┘                                     │
│                                                      │
│  ┌───────────────────────────────────────────────┐  │
│  │  Ingestion Scheduler (APScheduler)            │  │
│  │  1. Read source URLs from SQLite              │  │
│  │  2. Scrape HTML → extract article text        │  │
│  │  3. Chunk text                                │  │
│  │  4. Embed chunks (sentence-transformers)      │  │
│  │  5. Upsert into Qdrant                        │  │
│  └───────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

## Deployment

All components run in a single process (FastAPI + embedded APScheduler).  
Qdrant runs as a separate Docker container alongside the app.

Recommended `docker-compose.yml` services:
- `qdrant` — official `qdrant/qdrant` image, port 6333
- `app` — Python FastAPI app, port 8000

## Configuration (environment variables)

| Variable | Default | Description |
|---|---|---|
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant gRPC/HTTP port |
| `QDRANT_COLLECTION` | `news` | Collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model ID |
| `SCRAPE_INTERVAL_MINUTES` | `60` | How often to re-scrape all sources |
| `CHUNK_SIZE` | `500` | Target token count per chunk |
| `CHUNK_OVERLAP` | `50` | Token overlap between consecutive chunks |
| `DATABASE_URL` | `sqlite:///./news.db` | SQLAlchemy database URL |
| `LOG_LEVEL` | `INFO` | Python logging level |
