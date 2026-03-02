-- init.sql
CREATE SCHEMA IF NOT EXISTS tripin_auth;
CREATE SCHEMA IF NOT EXISTS tripin_trips;

-- Users table

CREATE TABLE IF NOT EXISTS tripin_auth.userdata (
    id SERIAL PRIMARY KEY, 
    email TEXT,
    display_name TEXT,
    user_name TEXT, 
    password TEXT,
    created_time TIMESTAMP NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    avatar TEXT, 
    etag TEXT, 
    trips_data_version BIGINT DEFAULT 1, 
    trips_data_etag TEXT, 
    userdata_version BIGINT DEFAULT 0);

CREATE TABLE IF NOT EXISTS tripin_auth.tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tripin_auth.userdata(id) ON DELETE CASCADE,
    user_name TEXT NOT NULL,
    token TEXT NOT NULL,
    issued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expired_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE
    );

-- Trips table
CREATE TABLE IF NOT EXISTS tripin_trips.trips_table (
    id SERIAL PRIMARY KEY,
    trip_name TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES tripin_auth.userdata(id) ON DELETE CASCADE,
    created_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_time TIMESTAMPTZ,
    active BOOLEAN NOT NULL DEFAULT FALSE,
    image TEXT,
    etag TEXT,
    trip_coordinates_version BIGINT DEFAULT 0,
    trip_medias_version BIGINT DEFAULT 0,
    trip_informations_version BIGINT DEFAULT 0
);

-- Trip coordinates
CREATE TABLE IF NOT EXISTS tripin_trips.trip_coordinates (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES tripin_trips.trips_table(id) ON DELETE CASCADE,
    altitude REAL NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    speed REAL NOT NULL,
    heading REAL NOT NULL,
    time_stamp BIGINT NOT NULL,
    batch_version BIGINT DEFAULT 0
);

-- Trip medias
CREATE TABLE IF NOT EXISTS tripin_trips.trip_medias (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER NOT NULL REFERENCES tripin_trips.trips_table(id) ON DELETE CASCADE,
    media_type TEXT,
    media_path TEXT NOT NULL,
    longitude REAL,
    latitude REAL,
    version BIGINT DEFAULT 0,
    time_stamp BIGINT NOT NULL
);
