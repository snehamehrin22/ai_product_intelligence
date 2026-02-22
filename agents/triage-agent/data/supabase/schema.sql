-- Triage Agent - Supabase Schema
-- Two tables in 'raw' schema: processed_files (duplicate tracking) and triage_items (Layer 1 output)

-- Create raw schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS raw;

-- Grant permissions on schema and sequences
GRANT USAGE ON SCHEMA raw TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA raw TO anon, authenticated, service_role;

-- Table 1: Track which Obsidian files have been processed
CREATE TABLE IF NOT EXISTS raw.processed_files (
    id SERIAL PRIMARY KEY,
    file_path TEXT UNIQUE NOT NULL,
    file_hash TEXT NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    item_count INTEGER DEFAULT 0
);

-- Index for fast lookup
CREATE INDEX IF NOT EXISTS idx_processed_files_path ON raw.processed_files(file_path);
CREATE INDEX IF NOT EXISTS idx_processed_files_hash ON raw.processed_files(file_hash);

-- Table 2: Store triage items (Layer 1 output)
CREATE TABLE IF NOT EXISTS raw.triage_items (
    id TEXT PRIMARY KEY,
    source_file TEXT NOT NULL,
    date DATE NOT NULL,
    raw_context TEXT NOT NULL,
    personal_or_work TEXT NOT NULL,
    domain TEXT NOT NULL,
    type TEXT NOT NULL,
    tags TEXT NOT NULL,
    niche_signal BOOLEAN NOT NULL,
    publishable BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (source_file) REFERENCES raw.processed_files(file_path) ON DELETE CASCADE
);

-- Indexes for querying
CREATE INDEX IF NOT EXISTS idx_triage_items_source ON raw.triage_items(source_file);
CREATE INDEX IF NOT EXISTS idx_triage_items_date ON raw.triage_items(date);
CREATE INDEX IF NOT EXISTS idx_triage_items_type ON raw.triage_items(type);
CREATE INDEX IF NOT EXISTS idx_triage_items_domain ON raw.triage_items(domain);
CREATE INDEX IF NOT EXISTS idx_triage_items_niche ON raw.triage_items(niche_signal);
CREATE INDEX IF NOT EXISTS idx_triage_items_publishable ON raw.triage_items(publishable);

-- Table 3: Store insights (Layer 2 output)
CREATE TABLE IF NOT EXISTS raw.insights (
    insight_id TEXT PRIMARY KEY,
    linked_triage_ids TEXT NOT NULL,
    insight TEXT NOT NULL,
    tags TEXT NOT NULL,
    publishable_angle TEXT,
    status TEXT DEFAULT 'Draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for querying insights
CREATE INDEX IF NOT EXISTS idx_insights_status ON raw.insights(status);
CREATE INDEX IF NOT EXISTS idx_insights_created ON raw.insights(created_at);

-- Enable Row Level Security (optional, but recommended)
ALTER TABLE raw.processed_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw.triage_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw.insights ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for service role)
CREATE POLICY "Allow all for service role - processed_files" ON raw.processed_files
    FOR ALL USING (true);

CREATE POLICY "Allow all for service role - triage_items" ON raw.triage_items
    FOR ALL USING (true);

CREATE POLICY "Allow all for service role - insights" ON raw.insights
    FOR ALL USING (true);
