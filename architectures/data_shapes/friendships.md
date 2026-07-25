# Friendship Data Shapes

## Return Friendship Shape

```ts
type ReturnFriendship = {
  user_id1: number;
  user_id2: number;
  status: string;
  last_update: number; // Unix timestamp in milliseconds
};
```

## Stored Friendship Shape

```ts
type StoredFriendship = {
  user_id1: number;
  user_id2: number;
  status: string;
  last_update: timestamptz;
};
```

# Field Descriptions

| Field | Description |
|---------|-------------|
| `user_id1` | First user participating in the relationship. The exact meaning depends on the friendship relationship model defined in the Friendship documentation. |
| `user_id2` | Second user participating in the relationship. The exact meaning depends on the friendship relationship model defined in the Friendship documentation. |
| `status` | Relationship status between `user_id1` and `user_id2`. Valid values are defined by the friendship system (e.g. `FRIEND`, `REQ1`, `REQ2`). |
| `last_update` | Timestamp updated whenever the friendship relationship changes state or is modified. |
