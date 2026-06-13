# AGENTS.md — News Aggregator (Root)

Guide for AI coding agents working in this monorepo.

---

## What This Project Is

A full-stack semantic news search application:

- Users register news website URLs.
- A backend scrapes those sites on a schedule, chunks and embeds the text, and stores it in a vector database.
- Users search using natural-language queries; results are ranked by semantic similarity.

---

## Repository Layout

```
NewsAggregator/
├── BE/        # Backend v1 — FastAPI + PostgreSQL + pgvector (not in active use)
├── BE_CC/     # Backend v2 — FastAPI + Qdrant + SQLite (ACTIVE)
└── FE/        # Frontend — React 19 + TypeScript + Redux Toolkit + MUI
```

**Active production stack:** `BE_CC` + `FE`. `BE` is a superseded implementation; do not add new features there.

---

## Per-Directory Agent Guides

Each sub-directory has its own detailed AGENTS.md. **Read it before touching that directory.**

| Directory | Guide | What It Covers |
|---|---|---|
| `BE_CC/` | [BE_CC/AGENTS.md](BE_CC/AGENTS.md) | Architecture, invariants, API, env vars, chunking logic, what to avoid |
| `FE/` | [FE/AGENTS.md](FE/AGENTS.md) | Architecture, Redux state, API flow, code guidelines, what to avoid |

---

## How the Two Services Connect

```
User browser (FE — :5173)
    ↕ HTTP/REST
FastAPI backend (BE_CC — :8000)
    ↕
Qdrant (:6333) + SQLite (news.db)
```

- The frontend never talks to Qdrant or SQLite directly.
- All API calls go through `http://localhost:8000`.
- The backend base URL is configured in `FE/.env` (`VITE_API_BASE_URL`).

---

## Running Everything Locally

```bash
# Terminal 1 — Qdrant
cd BE_CC && docker compose up -d

# Terminal 2 — Backend
cd BE_CC && uv run uvicorn app.main:app --reload

# Terminal 3 — Frontend
cd FE && npm run dev
```

- Backend: `http://localhost:8000` (Swagger: `/docs`)
- Frontend: `http://localhost:5173`

---

## Key Invariants Across the Stack

### API contract
The frontend and backend share a fixed JSON contract. Changing a response field name or shape in `BE_CC` requires updating the corresponding TypeScript types in `FE/src/features/*/types.ts` — and vice versa.

| Endpoint | FE consumer |
|---|---|
| `GET /search?s=` | `features/search/api/searchApi.ts` |
| `GET /setup/items` | `features/settings/api/settingsApi.ts` |
| `POST/PUT/DELETE /setup/item` | `features/settings/api/settingsApi.ts` |

### Error format
All backend errors return `{"detail": "..."}`. The frontend extracts this with `shared/api/getApiErrorMessage.ts`. Do not change the error envelope shape.

### No auth
All endpoints are intentionally unauthenticated. Do not add authentication to either service.

---

## Running Tests

```bash
# Backend (no Qdrant required)
cd BE_CC && uv run pytest

# Frontend type check + build
cd FE && npm run build
```

---

## What to Avoid

- Making changes to `BE/` — it is superseded by `BE_CC/`.
- Calling Axios directly from React components — all HTTP goes through `FE/src/shared/api/httpClient.ts`.
- Storing article HTML in Qdrant — only extracted text chunks are stored.
- Adding authentication, keyword search, or RSS to `BE_CC/` — these are explicitly out of scope.
- Changing the Qdrant chunk ID generation logic without updating deduplication logic (`BE_CC/app/services/ingestion_service.py`).
