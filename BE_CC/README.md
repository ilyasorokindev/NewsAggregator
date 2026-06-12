# News Aggregator — Backend

A Python backend service that periodically scrapes news articles from configurable websites, stores them as vector embeddings in Qdrant, and exposes a semantic search API.

## Features

- Register arbitrary news website URLs for scraping
- Automatic background scraping on a configurable interval
- Semantic (vector) search over all ingested content
- CRUD API for managing news sources
- Deduplication — re-scraping the same content is a no-op

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| Vector store | Qdrant |
| Relational store | SQLite (via SQLAlchemy) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| HTML scraping | httpx + BeautifulSoup4 |
| Background jobs | APScheduler |
| Dependency management | uv |

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
- [Docker](https://docs.docker.com/get-docker/) — for running Qdrant

Install `uv` if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd BE_CC
```

### 2. Install dependencies

```bash
uv sync
```

To include dev dependencies (pytest etc.):

```bash
uv sync --extra dev
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` to adjust any values. All variables have sensible defaults:

| Variable | Default | Description |
|---|---|---|
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `QDRANT_COLLECTION` | `news` | Qdrant collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model |
| `SCRAPE_INTERVAL_MINUTES` | `60` | How often to re-scrape all sources |
| `CHUNK_SIZE` | `500` | Target word count per chunk |
| `CHUNK_OVERLAP` | `50` | Word overlap between consecutive chunks |
| `DATABASE_URL` | `sqlite:///./news.db` | SQLAlchemy database URL |
| `LOG_LEVEL` | `INFO` | Python logging level |

### 4. Start Qdrant

```bash
docker compose up -d
```

This starts Qdrant on port `6333`. Data is persisted in a Docker volume.

---

## Running the Application

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

On startup the app will:
1. Create the SQLite database and tables if they don't exist
2. Create the Qdrant collection if it doesn't exist
3. Start the background scraping scheduler
4. Trigger an immediate ingestion pass if the collection is empty

---

## API

Interactive docs (Swagger UI): `http://localhost:8000/docs`

### Search

```
GET /search?s=<query>&limit=10
```

Returns a list of semantically matching text chunks ordered by relevance.

### Manage Sources

| Method | Path | Description |
|---|---|---|
| `GET` | `/setup/items` | List all registered sources |
| `POST` | `/setup/item` | Add a new source URL |
| `PUT` | `/setup/item` | Update a source URL |
| `DELETE` | `/setup/item` | Remove a source and its chunks |

**Add a source:**

```bash
curl -X POST http://localhost:8000/setup/item \
  -H "Content-Type: application/json" \
  -d '{"url": "https://techcrunch.com"}'
```

**Search:**

```bash
curl "http://localhost:8000/search?s=artificial+intelligence&limit=5"
```

---

## Running Tests

Tests use an in-memory SQLite database and do not require Qdrant to be running.

```bash
uv run pytest tests/
```

---

## Project Structure

```
app/
├── main.py                  # FastAPI app factory, scheduler startup
├── config.py                # Settings from env vars (pydantic-settings)
├── database.py              # SQLAlchemy engine + session factory
├── models/
│   └── source.py            # ORM model: NewsSource
├── schemas/
│   ├── source.py            # Request/response schemas for /setup
│   └── search.py            # Response schema for /search
├── routers/
│   ├── search.py            # GET /search
│   └── setup.py             # CRUD /setup/item(s)
├── services/
│   ├── source_service.py    # CRUD logic for news_sources table
│   ├── search_service.py    # Embed query + search Qdrant
│   └── ingestion_service.py # Scrape → chunk → embed → upsert pipeline
└── infrastructure/
    ├── qdrant_client.py     # Qdrant client singleton + collection init
    └── embedder.py          # sentence-transformers model wrapper
```
