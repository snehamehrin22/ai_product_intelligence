-- ============================================================================
-- Zerobus Bronze Tables Setup (Azure ADLS Gen2 with HNS)
-- Storage credential 'zerobus-ingest' already created via UI
-- External location 'zerobusingest_final' already created
-- Run this script in Databricks SQL Editor
-- ============================================================================

-- Step 1: Verify Prerequisites
DESCRIBE STORAGE CREDENTIAL `zerobus-ingest`;
DESCRIBE EXTERNAL LOCATION zerobusingest_final;

-- ============================================================================
-- Step 2: Set Managed Location on Bronze Schema
-- ============================================================================

USE CATALOG signaltogrowth;

-- Set managed storage location for bronze schema
ALTER SCHEMA bronze SET MANAGED LOCATION 'abfss://zerobusingest2@signaltogrowthdata2.dfs.core.windows.net/bronze/';

-- Verify schema has managed location
DESCRIBE SCHEMA EXTENDED bronze;

-- ============================================================================
-- Step 3: Drop and Recreate Tables (to pick up managed storage)
-- ============================================================================

USE SCHEMA bronze;

-- Drop existing tables (they were created without managed storage)
DROP TABLE IF EXISTS platform_events;
DROP TABLE IF EXISTS agent_traces;

-- Platform Events Table
CREATE TABLE platform_events (
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
  'delta.feature.allowColumnDefaults' = 'supported',
  'comment' = 'Platform events for Zerobus Ingest (with managed storage)'
);

-- Agent Traces Table
CREATE TABLE agent_traces (
  trace_id STRING NOT NULL COMMENT 'OpenTelemetry trace ID',
  span_id STRING NOT NULL COMMENT 'OpenTelemetry span ID',
  span_name STRING NOT NULL COMMENT 'Span operation name',
  parent_span_id STRING COMMENT 'Parent span ID for nested traces',
  session_id STRING NOT NULL COMMENT 'User session identifier (join key with platform_events)',
  user_id STRING COMMENT 'User identifier',
  timestamp TIMESTAMP NOT NULL COMMENT 'Span start time',
  duration_ms BIGINT COMMENT 'Span duration in milliseconds',
  status_code STRING COMMENT 'Span status: OK, ERROR',
  gen_ai_request_model STRING COMMENT 'LLM model name',
  gen_ai_usage_input_tokens INT COMMENT 'Input token count',
  gen_ai_usage_output_tokens INT COMMENT 'Output token count',
  gen_ai_usage_total_tokens INT COMMENT 'Total token count',
  gen_ai_response_finish_reason STRING COMMENT 'Completion reason',
  gen_ai_prompt STRING COMMENT 'LLM prompt text',
  gen_ai_completion STRING COMMENT 'LLM response text',
  attributes MAP<STRING, STRING> COMMENT 'Additional span attributes',
  events ARRAY<STRUCT<timestamp: TIMESTAMP, name: STRING, attributes: MAP<STRING, STRING>>> COMMENT 'Span events',
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Zerobus ingestion timestamp'
)
USING DELTA
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.feature.allowColumnDefaults' = 'supported',
  'comment' = 'Agent traces for Zerobus Ingest (with managed storage)'
);

-- ============================================================================
-- Step 4: Grant Permissions to Service Principal (for Zerobus SDK)
-- ============================================================================

-- Service principal: 46538e1a-e97d-447e-99ef-2685a8492b8f
GRANT USE CATALOG ON CATALOG signaltogrowth TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;
GRANT USE SCHEMA ON SCHEMA signaltogrowth.bronze TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;
GRANT MODIFY, SELECT ON TABLE signaltogrowth.bronze.platform_events TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;
GRANT MODIFY, SELECT ON TABLE signaltogrowth.bronze.agent_traces TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;

-- ============================================================================
-- Step 5: Verify Storage Location (CRITICAL FOR ZEROBUS)
-- ============================================================================

-- Check platform_events has storage location
DESCRIBE EXTENDED signaltogrowth.bronze.platform_events;

-- The Location field MUST show an abfss:// path like:
-- abfss://zerobusingest2@signaltogrowthdata2.dfs.core.windows.net/bronze/platform_events
--
-- ✅ If Location shows abfss:// path → Zerobus will work!
-- ❌ If Location is empty or dbfs:/ → Zerobus will fail with Error 4024

-- Check agent_traces storage location
DESCRIBE EXTENDED signaltogrowth.bronze.agent_traces;

-- ============================================================================
-- Step 6: Verify Tables and Permissions
-- ============================================================================

-- Verify tables are empty
SELECT COUNT(*) as event_count FROM signaltogrowth.bronze.platform_events;
SELECT COUNT(*) as trace_count FROM signaltogrowth.bronze.agent_traces;

-- Verify service principal has permissions
SHOW GRANTS ON TABLE signaltogrowth.bronze.platform_events;
SHOW GRANTS ON TABLE signaltogrowth.bronze.agent_traces;

-- ============================================================================
-- Setup Complete!
-- ============================================================================

-- Expected results:
-- 1. Schema has managed location: abfss://zerobusingest2@signaltogrowthdata2.dfs.core.windows.net/bronze/
-- 2. Tables inherit storage location from schema
-- 3. Service principal has MODIFY and SELECT on both tables
--
-- Next: Update test_zerobus_connection.py to use signaltogrowth.bronze.platform_events
