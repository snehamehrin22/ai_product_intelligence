# AI-Powered Todo App — Full-Stack Learning Project

**One-liner:** Build a Todoist-like app with an AI agent assistant, full event instrumentation, and a production-grade Databricks data pipeline — learn the complete modern data + AI stack.

---

## What You're Actually Building

**The App:** A todo list with an AI agent that:
- Creates tasks from natural language ("Remind me to buy groceries tomorrow at 3pm")
- Suggests task breakdowns ("Plan wedding" → subtasks)
- Re-prioritizes based on context
- Summarizes your week

**The Learning Path:** Every layer of a modern data + AI platform:
1. **Frontend** (React) → **Backend** (FastAPI) → **Transactional DB** (Lakebase in Databricks)
2. **Event instrumentation** (platform clicks + agent traces)
3. **Streaming ingestion** (Kafka → Databricks)
4. **Medallion architecture** (Bronze → Silver → Gold) with **dbt**
5. **Unity Catalog** (governance), **Auto Loader** (incremental ingestion), **Lakehouse** architecture
6. **Agent telemetry + evaluation** (OTel, LangSmith/Langfuse)

**Why this works:** You get a real app you'll actually use, while learning every piece of the AgentOS architecture.

---

## Tech Stack — Production-Grade Databricks Ecosystem

| Layer | Technology | Why | Learning Goal |
|-------|-----------|-----|---------------|
| **Frontend** | React | Modern web UI | Component design, state management, API integration |
| **Backend** | FastAPI (Azure AKS or local) | Async Python API | RESTful design, auth, business logic |
| **Transactional DB** | **Lakebase** (Databricks) | Replace Postgres with lakehouse-native OLTP | Understand when lakehouse replaces traditional DBs |
| **Message Broker** | **Azure Event Hubs** (Kafka API) | Streaming event ingestion | Kafka fundamentals, partitioning, consumer groups |
| **Agent Framework** | LangGraph | Multi-step agent orchestration | Tool calling, state management, streaming |
| **Model Gateway** | LiteLLM (local ROKAI equivalent) | Model routing, cost tracking | Unified LLM interface, fallbacks |
| **Lakehouse** | **Databricks** (Unity Catalog, Delta Lake) | Single source of truth | Medallion arch, governance, lineage |
| **Ingestion** | **Auto Loader** | Incremental file/stream processing | `COPY INTO`, checkpointing, schema evolution |
| **Transformation** | **dbt Core** (on Databricks) | SQL-based transformations | Medallion layers, tests, docs, lineage |
| **Observability (Platform)** | Custom events → Kafka → Databricks | UI interaction tracking | Event schema design, instrumentation |
| **Observability (Agent)** | **OpenTelemetry + Langfuse** | LLM trace visualization | OTel GenAI conventions, trace propagation |
| **Evaluation** | **LangSmith** or custom eval harness | Agent quality gates | Golden datasets, online/offline eval |
| **Orchestration** | **Databricks Workflows** | Schedule dbt, evals, reports | DAG design, dependencies, alerting |

---

## Architecture Diagram (What You're Building)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                           │
│  - Todo List UI                                                     │
│  - AI Agent Chat Interface                                          │
│  - Platform Event Emitter (page_viewed, task_created, etc.)        │
└────────────────┬────────────────────────────────────────────────────┘
                 │ REST API + WebSocket (streaming)
                 │ session_id propagation
                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI on Azure AKS)                  │
│  - /tasks CRUD endpoints                                            │
│  - /agent/chat (LangGraph runtime)                                 │
│  - Event publishing (platform events → Kafka)                      │
│  - OTel instrumentation (agent traces)                             │
└─────┬───────────────────────────────┬───────────────────────────────┘
      │                               │
      │ Writes/Reads                  │ Publishes events
      ▼                               ▼
┌──────────────────────┐    ┌─────────────────────────────────────┐
│   LAKEBASE (OLTP)    │    │   AZURE EVENT HUBS (Kafka API)      │
│   Databricks         │    │   - platform_events topic           │
│   - tasks table      │    │   - agent_traces topic              │
│   - users table      │    └─────────────┬───────────────────────┘
│   Unity Catalog      │                  │
└──────────────────────┘                  │ Auto Loader subscribes
                                          ▼
                    ┌───────────────────────────────────────────────┐
                    │      DATABRICKS LAKEHOUSE (Unity Catalog)     │
                    │                                               │
                    │  BRONZE (Raw)                                 │
                    │  - bronze.platform_events (Auto Loader)       │
                    │  - bronze.agent_traces (Auto Loader)          │
                    │                                               │
                    │  SILVER (Cleaned, Joined) — dbt               │
                    │  - silver.task_events (dedupe, validate)      │
                    │  - silver.agent_sessions (join by session_id) │
                    │                                               │
                    │  GOLD (Aggregated) — dbt                      │
                    │  - gold.daily_metrics (DAU, tasks created)    │
                    │  - gold.agent_performance (success rate, $)   │
                    │                                               │
                    │  Databricks SQL Dashboards                    │
                    └───────────────────────────────────────────────┘
                                          │
                                          │ dbt runs on schedule
                                          ▼
                    ┌───────────────────────────────────────────────┐
                    │       DATABRICKS WORKFLOWS                    │
                    │  - Daily: Bronze → Silver → Gold (dbt)        │
                    │  - Weekly: Agent evaluation suite             │
                    │  - Alerts: Data quality, cost anomalies       │
                    └───────────────────────────────────────────────┘
