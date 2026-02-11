-- Recreate carousel_evals table with complete schema in case_studies_factory
-- Run this in Supabase SQL Editor

-- Drop existing table (WARNING: This deletes all data)
DROP TABLE IF EXISTS case_studies_factory.carousel_evals CASCADE;

-- Create with full schema
CREATE TABLE case_studies_factory.carousel_evals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Input context
  research_file TEXT NOT NULL,
  research_name TEXT NOT NULL,
  pillar_id TEXT NOT NULL CHECK (pillar_id IN ('pillar_01', 'pillar_02', 'pillar_03')),

  -- Expected vs Generated
  expected_output JSONB NOT NULL,
  generated_output JSONB NOT NULL,

  -- Generation metadata
  iteration INT DEFAULT 1,
  prompt_version_id UUID REFERENCES case_studies_factory.prompt_versions(id),
  model_used TEXT DEFAULT 'claude-sonnet-4-20250514',

  -- Comparison metrics
  match_score FLOAT CHECK (match_score >= 0 AND match_score <= 1),
  structure_match FLOAT,
  content_similarity FLOAT,
  style_match FLOAT,
  differences JSONB,

  -- Human evaluation
  human_approved BOOLEAN DEFAULT FALSE,
  human_feedback TEXT,
  human_rating INT CHECK (human_rating >= 1 AND human_rating <= 5),

  -- Prompt iteration
  prompt_adjustments JSONB,
  parent_eval_id UUID REFERENCES case_studies_factory.carousel_evals(id),
  next_eval_id UUID REFERENCES case_studies_factory.carousel_evals(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_carousel_evals_research ON case_studies_factory.carousel_evals(research_name);
CREATE INDEX IF NOT EXISTS idx_carousel_evals_pillar ON case_studies_factory.carousel_evals(pillar_id);
CREATE INDEX IF NOT EXISTS idx_carousel_evals_score ON case_studies_factory.carousel_evals(match_score DESC);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION case_studies_factory.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_carousel_evals_updated_at
BEFORE UPDATE ON case_studies_factory.carousel_evals
FOR EACH ROW EXECUTE FUNCTION case_studies_factory.update_updated_at_column();
