-- ============================================================================
-- Stellar AI - Unified Canonical PostgreSQL Database Schema
-- Version: 001_initial_schema.sql
-- Single Source of Truth for both Express API Gateway and FastAPI Microservice
-- ============================================================================

-- Enable PostGIS / UUID if available (optional extensions)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ----------------------------------------------------------------------------
-- 1. Users Table (Core Identity & RBAC)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'user', -- 'admin', 'analyst', 'user'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ----------------------------------------------------------------------------
-- 2. Queries Table (Orchestration Jobs & Spatial Workflows)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS queries (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(64) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id VARCHAR(128),
    query_text TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed'
    geo_context JSONB DEFAULT '{}'::jsonb,
    modalities JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    error TEXT,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_queries_job_id ON queries(job_id);
CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_status ON queries(status);
CREATE INDEX IF NOT EXISTS idx_queries_started_at ON queries(started_at DESC);

-- ----------------------------------------------------------------------------
-- 3. Execution Traces Table (Audit Logs & Step Provenance)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS execution_traces (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL REFERENCES queries(job_id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL, -- 'job_started', 'tool_invoked', 'state_updated', etc.
    status VARCHAR(50),
    message TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_traces_job_id ON execution_traces(job_id);
CREATE INDEX IF NOT EXISTS idx_traces_event_type ON execution_traces(event_type);

-- ----------------------------------------------------------------------------
-- 4. Artifacts Table (Deliverables: GeoTIFFs, Change Masks, PDF Reports)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS artifacts (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(64) REFERENCES queries(job_id) ON DELETE CASCADE,
    artifact_type VARCHAR(100) NOT NULL, -- 'change_mask', 'audit_report', 'geojson_features'
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_artifacts_job_id ON artifacts(job_id);

-- ----------------------------------------------------------------------------
-- 5. Images Table (Satellite Raster Catalog & Metadata)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(64) UNIQUE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_format VARCHAR(50),
    modality VARCHAR(50), -- 'optical', 'sar', 'multispectral'
    width INTEGER,
    height INTEGER,
    band_count INTEGER,
    crs VARCHAR(100),
    resolution_x DOUBLE PRECISION,
    resolution_y DOUBLE PRECISION,
    bounds JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_images_image_id ON images(image_id);
CREATE INDEX IF NOT EXISTS idx_images_user_id ON images(user_id);

-- ----------------------------------------------------------------------------
-- 6. Spatial Regions of Interest (User Annotations & Saved AOIs)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS spatial_rois (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(64) REFERENCES queries(job_id) ON DELETE SET NULL,
    label VARCHAR(255),
    bbox_geojson JSONB NOT NULL,
    crs VARCHAR(100) DEFAULT 'EPSG:4326',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_spatial_rois_user_id ON spatial_rois(user_id);