```

---

## Phase Breakdown — Learn, Build, Ship

### **Phase 1: Core App (Week 1)**
*Learn: React, FastAPI, Lakebase, basic Databricks*

**Build:**
1. **Frontend (React):**
   - Task list (create, edit, complete, delete)
   - Simple chat interface for AI agent
   - Emit events: `task_created`, `task_completed`, `agent_message_sent`

2. **Backend (FastAPI):**
   - `/tasks` CRUD (POST, GET, PUT, DELETE)
   - `/agent/chat` (streaming LangGraph responses)
   - Writes to **Lakebase** (not Postgres)

3. **Lakebase Setup:**
   - Create `tasks` table in Unity Catalog (`main.todo_app.tasks`)
   - Use Databricks SQL Connector from FastAPI
   - Understand: Delta Lake ACID transactions, time travel

**Validation:** You have a working todo app. No events yet, no pipeline.

**Learning Checkpoints:**
- ✅ Why Lakebase instead of Postgres? (Answer: Unified governance, no ETL from app DB → warehouse, native Delta Lake)
- ✅ How does Unity Catalog enforce access? (Catalog → Schema → Table RBAC)
- ✅ What's the write path? (FastAPI → Databricks SQL Connector → Delta Lake)

---

### **Phase 2: Dual Event Instrumentation (Week 2)**
*Learn: Event schema design, OTel, Kafka fundamentals*

**Build:**

**1. Platform Events (UI interactions):**
- Schema (8 events):
  ```
  task_created, task_completed, task_deleted, task_updated
  page_viewed, agent_message_sent, agent_message_received, session_started
  ```
- Frontend sends to `/events` endpoint
- Backend publishes to **Azure Event Hubs** (`platform_events` topic)

**2. Agent Traces (LLM execution):**
- Instrument LangGraph with OpenTelemetry
- Emit `gen_ai.*` spans to **Langfuse** (real-time viz)
- Also publish to Event Hubs (`agent_traces` topic)

**3. Session ID Propagation:**
- Frontend generates `session_id` on load
- Passed in headers to backend
- Backend injects into Kafka events + OTel spans
- **This is your join key**

**Validation:** Langfuse shows live agent traces. Event Hubs has both topics receiving messages.

**Learning Checkpoints:**
- ✅ Why separate topics? (Different schemas, retention, consumers)
- ✅ What's the difference between platform events and agent traces? (Who vs What: user actions vs agent execution)
- ✅ How does `session_id` propagate? (HTTP headers → Kafka message → OTel baggage)

---

### **Phase 3: Streaming Ingestion + Bronze Layer (Week 3)**
*Learn: Auto Loader, Kafka → Databricks, schema evolution*

**Build:**

**1. Auto Loader Streams (Databricks notebooks):**

```python
# Bronze: platform_events
(spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "<event-hubs-namespace>.servicebus.windows.net:9093")
  .option("subscribe", "platform_events")
  .option("kafka.sasl.mechanism", "PLAIN")
  .option("kafka.security.protocol", "SASL_SSL")
  .option("kafka.sasl.jaas.config", f'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{connection_string}";')
  .load()
  .selectExpr("CAST(value AS STRING) as json_payload")
  .writeStream
  .format("delta")
  .option("checkpointLocation", "/checkpoints/platform_events")
  .trigger(processingTime="10 seconds")
  .table("bronze.platform_events"))
```

```python
# Bronze: agent_traces (same pattern)
# Write to bronze.agent_traces
```

**2. Schema Registry (Unity Catalog):**
- Store event schemas as JSON in Unity Catalog
- Enforce schema validation on write

**Validation:** Data flows from Event Hubs → Bronze Delta tables in <30 seconds.

**Learning Checkpoints:**
- ✅ How does Auto Loader handle late-arriving data? (Watermarking)
- ✅ What happens if schema changes? (Schema evolution modes: merge, overwrite, fail)
- ✅ Why checkpoints? (Exactly-once processing, fault tolerance)

---

### **Phase 4: dbt Transformations (Silver/Gold) (Week 4)**
*Learn: dbt on Databricks, medallion architecture, data quality tests*

**Build:**

**1. dbt Project Setup:**
```yaml
# dbt_project.yml
models:
  todo_app:
    bronze:
      +materialized: view
    silver:
      +materialized: incremental
    gold:
      +materialized: table
