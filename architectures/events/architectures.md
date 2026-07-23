# Redis WebSocket Notification Architecture

## Overview

The WebSocket system is separated into two services:

* **Main Server (this)**

  * Handles application logic.
  * Processes user actions.
  * Publishes WebSocket events to Redis.
  * Does **not** maintain WebSocket connections.

* **Events Server (fastapi)**

  * Maintains all WebSocket connections.
  * Subscribes to Redis Pub/Sub channels.
  * Receives events from Redis and forwards them to connected clients.
  * Authenticates with the Main Server before starting.

* **Redis**

  * Acts as the communication layer between services.
  * Delivers events from the Main Server to the Events Server.

---

# Architecture

```text
                    +------------------+
                    |    Main Server   |
                    +------------------+
                              |
                              | Publish Event
                              v
                    +------------------+
                    |      Redis       |
                    |      Pub/Sub     |
                    +------------------+
                              |
                              | Subscribe
                              v
                    +------------------+
                    |   Events Server  |
                    +------------------+
                              |
                              | WebSocket
                              v
                    +------------------+
                    |      Client      |
                    +------------------+
```

---

# Service Authentication

Before handling WebSocket events, the Events Server must authenticate with the Main Server.

## Authentication Flow

```text
Events Server
      |
      | Service Token
      v
Main Server
      |
      | Validate Token
      v
Authentication Success
      |
      v
WebSocket Service Enabled
```

## Validation Process

1. Events Server starts.
2. Events Server sends its service token to the Main Server.
3. Main Server validates the token.
4. If validation succeeds:

   * Events Server is authorized.
   * WebSocket processing begins.
5. If validation fails:

   * Events Server must not accept or process events.

## Auth Payload
```json
{
  "auth":{
    "access_token":...
  }
}

---

# Redis Event Payload

All WebSocket notifications published to Redis must follow the structure below.

```json
{
  "room_id": "user:[user_id]",
  "event_type": "[event_type]",
  "data": {
    "...": "..."
  }
}
```

---

# Payload Fields

## room_id

Unique room identifier.

### Format

```text
user:[user_id]
```

### Examples

```text
user:1
user:42
user:123
```

### Description

The Events Server uses this value to determine which connected user should receive the event.

---

## event_type

Type of WebSocket event being delivered.

### Reference

See:

```text
web_socket/friendships.events.md
```

### Examples

```text
friend_request
friend_accept
```

---

## data

Event-specific payload.

### Description

Contains the data required by the client to process the event.

### Example

```json
{
  "sender_id": "123",
  "sender_username": "john"
}
```

---

# Example Events

## Friend Request

```json
{
  "room_id": "user:456",
  "event_type": "friend_request",
  "data": {
    "sender_id": "123",
    "sender_username": "john"
  }
}
```




---

# Redis Channel

Recommended channel:

```text
notifications
```

---

# Publishing Events

The Main Server publishes events to Redis.

Example:

```typescript
await redis.publish(
  "notifications",
  JSON.stringify({
    room_id: "user:123",
    event_type: "friend_request",
    data: {
      sender_id: "456"
    }
  })
);
```

---

# Event Delivery Flow

```text
User Action
     |
     v
Main Server
     |
     | Publish Event
     v
Redis Pub/Sub
     |
     | Receive Event
     v
Events Server
     |
     | Find Connected Room
     v
WebSocket Client
```

---

# Events Server Processing

When a Redis message is received:

1. Deserialize the payload.
2. Validate required fields.
3. Locate the target room using `room_id`.
4. Send the event to all active connections in the room.
5. Ignore malformed payloads.

---

# Validation Rules

## Required Fields

```text
room_id
event_type
data
```

All fields are required.

---

## room_id

Must follow:

```text
user:[user_id]
```

---

## event_type

Must exist in:

```text
web_socket/event_types.md
```

---

## data

Must be a JSON object.

Valid:

```json
{
  "key": "value"
}
```

Invalid:

```json
"string"
```

```json
123
```

```json
null
```

---

# Summary

* The Main Server is responsible for triggering WebSocket events.
* Redis Pub/Sub is used as the communication layer.
* The Events Server maintains all WebSocket connections.
* The Events Server subscribes to Redis and forwards events to clients.
* Service authentication is required before the Events Server becomes active.
* All events must follow the standard Redis payload structure.
