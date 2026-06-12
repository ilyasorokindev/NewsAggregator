# API Specification

Base path: `/`  
Content-Type: `application/json`  
Auth: none

---

## Search

### `GET /search`

Perform a semantic similarity search over all ingested news chunks.

**Query parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `s` | string | Yes | Natural-language search query |
| `limit` | integer | No | Max results to return (default: `10`, max: `100`) |

**Response `200 OK`**

```json
[
  {
    "guid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "text": "OpenAI announced a new model capable of reasoning across..."
  },
  {
    "guid": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "text": "Microsoft confirmed a partnership with OpenAI to..."
  }
]
```

Results are ordered by descending cosine similarity score. The score itself is not exposed.

**Error responses**

| Status | Condition |
|---|---|
| `400 Bad Request` | `s` parameter missing or empty |
| `503 Service Unavailable` | Qdrant unreachable |

---

## Setup — List Sources

### `GET /setup/items`

Return all registered news source URLs.

**Response `200 OK`**

```json
[
  {
    "guid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "url": "https://techcrunch.com"
  },
  {
    "guid": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "url": "https://bbc.com/news"
  }
]
```

Returns an empty array `[]` when no sources are registered.

---

## Setup — Manage a Source

All three mutating operations use the path `/setup/item`.

---

### `POST /setup/item`

Register a new news source.

**Request body**

```json
{
  "url": "https://theverge.com"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `url` | string | Yes | Full URL of the news site |

A new UUID v4 `guid` is generated server-side; clients must not supply it.

**Response `201 Created`**

```json
{
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://theverge.com"
}
```

**Error responses**

| Status | Condition |
|---|---|
| `400 Bad Request` | `url` missing, empty, or not a valid URL |
| `409 Conflict` | A source with the same URL already exists |

---

### `PUT /setup/item`

Update the URL of an existing news source.

**Request body**

```json
{
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://theverge.com/tech"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `guid` | string | Yes | UUID of the source to update |
| `url` | string | Yes | New URL value |

When the URL changes, all Qdrant chunks belonging to this source are deleted and the source is queued for immediate re-scrape.

**Response `200 OK`**

```json
{
  "guid": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://theverge.com/tech"
}
```

**Error responses**

| Status | Condition |
|---|---|
| `400 Bad Request` | `guid` or `url` missing / invalid |
| `404 Not Found` | No source with given `guid` |
| `409 Conflict` | Another source already uses the new URL |

---

### `DELETE /setup/item`

Remove a news source and all its associated chunks from Qdrant.

**Request body**

```json
{
  "guid": "550e8400-e29b-41d4-a716-446655440000"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `guid` | string | Yes | UUID of the source to delete |

**Response `204 No Content`** — empty body.

**Error responses**

| Status | Condition |
|---|---|
| `400 Bad Request` | `guid` missing or not a valid UUID |
| `404 Not Found` | No source with given `guid` |

---

## Error Envelope

All error responses use the following body shape:

```json
{
  "detail": "Human-readable error message"
}
```

This is the FastAPI default and compatible with its validation error format.

---

## OpenAPI

FastAPI auto-generates an OpenAPI 3.1 schema at `/openapi.json`  
and interactive Swagger UI at `/docs`.
