# Data Model

## 1. Relational Store (SQLite) — News Sources

Stores user-configured news website URLs. This is the only persistent relational data.

### Table: `news_sources`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `guid` | `TEXT` | PK, not null | UUID v4, assigned on creation |
| `url` | `TEXT` | unique, not null | Full URL of the news site to scrape |
| `created_at` | `DATETIME` | not null, default now | When the source was registered |
| `updated_at` | `DATETIME` | not null, default now | Last modification time |

**Example row**

```json
{
  "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "url": "https://techcrunch.com",
  "created_at": "2026-06-12T10:00:00Z",
  "updated_at": "2026-06-12T10:00:00Z"
}
```

---

## 2. Vector Store (Qdrant) — News Chunks

Stores embedded text chunks extracted from scraped articles.

### Collection: `news` (name configurable)

**Vector config**

| Field | Value |
|---|---|
| Size | `384` (matches `all-MiniLM-L6-v2` output) |
| Distance | `Cosine` |

**Point payload (metadata)**

| Field | Type | Description |
|---|---|---|
| `guid` | `string` | UUID v4, unique per chunk |
| `text` | `string` | Raw chunk text (no HTML) |
| `date_added` | `string` | ISO 8601 UTC timestamp of ingestion |
| `source_guid` | `string` | FK → `news_sources.guid` |
| `source_url` | `string` | URL of the originating site (denormalized for query convenience) |

> Only `text` and `date_added` are required per the product spec. `source_guid` and `source_url` are included as they are necessary for source deletion (cascade removal of chunks).

**Example Qdrant point**

```json
{
  "id": "a1b2c3d4-...",
  "vector": [0.021, -0.134, ...],
  "payload": {
    "guid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "text": "OpenAI announced a new model capable of...",
    "date_added": "2026-06-12T11:23:00Z",
    "source_guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "source_url": "https://techcrunch.com"
  }
}
```

---

## 3. Chunking Strategy

1. Extract visible text from the scraped HTML page (strip scripts, styles, nav, footer).
2. Split text using a sliding window: `CHUNK_SIZE` tokens, `CHUNK_OVERLAP` token overlap (configurable).
3. Discard chunks shorter than 50 characters (navigation remnants, whitespace).
4. Each chunk is embedded independently and stored as a separate Qdrant point.

**Deduplication**: before upserting, generate a deterministic UUID v5 from `(source_url + chunk_text)`. If a point with that ID already exists in Qdrant, skip it. This prevents re-ingesting duplicate content on repeated scrapes.
