# Trip Data Shapes

## Trip Data Shape

```ts
type TripData = {
  active: boolean;
  content_modified_time: number; // Unix timestamp in milliseconds
  created_time: number;          // Unix timestamp in milliseconds
  ended_time: number;            // Unix timestamp in milliseconds
  event: string;
  id: number;
  image: string | null;          // S3-generated trip cover URL
  modified_time: number;         // Unix timestamp in milliseconds
  privacy: string;
  trip_id: number;
  trip_name: string;
  user_id: number;
};
```

## Stored Trip Data Shape

```ts
type StoredTripData = {
  active: boolean;
  content_modified_time: timestamptz;
  created_time: timestamptz;
  ended_time: timestamptz;
  event: string;
  id: number;
  image: string | null;          // Cover image path prefix
  modified_time: timestamptz;
  privacy: string;
  trip_id: number;
  trip_name: string;
  user_id: number;
};
```

## Trip Data From Other User Shape

```ts
type TripDataFromOtherUser = {
  created_time: timestamptz;
  ended_time: timestamptz;
  id: number;
  image: string | null;          // Cover image path prefix
  trip_id: number;
  trip_name: string;
  user_id: number;
  author: string;
};
```

# Field Descriptions

| Field | Description |
|---------|-------------|
| `active` | Indicates whether the trip is currently active. |
| `content_modified_time` | Timestamp updated whenever trip content changes (e.g. itinerary, posts, locations, media). Useful for cache invalidation and synchronization. |
| `created_time` | Time when the trip was created. |
| `ended_time` | End date and time of the trip. |
| `event` | Event type or category associated with the trip. |
| `id` | Internal database identifier for the trip record. |
| `image` | Trip cover image. Returns a generated S3 URL in API responses and stores the internal path prefix in the database. Returns `null` if no cover image exists. |
| `modified_time` | Timestamp updated whenever any trip metadata is modified. |
| `privacy` | Visibility setting for the trip (e.g. `public`, `private`, `friends`). |
| `trip_id` | Public-facing unique trip identifier. |
| `trip_name` | Name of the trip. |
| `user_id` | Identifier of the trip owner. |
| `author` | Display name or username of the trip owner when viewing trips from other users. |
