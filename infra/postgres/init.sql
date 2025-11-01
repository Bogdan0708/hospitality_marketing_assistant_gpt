CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS instagram_media (
    id TEXT PRIMARY KEY,
    caption TEXT,
    media_type TEXT,
    media_url TEXT,
    timestamp TIMESTAMPTZ,
    like_count INT,
    comments_count INT,
    inserted_at TIMESTAMPTZ DEFAULT NOW()
);
