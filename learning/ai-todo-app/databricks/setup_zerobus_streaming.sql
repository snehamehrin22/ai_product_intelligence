-- Databricks Zerobus Ingest Setup Script (Lakehouse Architecture)
-- Phase 2: Event Instrumentation with Streaming Tables
-- Purpose: Create Streaming Tables for platform events and agent traces (Bronze layer)

-- ============================================================================
-- Architecture Overview
-- ============================================================================
--
-- LAKEBASE (OLTP - Transactional):
--   signaltogrowth.todo_app.tasks  (existing - for frequent updates/deletes)
--   signaltogrowth.todo_app.users  (existing - for point queries)
--
-- BRONZE (Append-Only Event Streams via Zerobus):
--   signaltogrowth.bronze.platform_events  (STREAMING TABLE)
--   signaltogrowth.bronze.agent_traces     (STREAMING TABLE)
--
-- SILVER (Enriched - Phase 3):
--   signaltogrowth.silver.enriched_events  (MATERIALIZED VIEW)
--   signaltogrowth.silver.agent_sessions   (MATERIALIZED VIEW)
--
-- GOLD (Aggregated - Phase 4):
--   signaltogrowth.gold.user_metrics       (MATERIALIZED VIEW)
--   signaltogrowth.gold.agent_performance  (MATERIALIZED VIEW)
--
-- ============================================================================

USE CATALOG signaltogrowth;

-- ============================================================================
-- Create Bronze Schema (Event Streams)
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS signaltogrowth.bronze
COMMENT 'Bronze layer: Raw event streams from Zerobus Ingest (append-only)';

USE SCHEMA bronze;

-- ============================================================================
-- Platform Events Streaming Table
-- ============================================================================

CREATE OR REPLACE STREAMING TABLE signaltogrowth.bronze.platform_events (
  event_id STRING NOT NULL COMMENT 'Unique event identifier (UUID)',
  event_name STRING NOT NULL COMMENT 'Event type: task_created, task_completed, etc.',
  event_version STRING NOT NULL COMMENT 'Schema version for evolution (e.g., v1, v2)',
  timestamp TIMESTAMP NOT NULL COMMENT 'Event occurrence time (ISO8601)',
  session_id STRING NOT NULL COMMENT 'User session identifier (join key)',
  user_id STRING NOT NULL COMMENT 'User identifier',
  properties MAP<STRING, STRING> COMMENT 'Event-specific data (task_id, task_title, etc.)',
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Zerobus ingestion timestamp'
)
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'comment' = 'Platform events from frontend and backend user interactions (Streaming Table for Zerobus)'
);

-- Add constraints
ALTER TABLE signaltogrowth.bronze.platform_events
ADD CONSTRAINT event_id_not_null CHECK (event_id IS NOT NULL);

ALTER TABLE signaltogrowth.bronze.platform_events
ADD CONSTRAINT session_id_not_null CHECK (session_id IS NOT NULL);

-- ============================================================================
-- Agent Traces Streaming Table
-- ============================================================================

CREATE OR REPLACE STREAMING TABLE signaltogrowth.bronze.agent_traces (
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
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'comment' = 'OpenTelemetry agent traces with GenAI semantic conventions (Streaming Table for Zerobus)'
);

-- Add constraints
ALTER TABLE signaltogrowth.bronze.agent_traces
ADD CONSTRAINT trace_id_not_null CHECK (trace_id IS NOT NULL);

ALTER TABLE signaltogrowth.bronze.agent_traces
ADD CONSTRAINT session_id_not_null_traces CHECK (session_id IS NOT NULL);

-- ============================================================================
-- Grant Permissions (Service Principal for Zerobus)
-- ============================================================================

-- Service Principal ID: 46538e1a-e97d-447e-99ef-2685a8492b8f

-- Grant catalog and schema access
GRANT USE CATALOG ON CATALOG signaltogrowth TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;
GRANT USE SCHEMA ON SCHEMA signaltogrowth.bronze TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;

-- Grant table permissions (MODIFY for Zerobus writes, SELECT for queries)
GRANT MODIFY, SELECT ON TABLE signaltogrowth.bronze.platform_events TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;
GRANT MODIFY, SELECT ON TABLE signaltogrowth.bronze.agent_traces TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;

-- ============================================================================
-- Verify Setup
-- ============================================================================

-- Show table details
DESCRIBE EXTENDED signaltogrowth.bronze.platform_events;
DESCRIBE EXTENDED signaltogrowth.bronze.agent_traces;

-- Verify permissions
SHOW GRANTS ON TABLE signaltogrowth.bronze.platform_events;
SHOW GRANTS ON TABLE signaltogrowth.bronze.agent_traces;

-- Count records (should be 0 initially)
SELECT COUNT(*) as event_count FROM signaltogrowth.bronze.platform_events;
SELECT COUNT(*) as trace_count FROM signaltogrowth.bronze.agent_traces;

-- ============================================================================
-- Sample Queries for Validation
-- ============================================================================

-- Join events and traces by session_id
SELECT
  e.event_name,
  e.session_id,
  e.timestamp as event_timestamp,
  t.span_name,
  t.gen_ai_request_model,
  t.gen_ai_usage_total_tokens
FROM signaltogrowth.bronze.platform_events e
LEFT JOIN signaltogrowth.bronze.agent_traces t ON e.session_id = t.session_id
WHERE e.session_id = '<test-session-id>'
ORDER BY e.timestamp;

-- ============================================================================
-- Setup Complete
-- ============================================================================

-- Next steps:
-- 1. Update backend/.env with table names: signaltogrowth.bronze.platform_events
-- 2. Run test_zerobus_connection.py to verify connection
-- 3. Proceed with implementing ZerobusPublisher service (US-2.2)
