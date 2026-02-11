-- Create expected_outputs table in case_studies_factory schema
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS case_studies_factory.expected_outputs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  research_name TEXT NOT NULL,
  pillar_id TEXT NOT NULL,

  carousel_data JSONB NOT NULL,  -- Expected carousel structure
  source TEXT,  -- Where this gold standard came from (e.g., "manually_created", "approved_output")
  notes TEXT,

  UNIQUE(research_name, pillar_id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_expected_outputs_lookup
ON case_studies_factory.expected_outputs(research_name, pillar_id);
