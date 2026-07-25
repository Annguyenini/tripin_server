# User Module

## Overview

Handles user data retrieval and avatar management — fetching profile data and a two-step presigned URL flow for uploading avatars to S3.

---

## Routes (`UsersRoutes`)

All routes require JWT authentication.

| Method | Endpoint | Handler |
|--------|----------|---------|
| `GET` | `/<user_id>` | `get_user_data` |
| `GET` | `/search?keywords=[keywords]&with-relationships =[boolean]` | `search_user` |

---

### `GET /get-user-data`

Fetch the user's profile data, required authentication. Supports caching.

**Headers**
- `Authorization: Bearer <access_token>`

**Response**
  - `User Data shape : {"user_data": {
          "avatar": "...",
          "display_name": "...",
          "user_id": int,
          "user_name": "..."
      }}`
| Code | Body |
|------|------|
| `200` | `{ user_data: {...}, code: "successfully" }` |
| `304` | Not modified |
| `401` | Auth error |
| `500` | User not found or server error |

If the user has an avatar, it's replaced with a temporary S3 URI before returning.

---

### `GET /search-user/keywords=[...]$with-realtionships=[...]`
| params  | purpose |
|------|------|
|keywords | keywords for search, require 3 or more letters
|with-relationships | request a relationship check between users in result list and the requestor. Required requestor to be authenticated
Phase 1 of avatar update. Generates an S3 presigned upload URL and a `pending_token` to track the pending upload.

**Headers**
- `Authorization: Bearer <access_token>` (optional, will throw code 400 if not include in requests that want the relationship check)

**Response**

| Code | Body |
|------|------|
| `201` | `{ code: "successfully", user_data:{user_data shape and friendships shape}  }` |
| `400` | Missing inputs |
| `401` | Invalid token |
| `500` | Failed to generate presigned URL |

The `pending_token` is stored in Redis (TTL 300s) mapping to the S3 key. Upload must be completed directly to S3 via `presign_url` before calling the next endpoint.

**Constraints**
- Content type: `image/jpeg` only
- Max size: 5 MB
- S3 key format: `{AVATAR_DIR}user{user_id}_avatar.jpg`

---

### `POST /complete-update-avatar`

Phase 2 of avatar update. Confirms the upload happened, then updates the avatar path in PostgreSQL.

**Headers**
- `Authorization: Bearer <access_token>`

**Request Body**
```json
{
  "pending_token": "string",
  "modified_time": 1700000000000
}
```

**Response**

| Code | Body |
|------|------|
| `200` | `{ code: "successfully" }` |
| `400` | Missing inputs |
| `401` | Invalid token |
| `404` | `pending_token` not found or S3 object missing |
| `500` | DB update failed or S3 unreachable |

Flow: looks up `pending_token` in Redis → verifies the S3 object exists → updates DB with up to 2 retries → deletes token from Redis → writes audit log.

---

## Service (`UserService`)

Singleton. Depends on:
- `UserDataDataBaseService` — user CRUD
- `S3Service` — presigned URL generation and object existence check
- `UserdataEtag` — ETag generation from `modified_time`
- `AuthEtagService`
- `Cache` — Redis for pending token storage
- `UserdataAudit` — audit logging
- `ErrorHandler`

---

### Key Methods

#### `get_user_data_from_database(user_id, client_etag)`
Fetches user row, generates ETag from `modified_time`, returns `304` on match. Replaces `avatar` field with a temporary S3 URI if set.

#### `request_user_avatar_upload_presign_url(user_id)`
Generates a presigned S3 upload URL restricted to `image/jpeg` and 5 MB max. Stores the S3 key in Redis under a random `pending_token` (TTL 300s) and returns both to the client.

#### `process_update_user_avatar(user_id, pending_token, modified_time, ip_address)`
- Retrieves S3 key from Redis via `pending_token`
- Verifies the object exists in S3 (`check_s3_object_exists`)
- Updates `avatar` path and `modified_time` in PostgreSQL (up to 2 retries)
- Deletes `pending_token` from Redis
- Writes an audit entry via `UserdataAudit.change_user_avatar_audit`

---

## Notes

- Avatar S3 key is deterministic: `{AVATAR_DIR}user{user_id}_avatar.jpg` — re-uploading overwrites the previous image
- `pending_token` format: `update_avatar::{user_id}::{uuid4}`
- DB update uses a retry loop (`MAX_RETRY = 2`) before returning a 500
- Audit log is non-blocking — a failure there won't fail the request
- `_user_jwt_validation_policy()` raises `PermissionError` on invalid token (vs `_get_authenticated_user()` which returns an error dict)
