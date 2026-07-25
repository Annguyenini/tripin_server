# Friendship Database Schema Design

## Overview

The friendship system stores all relationships in a single table.

A friendship relationship is represented by a unique row between two users.

### Design Goals

- Prevent duplicate relationships.
- Support pending friend requests.
- Support accepted friendships.
- Support request rejection.
- Support request cancellation.
- Allow efficient lookups and updates.

---

# Table

**Schema**

```sql
tripin_friendships.friendships_table
```

## Columns

| Column | Type | Description |
|----------|----------|----------|
| user_id_1 | INT | Smaller user ID |
| user_id_2 | INT | Larger user ID |
| status | REL_STA | Current relationship status |
| time | TIMESTAMPTZ | Relationship timestamp |

---

# Primary Key

```sql
PRIMARY KEY (user_id_1, user_id_2)
```
This guarantees that only one relationship can exist between two users.

---

# User ID Ordering Rule

## Constraints

```sql
user_order_check Check (user_id_1< user_id_2)
```
To ensure uniqueness:

```text
user_id_1 = smaller user id
user_id_2 = larger user id
```

Example:

```text
User A = 5
User B = 3

Stored as:

user_id_1 = 3
user_id_2 = 5
```

Never:

```text
user_id_1 = 5
user_id_2 = 3
```

This prevents duplicate records such as:

```text
(3, 5)
(5, 3)
```

Only one row may exist for a pair of users.

---

# Relationship Status Enum

## REL_STA

```sql
ENUM (
    REQ_1,
    REQ_2,
    FRIEND
)
```

### REQ_1

Friend request initiated by `user_id_1`.

Example:

```text
user_id_1 sends request to user_id_2
```

---

### REQ_2

Friend request initiated by `user_id_2`.

Example:

```text
user_id_2 sends request to user_id_1
```

---

### FRIEND

Both users are friends.

Example:

```text
Friendship established.
```

---

# Rejection Behavior

There is no dedicated `REJECT` status.

When a friend request is rejected:

```text
DELETE ROW
```

The relationship record is removed entirely.

---

# Cancellation Behavior

There is no dedicated `CANCEL` status.

When a friend request is cancelled:

```text
DELETE ROW
```

The relationship record is removed entirely.

---

# Relationship Lifecycle

## Send Friend Request

```text
No Relationship
       |
       v
REQ_1 or REQ_2
```

---

## Accept Friend Request

```text
REQ_1 / REQ_2
       |
       v
    FRIEND
```

---

## Reject Friend Request

```text
REQ_1 / REQ_2
       |
       v
   DELETE ROW
```

---

## Cancel Friend Request

```text
REQ_1 / REQ_2
       |
       v
   DELETE ROW
```

---

## Remove Friend

```text
FRIEND
   |
   v
DELETE ROW
```

---

# Example Scenario

## Bob Sends Alice a Friend Request

### Users

```text
Bob user_id   = 3
Alice user_id = 5
```

Since `3 < 5`:

```text
user_id_1 = 3
user_id_2 = 5
```

### Request Created

| user_id_1 | user_id_2 | status | time |
|------------|------------|---------|---------|
| 3 | 5 | REQ_1 | current timestamp |

Explanation:

```text
REQ_1 means user_id_1 initiated the request.
```

Since Bob is `user_id_1`, Bob initiated the request.

---

## Alice Accepts

The existing row is updated.

| user_id_1 | user_id_2 | status | time |
|------------|------------|---------|---------|
| 3 | 5 | FRIEND | current timestamp |

Result:

```text
Bob and Alice are now friends.
```

---

## Alice Rejects

The row is removed.

```sql
DELETE FROM tripin_friendships.friendships_table
WHERE user_id_1 = 3
AND user_id_2 = 5;
```

Result:

```text
No relationship exists.
```

---

# Example States

## Pending Request From user_id_1

| user_id_1 | user_id_2 | status |
|------------|------------|---------|
| 3 | 5 | REQ_1 |

---

## Pending Request From user_id_2

| user_id_1 | user_id_2 | status |
|------------|------------|---------|
| 3 | 5 | REQ_2 |

---

## Active Friendship

| user_id_1 | user_id_2 | status |
|------------|------------|---------|
| 3 | 5 | FRIEND |

---

# Query Examples

## Check Friendship

```sql
SELECT *
FROM tripin_friendships.friendships_table
WHERE user_id_1 = LEAST($1, $2)
  AND user_id_2 = GREATEST($1, $2);
```

---

## Create Friend Request

Request sent by user_id_1:

```sql
INSERT INTO tripin_friendships.friendships_table (
    user_id_1,
    user_id_2,
    status,
    time
)
VALUES (
    3,
    5,
    'REQ_1',
    NOW()
);
```

---

## Accept Friend Request

```sql
UPDATE tripin_friendships.friendships_table
SET status = 'FRIEND',
    time = NOW()
WHERE user_id_1 = 3
  AND user_id_2 = 5;
```

---

## Remove Friendship

```sql
DELETE FROM tripin_friendships.friendships_table
WHERE user_id_1 = 3
  AND user_id_2 = 5;
```

---

# Summary

- One row represents one relationship.
- `(user_id_1, user_id_2)` is the primary key.
- `user_id_1` is always the smaller ID.
- `user_id_2` is always the larger ID.
- `REQ_1` means `user_id_1` initiated the request.
- `REQ_2` means `user_id_2` initiated the request.
- `FRIEND` means an established friendship.
- Rejections, cancellations, and friendship removals delete the row.
- Duplicate friendships cannot exist due to the primary key and user ordering rule.
