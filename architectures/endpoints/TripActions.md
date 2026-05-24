# Trip Module

## Overview

Handles all core trip lifecycle operations — creating, fetching, updating, ending, and deleting trips.

---

## Routes (`TripRoute`)

All routes require JWT authentication unless otherwise noted.

| Method | Endpoint | Handler |
|--------|----------|---------|
| `POST` | `/new-trip` | `request_new_trip` |
| `GET` | `/all-trips/full` | `request_all_trips_data` |
| `GET` | `/current-trip-id` | `request_current_trip_id` |
| `POST` | `/end-trip` | `end_trip` |
| `POST` | `/trip` | `request_trip_data` |
| `GET` | `/trip-by-token/<token>` | `request_trip_data_by_shared_links` |
| `POST` | `/modify-trip-data` | `change_trip_data` |
| `DELETE` | `/trip` | `request_remove_trip` |

---

### `POST /new-trip`

Create a new trip. Uses `multipart/form-data` to support optional cover image.

**Form Fields**

| Field | Type | Required |
|-------|------|----------|
| `trip_name` | string | yes |
| `created_time` | ms timestamp | yes |
| `image` | file | no |

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully", trip_id }` |
| `400` | `{ code: "active_trip" }` — already on a trip |
| `400` | `{ code: "exists_trip_name" }` — name taken |
| `401` | Auth error |
| `500` | Cloud or DB failure |

If an image is provided and upload fails, the newly created trip is deleted via a rollback callback.

---

### `GET /all-trips/full`

Fetch all active trips for the authenticated user. Supports ETag caching.

**Headers**
- `If-None-Match` *(optional)* — client's cached ETag

**Response**

| Code | Body |
|------|------|
| `200` | `{ all_trip_data: [...], etag }` |
| `200` | `{ code: "empty" }` — no trips yet |
| `304` | ETag matched, use cached data |
| `401` | Auth error |
| `500` | Server error |

Each trip includes a temporary S3 URI for its cover image. Timestamps are in milliseconds.

---

### `GET /current-trip-id`

Returns the user's currently active trip ID, or `null` if not on a trip.

**Response**

| Code | Body |
|------|------|
| `200` | `{ current_trip_id: "string" \| null }` |
| `401` | Auth error |

---

### `POST /trip`

Fetch a single trip's data by ID. Supports ETag caching.

**Headers**
- `If-None-Match` *(optional)*

**Request Body**
```json
{ "trip_id": "string" }
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ trip_data: {...}, etag }` |
| `304` | Not modified |
| `400` | Trip not found or soft-deleted |
| `401` | Auth error |
| `403` | Not trip owner |

`trip_data` includes `trip_id` (alias of `id`), ms timestamps, and a temporary image URI.

---

### `GET /trip-by-token/<token>`

Fetch trip data via a shared link token. No JWT required. Token must be a 64-character SHA-256 hex string.

**Headers**
- `If-None-Match` *(optional)* — browser cache ETag

**Response**

| Code | Body |
|------|------|
| `200` | `{ trip_data }` + `ETag` header |
| `304` | `{ etag }` — data unchanged |
| `404` | Invalid or malformed token |
| `500` | Server error |

---

### `POST /modify-trip-data`

Update trip name and/or cover image. Uses `multipart/form-data`.

**Form Fields**

| Field | Type | Required |
|-------|------|----------|
| `trip_id` | string | yes |
| `modified_time` | ms timestamp | yes |
| `trip_name` | string | no |
| `image` | file | no |

At least one of `trip_name` or `image` must be provided.

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully" }` |
| `400` | Trip not found, duplicate name, or missing inputs |
| `401` | Auth error |
| `403` | Not trip owner |
| `500` | DB or cloud failure |

If S3 upload fails after a name change, the name is rolled back.

---

### `DELETE /trip`

Soft-delete a trip (sets `event = "remove"`). Cover image in S3 is NOT deleted.

**Request Body**
```json
{
  "trip_id": "string",
  "deleted_time": 1700000000000
}
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully" }` |
| `400` | Already removed or missing inputs |
| `401` | Auth error |
| `500` | DB failure |

---

### `POST /end-trip`

Mark a trip as ended.

**Request Body**
```json
{
  "trip_id": "string",
  "ended_time": 1700000000000
}
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully" }` or `{ code: "trip_ended" }` if already ended |
| `400` | Trip not found |
| `401` | Auth error |
| `403` | Not trip owner |
| `500` | DB failure |

---

## Service (`TripService`)

Singleton. Depends on:
- `TripDataBaseService` — primary trip CRUD
- `TripDatabaseService` — secondary trip queries
- `UserDataDataBaseService` — user-level `trips_modified_time` updates
- `S3Service` — cover image upload and temp URI generation
- `AllTripsDataEtag` / `TripDataEtag` — ETag generation and Redis caching
- `EtagService`, `Cache`, `InputValidation`, `ErrorHandler`, `TokenService`

---

### Key Methods

#### `process_new_trip(user_id, trip_name, created_time, image)`
Validates no active trip exists and trip name is unique, inserts the trip, optionally uploads a cover image to S3. Rollback deletes the trip from DB if S3 fails.

#### `end_a_trip(trip_id, user_id, ended_time)`
Validates trip exists, is still active, and is owned by the user, then updates `ended_time` in the DB.

#### `get_current_trip_id(user_id)`
Returns `current_trip_id` from the DB (or `null`).

#### `get_trip_data(user_id, trip_id, client_etag)`
Generates ETag from `modified_time` + hourly bucket. Returns `304` on match. Converts timestamps to ms and generates a temp S3 URI for the cover image.

#### `get_trip_data_from_token(client_etag, token)`
Same ETag logic as above but looks up trip via shared token. No ownership check.

#### `get_all_trip_data(user_id, want_images, client_etag)`
ETag is derived from `user.trips_modified_time` + hourly bucket. Converts all trips and optionally attaches temp image URIs.

#### `change_trip_data(new_trip_name, trip_id, user_id, modified_time, image)`
Updates name and/or image with rollback on failure. Updates both `trip.modified_time` and `user.trips_modified_time` to invalidate ETags.

#### `remove_trip(user_id, trip_id, deleted_time)`
Soft-delete via `event = "remove"`. Updates `user.trips_modified_time`.

#### `trip_owner_validation(user_id, trip_data)` *(private)*
Returns `bool` — checks `trip_data["user_id"] == user_id`.

---

## Notes

- ETag bucket resets hourly (`int(time.time() // 3600)`) to force S3 temp URL refresh
- `ms_to_timestamptz` / `timestamptz_to_ms` are defined in this module and shared with `TripContentsService`
- S3 cover image path is always `trips/{trip_id}/cover.jpg`
- `remove_trip` is a ghost/soft delete — S3 cover image is intentionally left in place
