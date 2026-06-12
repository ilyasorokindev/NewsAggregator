# Ingestion Pipeline

The ingestion pipeline runs as a background job inside the same FastAPI process, managed by APScheduler. It fires every `SCRAPE_INTERVAL_MINUTES` minutes (default: 60).

## Pipeline Steps

```
┌──────────────────────────────────────────────────────┐
│  Trigger: APScheduler interval job                   │
│                                                      │
│  1. Load source URLs                                 │
│     └─ SELECT * FROM news_sources                    │
│                                                      │
│  2. For each source URL (concurrent, max 5 workers)  │
│     │                                                │
│     ├─ 2a. Fetch HTML                                │
│     │      httpx.AsyncClient GET url                 │
│     │      timeout: 15s, follow redirects            │
│     │                                                │
│     ├─ 2b. Extract text                              │
│     │      BeautifulSoup4 parse                      │
│     │      Remove: <script> <style> <nav> <footer>   │
│     │              <header> <aside> <form>           │
│     │      Collect: <p> <article> <section> <main>   │
│     │                                                │
│     ├─ 2c. Chunk text                                │
│     │      Sliding window: CHUNK_SIZE / CHUNK_OVERLAP│
│     │      Discard chunks < 50 chars                 │
│     │                                                │
│     ├─ 2d. Deduplicate                               │
│     │      UUID v5 = hash(source_url + chunk_text)   │
│     │      Filter out IDs already in Qdrant          │
│     │                                                │
│     ├─ 2e. Embed                                     │
│     │      sentence-transformers encode(new_chunks)  │
│     │      Batch size: 32                            │
│     │                                                │
│     └─ 2f. Upsert into Qdrant                        │
│            payload: {guid, text, date_added,         │
│                      source_guid, source_url}        │
│                                                      │
│  3. Log summary: sources processed, chunks added     │
└──────────────────────────────────────────────────────┘
```

## Error Handling

| Failure point | Behavior |
|---|---|
| HTTP fetch fails (timeout, 4xx, 5xx) | Log warning, skip this source, continue with others |
| HTML parsing yields empty text | Log warning, skip source |
| Embedding model error | Log error, abort job run, retry on next interval |
| Qdrant upsert error | Log error, abort job run, retry on next interval |

A single failing source never blocks other sources in the same run.

## Triggered Re-Scrape

When a source URL is updated via `PUT /setup/item`:
1. All existing Qdrant points for `source_guid` are deleted (filter by `source_guid` payload field).
2. The source is immediately queued for a one-shot scrape job (does not reset the regular interval).

## Startup Behavior

On application startup, the scheduler starts immediately. The first scrape run fires after the first interval tick (not immediately at boot), unless no Qdrant data exists for a source — in that case the first run fires within 10 seconds of startup.

## Concurrency

- Up to **5 sources** are scraped concurrently (asyncio semaphore).
- The embedding step within a single source run is CPU-bound; it runs in a `ProcessPoolExecutor` thread so it does not block the event loop.
- Only one ingestion job instance can run at a time (APScheduler `max_instances=1`).

## Logging

Each ingestion run emits structured log lines at the following points:

- Job start: total sources count
- Per source: URL, chunks extracted, new chunks upserted
- Job end: total duration, total new chunks across all sources
- Any skipped/failed sources with reason
