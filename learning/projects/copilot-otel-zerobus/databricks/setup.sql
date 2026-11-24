-- Copilot OTel → ZeroBus: Delta Table Setup
-- Reuses existing catalog: signaltogrowth_zerobus.bronze
-- Run in Databricks SQL Editor against your SQL Warehouse

-- ─── Spans ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS signaltogrowth_zerobus.bronze.copilot_otel_spans (
  record_id                 STRING,
  time                      TIMESTAMP,
  date                      DATE,
  service_name              STRING,
  trace_id                  STRING,
  span_id                   STRING,
  trace_state               STRING,
  parent_span_id            STRING,
  flags                     INT,
  name                      STRING,
  kind                      STRING,
  start_time_unix_nano      LONG,
  end_time_unix_nano        LONG,
  attributes                VARIANT,
  dropped_attributes_count  INT,
  events                    ARRAY<STRUCT<
                              time_unix_nano: LONG,
                              name: STRING,
                              attributes: VARIANT,
                              dropped_attributes_count: INT
                            >>,
  dropped_events_count      INT,
  links                     ARRAY<STRUCT<
                              trace_id: STRING,
                              span_id: STRING,
                              trace_state: STRING,
                              attributes: VARIANT,
                              dropped_attributes_count: INT,
                              flags: INT
                            >>,
  dropped_links_count       INT,
  status                    STRUCT<message: STRING, code: STRING>,
  resource                  STRUCT<attributes: VARIANT, dropped_attributes_count: INT>,
  resource_schema_url       STRING,
  instrumentation_scope     STRUCT<
                              name: STRING,
                              version: STRING,
                              attributes: VARIANT,
                              dropped_attributes_count: INT
                            >,
  span_schema_url           STRING
)
USING DELTA
CLUSTER BY (time, service_name, trace_id)
TBLPROPERTIES (
  'otel.schemaVersion' = 'v2',
  'delta.checkpointPolicy' = 'classic'
);

-- ─── Logs ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS signaltogrowth_zerobus.bronze.copilot_otel_logs (
  record_id                  STRING,
  time                       TIMESTAMP,
  date                       DATE,
  service_name               STRING,
  event_name                 STRING,
  trace_id                   STRING,
  span_id                    STRING,
  time_unix_nano             LONG,
  observed_time_unix_nano    LONG,
  severity_number            STRING,
  severity_text              STRING,
  body                       VARIANT,
  attributes                 VARIANT,
  dropped_attributes_count   INT,
  flags                      INT,
  resource                   STRUCT<attributes: VARIANT, dropped_attributes_count: INT>,
  resource_schema_url        STRING,
  instrumentation_scope      STRUCT<
                               name: STRING,
                               version: STRING,
                               attributes: VARIANT,
                               dropped_attributes_count: INT
                             >,
  log_schema_url             STRING
)
USING DELTA
CLUSTER BY (time, service_name)
TBLPROPERTIES (
  'otel.schemaVersion' = 'v2',
  'delta.checkpointPolicy' = 'classic'
);

-- ─── Metrics ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS signaltogrowth_zerobus.bronze.copilot_otel_metrics (
  record_id             STRING,
  time                  TIMESTAMP,
  date                  DATE,
  service_name          STRING,
  start_time_unix_nano  LONG,
  time_unix_nano        LONG,
  name                  STRING,
  description           STRING,
  unit                  STRING,
  metric_type           STRING,
  gauge STRUCT<
    value: DOUBLE,
    exemplars: ARRAY<STRUCT<time_unix_nano: LONG, value: DOUBLE, span_id: STRING, trace_id: STRING, filtered_attributes: VARIANT>>,
    attributes: VARIANT,
    flags: INT
  >,
  sum STRUCT<
    value: DOUBLE,
    exemplars: ARRAY<STRUCT<time_unix_nano: LONG, value: DOUBLE, span_id: STRING, trace_id: STRING, filtered_attributes: VARIANT>>,
    attributes: VARIANT,
    flags: INT,
    aggregation_temporality: STRING,
    is_monotonic: BOOLEAN
  >,
  histogram STRUCT<
    count: LONG,
    sum: DOUBLE,
    bucket_counts: ARRAY<LONG>,
    explicit_bounds: ARRAY<DOUBLE>,
    exemplars: ARRAY<STRUCT<time_unix_nano: LONG, value: DOUBLE, span_id: STRING, trace_id: STRING, filtered_attributes: VARIANT>>,
    attributes: VARIANT,
    flags: INT,
    min: DOUBLE,
    max: DOUBLE,
    aggregation_temporality: STRING
  >,
  metadata             VARIANT,
  resource             STRUCT<attributes: VARIANT, dropped_attributes_count: INT>,
  resource_schema_url  STRING,
  instrumentation_scope STRUCT<
    name: STRING,
    version: STRING,
    attributes: VARIANT,
    dropped_attributes_count: INT
  >,
  metric_schema_url    STRING
)
USING DELTA
CLUSTER BY (time, service_name)
TBLPROPERTIES (
  'otel.schemaVersion' = 'v2',
  'delta.checkpointPolicy' = 'classic'
);

-- ─── Grant permissions to existing service principal ──────────────────────────
-- Replace <SERVICE_PRINCIPAL_CLIENT_ID> with your service principal application ID.
-- (catalog + schema USE already granted from ai-todo-app setup)

GRANT MODIFY, SELECT ON TABLE signaltogrowth_zerobus.bronze.copilot_otel_spans
  TO `<SERVICE_PRINCIPAL_CLIENT_ID>`;

GRANT MODIFY, SELECT ON TABLE signaltogrowth_zerobus.bronze.copilot_otel_logs
  TO `<SERVICE_PRINCIPAL_CLIENT_ID>`;

GRANT MODIFY, SELECT ON TABLE signaltogrowth_zerobus.bronze.copilot_otel_metrics
  TO `<SERVICE_PRINCIPAL_CLIENT_ID>`;

-- ─── Verify ───────────────────────────────────────────────────────────────────
SELECT COUNT(*) AS spans_count   FROM signaltogrowth_zerobus.bronze.copilot_otel_spans;
SELECT COUNT(*) AS logs_count    FROM signaltogrowth_zerobus.bronze.copilot_otel_logs;
SELECT COUNT(*) AS metrics_count FROM signaltogrowth_zerobus.bronze.copilot_otel_metrics;
