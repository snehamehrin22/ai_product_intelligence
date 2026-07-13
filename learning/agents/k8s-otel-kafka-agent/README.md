# Kubernetes + OpenTelemetry + Kafka Agent Learning Project

**Goal:** Understand end-to-end observability pipeline for AI agents in production

**Timeline:** 5 hours (aggressive sprint)

---

## What You'll Learn

1. **Kubernetes (AKS)**
   - Deployments, Services, ConfigMaps, Secrets
   - Container networking and service discovery
   - kubectl basics

2. **OpenTelemetry**
   - OTLP protocol (agent → collector)
   - Collector architecture (receivers, processors, exporters)
   - GenAI semantic conventions for LLM tracing

3. **Kafka Pipeline**
   - Azure Event Hubs (Kafka-compatible)
   - Why Kafka for telemetry (vs direct writes)
   - Multi-consumer architecture

4. **Databricks**
   - Auto Loader for streaming ingestion
   - OTLP JSON parsing and flattening
   - Delta Lake for observability data

---

## Architecture

```
┌─────────────────────────────────────────────┐
│     Azure Kubernetes Service (AKS)          │
│                                             │
│  ┌─────────────┐       ┌──────────────┐   │
│  │   Agent     │──────▶│ OTLP         │   │
│  │   Pod       │ :4317 │ Collector    │   │
│  │             │       │ Pod          │   │
│  └─────────────┘       └──────────────┘   │
│        ↑                      │             │
│        │                      │             │
│   LoadBalancer             Kafka           │
│   (public IP)             Exporter         │
└────────┼──────────────────────┼────────────┘
         │                      │
    HTTP requests               ▼
    from your          Azure Event Hubs
    laptop             (Kafka-compatible)
                              │
                              ▼
                        Databricks
                     Auto Loader ──▶ Delta Lake
                                     (queries)
```

---

## Project Structure

```
k8s-otel-kafka-agent/
├── prd.json                    # User stories, acceptance criteria
├── progress.txt                # Work log
├── README.md                   # This file
│
├── agent-service/              # Standalone agent microservice
│   ├── app.py                  # FastAPI + OpenTelemetry
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── k8s/                        # Kubernetes manifests
│   ├── agent-deployment.yaml
│   ├── agent-service.yaml
│   ├── otel-collector-configmap.yaml
│   ├── otel-collector-deployment.yaml
│   └── otel-collector-service.yaml
│
├── scripts/                    # Automation scripts
│   ├── setup_aks.sh           # Create AKS cluster + ACR
│   ├── setup_eventhub.sh      # Create Event Hubs
│   ├── test_agent.sh          # Test agent endpoint
│   ├── consume_traces.py      # Kafka consumer (validation)
│   └── cleanup_all.sh         # Delete all resources
│
├── databricks/                 # Databricks notebooks
│   ├── ingest_traces_from_kafka.py
│   └── query_traces.sql
│
├── docs/                       # Documentation
│   ├── AKS_SETUP.md
│   ├── KAFKA_CONFIG.md
│   ├── DATABRICKS_SETUP.md
│   └── ARCHITECTURE.md
│
└── tests/
    └── test_e2e_pipeline.py    # End-to-end validation
```

---

## Prerequisites

Before starting, ensure you have:

1. **Azure Subscription** with credits ($5-10 budget)
2. **Azure CLI** installed: `az --version`
3. **Docker** installed: `docker --version`
4. **kubectl** installed: `kubectl version --client`
5. **Python 3.13** with venv
6. **OpenAI API Key** (for agent LLM calls)
7. **Databricks workspace** (you already have this)

**Login to Azure:**
```bash
az login
az account show  # Verify correct subscription
```

---

## Quick Start (5-Hour Sprint)

### Hour 1: Agent Service (US-1, US-2)
```bash
cd agent-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Test locally
export OPENAI_API_KEY=sk-...
python app.py

# Test endpoint
curl http://localhost:8080/health
curl -X POST http://localhost:8080/process -H "Content-Type: application/json" -d '{"message":"buy milk tomorrow"}'

# Build Docker image
docker build -t agent:local .
docker run -p 8080:8080 -e OPENAI_API_KEY=$OPENAI_API_KEY agent:local
```

