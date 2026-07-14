# K8s + OpenTelemetry + Kafka Learning Project

**Goal:** Learn OpenTelemetry for AI agents by building a complete observability pipeline from K8s to Databricks.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Azure Kubernetes Service (AKS)          │
│                                                                 │
│  ┌──────────────┐      ┌─────────────────────────────────┐    │
│  │              │ OTLP │                                   │    │
│  │  AI Agent    ├─────►│  OTLP Collector                  │    │
│  │  (FastAPI)   │ :4317│  - Receivers: OTLP gRPC          │    │
│  │              │      │  - Processors: Batch             │    │
│  └──────────────┘      │  - Exporters: Logging + Kafka    │    │
│                        └─────────────────────────────────┘    │
│                                       │                        │
└───────────────────────────────────────┼────────────────────────┘
                                        │ Kafka Protocol
                                        │ (port 9093)
                                        ▼
                        ┌──────────────────────────────┐
                        │   Azure Event Hubs           │
                        │   (Kafka-compatible)         │
                        │   Topic: agent-traces        │
                        └──────────────────────────────┘
                                        │
                                        │ Structured Streaming
                                        ▼
                        ┌──────────────────────────────┐
                        │   Databricks                 │
                        │   - Auto Loader              │
                        │   - OTLP JSON parsing        │
                        │   - Delta Lake storage       │
                        └──────────────────────────────┘
```

## What You'll Learn

1. **OpenTelemetry SDK** - Instrumenting Python applications with OTLP
2. **OTLP Collector** - Middleware for receiving, processing, and exporting telemetry
3. **Kubernetes** - Container orchestration, deployments, services, ConfigMaps, secrets
4. **Azure Kubernetes Service (AKS)** - Managed Kubernetes in Azure
5. **Azure Container Registry (ACR)** - Private Docker registry
6. **Azure Event Hubs** - Kafka-compatible message streaming
7. **Databricks Structured Streaming** - Real-time data ingestion
8. **Delta Lake** - Analytics storage layer
9. **GenAI Semantic Conventions** - Standardized attributes for AI/LLM traces

## Prerequisites

- **Azure Account** with active subscription
- **Azure CLI** installed and logged in (`az login`)
- **kubectl** installed
- **OpenAI API Key** (from https://platform.openai.com/)
- **Databricks workspace** with SQL Warehouse

## Quick Start (5-Hour Sprint)

### Option A: Full Automated Deployment

```bash
cd scripts

# Set OpenAI key
export OPENAI_API_KEY='sk-proj-...'

# Deploy everything
./deploy_all.sh
```

This will:
1. Create AKS cluster + ACR (~20 min)
2. Build and push agent image (~3 min)
3. Deploy OTLP Collector (~2 min)
4. Deploy agent (~3 min)
5. Create Event Hubs (~2 min)
6. Configure Kafka exporter (~1 min)
7. Send test traces (~1 min)

### Option B: Step-by-Step (Recommended for Learning)

```bash
cd scripts

# 1. Setup AKS and build agent image (US-3)
./setup_aks.sh

# 2. Deploy OTLP Collector (US-4)
cd ../k8s
kubectl apply -f otel-collector-configmap.yaml
kubectl apply -f otel-collector-deployment.yaml
kubectl apply -f otel-collector-service.yaml

# 3. Deploy Agent (US-5)
export OPENAI_API_KEY='sk-proj-...'
kubectl create secret generic openai-key --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY
kubectl apply -f agent-deployment.yaml
kubectl apply -f agent-service.yaml

