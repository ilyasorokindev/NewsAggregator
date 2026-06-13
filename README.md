# News Aggregator

A full-stack application for semantic search over news articles. Users register news website URLs; the backend periodically scrapes them, embeds the text as vectors, and exposes a natural-language search API. The frontend provides a search interface and a settings page for managing sources.

---

## Repository Structure

```
NewsAggregator/
├── BE/        # Backend v1 — FastAPI + PostgreSQL + pgvector + RSS
├── BE_CC/     # Backend v2 — FastAPI + Qdrant + SQLite (active)
└── FE/        # Frontend — React + TypeScript + Redux + MUI
```

The **active stack** is `BE_CC` (backend) + `FE` (frontend). `BE` is an earlier implementation using PostgreSQL/pgvector instead of Qdrant.

---

## Quick Start

### 1. Start the backend (BE_CC)

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Docker.

```bash
cd BE_CC

# Start Qdrant
docker compose up -d

# Install dependencies
uv sync

# Copy env
cp .env.example .env

# Run
uv run uvicorn app.main:app --reload
```

API available at `http://localhost:8000`. Swagger UI: `http://localhost:8000/docs`.

### 2. Start the frontend (FE)

**Prerequisites:** Node.js 18+, npm.

```bash
cd FE

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend available at `http://localhost:5173`.

---

## What It Does

1. **Register sources** — POST a news website URL via the Settings page or API.
2. **Background scraping** — the backend scrapes registered URLs every 60 minutes (configurable), extracts article text, chunks it, embeds it with `all-MiniLM-L6-v2`, and upserts into Qdrant. Re-scraping the same content is a no-op (deduplication by content hash).
3. **Semantic search** — enter a natural-language query; the backend embeds it and returns the most relevant chunks ranked by cosine similarity.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend (active) | Python 3.12, FastAPI, Qdrant, SQLite, sentence-transformers, APScheduler |
| Backend (v1) | Python 3.12, FastAPI, PostgreSQL, pgvector, Alembic, feedparser |
| Frontend | React 19, TypeScript 5, Redux Toolkit, React Router 7, MUI 6, Vite 6 |

---

## API

| Method | Path | Description |
|---|---|---|
| GET | `/search?s={query}` | Semantic search over ingested articles |
| GET | `/setup/items` | List all registered source URLs |
| POST | `/setup/item` | Add a source URL |
| PUT | `/setup/item` | Update a source URL |
| DELETE | `/setup/item` | Delete a source and its chunks |

All endpoints are unauthenticated. Errors return `{"detail": "..."}`.

---

## Environment Variables (BE_CC)

| Variable | Default | Description |
|---|---|---|
| `QDRANT_HOST` | `localhost` | Qdrant host |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `QDRANT_COLLECTION` | `news` | Qdrant collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model |
| `SCRAPE_INTERVAL_MINUTES` | `60` | Scrape frequency |
| `CHUNK_SIZE` | `500` | Words per chunk |
| `CHUNK_OVERLAP` | `50` | Word overlap between chunks |
| `DATABASE_URL` | `sqlite:///./news.db` | SQLAlchemy DB URL |
| `LOG_LEVEL` | `INFO` | Python log level |

---

## Running Tests

```bash
# Backend tests (no Qdrant required)
cd BE_CC && uv run pytest

# Frontend type-check + build
cd FE && npm run build
```

---

## Further Reading

- [BE_CC/AGENTS.md](BE_CC/AGENTS.md) — backend architecture, invariants, and agent guide
- [FE/AGENTS.md](FE/AGENTS.md) — frontend architecture, code guidelines, and agent guide
- [BE_CC/spec/](BE_CC/spec/) — authoritative backend specifications
