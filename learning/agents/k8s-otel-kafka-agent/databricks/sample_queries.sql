-- ================================================================
-- Sample Queries for OpenTelemetry Traces Analysis
-- ================================================================
-- Use these queries in Databricks SQL Editor or notebooks
-- ================================================================

USE CATALOG telemetry;
USE SCHEMA agent_traces;

-- ================================================================
-- 1. VERIFICATION QUERIES
-- ================================================================

-- Check raw traces count
SELECT COUNT(*) as total_raw_traces
FROM raw_traces;

-- Check latest raw ingestion
SELECT
  MAX(ingestion_timestamp) as last_ingestion,
  MAX(kafka_timestamp) as last_kafka_message,
  COUNT(*) as message_count
FROM raw_traces;

-- Check parsed traces count
SELECT COUNT(*) as total_parsed_traces
FROM parsed_traces;

-- ================================================================
-- 2. RECENT ACTIVITY
-- ================================================================

-- Last 10 traces with details
SELECT
  trace_id,
  span_name,
  service_name,
  gen_ai_request_model,
  gen_ai_usage_total_tokens,
  duration_ms,
  agent_success,
  extraction_confidence,
  ingestion_timestamp
FROM parsed_traces
ORDER BY ingestion_timestamp DESC
LIMIT 10;

-- Traces from last hour
SELECT
  DATE_TRUNC('minute', ingestion_timestamp) as minute,
  COUNT(*) as trace_count,
  AVG(duration_ms) as avg_duration_ms
FROM parsed_traces
WHERE ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
GROUP BY minute
ORDER BY minute DESC;

-- ================================================================
-- 3. GenAI TOKEN USAGE ANALYSIS
-- ================================================================

-- Total token usage by model
SELECT
  gen_ai_request_model,
  COUNT(*) as request_count,
  SUM(gen_ai_usage_input_tokens) as total_input_tokens,
  SUM(gen_ai_usage_output_tokens) as total_output_tokens,
  SUM(gen_ai_usage_total_tokens) as total_tokens,
  AVG(gen_ai_usage_total_tokens) as avg_tokens_per_request,
  AVG(duration_ms) as avg_duration_ms
FROM parsed_traces
WHERE gen_ai_request_model IS NOT NULL
GROUP BY gen_ai_request_model
ORDER BY total_tokens DESC;

-- Token usage over time (hourly)
SELECT
  DATE_TRUNC('hour', ingestion_timestamp) as hour,
  gen_ai_request_model,
  COUNT(*) as requests,
  SUM(gen_ai_usage_total_tokens) as total_tokens,
  AVG(gen_ai_usage_total_tokens) as avg_tokens,
  MAX(gen_ai_usage_total_tokens) as max_tokens
FROM parsed_traces
WHERE gen_ai_request_model IS NOT NULL
  AND ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 24 HOURS
GROUP BY hour, gen_ai_request_model
ORDER BY hour DESC, gen_ai_request_model;

-- High token usage traces (potential cost anomalies)
SELECT
  trace_id,
  span_name,
  gen_ai_request_model,
  gen_ai_usage_total_tokens,
  gen_ai_usage_input_tokens,
  gen_ai_usage_output_tokens,
  duration_ms,
  ingestion_timestamp
FROM parsed_traces
WHERE gen_ai_usage_total_tokens > 500  -- Adjust threshold as needed
ORDER BY gen_ai_usage_total_tokens DESC
LIMIT 20;

-- Token usage by finish reason (check for truncations)
SELECT
  gen_ai_response_finish_reason,
  COUNT(*) as count,
  AVG(gen_ai_usage_total_tokens) as avg_tokens,
  AVG(duration_ms) as avg_duration_ms
FROM parsed_traces
WHERE gen_ai_request_model IS NOT NULL
GROUP BY gen_ai_response_finish_reason
ORDER BY count DESC;

-- ================================================================
-- 4. AGENT PERFORMANCE METRICS
-- ================================================================

-- Overall performance summary
SELECT
  COUNT(*) as total_requests,
  AVG(duration_ms) as avg_duration_ms,
  PERCENTILE_APPROX(duration_ms, 0.5) as p50_duration_ms,
  PERCENTILE_APPROX(duration_ms, 0.95) as p95_duration_ms,
  PERCENTILE_APPROX(duration_ms, 0.99) as p99_duration_ms,
  MAX(duration_ms) as max_duration_ms,
  SUM(CASE WHEN agent_success THEN 1 ELSE 0 END) as success_count,
  AVG(CASE WHEN agent_success THEN 1.0 ELSE 0.0 END) as success_rate
