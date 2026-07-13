# Databricks Integration for OpenTelemetry Traces

This directory contains setup files for ingesting OpenTelemetry traces from Kafka into Databricks Delta Lake.

## Architecture

```
Agent (AKS)
  ↓ OTLP/gRPC
OTLP Collector (AKS)
  ↓ Kafka Protocol
Kafka (AKS)
  ↓ Structured Streaming
Databricks Delta Lake
  ├── Bronze: raw_traces (raw Kafka messages)
  ├── Silver: parsed_traces (parsed OTLP data with GenAI attributes)
  └── Gold: agent_metrics_hourly (aggregated metrics)
```

## Prerequisites

1. **Databricks workspace** with Unity Catalog enabled
2. **Network connectivity** from Databricks to Kafka:
   - Option A: Kafka LoadBalancer with public IP
   - Option B: VNet peering between AKS and Databricks
   - Option C: Azure Private Link
3. **Databricks cluster** with:
   - Databricks Runtime 13.3 LTS or higher
   - Python 3.10+
   - Install: `protobuf==4.25.1`

## Setup Steps

### Step 1: Expose Kafka Service

The Kafka service needs to be accessible from Databricks. Let's create a LoadBalancer service:

```bash
# Apply the Kafka LoadBalancer service
kubectl apply -f ../k8s/kafka-loadbalancer-service.yaml

# Get the external IP (may take a few minutes)
kubectl get svc kafka-external -w

# Note the EXTERNAL-IP for use in Databricks
```

### Step 2: Create Delta Tables

1. Open Databricks SQL Editor or a Databricks notebook
2. Run the SQL script: `setup_kafka_streaming.sql`
3. This creates:
   - Catalog: `telemetry`
   - Schema: `agent_traces`
   - Tables: `raw_traces`, `parsed_traces`, `agent_metrics_hourly`
   - Views: `recent_traces`, `token_usage_summary`, `agent_performance`

```sql
-- In Databricks SQL Editor
-- Copy and paste the contents of setup_kafka_streaming.sql
```

### Step 3: Configure Streaming Notebook

1. Import `streaming_ingestion_notebook.py` into Databricks
2. Update the Kafka broker configuration:
   ```python
   KAFKA_BROKER = "<KAFKA_EXTERNAL_IP>:9092"  # From Step 1
   KAFKA_TOPIC = "agent-traces"
   ```
3. Run the notebook to start streaming ingestion

### Step 4: Verify Data Flow

```sql
-- Check raw traces
SELECT COUNT(*) FROM telemetry.agent_traces.raw_traces;

-- View recent traces
SELECT * FROM telemetry.agent_traces.recent_traces LIMIT 10;

-- Check token usage
SELECT * FROM telemetry.agent_traces.token_usage_summary;
```

## Data Schema

### Bronze Layer: `raw_traces`
Raw Kafka messages with metadata:
- `kafka_value`: OTLP Protobuf binary data
- `kafka_topic`, `kafka_partition`, `kafka_offset`
- `ingestion_timestamp`

### Silver Layer: `parsed_traces`
Structured trace data with:
- Trace/Span IDs
- GenAI semantic conventions (model, tokens, finish reason)
- Agent attributes (priority, confidence, processing time)
- Service metadata (name, version, environment)

### Gold Layer: `agent_metrics_hourly`
Aggregated metrics:
- LLM usage (total requests, tokens by model)
- Performance (avg/p50/p95/p99 duration)
- Success rates
- Task extraction metrics

## Querying Examples

### Token Usage by Model
```sql
SELECT
  gen_ai_request_model,
  COUNT(*) as requests,
  SUM(gen_ai_usage_total_tokens) as total_tokens,
  AVG(gen_ai_usage_total_tokens) as avg_tokens
FROM telemetry.agent_traces.parsed_traces
WHERE ingestion_date = CURRENT_DATE()
GROUP BY gen_ai_request_model;
```

### Agent Performance Over Time
```sql
SELECT
  DATE_TRUNC('hour', ingestion_timestamp) as hour,
  COUNT(*) as requests,
  AVG(duration_ms) as avg_duration_ms,
  AVG(extraction_confidence) as avg_confidence,
  AVG(CASE WHEN agent_success THEN 1.0 ELSE 0.0 END) as success_rate
FROM telemetry.agent_traces.parsed_traces
WHERE span_name = 'agent.process_message'
  AND ingestion_date >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY hour
ORDER BY hour DESC;
```

### High Token Usage Traces
```sql
SELECT
  trace_id,
  span_name,
  gen_ai_request_model,
  gen_ai_usage_total_tokens,
  duration_ms,
  ingestion_timestamp
FROM telemetry.agent_traces.parsed_traces
WHERE gen_ai_usage_total_tokens > 1000
ORDER BY gen_ai_usage_total_tokens DESC
LIMIT 100;
```

## Monitoring Streaming Jobs

### Check Stream Status
```python
# In Databricks notebook
for stream in spark.streams.active:
    print(f"Stream: {stream.name}")
    print(f"  Status: {stream.status}")
    print(f"  Processed: {stream.lastProgress}")
```

### Stream Metrics
```sql
-- Check ingestion lag
SELECT
  MAX(ingestion_timestamp) as last_ingestion,
  MAX(kafka_timestamp) as last_kafka_message,
  TIMESTAMPDIFF(SECOND, MAX(kafka_timestamp), MAX(ingestion_timestamp)) as lag_seconds
FROM telemetry.agent_traces.raw_traces;
```

## Troubleshooting

### Issue: Cannot connect to Kafka
- **Check**: Kafka LoadBalancer has external IP
- **Check**: Network connectivity from Databricks to AKS
- **Check**: Kafka service is running: `kubectl get pods -l app=kafka`

### Issue: No data in raw_traces
- **Check**: Kafka has messages: `kubectl exec kafka-0 -- kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic agent-traces`
- **Check**: Stream is running in Databricks
- **Check**: Checkpoint location is accessible

### Issue: Parsing errors
- **Check**: OTLP data format (protobuf vs JSON)
- **Check**: Parser implementation matches data format
- **Check**: protobuf library installed: `%pip install protobuf`

## Cost Optimization

1. **Partitioning**: Tables are partitioned by `ingestion_date` for efficient queries
2. **Auto-optimization**: Delta Lake auto-optimize enabled for write optimization
3. **Retention**: Set retention policy:
   ```sql
   -- Keep last 90 days
   ALTER TABLE telemetry.agent_traces.raw_traces
   SET TBLPROPERTIES ('delta.deletedFileRetentionDuration' = 'interval 7 days');

   OPTIMIZE telemetry.agent_traces.raw_traces;
   VACUUM telemetry.agent_traces.raw_traces RETAIN 7 HOURS;
   ```

## Next Steps

1. **Implement OTLP Parser**: Complete the protobuf parsing logic in the notebook
2. **Create Dashboards**: Build Databricks SQL dashboards for metrics
3. **Set up Alerts**: Configure alerts for high token usage, errors, or latency
4. **Add Data Quality**: Implement expectations using Delta Live Tables
5. **Automate Aggregations**: Schedule jobs to update gold layer tables
