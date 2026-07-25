# Friendship Events Documentation

## Overview

Friendship events represent all actions that can occur during the lifecycle of a friendship between users.

These events are emitted whenever a friendship-related action happens, allowing other systems such as notifications, real-time updates, activity tracking, and analytics to react accordingly.

---

## Friendship Event Enum

```typescript
enum FriendshipEvent {
    FRIEND_REQUEST = 'friend_request',
    FRIEND_REMOVED = 'friend_removed',
    FRIEND_REJECT = 'friend_reject',
    FRIEND_CANCEL = 'friend_cancel',
    FRIEND_ACCEPT = 'friend_accept'
}
```

---

# Events

## FRIEND_REQUEST

**Event:**

```text
friend_request
```

### Description

Triggered when a user sends a friend request to another user.

### Example

```
User A → sends friend request → User B

Event:
FRIEND_REQUEST
```

### Result

- A pending friend request is created.
- The receiver may accept or reject the request.
- Notifications may be sent to the receiver (incl. push notification).

---

## FRIEND_ACCEPT

**Event:**

```text
friend_accept
```

### Description

Triggered when a user accepts an incoming friend request.

### Example

```
User B → accepts request from User A

Event:
FRIEND_ACCEPT
```

### Result

- The friendship becomes active.
- Both users appear in each other's friend lists.
- Friendship notifications may be sent (incl. push notification).

---

## FRIEND_REJECT

**Event:**

```text
friend_reject
```

### Description

Triggered when a user rejects an incoming friend request.

### Example

```
User B → rejects request from User A

Event:
FRIEND_REJECT
```

### Result

- The pending request is removed.
- No friendship is created.
- - Friendship notifications may be sent.

---

## FRIEND_CANCEL

**Event:**

```text
friend_cancel
```

### Description

Triggered when a user cancels a friend request they previously sent.

### Example

```
User A → cancels request to User B

Event:
FRIEND_CANCEL
```

### Result

- The pending request is removed.
- The receiver can no longer accept the canceled request.
- Friendship notifications may be sent.

---

## FRIEND_REMOVED

**Event:**

```text
friend_removed
```

### Description

Triggered when a user removes an existing friend.

### Example

```
User A → removes User B from friends

Event:
FRIEND_REMOVED
```

### Result

- The friendship connection is deleted.
- Both users are no longer connected.
- Friend lists are updated.
- Friendship notifications may be sent.


---

# Friendship Lifecycle

```
                 FRIEND_REQUEST
                       |
                       |
          +------------+------------+
          |                         |
          v                         v
   FRIEND_ACCEPT             FRIEND_REJECT
          |                         |
          v                         v
 Friendship Created          Request Removed
          |
          |
          v
  FRIEND_REMOVED
          |
          v
 Friendship Deleted


FRIEND_REQUEST
       |
       v
FRIEND_CANCEL
       |
       v
Request Cancelled
```

---

# Event Payload Example

A friendship event should include enough information for listeners to process the change.

Example:

```json
{
    "event": "friend_accept",
    "target_user_id": "user_123",
    "avatar": "...",
    "display_name": "user",
    "timestamp": "2026-07-19T12:00:00Z"
}
```

---

# Event Handling Rules

## 1. Emit After Successful Changes

Events should only be emitted after the friendship state has successfully changed.

Example:

```
Update Database
        |
        v
Confirm Success
        |
        v
Emit Event
```

---

## 2. Events Are Actions

Events describe something that already happened.

Correct:

```
friend_accept
friend_removed
friend_request
```

Incorrect:

```
accept_friend
remove_friend
send_friend_request_action
```

---

## 3. Event Consumers

Possible systems that can consume friendship events:

- Notification service
- WebSocket / real-time service
- Activity feed
- Analytics
- Audit logs
- Achievement systems

---

# Event Summary

| Enum | Event | Description |
|---|---|---|
| `FRIEND_REQUEST` | `friend_request` | A user sends a friend request |
| `FRIEND_ACCEPT` | `friend_accept` | A user accepts a friend request |
| `FRIEND_REJECT` | `friend_reject` | A user rejects a friend request |
| `FRIEND_CANCEL` | `friend_cancel` | A user cancels a sent request |
| `FRIEND_REMOVED` | `friend_removed` | A user removes an existing friend |

---

# Notes

- Every friendship state change should emit exactly one event.
- Event names should remain stable to avoid breaking consumers.
- Event handlers should safely handle duplicate events.
- Friendship events should only represent completed actions.
