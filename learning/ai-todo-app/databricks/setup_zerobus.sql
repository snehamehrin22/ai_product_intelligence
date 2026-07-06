-- Databricks Zerobus Ingest Setup Script
-- Phase 2: Event Instrumentation
-- Purpose: Create Delta tables for platform events and agent traces

-- ============================================================================
-- Create Catalog and Schema (if not exists)
-- ============================================================================

CREATE CATALOG IF NOT EXISTS main
COMMENT 'Main catalog for AI Todo App';

CREATE SCHEMA IF NOT EXISTS main.events
COMMENT 'Schema for event data (platform events and agent traces)';

USE CATALOG main;
USE SCHEMA events;

-- ============================================================================
-- Platform Events Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS main.events.platform_events (
  event_id STRING NOT NULL COMMENT 'Unique event identifier (UUID)',
  event_name STRING NOT NULL COMMENT 'Event type: task_created, task_completed, etc.',
  event_version STRING NOT NULL COMMENT 'Schema version for evolution (e.g., v1, v2)',
  timestamp TIMESTAMP NOT NULL COMMENT 'Event occurrence time (ISO8601)',
  session_id STRING NOT NULL COMMENT 'User session identifier (join key)',
  user_id STRING NOT NULL COMMENT 'User identifier',
  properties MAP<STRING, STRING> COMMENT 'Event-specific data (task_id, task_title, etc.)',
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Zerobus ingestion timestamp'
)
USING DELTA
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'comment' = 'Platform events from frontend and backend user interactions'
);

-- Add constraints
ALTER TABLE main.events.platform_events
ADD CONSTRAINT event_id_not_null CHECK (event_id IS NOT NULL);

ALTER TABLE main.events.platform_events
ADD CONSTRAINT session_id_not_null CHECK (session_id IS NOT NULL);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_session_id ON main.events.platform_events (session_id);
CREATE INDEX IF NOT EXISTS idx_event_name ON main.events.platform_events (event_name);
CREATE INDEX IF NOT EXISTS idx_timestamp ON main.events.platform_events (timestamp);

-- ============================================================================
-- Agent Traces Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS main.events.agent_traces (
  trace_id STRING NOT NULL COMMENT 'OpenTelemetry trace ID',
  span_id STRING NOT NULL COMMENT 'OpenTelemetry span ID',
  span_name STRING NOT NULL COMMENT 'Span operation name',
  parent_span_id STRING COMMENT 'Parent span ID for nested traces',
  session_id STRING NOT NULL COMMENT 'User session identifier (join key with platform_events)',
  user_id STRING COMMENT 'User identifier',
  timestamp TIMESTAMP NOT NULL COMMENT 'Span start time',
  duration_ms BIGINT COMMENT 'Span duration in milliseconds',
  status_code STRING COMMENT 'Span status: OK, ERROR',
  -- GenAI semantic conventions
  gen_ai_request_model STRING COMMENT 'LLM model name (e.g., gpt-4o-mini)',
  gen_ai_usage_input_tokens INT COMMENT 'Input token count',
  gen_ai_usage_output_tokens INT COMMENT 'Output token count',
  gen_ai_usage_total_tokens INT COMMENT 'Total token count',
  gen_ai_response_finish_reason STRING COMMENT 'Completion reason: stop, length, etc.',
  gen_ai_prompt STRING COMMENT 'LLM prompt text (if logged)',
  gen_ai_completion STRING COMMENT 'LLM response text (if logged)',
  -- Additional attributes
  attributes MAP<STRING, STRING> COMMENT 'Additional span attributes',
  events ARRAY<STRUCT<timestamp: TIMESTAMP, name: STRING, attributes: MAP<STRING, STRING>>> COMMENT 'Span events',
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Zerobus ingestion timestamp'
)
USING DELTA
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'comment' = 'OpenTelemetry agent traces with GenAI semantic conventions'
);

-- Add constraints
ALTER TABLE main.events.agent_traces
ADD CONSTRAINT trace_id_not_null CHECK (trace_id IS NOT NULL);

ALTER TABLE main.events.agent_traces
ADD CONSTRAINT session_id_not_null_traces CHECK (session_id IS NOT NULL);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_traces_session_id ON main.events.agent_traces (session_id);
CREATE INDEX IF NOT EXISTS idx_traces_trace_id ON main.events.agent_traces (trace_id);
CREATE INDEX IF NOT EXISTS idx_traces_timestamp ON main.events.agent_traces (timestamp);

-- ============================================================================
-- Sample Queries for Validation
-- ============================================================================

-- Count platform events
SELECT COUNT(*) as event_count FROM main.events.platform_events;

-- Count agent traces
SELECT COUNT(*) as trace_count FROM main.events.agent_traces;

-- Join events and traces by session_id
SELECT
  e.event_name,
  e.session_id,
  e.timestamp as event_timestamp,
  t.span_name,
  t.gen_ai_request_model,
  t.gen_ai_usage_total_tokens
FROM main.events.platform_events e
LEFT JOIN main.events.agent_traces t ON e.session_id = t.session_id
WHERE e.session_id = '<test-session-id>'
ORDER BY e.timestamp;

-- ============================================================================
-- Grant Permissions (for service principal)
-- ============================================================================

-- IMPORTANT: Replace <service-principal-id> with your actual service principal application ID
-- Get this from: Settings → Identity & Access → Service Principals → Copy Application ID
--
-- Example format: GRANT USE CATALOG ON CATALOG main TO `abc12345-6789-abcd-ef01-23456789abcd`;

-- Grant catalog and schema access
-- GRANT USE CATALOG ON CATALOG main TO `<service-principal-id>`;
-- GRANT USE SCHEMA ON SCHEMA main.events TO `<service-principal-id>`;

-- Grant table permissions (MODIFY for writes, SELECT for reads)
-- GRANT MODIFY, SELECT ON TABLE main.events.platform_events TO `<service-principal-id>`;
-- GRANT MODIFY, SELECT ON TABLE main.events.agent_traces TO `<service-principal-id>`;

-- Verify grants (uncomment to check)
-- SHOW GRANTS ON TABLE main.events.platform_events;
-- SHOW GRANTS ON TABLE main.events.agent_traces;

-- ============================================================================
-- Setup Complete
-- ============================================================================

DESCRIBE EXTENDED main.events.platform_events;
DESCRIBE EXTENDED main.events.agent_traces;