### Hour 2: AKS Setup (US-3)
```bash
cd scripts
./setup_aks.sh  # Creates AKS cluster, ACR, pushes image

# Wait 15-20 minutes for cluster creation
# While waiting, work on US-4 (OTLP Collector manifests)
```

### Hour 3: Deploy Collector & Agent (US-4, US-5)
```bash
# Deploy OTLP Collector
kubectl apply -f k8s/otel-collector-configmap.yaml
kubectl apply -f k8s/otel-collector-deployment.yaml
kubectl apply -f k8s/otel-collector-service.yaml

# Verify collector running
kubectl get pods -l app=otel-collector
kubectl logs -l app=otel-collector

# Deploy agent
kubectl create secret generic openai-key --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY
kubectl apply -f k8s/agent-deployment.yaml
kubectl apply -f k8s/agent-service.yaml

# Get agent external IP
kubectl get svc agent -w

# Test agent
export AGENT_IP=$(kubectl get svc agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
./scripts/test_agent.sh $AGENT_IP
```

### Hour 4: Kafka Pipeline (US-6)
```bash
# Create Event Hubs
./scripts/setup_eventhub.sh

# Update collector config with Kafka exporter
kubectl apply -f k8s/otel-collector-configmap.yaml
kubectl rollout restart deployment/otel-collector

# Test Kafka consumer
python scripts/consume_traces.py
```

### Hour 5: Databricks Ingestion (US-7)
```bash
# Open Databricks workspace
# Create notebook: databricks/ingest_traces_from_kafka.py
# Run streaming job
# Query traces: SELECT * FROM main.observability.agent_traces_k8s
```

---

## Cost Breakdown

| Resource | SKU | Cost (5 hours) |
|----------|-----|----------------|
| AKS (1 node) | Standard_B2s | ~$0.50 |
| ACR | Basic | ~$0.04 |
| Event Hubs | Standard | ~$0.02 |
| LoadBalancer | Public IP | ~$0.02 |
| Databricks | Existing | $0 |
| **Total** | | **~$0.58** |

**Daily cost if left running:** ~$2.78

**Cleanup immediately after learning to minimize costs!**

---

## Cleanup

**Delete everything:**
```bash
./scripts/cleanup_all.sh
```

This deletes:
- AKS cluster
- ACR
- Event Hubs namespace
- Resource group
- All associated resources

---

## Success Criteria

✅ Agent runs in AKS and responds to HTTP requests
✅ OTLP Collector receives traces from agent
✅ Traces flow to Azure Event Hubs (Kafka)
✅ Databricks ingests traces to Delta Lake
✅ Can query traces with SQL

**End-to-end test:** Send agent request → Wait 60s → See trace in Delta Lake

---

## What's Next?

After completing this sprint, you'll understand:
- How production observability pipelines work
- Why companies use Kafka for telemetry
- How Kubernetes orchestrates microservices
- How OpenTelemetry standardizes observability

**Next learning projects:**
- Add Prometheus metrics collection
- Implement distributed tracing across multiple services
- Add log aggregation (Loki or Azure Monitor)
- Build alerting on trace anomalies

---

## Troubleshooting

**Agent pod not starting:**
```bash
kubectl describe pod -l app=agent
kubectl logs -l app=agent
```

**Collector not receiving traces:**
```bash
kubectl logs -l app=otel-collector | grep -i error
# Check OTEL_EXPORTER_OTLP_ENDPOINT in agent pod
kubectl exec -it <agent-pod> -- env | grep OTEL
```

**Event Hubs not receiving data:**
```bash
# Check collector logs for Kafka errors
kubectl logs -l app=otel-collector | grep -i kafka
# Verify connection string in secret
kubectl get secret eventhub-conn -o yaml
```

---

**Ready to start?** Begin with US-1 (Extract Agent Service)
