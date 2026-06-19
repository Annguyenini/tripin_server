# Trip Contents Module

## Overview

Handles all content card operations for trips — fetching, syncing, presigned URL generation, and hash-based cache validation.

---

## Routes (`TripContentRoutes`)

Base: `/trip-contents` *(or whatever prefix is registered in `app.py`)*

| Method | Endpoint | Handler |
|--------|----------|---------|
| `GET` | `/get-all-contents/<trip_id>` | `get_trip_contents` |
| `POST` | `/sync` | `sync_content_cards` |
| `POST` | `/request-presign-urls` | `request_cloud_presign_url` |
| `POST` | `/request-trip-contents-hash` | `request_trip_contents_hash` |
| `POST` | `/request-trip-contents-metadata` | `request_trip_contents_metadata_for_sync` |

All routes require JWT authentication. The user's `user_id` is extracted from the token.

---

### `GET /get-all-contents/<trip_id>`

Fetch all content cards for a trip. Supports ETag-based caching via the `If-None-Match` header. Layer that access database from `TripContentsRepository` then generate and inject image url from s3

Cache use - `trip_contents::{trip_id}`

**Headers**
- `Authorization` — JWT token
- `If-None-Match` *(optional)* — client's current hash

**Response**

| Code | Body |
|------|------|
| `200` | `{ code, content_cards }` |
| `304` | `{ code: "match" }` — hash matched, no data returned |
| `401` | Auth error |
| `402` | Missing required inputs |
| `403` | Not trip owner |
| `502` | Server error |

Media paths for `photo`/`video` types are replaced with temporary S3 presigned URIs. Timestamps are converted from `timestamptz` to milliseconds.

---

### `POST /sync`

Sync content cards from the client. Processes `add` and `remove` events in order.

**Request Body**

```json
{
  "trip_id": "string",
  "content_cards": [
    {
      "event": "add" | "remove",
      "uuid": "string",
      "time_stamp": 1700000000000,
      "media_type": "photo" | "video" | "text",
      "filename": "string",
      "media_id": "string",
      "altitude": 0.0,
      "latitude": 0.0,
      "longitude": 0.0,
      "speed": 0.0,
      "heading": 0.0,
      "city": "string",
      "region": "string",
      "country": "string",
      "iso_country_code": "string"
    }
  ]
}
```

For `remove` events, also include:
```json
{ "modified_time": 1700000000000 }
```

For `add` events, we assuming that contents been push to s3 and verified by app.

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully" }` |
| `400` | Missing inputs |
| `401` | Auth error |
| `500` | `{ code: "requests_failed", request: [...] }` — partial failure list |

---

### `POST /request-presign-urls`

Generate S3 presigned upload URLs for a batch of media files.

**Request Body**
```json
{
  "trip_id": "string",
  "content_cards": [
    { "filename": "string", "minetype": "image/jpeg" }
  ]
}
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code, presign_urls: [...content_cards with presign_url added] }` |
| `401` | Auth error |
| `403` | Not trip owner |
| `500` | Server error |

S3 key format: `trips/{trip_id}/{filename}`

---

### `POST /request-trip-contents-hash`

Get the current MD5 hash of all content cards for a trip. Used by the client to check if a sync is needed.

**Request Body**
```json
{ "trip_id": "string" }
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code, hash: "string" }` |
| `401` | Auth error |
| `403` | Not trip owner |
| `500` | Server error |

---

### `POST /request-trip-contents-metadata`

Fetch lightweight metadata for all content cards (no presigned URLs, no timestamp conversion).

**Request Body**
```json
{ "trip_id": "string" }
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code, content_cards: [...] }` |
| `401` | Auth error |
| `402` | Missing inputs |
| `403` | Not trip owner |
| `502` | Server error |

---

## Service (`TripContentsService`)

Singleton. Depends on:
- `TripContentsDatabaseService` — PostgreSQL queries
- `TripPolicy` — trip ownership lookup
- `S3Service` — presigned URL generation and media deletion
- `TokenService`
- `ErrorHandler`
- `TripRepository` - access model from database 

---

### Key Methods

#### `generate_presign_url_for_medias(trip_id, user_id, content_cards)`
Validates trip ownership, then mutates each `content_card` dict in-place to add a `presign_url` field. Returns the modified list.

#### `handle_sync(trip_id, user_id, content_cards)`
Iterates cards and dispatches to `_insert_card_to_database` or `_delete_content_card` based on `event`. Collects failures and returns them if any exist.

#### `_insert_card_to_database(user_id, trip_id, card_data)`
Inserts a single content card into PostgreSQL. Converts `time_stamp` from ms to `timestamptz`. Required fields: `uuid`, `time_stamp`.

#### `_delete_content_card(card_data, trip_id)`
- Fetches the existing card from the DB to get `media_path` and `media_type`
- Deletes from S3 if `photo` or `video`
- Deletes from PostgreSQL
- Returns `404` if card not found

#### `get_all_content_card_from_trip_id(trip_id, user_id, client_hash)`
- Validates ownership
- Compares `client_hash` against `server_hash` — returns `304` on match
- Fetches all cards, replaces `media_path` with temp S3 URI for media types
- Converts timestamps to ms

#### `requestTripContentsHash(user_id, trip_id)`
Returns `{ hash }` from `TripContentsDatabase.generate_contents_hash`.

#### `get_all_content_card_meta_data_from_trip_id(trip_id, user_id)`
Returns raw content card rows without URL generation or timestamp conversion.

---

## Notes

- `ms_to_timestamptz` / `timestamptz_to_ms` are imported from `utils` for timestamp conversion
- S3 path format: `trips/{trip_id}/{media_path}`
- Hash comparison uses `generate_contents_hash` (MD5 of sorted media IDs) — `null` hash on server always triggers full pull
- `handle_sync` uses a shadow variable `request` inside the loop that shadows Flask's `request` — be careful if refactoring
