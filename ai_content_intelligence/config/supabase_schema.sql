-- Supabase schema for carousel evaluation system

-- Table: carousel_evals
-- Stores each generation attempt and comparison with expected output
CREATE TABLE IF NOT EXISTS carousel_evals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Input context
  research_file TEXT NOT NULL,
  research_name TEXT NOT NULL,
  pillar_id TEXT NOT NULL CHECK (pillar_id IN ('pillar_01', 'pillar_02', 'pillar_03')),

  -- Expected vs Generated
  expected_output JSONB NOT NULL,  -- Gold standard carousel
  generated_output JSONB NOT NULL,  -- What the system produced

  -- Generation metadata
  iteration INT DEFAULT 1,
  prompt_version_id UUID REFERENCES prompt_versions(id),
  model_used TEXT DEFAULT 'claude-sonnet-4-20250514',

  -- Comparison metrics
  match_score FLOAT CHECK (match_score >= 0 AND match_score <= 1),
  structure_match FLOAT,  -- Slide count, titles match
  content_similarity FLOAT,  -- Semantic similarity per slide
  style_match FLOAT,  -- Tone, length, format
  differences JSONB,  -- Detailed diff object

  -- Human evaluation
  human_approved BOOLEAN DEFAULT FALSE,
  human_feedback TEXT,
  human_rating INT CHECK (human_rating >= 1 AND human_rating <= 5),

  -- Prompt iteration
  prompt_adjustments JSONB,  -- What was changed
  parent_eval_id UUID REFERENCES carousel_evals(id),  -- Previous iteration
  next_eval_id UUID REFERENCES carousel_evals(id)  -- Next iteration
);

-- Table: prompt_versions
-- Track prompt evolution per pillar
CREATE TABLE IF NOT EXISTS prompt_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  pillar_id TEXT NOT NULL CHECK (pillar_id IN ('pillar_01', 'pillar_02', 'pillar_03')),
  version INT NOT NULL,

  -- Prompt content
  prompt_template TEXT NOT NULL,
  prompt_components JSONB,  -- Breakdown of role, context, instructions, etc.

  -- Performance
  avg_match_score FLOAT,
  total_evals INT DEFAULT 0,
  approval_rate FLOAT,

  -- Metadata
  notes TEXT,
  is_active BOOLEAN DEFAULT TRUE,

  UNIQUE(pillar_id, version)
);

-- Table: expected_outputs
-- Store gold standard carousels for evaluation
CREATE TABLE IF NOT EXISTS expected_outputs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  research_name TEXT NOT NULL,
  pillar_id TEXT NOT NULL,

  carousel_data JSONB NOT NULL,  -- Expected carousel structure
  source TEXT,  -- Where this gold standard came from (e.g., "manually_created", "approved_output")
  notes TEXT,

  UNIQUE(research_name, pillar_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_carousel_evals_research ON carousel_evals(research_name);
CREATE INDEX IF NOT EXISTS idx_carousel_evals_pillar ON carousel_evals(pillar_id);
CREATE INDEX IF NOT EXISTS idx_carousel_evals_score ON carousel_evals(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_prompt_versions_pillar ON prompt_versions(pillar_id);
CREATE INDEX IF NOT EXISTS idx_expected_outputs_lookup ON expected_outputs(research_name, pillar_id);

-- Updated timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_carousel_evals_updated_at BEFORE UPDATE ON carousel_evals
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