FROM parsed_traces
WHERE span_name = 'agent.process_message';

-- Performance by hour
SELECT
  DATE_TRUNC('hour', ingestion_timestamp) as hour,
  COUNT(*) as requests,
  AVG(duration_ms) as avg_duration_ms,
  PERCENTILE_APPROX(duration_ms, 0.95) as p95_duration_ms,
  AVG(CASE WHEN agent_success THEN 1.0 ELSE 0.0 END) as success_rate
FROM parsed_traces
WHERE span_name = 'agent.process_message'
  AND ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 24 HOURS
GROUP BY hour
ORDER BY hour DESC;

-- Slowest traces
SELECT
  trace_id,
  span_name,
  duration_ms,
  agent_success,
  gen_ai_usage_total_tokens,
  ingestion_timestamp
FROM parsed_traces
WHERE span_name = 'agent.process_message'
ORDER BY duration_ms DESC
LIMIT 20;

-- Failed requests analysis
SELECT
  trace_id,
  span_name,
  duration_ms,
  extraction_priority,
  extraction_confidence,
  gen_ai_usage_total_tokens,
  ingestion_timestamp
FROM parsed_traces
WHERE agent_success = FALSE
ORDER BY ingestion_timestamp DESC
LIMIT 50;

-- ================================================================
-- 5. TASK EXTRACTION ANALYSIS
-- ================================================================

-- Tasks by priority
SELECT
  extraction_priority,
  COUNT(*) as task_count,
  AVG(extraction_confidence) as avg_confidence,
  AVG(duration_ms) as avg_duration_ms,
  SUM(CASE WHEN extraction_has_due_date THEN 1 ELSE 0 END) as tasks_with_due_date
FROM parsed_traces
WHERE span_name = 'agent.extract_task'
GROUP BY extraction_priority
ORDER BY
  CASE extraction_priority
    WHEN 'high' THEN 1
    WHEN 'medium' THEN 2
    WHEN 'low' THEN 3
  END;

-- High confidence extractions
SELECT
  trace_id,
  extraction_priority,
  extraction_confidence,
  extraction_has_due_date,
  gen_ai_usage_total_tokens,
  duration_ms,
  ingestion_timestamp
FROM parsed_traces
WHERE span_name = 'agent.extract_task'
  AND extraction_confidence > 0.9
ORDER BY extraction_confidence DESC
LIMIT 50;

-- Low confidence extractions (may need review)
SELECT
  trace_id,
  extraction_priority,
  extraction_confidence,
  gen_ai_usage_total_tokens,
  duration_ms,
  ingestion_timestamp
FROM parsed_traces
WHERE span_name = 'agent.extract_task'
  AND extraction_confidence < 0.7
ORDER BY extraction_confidence ASC
LIMIT 50;

-- Confidence distribution
SELECT
  FLOOR(extraction_confidence * 10) / 10 as confidence_bucket,
  COUNT(*) as count,
  AVG(duration_ms) as avg_duration_ms
FROM parsed_traces
WHERE span_name = 'agent.extract_task'
GROUP BY confidence_bucket
ORDER BY confidence_bucket DESC;

-- ================================================================
-- 6. TRACE RELATIONSHIPS (Parent-Child Spans)
-- ================================================================

-- Find complete traces with all spans
WITH trace_spans AS (
  SELECT
    trace_id,
    COUNT(*) as span_count,
    MIN(start_time_unix_nano) as trace_start,
    MAX(end_time_unix_nano) as trace_end,
    COLLECT_LIST(span_name) as span_names
  FROM parsed_traces
  WHERE ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
  GROUP BY trace_id
)
SELECT
  trace_id,
  span_count,
  (trace_end - trace_start) / 1000000.0 as total_trace_duration_ms,
  span_names
FROM trace_spans
ORDER BY span_count DESC, total_trace_duration_ms DESC
LIMIT 20;

-- ================================================================
-- 7. COST ANALYSIS
-- ================================================================