# 4. Test initial deployment
kubectl get svc agent-service  # Wait for EXTERNAL-IP
AGENT_IP=$(kubectl get svc agent-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$AGENT_IP/health
curl -X POST http://$AGENT_IP/process \
  -H "Content-Type: application/json" \
  -d '{"message": "Buy milk tomorrow", "user_id": "test"}'

# 5. Setup Event Hubs (US-6)
cd ../scripts
./setup_eventhub.sh

# 6. Enable Kafka exporter in collector
cd ../k8s
kubectl apply -f otel-collector-configmap-with-kafka.yaml
kubectl rollout restart deployment/otel-collector

# 7. Configure Databricks notebook (US-7)
# Open: databricks/ingest_traces_from_kafka.py
# Set EVENTHUB_NAMESPACE and CONNECTION_STRING
# Run all cells

# 8. Validate end-to-end (US-8)
cd ../scripts
./validate_e2e.sh
```

## Project Structure

```
k8s-otel-kafka-agent/
├── README.md                              # This file
├── TROUBLESHOOTING.md                     # Common issues and solutions
├── prd.json                               # User stories and acceptance criteria
├── progress.txt                           # Work log and learnings
│
├── agent-service/                         # AI Agent
│   ├── app.py                            # FastAPI app with OTLP instrumentation
│   ├── Dockerfile                        # Multi-stage build
│   ├── requirements.txt                  # Python dependencies
│   └── .env.example                      # Environment variable template
│
├── k8s/                                   # Kubernetes Manifests
│   ├── otel-collector-configmap.yaml     # Collector config (logging only)
│   ├── otel-collector-configmap-with-kafka.yaml  # With Kafka exporter
│   ├── otel-collector-deployment.yaml    # Collector deployment
│   ├── otel-collector-service.yaml       # Collector service (ClusterIP)
│   ├── agent-deployment.yaml             # Agent deployment
│   └── agent-service.yaml                # Agent service (LoadBalancer)
│
├── scripts/                               # Automation Scripts
│   ├── setup_aks.sh                      # Create AKS + ACR
│   ├── setup_eventhub.sh                 # Create Event Hubs
│   ├── deploy_all.sh                     # Full deployment pipeline
│   ├── validate_e2e.sh                   # End-to-end testing
│   └── cleanup_aks.sh                    # Delete all resources
│
└── databricks/                            # Databricks Notebooks
    └── ingest_traces_from_kafka.py       # Streaming ingestion notebook
```

## Key Concepts Explained

### 1. OpenTelemetry Spans

Spans represent units of work in distributed tracing:

```python
# In app.py
with tracer.start_as_current_span("agent.process_message") as span:
    # Do work...
    span.set_attribute("gen_ai.request.model", "gpt-4o-mini")
    span.set_attribute("gen_ai.usage.input_tokens", 123)
```

Each span captures:
- **Trace ID**: Groups related spans
- **Span ID**: Unique identifier
- **Parent Span ID**: Creates hierarchy
- **Timestamps**: Start and end time
- **Attributes**: Custom metadata (GenAI conventions)
- **Status**: Success or error

### 2. OTLP Collector Pipeline

```yaml
receivers:     # How telemetry enters
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:    # How telemetry is transformed
  batch:
    timeout: 10s

exporters:     # Where telemetry goes
  logging:     # Print to stdout
  kafka:       # Send to Event Hubs
```

The collector acts as middleware:
- **Decouples** agents from backends
- **Batches** data for efficiency
- **Routes** to multiple destinations
- **Transforms** data (filtering, sampling, etc.)

### 3. Kubernetes Service Discovery

Services provide stable DNS names:

```yaml
# Agent connects to collector via DNS
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

Inside the cluster:
- `otel-collector` resolves to the collector's ClusterIP
- No hardcoded IPs needed
- Seamless scaling and replacement

### 4. Event Hubs as Kafka

Event Hubs speaks Kafka protocol:

```python
# In Databricks
df = spark.readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "namespace.servicebus.windows.net:9093") \
  .option("kafka.security.protocol", "SASL_SSL") \
  .option("subscribe", "agent-traces") \
  .load()
```

Why Event Hubs?
- Fully managed (no Kafka cluster maintenance)
- Azure-native integration
- Auto-scaling
- Pay-per-use pricing

### 5. GenAI Semantic Conventions

Standardized attributes for AI/LLM observability:

```python
span.set_attribute("gen_ai.request.model", "gpt-4o-mini")
span.set_attribute("gen_ai.usage.input_tokens", prompt_tokens)
span.set_attribute("gen_ai.usage.output_tokens", completion_tokens)
span.set_attribute("gen_ai.usage.total_tokens", total_tokens)
```

Enables:
- Token usage tracking
- Model performance comparison
- Cost attribution
- Request tracing

## Querying Traces in Databricks

Once ingestion is running:

```sql
-- Recent traces
SELECT
  trace_id,
  span_name,
  gen_ai_model,
  gen_ai_total_tokens,
  duration_ms,
  start_time,
  session_id
FROM main.observability.agent_traces_k8s
ORDER BY start_time DESC
LIMIT 10;

-- Token usage by session
SELECT
  session_id,
  COUNT(*) as request_count,
  SUM(gen_ai_input_tokens) as total_input_tokens,
  SUM(gen_ai_output_tokens) as total_output_tokens,
  AVG(duration_ms) as avg_duration_ms
FROM main.observability.agent_traces_k8s
WHERE session_id IS NOT NULL
GROUP BY session_id
ORDER BY request_count DESC;

-- Slowest spans
SELECT
  trace_id,
  span_name,
  duration_ms,
  start_time
FROM main.observability.agent_traces_k8s
WHERE duration_ms > 1000
ORDER BY duration_ms DESC;
```

## Cost Estimation

**Running costs (if left on 24/7):**
- AKS nodes (2x Standard_B2s): ~$60/month
- Public IPs (2): ~$6/month
- Event Hubs (Standard): ~$11/month
- Databricks (pay-per-DBU): Variable

**Total: ~$77/month if left running continuously**

**💡 Cost Saving Tips:**
```bash
# Stop AKS when not in use (saves 78%)
az aks stop -n aks-learning -g rg-k8s-learning

# Start when needed
az aks start -n aks-learning -g rg-k8s-learning

# Or delete everything
cd scripts
./cleanup_aks.sh
```

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed solutions to common issues:
- AKS / Kubernetes problems
- OTLP Collector connection issues
- Agent errors
- Event Hubs authentication
- Databricks streaming problems

Quick diagnostics:
```bash
# Check pod status
kubectl get pods

# View logs
kubectl logs -l app=otel-collector --tail=50
kubectl logs -l app=agent --tail=50

# Test agent
AGENT_IP=$(kubectl get svc agent-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$AGENT_IP/health
```

## Learning Outcomes

After completing this project, you'll understand:

✅ **How OpenTelemetry works**
- SDK instrumentation
- OTLP protocol
- Span creation and attributes

✅ **How OTLP Collector works**
- Receiver/Processor/Exporter architecture
- Batching and buffering
- Multiple exporters

✅ **How Kubernetes works**
- Deployments and pods
- Services and DNS
- ConfigMaps and secrets
- LoadBalancers

✅ **How to deploy to AKS**
- Cluster creation
- ACR integration
- Image building and pushing
- kubectl basics

✅ **How Event Hubs works as Kafka**
- Kafka protocol compatibility
- SASL authentication
- Topic/partition model

✅ **How Databricks streaming works**
- Structured Streaming
- Kafka source
- Auto Loader
- Delta Lake writes

## Next Steps

1. **Add more agent operations** - Expand beyond simple task extraction
2. **Implement sampling** - Reduce data volume for production
3. **Add metrics** - Complement traces with metrics (Prometheus)
4. **Build dashboards** - Visualize traces in Grafana or Databricks
5. **Implement alerts** - Alert on error rates or latency
6. **Production hardening** - TLS, authentication, resource limits

## References

- [OpenTelemetry Docs](https://opentelemetry.io/docs/)
- [OTLP Specification](https://opentelemetry.io/docs/specs/otlp/)
- [GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Event Hubs Kafka](https://learn.microsoft.com/azure/event-hubs/event-hubs-for-kafka-ecosystem-overview)
- [Databricks Structured Streaming](https://docs.databricks.com/structured-streaming/)

## License

MIT - This is a learning project, use however you like!
