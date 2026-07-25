# tripin_server

Backend server for the **Tripping** application.

The server is responsible for:

- User authentication and authorization
- Trip management
- Trip content management
- Data synchronization
- Friendships
- Real-time event triggering
- Caching and rate limiting
- User data management

Architecture diagrams and technical documentation can be found in the `/architectures` directory.

---

# Tech Stack

| Layer | Technology |
|---------|---------|
| Language | Python |
| Framework | Flask |
| Database | PostgreSQL |
| Object Storage | AWS S3 |
| Cache | Redis |
| CI/CD | GitHub Actions |
| Containerization | Docker |
| Testing | pytest |
| Monitoring | Internal logging service |

Monitoring service:

:contentReference[oaicite:0]{index=0}

---

# Infrastructure

## Containers

The application runs using the following containers:

1. PostgreSQL
2. Redis
3. tripin_server

---

# Environment Variables

An example environment configuration can be found in:

```text
/architectures
```

---

# Authentication

Most endpoints require a valid JWT access token.

## Authorization Header

```http
Authorization: Bearer <access_token>
```

---

## Token Refresh

Access tokens can be refreshed through:

```http
POST /auth/request-access-token
```

using a valid refresh token.

---

## ETag Support

Most `GET` endpoints support ETag caching.

Example:

```http
If-None-Match: "<etag>"
```

When the resource has not changed, the server responds with:

```http
304 Not Modified
```

---

# API Modules

## Authentication

Base path:

```text
/auth
```

Handles:

- Login
- Registration
- Access token refresh
- Logout
- Account verification

---

## Trips

Base path:

```text
/trip
```

Handles:

- Create trip
- Update trip
- Delete trip
- Trip permissions
- Trip metadata

---

## Trip Contents

Base path:

```text
/trip-contents
```

Handles:

- Activities
- Notes
- Locations
- Media references
- Content management

---

## Users

Base path:

```text
/user
```

Handles:

- User profile
- User settings
- User data

---

## Synchronization

Base path:

```text
/ sync
```

Handles:

- Client synchronization
- Incremental updates
- Conflict resolution

---

## Trip View

Base path:

```text
/trip-view
```

Handles:

- Read-only trip access
- Public trip data
- Shared trip views

---

# Documentation

## API Documentation

Detailed endpoint documentation can be found in:

```text
/architectures
```

---

## Friendships

Friendship architecture and data model:

```text
/architectures/friendships
```

Includes:

- Database schema
- Relationship lifecycle
- Friend request flow
- Event integration

---

## Rate Limiting

Rate limiter architecture and limits:

```text
/architectures/ratelimiter
```

Includes:

- Per-endpoint limits
- Redis implementation
- Enforcement strategy

---

## Caching

Caching architecture:

```text
/architectures/caching
```

Includes:

- ETag generation
- Redis caching
- Cache invalidation

---

## Data Shapes

Shared request and response schemas:

```text
/architectures/data_shapes
```

---

# Event System

A dedicated microservice is responsible for WebSocket communication and event delivery.

## Stack

- FastAPI
- Redis Pub/Sub
- Socketio

## Responsibilities

- Maintain WebSocket connections
- Subscribe to Redis events
- Deliver events to connected users
- Handle real-time notifications

The main Flask server publishes events, while the event server distributes them to clients.

Documentation:

```text
/architectures/events
```

---

# Architecture Documentation

All architecture diagrams, flowcharts, schemas, and service documentation are available in:

```text
/architectures
```

This includes:

- API documentation
- Database designs
- Friendships
- Events
- Rate limiting
- Caching
- Data shapes
- Service communication diagrams
