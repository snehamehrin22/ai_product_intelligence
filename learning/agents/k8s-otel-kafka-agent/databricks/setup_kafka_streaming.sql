-- ================================================================
-- Databricks Delta Lake Setup for OpenTelemetry Traces from Kafka
-- ================================================================
-- This script creates Delta tables and sets up streaming ingestion
-- from the self-hosted Kafka cluster in AKS
--
-- Prerequisites:
-- 1. Databricks workspace with Unity Catalog enabled
-- 2. Network connectivity from Databricks to AKS Kafka service
-- 3. Kafka broker accessible (we'll use LoadBalancer or VPN/VNet peering)
-- ================================================================

-- Create catalog for telemetry data
CREATE CATALOG IF NOT EXISTS telemetry;

USE CATALOG telemetry;

-- Create schema for agent traces
CREATE SCHEMA IF NOT EXISTS agent_traces
COMMENT 'OpenTelemetry traces from AI agents with GenAI semantic conventions';

USE SCHEMA agent_traces;

-- ================================================================
-- Raw traces table (Bronze layer - direct from Kafka)
-- ================================================================
CREATE TABLE IF NOT EXISTS raw_traces (
  -- Kafka metadata
  kafka_key BINARY,
  kafka_value BINARY COMMENT 'OTLP trace data in Protobuf format',
  kafka_topic STRING,
  kafka_partition INT,
  kafka_offset BIGINT,
  kafka_timestamp TIMESTAMP,

  -- Ingestion metadata
  ingestion_timestamp TIMESTAMP COMMENT 'When this record was ingested into Delta Lake',

  -- Partitioning for efficient queries
  ingestion_date DATE GENERATED ALWAYS AS (CAST(ingestion_timestamp AS DATE))
)
USING DELTA
PARTITIONED BY (ingestion_date)
COMMENT 'Raw OTLP traces from Kafka - Bronze layer'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- ================================================================
-- Parsed traces table (Silver layer - decoded OTLP data)
-- ================================================================
-- This will be populated by a notebook that parses the Protobuf data
CREATE TABLE IF NOT EXISTS parsed_traces (
  -- Trace identifiers
  trace_id STRING COMMENT 'Unique trace identifier (hex string)',
  span_id STRING COMMENT 'Unique span identifier (hex string)',
  parent_span_id STRING COMMENT 'Parent span identifier',

  -- Span metadata
  span_name STRING COMMENT 'Name of the operation (e.g., agent.extract_task)',
  span_kind STRING COMMENT 'CLIENT, SERVER, PRODUCER, CONSUMER, INTERNAL',
  start_time_unix_nano BIGINT COMMENT 'Span start time in nanoseconds since epoch',
  end_time_unix_nano BIGINT COMMENT 'Span end time in nanoseconds since epoch',
  duration_ms DOUBLE COMMENT 'Span duration in milliseconds',

  -- Resource attributes (service-level)
  service_name STRING COMMENT 'Name of the service (e.g., ai-agent)',
  service_version STRING COMMENT 'Version of the service',
  deployment_environment STRING COMMENT 'Environment: production, staging, dev',

  -- GenAI semantic conventions
  gen_ai_request_model STRING COMMENT 'LLM model used (e.g., gpt-4o-mini)',
  gen_ai_usage_input_tokens INT COMMENT 'Number of input tokens',
  gen_ai_usage_output_tokens INT COMMENT 'Number of output tokens',
  gen_ai_usage_total_tokens INT COMMENT 'Total tokens used',
  gen_ai_response_finish_reason STRING COMMENT 'Completion reason: stop, length, etc.',

  -- Custom agent attributes
  extraction_priority STRING COMMENT 'Task priority: low, medium, high',
  extraction_confidence DOUBLE COMMENT 'Confidence score 0-1',
  extraction_has_due_date BOOLEAN COMMENT 'Whether task has a due date',
  message_length INT COMMENT 'Length of user message',
  agent_success BOOLEAN COMMENT 'Whether agent operation succeeded',
  agent_processing_time_ms DOUBLE COMMENT 'Agent processing time',

  -- All attributes as JSON for flexibility
  attributes STRING COMMENT 'All span attributes as JSON',
  resource_attributes STRING COMMENT 'All resource attributes as JSON',

  -- Ingestion metadata
  ingestion_timestamp TIMESTAMP,
  ingestion_date DATE GENERATED ALWAYS AS (CAST(ingestion_timestamp AS DATE)),

  -- Kafka source metadata
  kafka_topic STRING,
  kafka_partition INT,
  kafka_offset BIGINT
)
USING DELTA
PARTITIONED BY (ingestion_date, service_name)
COMMENT 'Parsed OTLP traces with GenAI semantic conventions - Silver layer'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- ================================================================
-- Aggregated metrics table (Gold layer - business metrics)
-- ================================================================
CREATE TABLE IF NOT EXISTS agent_metrics_hourly (
  -- Time dimension
  metric_hour TIMESTAMP COMMENT 'Start of the hour',
  metric_date DATE GENERATED ALWAYS AS (CAST(metric_hour AS DATE)),

  -- Service dimension
  service_name STRING,
  deployment_environment STRING,

  -- GenAI metrics
  llm_model STRING COMMENT 'LLM model used',
  total_requests BIGINT COMMENT 'Total LLM requests',
  total_input_tokens BIGINT COMMENT 'Total input tokens consumed',
  total_output_tokens BIGINT COMMENT 'Total output tokens generated',
  total_tokens BIGINT COMMENT 'Total tokens (input + output)',
  avg_input_tokens DOUBLE COMMENT 'Average input tokens per request',
  avg_output_tokens DOUBLE COMMENT 'Average output tokens per request',

  -- Performance metrics
  avg_duration_ms DOUBLE COMMENT 'Average span duration',
  p50_duration_ms DOUBLE COMMENT '50th percentile duration',
  p95_duration_ms DOUBLE COMMENT '95th percentile duration',
  p99_duration_ms DOUBLE COMMENT '99th percentile duration',
  max_duration_ms DOUBLE COMMENT 'Maximum duration',

  -- Success metrics
  total_spans BIGINT COMMENT 'Total spans processed',
  success_count BIGINT COMMENT 'Successful operations',
  error_count BIGINT COMMENT 'Failed operations',
  success_rate DOUBLE COMMENT 'Success rate (0-1)',

  -- Task extraction metrics
  tasks_extracted BIGINT COMMENT 'Total tasks extracted',
  high_priority_tasks BIGINT COMMENT 'High priority tasks',
  medium_priority_tasks BIGINT COMMENT 'Medium priority tasks',
  low_priority_tasks BIGINT COMMENT 'Low priority tasks',
  avg_confidence DOUBLE COMMENT 'Average extraction confidence'
)
USING DELTA
PARTITIONED BY (metric_date, service_name)
COMMENT 'Hourly aggregated metrics for agent performance - Gold layer'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- ================================================================
-- Create views for easier querying
-- ================================================================

-- Recent traces view (last 24 hours)
CREATE OR REPLACE VIEW recent_traces AS
SELECT
  trace_id,
  span_name,
  service_name,
  gen_ai_request_model,
  gen_ai_usage_total_tokens,
  duration_ms,
  agent_success,
  ingestion_timestamp
FROM parsed_traces
WHERE ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 DAY
ORDER BY ingestion_timestamp DESC;

-- GenAI token usage summary
CREATE OR REPLACE VIEW token_usage_summary AS
SELECT
  service_name,
  gen_ai_request_model,
  COUNT(*) as request_count,
  SUM(gen_ai_usage_input_tokens) as total_input_tokens,
  SUM(gen_ai_usage_output_tokens) as total_output_tokens,
  SUM(gen_ai_usage_total_tokens) as total_tokens,
  AVG(gen_ai_usage_total_tokens) as avg_tokens_per_request,
  AVG(duration_ms) as avg_duration_ms
FROM parsed_traces
WHERE gen_ai_request_model IS NOT NULL
  AND ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
GROUP BY service_name, gen_ai_request_model;

-- Agent performance metrics
CREATE OR REPLACE VIEW agent_performance AS
SELECT
  DATE_TRUNC('hour', ingestion_timestamp) as metric_hour,
  service_name,
  COUNT(*) as total_requests,
  AVG(duration_ms) as avg_duration_ms,
  PERCENTILE_APPROX(duration_ms, 0.5) as p50_duration_ms,
  PERCENTILE_APPROX(duration_ms, 0.95) as p95_duration_ms,
  PERCENTILE_APPROX(duration_ms, 0.99) as p99_duration_ms,
  SUM(CASE WHEN agent_success THEN 1 ELSE 0 END) as success_count,
  AVG(CASE WHEN agent_success THEN 1.0 ELSE 0.0 END) as success_rate,
  AVG(extraction_confidence) as avg_confidence
FROM parsed_traces
WHERE span_name = 'agent.process_message'
  AND ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
GROUP BY DATE_TRUNC('hour', ingestion_timestamp), service_name
ORDER BY metric_hour DESC;

-- ================================================================
-- Grant permissions (adjust as needed)
-- ================================================================
-- GRANT SELECT, MODIFY ON CATALOG telemetry TO `data-engineers`;
-- GRANT SELECT ON CATALOG telemetry TO `analysts`;
