-- ============================================================
-- MemoGraph — Phase 1B
-- Initial PostgreSQL Schema
-- ============================================================

-- ============================================================
-- 1. USERS
-- ============================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- 2. SOURCES
-- ============================================================

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    CONSTRAINT sources_type_valid
        CHECK (
            source_type IN (
                'PDF',
                'TXT',
                'MD',
                'CHAT_EXPORT',
                'WEB_PAGE'
            )
        )
);

-- Only active sources participate in duplicate detection per user.
CREATE UNIQUE INDEX idx_sources_user_file_hash
ON sources (user_id, file_hash)
WHERE deleted_at IS NULL;

-- Active sources belonging to a user, newest first.
CREATE INDEX idx_sources_user_active
ON sources (user_id, created_at DESC)
WHERE deleted_at IS NULL;


-- ============================================================
-- 3. JOBS
-- ============================================================

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    source_id UUID NOT NULL REFERENCES sources(id),
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    retry_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT jobs_retry_count_non_negative
        CHECK (retry_count >= 0),

    CONSTRAINT jobs_status_valid
        CHECK (
            status IN (
                'QUEUED',
                'STARTED',
                'PROCESSING',
                'COMPLETED',
                'FAILED'
            )
        )
);

CREATE INDEX idx_jobs_user_created
ON jobs (user_id, created_at DESC);

CREATE INDEX idx_jobs_source
ON jobs (source_id);


-- ============================================================
-- 4. MEMORIES
-- ============================================================

CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    source_id UUID NOT NULL REFERENCES sources(id),
    summary TEXT NOT NULL,
    memory_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    CONSTRAINT memories_type_valid
        CHECK (
            memory_type IN (
                'FACT',
                'PREFERENCE',
                'EVENT',
                'CODE_SNIPPET'
            )
        )
);

CREATE INDEX idx_memories_source_active
ON memories (source_id, created_at DESC)
WHERE deleted_at IS NULL;

CREATE INDEX idx_memories_user_active
ON memories (user_id, created_at DESC)
WHERE deleted_at IS NULL;


-- ============================================================
-- 5. CHUNKS
-- ============================================================

CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    source_id UUID NOT NULL REFERENCES sources(id),
    memory_id UUID NOT NULL REFERENCES memories(id),
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    token_count INT NOT NULL,
    embedding_model VARCHAR(100) NOT NULL DEFAULT 'all-MiniLM-L6-v2',
    embedding_version VARCHAR(20) NOT NULL DEFAULT 'v1',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    CONSTRAINT chunks_index_non_negative
        CHECK (chunk_index >= 0),

    CONSTRAINT chunks_token_count_positive
        CHECK (token_count > 0)
);

CREATE INDEX idx_chunks_memory_active
ON chunks (memory_id)
WHERE deleted_at IS NULL;

CREATE INDEX idx_chunks_source_active
ON chunks (source_id)
WHERE deleted_at IS NULL;

CREATE INDEX idx_chunks_user_active
ON chunks (user_id)
WHERE deleted_at IS NULL;


-- ============================================================
-- 6. ENTITIES
-- ============================================================

CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    CONSTRAINT entities_name_lowercase
        CHECK (name = LOWER(name)),

    CONSTRAINT entities_type_valid
        CHECK (
            entity_type IN (
                'PERSON',
                'TECHNOLOGY',
                'CONCEPT',
                'ORGANIZATION',
                'LOCATION'
            )
        )
);

-- Canonical entity lookup per user.
CREATE INDEX idx_entities_user_name
ON entities (user_id, name)
WHERE deleted_at IS NULL;

CREATE INDEX idx_entities_user_active
ON entities (user_id, created_at DESC)
WHERE deleted_at IS NULL;


-- ============================================================
-- 7. UPDATED_AT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_sources_updated_at
BEFORE UPDATE ON sources
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_jobs_updated_at
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_memories_updated_at
BEFORE UPDATE ON memories
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_chunks_updated_at
BEFORE UPDATE ON chunks
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER set_entities_updated_at
BEFORE UPDATE ON entities
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();