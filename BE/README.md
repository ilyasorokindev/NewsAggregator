# News Aggregator Backend

Backend-only News Aggregator with semantic search powered by PostgreSQL and pgvector.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

API documentation: http://localhost:8000/docs

## Development

```bash
pip install -e ".[dev]"
alembic upgrade head
uvicorn news_aggregator.main:app --reload
```