```

**2. Silver Models:**

```sql
-- models/silver/task_events.sql
{{ config(materialized='incremental', unique_key='event_id') }}

SELECT
  event_id,
  event_name,
  session_id,
  user_id,
  timestamp,
  properties:task_id::string as task_id,
  properties:task_title::string as task_title
FROM {{ source('bronze', 'platform_events') }}
WHERE event_name IN ('task_created', 'task_completed', 'task_deleted')
{% if is_incremental() %}
  AND timestamp > (SELECT MAX(timestamp) FROM {{ this }})
{% endif %}
```

```sql
-- models/silver/agent_sessions.sql
-- Join platform_events + agent_traces by session_id
SELECT
  e.session_id,
  e.user_id,
  e.event_name,
  t.trace_id,
  t.span_name,
  t.gen_ai_usage_input_tokens,
  t.gen_ai_usage_output_tokens,
  t.gen_ai_request_model,
  t.gen_ai_response_finish_reason
FROM {{ ref('task_events') }} e
LEFT JOIN {{ source('bronze', 'agent_traces') }} t
  ON e.session_id = t.session_id
```

**3. Gold Models:**

```sql
-- models/gold/daily_metrics.sql
SELECT
  DATE(timestamp) as date,
  COUNT(DISTINCT user_id) as daily_active_users,
  COUNT(DISTINCT CASE WHEN event_name = 'task_created' THEN session_id END) as sessions_with_tasks_created,
  COUNT(DISTINCT CASE WHEN event_name = 'agent_message_sent' THEN session_id END) as sessions_with_agent_usage,
  SUM(gen_ai_usage_input_tokens) as total_input_tokens,
  SUM(gen_ai_usage_output_tokens) as total_output_tokens
FROM {{ ref('agent_sessions') }}
GROUP BY DATE(timestamp)
```

**4. dbt Tests:**
```yaml
# models/silver/schema.yml
models:
  - name: task_events
    columns:
      - name: event_id
        tests:
          - unique
          - not_null
      - name: timestamp
        tests:
          - not_null
```

**Validation:** `dbt run` populates Silver + Gold tables. `dbt test` passes.

**Learning Checkpoints:**
- ✅ Why incremental models? (Only process new data, not full refresh)
- ✅ How does dbt track lineage? (DAG visualization, column-level lineage)
- ✅ What are dbt tests? (Data quality assertions: uniqueness, not_null, custom SQL)

---

### **Phase 5: Agent Evaluation + Observability (Week 5)**
*Learn: LLM evaluation, golden datasets, online/offline testing*

**Build:**

**1. Golden Dataset:**
- 20 test prompts: "Add buy milk to my todo list", "What tasks do I have tomorrow?", etc.
- Expected outputs (task created, correct summary, etc.)
- Store in `eval.golden_dataset` table

**2. Offline Evaluation (Databricks notebook):**
```python
from langsmith import evaluate

def run_agent(prompt):
    # Your LangGraph agent
    return agent.invoke({"messages": [prompt]})

evaluate(
    run_agent,
    data="golden_dataset",
    evaluators=[correctness, latency, token_usage],
    experiment_prefix="todo-agent-v1"
)
```

**3. Online Evaluation:**
- Sample 10% of production traces
- Run lightweight evals (response time, token cost, tool call success)
- Write results to `gold.agent_eval_results`

**4. Dashboards:**
- Agent success rate (task correctly created from NL)
- Average response time
- Token cost per session
- User satisfaction (explicit thumbs up/down)

**Validation:** Evaluation suite runs automatically. Dashboard shows agent quality metrics.

**Learning Checkpoints:**
- ✅ What's the difference between offline and online eval? (Pre-deployment vs production monitoring)
- ✅ How do you measure agent quality? (Task success, latency, cost, user feedback)
- ✅ When do you block deployment? (Eval score below threshold)

---

### **Phase 6: Production Orchestration (Week 6)**
*Learn: Databricks Workflows, alerting, cost optimization*

**Build:**

**1. Databricks Workflow (DAG):**
```yaml
# daily_pipeline.yml
tasks:
  - task_key: bronze_ingestion
    notebook_task:
      notebook_path: /bronze/ingest_streams
    timeout_seconds: 3600

  - task_key: dbt_run
    depends_on:
      - task_key: bronze_ingestion
    dbt_task:
      commands: ["dbt run", "dbt test"]

  - task_key: agent_eval
    depends_on:
      - task_key: dbt_run
    notebook_task:
      notebook_path: /eval/run_golden_dataset
