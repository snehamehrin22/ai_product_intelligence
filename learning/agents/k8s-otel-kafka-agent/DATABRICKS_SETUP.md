# Databricks Setup Guide

## Quick Start

Your Kafka broker is now accessible at: **`20.121.166.131:9092`**

Follow these steps to ingest traces into Databricks:

### Step 1: Create Delta Tables in Databricks

1. Open your Databricks workspace
2. Go to **SQL Editor** or create a **new notebook**
3. Copy and paste the contents of `databricks/setup_kafka_streaming.sql`
4. Run the script to create:
   - Catalog: `telemetry`
   - Schema: `agent_traces`
   - Tables for Bronze/Silver/Gold layers
   - Views for easy querying

### Step 2: Import Streaming Notebook

1. Import `databricks/streaming_ingestion_notebook.py` into Databricks
2. Update the configuration:
   ```python
   KAFKA_BROKER = "20.121.166.131:9092"
   KAFKA_TOPIC = "agent-traces"
   ```
3. Attach to a cluster with Databricks Runtime 13.3 LTS or higher
4. Install dependencies:
   ```python
   %pip install protobuf==4.25.1
   ```

### Step 3: Start Streaming

Run the notebook to start streaming from Kafka to Delta Lake.

### Step 4: Verify Data

```sql
-- Check raw traces
SELECT COUNT(*) FROM telemetry.agent_traces.raw_traces;

-- View recent traces
SELECT * FROM telemetry.agent_traces.recent_traces LIMIT 10;

-- Token usage summary
SELECT * FROM telemetry.agent_traces.token_usage_summary;
```

## Architecture

```
Agent (FastAPI in AKS)
  ↓ OTLP/gRPC (port 4317)
OTLP Collector (AKS)
  ↓ Kafka Protocol
Kafka (AKS) - 20.121.166.131:9092
  ↓ Structured Streaming
Databricks Delta Lake
  ├── Bronze: raw_traces
  ├── Silver: parsed_traces (with GenAI attributes)
  └── Gold: agent_metrics_hourly
```

## What Gets Captured

### GenAI Semantic Conventions
- Model used (e.g., gpt-4o-mini)
- Token usage (input, output, total)
- Finish reason (stop, length, etc.)

### Agent Attributes
- Task priority (low, medium, high)
- Extraction confidence (0-1)
- Processing time
- Success/failure status

### Performance Metrics
- Span duration
- Request rates
- Success rates
- Error rates

## Sample Queries

### Token Usage by Hour
```sql
SELECT
  DATE_TRUNC('hour', ingestion_timestamp) as hour,
  gen_ai_request_model,
  COUNT(*) as requests,
  SUM(gen_ai_usage_total_tokens) as total_tokens,
  AVG(duration_ms) as avg_duration_ms
FROM telemetry.agent_traces.parsed_traces
WHERE ingestion_date = CURRENT_DATE()
GROUP BY hour, gen_ai_request_model
ORDER BY hour DESC;
```

### High Confidence Extractions
```sql
SELECT
  trace_id,
  span_name,
  extraction_priority,
  extraction_confidence,
  gen_ai_usage_total_tokens,
  duration_ms
FROM telemetry.agent_traces.parsed_traces
WHERE extraction_confidence > 0.9
  AND ingestion_date = CURRENT_DATE()
ORDER BY extraction_confidence DESC;
```

### Error Rate Analysis
```sql
SELECT
  DATE_TRUNC('hour', ingestion_timestamp) as hour,
  COUNT(*) as total_requests,
  SUM(CASE WHEN agent_success THEN 1 ELSE 0 END) as success_count,
  AVG(CASE WHEN agent_success THEN 1.0 ELSE 0.0 END) as success_rate
FROM telemetry.agent_traces.parsed_traces
WHERE span_name = 'agent.process_message'
  AND ingestion_date >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY hour
ORDER BY hour DESC;
```

## Next Steps

1. **Implement OTLP Parser**: Complete the protobuf parsing in the streaming notebook
2. **Create Dashboards**: Build visualizations for metrics
3. **Set up Alerts**: Configure alerts for anomalies
4. **Optimize Costs**: Set retention policies and optimize partitioning
5. **Add Security**: Consider VNet peering instead of public LoadBalancer

## Troubleshooting

### Can't connect to Kafka
```bash
# Test connectivity from your machine
telnet 20.121.166.131 9092

# Check Kafka pod status
kubectl get pods -l app=kafka

# Check Kafka service
kubectl get svc kafka-external
```

### No messages in Kafka
```bash
# Check message count
kubectl exec kafka-0 -- kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 --topic agent-traces

# Test agent endpoint
curl -X POST "http://20.75.255.1/process" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test trace", "user_id": "test"}'
```

## Resources

- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Databricks Structured Streaming](https://docs.databricks.com/structured-streaming/index.html)
- [Delta Lake Best Practices](https://docs.databricks.com/delta/best-practices.html)
