# Rate Limiter Configuration

This document defines all rate limiting rules enforced by the API.

---

# Rate Limiting Layers

The application uses a two-layer rate limiting strategy:

1. Reverse Proxy / Edge Protection
2. Application Process Rate Limiter

This protects against:

- DDoS attacks
- Brute-force authentication attempts
- Abuse of expensive endpoints
- Excessive API usage

---

# Reverse Proxy Rate Limiter

Applied before requests reach the application.

## Per-IP Limits

| Window | Limit |
|----------|----------|
| 1 second | 10 requests |
| 15 minutes | 9000 requests |

---

# Application Rate Limiter

Applied per endpoint after requests reach the application.

All limits are enforced per IP address.

---

# Auth Endpoints

| Method | Endpoint | Limit |
|----------|----------|----------|
| POST | `/login-via-token` | 5 / 15 mins |
| POST | `/login` | 5 / 15 mins |
| POST | `/signup` | 3 / 15 mins |
| POST | `/signup/verify` | 3 / 15 mins |
| POST | `/request-access-token` | 3 / 15 mins |
| POST | `/provider/<provider>` | 3 / 15 mins |
| POST | `/provider/complete-signup` | 3 / 15 mins |
| POST | `/reset-password` | 5 / 15 mins |
| POST | `/reset-password/verify` | 5 / 15 mins |
| POST | `/reset-password/reset` | 5 / 15 mins |

---

# Trip Endpoints

| Method | Endpoint | Limit |
|----------|----------|----------|
| POST | `/new-trip` | 15 / 15 mins |
| POST | `/trip-cover-upload-verification` | 15 / 15 mins |
| POST | `/end-trip` | 15 / 15 mins |
| POST | `/modify-trip-data` | 45 / 15 mins |
| DELETE | `/trip` | 45 / 15 mins |
| GET | `/all-trips/full` | 300 / 15 mins |
| GET | `/current-trip-id` | 300 / 15 mins |
| GET | `/trip/<trip_id>` | 450 / 15 mins |
| GET | `/trip-by-token/<token>` | 450 / 15 mins |

---

# Trip Contents Endpoints

| Method | Endpoint | Limit |
|----------|----------|----------|
| POST | `/sync` | 450 / 15 mins |
| POST | `/request-presign-urls` | 450 / 15 mins |
| GET | `/trip-contents-hash/<trip_id>` | 500 / 15 mins |
| GET | `/trip-contents-metadata/<trip_id>` | 500 / 15 mins |
| GET | `/all-contents` | 500 / 15 mins |

---

# User Endpoints

| Method | Endpoint | Limit |
|----------|----------|----------|
| GET | `/update-avatar-presign-url` | 45 / 15 mins |
| POST | `/complete-update-avatar` | 45 / 15 mins |
| GET | `/user-data` | 300 / 15 mins |

---

# Trip View Endpoints

| Method | Endpoint | Limit |
|----------|----------|----------|
| POST | `/generate-trip-view-link` | 75 / 15 mins |
| GET | `/<token>` | 300 / 15 mins |
| GET | `/<token>/contents` | 300 / 15 mins |

---

# User Settings Endpoints

| Method | Endpoint | Limit |
|----------|----------|----------|
| PATCH | `/user-settings` | 45 / 15 mins |
| GET | `/user-settings` | 300 / 15 mins |

---

# Friendship Endpoints

All friendship endpoints are limited to:

```text
300 requests / 15 minutes / IP
```

| Method | Endpoint |
|----------|----------|
| GET | `/friends` |
| GET | `/incoming-friend-list` |
| GET | `/outcoming-friend-list` |
| GET | `/overview` |
| POST | `/request-friend` |
| POST | `/accept-friend-request` |
| POST | `/reject-friend-request` |
| POST | `/cancel-friend-request` |
| POST | `/remove-friend` |
| DELETE | `/delete-relationship` |

---

# Public Users Endpoints

| Method | Endpoint | Limit |
|----------|----------|----------|
| GET | `/<user_id>`     | 300 / 15 mins |
| GET | `/search`        | 600 / 15 mins |

---

# Notes

- All limits are enforced per IP address.
- Limits are implemented using Redis-backed counters.
- Reverse proxy limits are evaluated before application limits.
- Exceeding a limit returns:

```http
429 Too Many Requests
```

- Rate limit counters automatically expire after their configured time window.
- Authentication endpoints have stricter limits to prevent brute-force attacks.
- Read-heavy endpoints have higher limits than write-heavy endpoints.
