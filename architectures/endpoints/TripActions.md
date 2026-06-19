# Trip Module

## Overview

The **Trip Module** manages the full lifecycle of user trips, including
creation, retrieval, updates, completion, and deletion.\
It integrates PostgreSQL, Redis caching, ETag optimization, and AWS S3
for media storage.

------------------------------------------------------------------------

## Routes (`TripRoute`)

All routes require JWT authentication unless explicitly stated.

  ----------------------------------------------------------------------------------
  Method             Endpoint                          Description
  ------------------ --------------------------------- -----------------------------
  POST               /new-trip                         Create a new trip

  POST               /trip-cover-upload-verification   Verify uploaded trip cover
                                                       image

  GET                /all-trips/full                   Fetch all user trips

  GET                /current-trip-id                  Get active trip ID

  POST               /end-trip                         End an active trip

  POST               /trip                             Fetch single trip

  GET                /trip-by-token/`<token>`{=html}   Public shared trip access

  POST               /modify-trip-data                 Update trip details

  DELETE             /trip                             Soft delete trip
  ----------------------------------------------------------------------------------

------------------------------------------------------------------------

## POST /new-trip

Creates a new trip with optional cover image.

### Request

``` json
{
  "trip_name": "string",
  "created_time": 1700000000000,
  "image": true
}
```

### Responses

``` json
{
  "trip_id": "int",
  "presign_url": optional("string"),
  "pending_token": int
}
```
-   201: Trip created successfully - \
-   400: Active trip exists / duplicate name / invalid input\
-   401: Authentication error\
-   500: Server or storage failure

### Notes

-   One active trip per user enforced
-   Trip names must be unique per user
-   Optional S3 upload via presigned URL

------------------------------------------------------------------------

## POST /trip-cover-upload-verification

Verifies S3 upload and attaches cover image.

### Request

``` json
{
  "pending_token": "string",
  "modified_time": 1700000000000
}
```

### Responses

-   200: Image successfully linked\
-   400: Invalid or missing token\
-   500: Upload verification failure

------------------------------------------------------------------------

## GET /all-trips/full

Returns all trips for a user with caching and ETag support.

### Features

-   Redis caching (1 hour TTL)
-   ETag-based conditional responses
-   S3 temporary image URLs injected

### Responses

-   200: Trip list + ETag\
-   304: Not modified\
-   401: Authentication error\
-   500: Server error

------------------------------------------------------------------------

## GET /current-trip-id

Returns currently active trip ID.

``` json
{
  "current_trip_id": "string | null"
}
```

------------------------------------------------------------------------

## POST /trip

Fetch a single trip by ID.

### Request

``` json
{
  "trip_id": "string"
}
```

### Responses

-   200: Trip data\
-   304: Not modified (ETag match)\
-   400: Trip not found or deleted\
-   401: Authentication error\
-   403: Unauthorized access

------------------------------------------------------------------------

## GET /trip-by-token/`<token>`{=html}

Public access to trip via shared token.

### Requirements

-   64-character SHA256 token

### Responses

-   200: Trip data\
-   304: Cached version valid\
-   404: Invalid token\
-   500: Server error

------------------------------------------------------------------------

## POST /modify-trip-data

Updates trip name and/or cover image.

### Request

``` json
{
  "trip_id": "string",
  "trip_name": "string (optional)",
  "modified_time": 1700000000000,
  "image": true
}
```

### Responses

-   201: Update successful\
-   400: Invalid input or duplicate name\
-   401: Authentication error\
-   403: Unauthorized\
-   500: Server failure

------------------------------------------------------------------------

## DELETE /trip

Soft deletes a trip (S3 image retained).

### Request

``` json
{
  "trip_id": "string",
  "deleted_time": 1700000000000
}
```

### Responses

-   200: Deleted successfully\
-   400: Already removed or invalid\
-   401: Authentication error\
-   500: Database failure

------------------------------------------------------------------------

## POST /end-trip

Marks a trip as completed.

### Request

``` json
{
  "trip_id": "string",
  "ended_time": 1700000000000
}
```

### Responses

-   200: Success / already ended\
-   400: Trip not found\
-   401: Authentication error\
-   403: Unauthorized\
-   500: Server error

------------------------------------------------------------------------

## Architecture Notes

### Services Used

-   PostgreSQL (Trip storage)
-   Redis (Caching layer)
-   AWS S3 (Image storage)
-   ETag Service (HTTP optimization)

### Caching Strategy

-   Trip list cached per user
-   Individual trip cached per ID
-   Invalidated on any mutation

### ETag Strategy

-   Based on:
    -   Modified timestamp
    -   Hourly bucket system
-   Used for conditional GET requests

### Ownership Rule

All modifications require:

    trip.user_id == user_id

------------------------------------------------------------------------

## Storage Conventions

-   Cover image path:

```{=html}
<!-- -->
```
    trips/{trip_id}/cover.jpg

-   Soft delete:
    -   Trips are marked as removed
    -   Media is retained in S3
