# User Data Shapes

## Return User Data Shape

```ts
type ReturnUserData = {
  avatar: string | null;          // S3-generated profile picture URL
  created_time: number;           // Unix timestamp in milliseconds
  display_name: string;
  user_name: string;
  email: string;
  id: number;
  modified_time: number;          // Unix timestamp in milliseconds
  provider: string;
  provider_id: string;
  role: string;
  trips_modified_time: number;    // Unix timestamp in milliseconds
};
```

## Stored User Data Shape

```ts
type StoredUserData = {
  avatar: string | null;          // Avatar path prefix
  created_time: timestamptz;
  display_name: string;
  user_name: string;
  email: string;
  id: number;
  modified_time: timestamptz;
  password: string;              // Hashed password
  provider: string;
  provider_id: string;
  role: string;
  trips_modified_time: timestamptz;
};
```

## Other User Data Shape

```ts
type PublicUserData = {
  avatar: string | null;          // Avatar path prefix
  display_name: string;
  user_name: string;
  id: number;
};
```

# Field Descriptions

| Field | Description |
|---------|-------------|
| `avatar` | Avatar image path. Returns `null` if no avatar exists. Returned data uses a generated S3 URL, while stored data uses the internal path prefix. |
| `created_time` | Time when the account was created. |
| `display_name` | User's preferred display name. |
| `user_name` | Unique username. |
| `email` | User email address. |
| `modified_time` | Time updated whenever the user profile is modified. |
| `password` | Hashed password. Only stored internally and should never be returned to clients. |
| `provider` | External authentication provider name (e.g. `google`, `apple`). |
| `provider_id` | Unique identifier assigned by the external provider. |
| `role` | User role within the system. |
| `trips_modified_time` | Timestamp updated whenever the user's trips change. Useful for ETag generation, caching, or change detection. |