```

**2. Alerts:**
- Data quality failure (dbt test fails) → Slack
- Cost spike (>$50/day on LLM) → Email
- Agent success rate <80% → PagerDuty

**3. Cost Optimization:**
- Set up budget alerts in Unity Catalog
- Use cheaper models for simple tasks (gpt-4o-mini)
- Cache frequent queries in Lakebase

**Validation:** Pipeline runs daily at 2am. Alerts fire correctly.

**Learning Checkpoints:**
- ✅ How do you schedule Databricks jobs? (Workflows = managed Airflow alternative)
- ✅ What's the difference between Workflows and dbt schedules? (Workflows = multi-language, dbt = SQL-only)
- ✅ How do you control costs? (Model selection, caching, auto-scaling clusters)

---

## File Structure

```
ai-todo-app/
├── frontend/                    # React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── TaskList.jsx
│   │   │   ├── TaskItem.jsx
│   │   │   └── AgentChat.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── telemetry.js     # Event emitter
│   │   └── App.jsx
│   └── package.json
│
├── backend/                     # FastAPI
│   ├── app/
│   │   ├── main.py             # API routes
│   │   ├── agent.py            # LangGraph runtime
│   │   ├── db.py               # Lakebase connector
│   │   ├── events.py           # Kafka publisher
│   │   └── telemetry.py        # OTel instrumentation
│   ├── requirements.txt
│   └── .env
│
├── databricks/
│   ├── notebooks/
│   │   ├── bronze/
│   │   │   ├── ingest_platform_events.py
│   │   │   └── ingest_agent_traces.py
│   │   ├── eval/
│   │   │   └── run_golden_dataset.py
│   │   └── workflows/
│   │       └── daily_pipeline.yml
│   │
│   └── dbt/                     # dbt project
│       ├── models/
│       │   ├── bronze/
│       │   ├── silver/
│       │   │   ├── task_events.sql
│       │   │   └── agent_sessions.sql
│       │   └── gold/
│       │       ├── daily_metrics.sql
│       │       └── agent_performance.sql
│       ├── tests/
│       └── dbt_project.yml
│
├── eval/
│   └── golden_dataset.jsonl    # Test prompts + expected outputs
│
└── README.md
```

---

## What You'll Master

| Technology | What You Learn | Why It Matters |
|-----------|----------------|----------------|
| **Lakebase** | When to replace Postgres with lakehouse OLTP | Modern data architecture decision |
| **Auto Loader** | Incremental ingestion from Kafka/files | Production-grade data pipelines |
| **dbt on Databricks** | SQL transformations, tests, lineage | Industry standard for analytics engineering |
| **Unity Catalog** | Data governance, access control, lineage | Enterprise data platform requirement |
| **Azure Event Hubs** | Kafka fundamentals, partitioning | Streaming data architecture |
| **OpenTelemetry** | Distributed tracing, GenAI conventions | Observability for AI systems |
| **LangGraph** | Multi-step agents, tool calling | Production agent orchestration |
| **Databricks Workflows** | DAG scheduling, dependencies, alerts | End-to-end pipeline orchestration |
| **Agent Evaluation** | Offline + online testing, quality gates | Ship reliable AI products |

---

## Success Criteria (6 Weeks)

✅ **You can confidently answer:**
- When should I use Lakebase vs Postgres?
- How do I stream events into Databricks?
- What's the right medallion architecture for my use case?
- How do I instrument agent telemetry?
- How do I evaluate agent quality?
- How do I orchestrate data + AI pipelines?
- How do I control costs in a lakehouse?

✅ **You have a portfolio piece:**
- GitHub repo with full source code
- Live demo (deploy frontend/backend to Azure)
- Databricks workspace with dashboards
- Documentation explaining architecture decisions

---

## Project Status

**Current Phase:** Planning
**Started:** 2026-07-01
**Target Completion:** 6 weeks from start

---

## Next Steps

1. Set up project repository structure
2. Configure Databricks workspace (Unity Catalog, compute)
3. Set up Azure Event Hubs namespace
4. Begin Phase 1: Core App implementation

---

**Related Projects:**
- AgentOS (enterprise AI control plane reference)
- TaskPilot (scaled-down learning mirror)

**Documentation References:**
- AgentOS Platform Architecture
- Agent_Tracing_Framework_v2
- AgentOS-Platform-Event-Schema
- Event Ingestion Architecture
