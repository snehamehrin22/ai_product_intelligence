-- ============================================================================
-- Zerobus Catalog and Tables Setup
-- Storage credential already created via UI
-- Run this script in Databricks SQL Editor
-- ============================================================================

-- Step 1: Verify Storage Credential Exists
DESCRIBE STORAGE CREDENTIAL azure_storage_credential;

-- ============================================================================
-- Step 2: Create External Location
-- ============================================================================

CREATE EXTERNAL LOCATION IF NOT EXISTS signaltogrowth_storage
URL 'abfss://databricks-data@signalogrowthdata.dfs.core.windows.net/unity-catalog'
WITH (STORAGE CREDENTIAL azure_storage_credential);

-- Verify external location
DESCRIBE EXTERNAL LOCATION signaltogrowth_storage;

-- ============================================================================
-- Step 3: Create Catalog with Managed Storage
-- ============================================================================

CREATE CATALOG IF NOT EXISTS signaltogrowth_zerobus
MANAGED LOCATION 'abfss://databricks-data@signalogrowthdata.dfs.core.windows.net/unity-catalog/signaltogrowth_zerobus'
COMMENT 'Catalog with managed storage for Zerobus Ingest';

-- Verify catalog has storage location (should show abfss:// path)
DESCRIBE CATALOG EXTENDED signaltogrowth_zerobus;

-- ============================================================================
-- Step 4: Create Bronze Schema
-- ============================================================================

USE CATALOG signaltogrowth_zerobus;

CREATE SCHEMA IF NOT EXISTS bronze
COMMENT 'Bronze layer: Raw event streams from Zerobus Ingest';

-- ============================================================================
-- Step 5: Create Tables for Zerobus
-- ============================================================================

USE SCHEMA bronze;

-- Drop existing tables if any (to ensure clean slate)
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
  'comment' = 'Agent traces for Zerobus Ingest (with managed storage)'
);

-- ============================================================================
-- Step 6: Grant Permissions to Service Principal (for Zerobus SDK)
-- ============================================================================

GRANT USE CATALOG ON CATALOG signaltogrowth_zerobus TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;
GRANT USE SCHEMA ON SCHEMA signaltogrowth_zerobus.bronze TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;
GRANT MODIFY, SELECT ON TABLE signaltogrowth_zerobus.bronze.platform_events TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;
GRANT MODIFY, SELECT ON TABLE signaltogrowth_zerobus.bronze.agent_traces TO `46538e1a-e97d-447e-99ef-2685a8492b8f`;

-- ============================================================================
-- Step 7: Verify Storage Location (CRITICAL FOR ZEROBUS)
-- ============================================================================

-- Check platform_events has storage location
DESCRIBE EXTENDED signaltogrowth_zerobus.bronze.platform_events;

-- The Location field should now show something like:
-- abfss://databricks-data@signalogrowthdata.dfs.core.windows.net/unity-catalog/signaltogrowth_zerobus/bronze/platform_events

-- If Location shows an abfss:// path, Zerobus will work! ✅

-- ============================================================================
-- Step 8: Verify Tables
-- ============================================================================

SELECT COUNT(*) as event_count FROM signaltogrowth_zerobus.bronze.platform_events;
SELECT COUNT(*) as trace_count FROM signaltogrowth_zerobus.bronze.agent_traces;

-- Show grants
SHOW GRANTS ON TABLE signaltogrowth_zerobus.bronze.platform_events;

-- ============================================================================
-- Setup Complete!
-- ============================================================================

-- Next: Update test_zerobus_connection.py to use signaltogrowth_zerobus.bronze.platform_events