-- Estimated costs (adjust pricing based on your model)
-- Assuming gpt-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
SELECT
  gen_ai_request_model,
  COUNT(*) as requests,
  SUM(gen_ai_usage_input_tokens) / 1000000.0 as input_tokens_millions,
  SUM(gen_ai_usage_output_tokens) / 1000000.0 as output_tokens_millions,
  (SUM(gen_ai_usage_input_tokens) / 1000000.0 * 0.15) as estimated_input_cost_usd,
  (SUM(gen_ai_usage_output_tokens) / 1000000.0 * 0.60) as estimated_output_cost_usd,
  (SUM(gen_ai_usage_input_tokens) / 1000000.0 * 0.15 +
   SUM(gen_ai_usage_output_tokens) / 1000000.0 * 0.60) as total_estimated_cost_usd
FROM parsed_traces
WHERE gen_ai_request_model = 'gpt-4o-mini'
GROUP BY gen_ai_request_model;

-- Daily cost trend
SELECT
  DATE(ingestion_timestamp) as date,
  COUNT(*) as requests,
  SUM(gen_ai_usage_total_tokens) / 1000000.0 as total_tokens_millions,
  (SUM(gen_ai_usage_input_tokens) / 1000000.0 * 0.15 +
   SUM(gen_ai_usage_output_tokens) / 1000000.0 * 0.60) as estimated_cost_usd
FROM parsed_traces
WHERE gen_ai_request_model = 'gpt-4o-mini'
GROUP BY date
ORDER BY date DESC;

-- ================================================================
-- 8. DATA QUALITY CHECKS
-- ================================================================

-- Check for missing critical fields
SELECT
  'Missing trace_id' as issue,
  COUNT(*) as count
FROM parsed_traces
WHERE trace_id IS NULL
UNION ALL
SELECT
  'Missing span_id' as issue,
  COUNT(*) as count
FROM parsed_traces
WHERE span_id IS NULL
UNION ALL
SELECT
  'Missing service_name' as issue,
  COUNT(*) as count
FROM parsed_traces
WHERE service_name IS NULL
UNION ALL
SELECT
  'Missing duration_ms' as issue,
  COUNT(*) as count
FROM parsed_traces
WHERE duration_ms IS NULL;

-- Check for anomalies
SELECT
  'Negative duration' as anomaly,
  COUNT(*) as count
FROM parsed_traces
WHERE duration_ms < 0
UNION ALL
SELECT
  'Zero duration' as anomaly,
  COUNT(*) as count
FROM parsed_traces
WHERE duration_ms = 0
UNION ALL
SELECT
  'Extremely long duration (>60s)' as anomaly,
  COUNT(*) as count
FROM parsed_traces
WHERE duration_ms > 60000;

-- ================================================================
-- 9. CREATE SAMPLE DASHBOARDS DATA
-- ================================================================

-- Real-time monitoring view (refresh every minute)
CREATE OR REPLACE VIEW realtime_metrics AS
SELECT
  DATE_TRUNC('minute', ingestion_timestamp) as timestamp,
  COUNT(*) as requests_per_minute,
  AVG(duration_ms) as avg_duration_ms,
  AVG(gen_ai_usage_total_tokens) as avg_tokens,
  AVG(CASE WHEN agent_success THEN 1.0 ELSE 0.0 END) as success_rate,
  AVG(extraction_confidence) as avg_confidence
FROM parsed_traces
WHERE ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 15 MINUTES
GROUP BY timestamp
ORDER BY timestamp DESC;

-- Service health view
CREATE OR REPLACE VIEW service_health AS
SELECT
  service_name,
  deployment_environment,
  COUNT(*) as total_requests,
  AVG(duration_ms) as avg_duration_ms,
  PERCENTILE_APPROX(duration_ms, 0.95) as p95_duration_ms,
  AVG(CASE WHEN agent_success THEN 1.0 ELSE 0.0 END) as success_rate,
  SUM(gen_ai_usage_total_tokens) as total_tokens_used,
  MAX(ingestion_timestamp) as last_seen
FROM parsed_traces
WHERE ingestion_timestamp >= CURRENT_TIMESTAMP() - INTERVAL 1 HOUR
GROUP BY service_name, deployment_environment;

-- Query the views
SELECT * FROM realtime_metrics;
SELECT * FROM service_health;
