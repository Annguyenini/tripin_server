# Trip Content Data Shapes

## Return Trip Content Shape

```ts
type ReturnTripContent = {
  altitude: number;
  city: string;
  country: string;
  event: string;
  heading: number;
  id: number;
  iso_country_code: string;
  latitude: number;
  longitude: number;
  media_id: string;
  media_path: string | null;      // S3-generated media URL
  media_type: string;
  modified_time: number;          // Unix timestamp in milliseconds
  region: string;
  speed: number;
  time_stamp: number;             // Unix timestamp in milliseconds
  trip_id: number;
  trip_name: string;
  uuid: string;                   // UUID
};
```

## Stored Trip Content Shape

```ts
type StoredTripContent = {
  altitude: REAL;
  city: string;
  country: string;
  event: string;
  heading: REAL;
  id: number;
  iso_country_code: string;
  latitude: REAL;
  longitude: REAL;
  media_id: string;
  media_path: string | null;      // Internal media path prefix
  media_type: string;
  modified_time: timestamptz;
  region: string;
  speed: REAL;
  time_stamp: timestamptz;
  trip_id: number;
  trip_name: string;
  uuid: string;                   // UUID
};
```

# Field Descriptions

| Field | Description |
|---------|-------------|
| `altitude` | Altitude of the recorded location, typically in meters above sea level. |
| `city` | City associated with the recorded location. |
| `country` | Country associated with the recorded location. |
| `event` | Event or activity associated with this trip content entry. |
| `heading` | Direction of travel in degrees relative to true north. |
| `id` | Internal database identifier for the trip content record. |
| `iso_country_code` | ISO 3166 country code (e.g. `US`, `JP`, `FR`). |
| `latitude` | Latitude coordinate of the recorded location. |
| `longitude` | Longitude coordinate of the recorded location. |
| `media_id` | Unique identifier for the associated media file. | (purpose to help identify the media with app local data to perform action like delete) ex. (photo:file:///data/user/0/com.anonymous.tripin/files/media/9afa2244-2e17-40a9-bfaf-f0aa3662b51f.jpg)
| `media_path` | Media file location. API responses return a generated S3 URL, while stored data uses the internal path prefix. Returns `null` if no media is attached. | 
| `media_type` | Type of media associated with the entry (e.g. `image`, `video`, `audio`). |
| `modified_time` | Timestamp updated whenever the trip content entry is modified. |
| `region` | Administrative region, state, or province associated with the location. |
| `speed` | Recorded movement speed at the time of capture. |
| `time_stamp` | Original timestamp when the content was captured or recorded. |
| `trip_id` | Identifier of the trip this content belongs to. |
| `trip_name` | Name of the associated trip. |
| `uuid` | Globally unique identifier for the content entry. |
