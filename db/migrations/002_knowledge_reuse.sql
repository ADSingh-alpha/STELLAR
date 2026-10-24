-- ============================================================================
-- SatQuery AI - NODUS-Inspired Knowledge Reuse Layer Schema Migration
-- Version: 002_knowledge_reuse.sql
-- Enables persistent storage for Knowledge Cards and Knowledge Chains.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Knowledge Cards Table (Captured Insights, Analysis Results, Reusable Items)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_cards (
    id VARCHAR(64) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    summary TEXT NOT NULL,
    content TEXT,
    structured_data JSONB DEFAULT '{}'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    queue VARCHAR(50) NOT NULL DEFAULT 'default', -- 'default', 'quick', 'q1', 'q2', 'q3', 'q4'
    source_image_ids JSONB DEFAULT '[]'::jsonb,
    source_job_id VARCHAR(64) REFERENCES queries(job_id) ON DELETE SET NULL,
    source_workflow VARCHAR(100), -- 'change_detection', 'grounding', 'vqa', 'cross_modal_fusion', 'compound'
    evidence_provenance JSONB DEFAULT '{}'::jsonb,
    user_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kcards_user_id ON knowledge_cards(user_id);
CREATE INDEX IF NOT EXISTS idx_kcards_queue ON knowledge_cards(queue);
CREATE INDEX IF NOT EXISTS idx_kcards_source_workflow ON knowledge_cards(source_workflow);
CREATE INDEX IF NOT EXISTS idx_kcards_created_at ON knowledge_cards(created_at DESC);

-- ----------------------------------------------------------------------------
-- 2. Knowledge Chains Table (Ordered Sequences of Linked Knowledge Nodes)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_chains (
    id VARCHAR(64) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags JSONB DEFAULT '[]'::jsonb,
    nodes JSONB NOT NULL DEFAULT '[]'::jsonb, -- Array of step nodes: [{ step_order, card_id, title, notes }]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kchains_user_id ON knowledge_chains(user_id);
CREATE INDEX IF NOT EXISTS idx_kchains_created_at ON knowledge_chains(created_at DESC);
