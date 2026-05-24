# tripin_server

Backend server for the **Tripping** app. Built with Python/Flask, handles all client requests for trip management, content sync, user data, and authentication.

Architectures and service diagrams can be found in `/architectures`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Server | Python, Flask |
| Database | PostgreSQL, AWS S3 |
| Cache | Redis |
| Deploy | GitHub Actions, Docker |
| Tests | pytest |
| Monitor | internal tool can be found the repo https://github.com/Annguyenini/server_log
**Containers:** 3 — PostgreSQL, Redis, Server

---

## Environment Variables

example env file can be found in `/architectures`


---

## Auth

All protected routes require a JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens are refreshed via `/auth/request-access-token` using a refresh token. ETag-based caching is supported on most `GET` endpoints via the `If-None-Match` header.

---

## Endpoints

### Auth `/auth`


### Trip `/trip`


### Trip Contents `/trip-contents`


### User `/user`

### Sync `/sync`

### Trip View `/trip-view`

### All endpoints docs can be found in `/architectures`
