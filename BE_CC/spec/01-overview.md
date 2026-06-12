# News Aggregator — Project Overview

## Purpose

A Python backend service that periodically scrapes news articles from a configurable list of websites, stores them as vector embeddings in Qdrant, and exposes a semantic search API along with a setup API for managing news sources.

## Goals

- Allow users to register arbitrary news website URLs for scraping.
- Automatically fetch and chunk article text from registered sites via HTML scraping.
- Embed and store each chunk in Qdrant with minimal metadata (text + ingestion date).
- Expose a semantic search endpoint that accepts a natural-language query and returns ranked matching chunks.
- Provide CRUD endpoints for managing news sources.

## Non-Goals

- User authentication or authorization (all endpoints are open).
- Full-text / keyword search (semantic vector search only).
- Frontend / UI.
- Multi-tenancy.
- PDF or binary document ingestion.

## Scope

| Capability | In scope |
|---|---|
| HTML scraping | Yes |
| RSS / Atom feeds | No |
| Semantic search | Yes |
| Keyword search | No |
| CRUD for news sources | Yes |
| Scheduled scraping | Yes (background job) |
| Auth | No |

## Constraints

- Language: **Python 3.12+**
- Vector store: **Qdrant**
- No external managed services required (fully self-hostable).
- REST API — JSON over HTTP, no GraphQL or gRPC.
