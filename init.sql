CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Set trigram similarity threshold
SELECT set_limit(0.3);

CREATE TABLE problems (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(20),
    tags TEXT[],

    -- Full-text search vector with truncation to avoid tsvector size limits
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english'::regconfig,
            LEFT(
                coalesce(title, '') || ' ' ||
                coalesce(description, ''),
                500000
            )
        )
    ) STORED,

    embedding vector(384),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_problems_fts ON problems USING GIN (search_vector);
CREATE INDEX idx_problems_trgm ON problems USING GIN (title gin_trgm_ops);
CREATE INDEX idx_problems_platform ON problems (platform);
-- HNSW index created AFTER embeddings are loaded (in generate_embeddings.py)
