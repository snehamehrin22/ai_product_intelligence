-- Add missing columns to carousel_evals table in case_studies_factory schema
-- Run this in Supabase SQL Editor

-- Comparison metrics
ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS content_similarity FLOAT;

ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS structure_match FLOAT;

ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS style_match FLOAT;

-- Prompt iteration columns
ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS prompt_adjustments JSONB;

ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS parent_eval_id UUID REFERENCES case_studies_factory.carousel_evals(id);

ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS next_eval_id UUID REFERENCES case_studies_factory.carousel_evals(id);

-- Human evaluation columns
ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS human_approved BOOLEAN DEFAULT FALSE;

ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS human_feedback TEXT;

ALTER TABLE case_studies_factory.carousel_evals
ADD COLUMN IF NOT EXISTS human_rating INT CHECK (human_rating >= 1 AND human_rating <= 5);
