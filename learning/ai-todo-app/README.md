# AI-Powered Todo App

Full-stack learning project: Todo app with AI agent assistant + production-grade Databricks data pipeline.

## Project Status

**Current Phase:** Phase 1 Complete - Core App Implemented ✅
**Started:** 2026-07-06
**Phase 1 Completed:** 2026-07-06
**Target:** 6 weeks

## Stack

- **Frontend:** React
- **Backend:** FastAPI + Python 3.11+
- **Database:** Databricks (Lakebase/Unity Catalog)
- **Streaming:** Azure Event Hubs (Kafka API)
- **AI:** OpenAI (GPT-4o-mini for agent)
- **Data Pipeline:** dbt + Databricks Workflows
- **Observability:** OpenTelemetry + Langfuse

## Documentation

- [Setup Guide](../SETUP_GUIDE.md) - Cloud services setup
- [Access Requirements](../ACCESS_REQUIREMENTS.md) - What you need
- [Learning Project Overview](../AI-TODO-APP-LEARNING-PROJECT.md) - Full architecture

## Project Structure

```
ai-todo-app/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── main.py      # API routes
│   │   ├── agent.py     # LangGraph agent
│   │   ├── db.py        # Databricks connector
│   │   ├── events.py    # Event publishing
│   │   └── telemetry.py # OpenTelemetry
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/             # React application
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
│
├── databricks/
│   ├── notebooks/       # Databricks notebooks
│   │   ├── bronze/      # Auto Loader ingestion
│   │   ├── eval/        # Agent evaluation
│   │   └── workflows/   # Workflow definitions
│   └── dbt/             # dbt project
│       └── models/
│           ├── bronze/
│           ├── silver/  # Cleaned data
│           └── gold/    # Aggregated metrics
│
├── eval/                # Agent evaluation
│   └── golden_dataset.jsonl
│
└── README.md
```

## Development Setup

### Prerequisites

✅ Complete all steps in [SETUP_GUIDE.md](../SETUP_GUIDE.md):
- [ ] Databricks workspace with Unity Catalog
- [ ] Azure Event Hubs namespace (Phase 2+)
- [ ] OpenAI API key
- [ ] Python 3.11+
- [ ] Node.js 18+

### Backend Setup

```bash
cd backend

# Create virtual environment
/usr/local/bin/python3.13 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials:
# - DATABRICKS_HOST (e.g., https://adb-xxx.azuredatabricks.net/)
# - DATABRICKS_HTTP_PATH (from SQL Warehouse connection details)
# - DATABRICKS_TOKEN (Personal Access Token)
# - OPENAI_API_KEY (starts with sk-proj-)

# Test Databricks connection
python -c "from app.db import test_connection; test_connection()"

# Run backend (development mode with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs at:** http://localhost:8000
**API docs:** http://localhost:8000/docs (Swagger UI)

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start
```

**Frontend runs at:** http://localhost:3000

### Running Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_api.py::TestTaskCRUD -v

# Skip slow tests (OpenAI API calls)
pytest tests/ -v -m "not slow"
```

## Phase-by-Phase Implementation

### Phase 1: Core App (Week 1) ✅ Completed
- [x] React todo list UI with task management
- [x] FastAPI CRUD API (POST, GET, PUT, DELETE /tasks)
- [x] Databricks Lakebase integration (signaltogrowth.todo_app schema)
- [x] AI Agent for natural language task creation
- [x] Floating chat interface with real-time responses
- [x] Pytest test suite for API endpoints
- [x] Full setup and run documentation

**Deliverables:**
- Backend API running on port 8000 with Swagger docs
- React frontend running on port 3000
- AI chat interface (click 🤖 button in bottom-right)
- Comprehensive test coverage (16 tests covering CRUD + agent)
- Database schema with Delta Lake + CDC enabled

### Phase 2: Event Instrumentation (Week 2)
- [ ] Platform event emitter
- [ ] Azure Event Hubs integration
- [ ] OpenTelemetry agent traces
- [ ] Langfuse visualization

### Phase 3: Streaming Ingestion (Week 3)
- [ ] Auto Loader notebooks
- [ ] Bronze layer tables
- [ ] Schema registry

### Phase 4: dbt Transformations (Week 4)
- [ ] Silver layer models
- [ ] Gold layer aggregations
- [ ] Data quality tests

### Phase 5: Agent Evaluation (Week 5)
- [ ] Golden dataset creation
- [ ] Offline evaluation
- [ ] Online evaluation
- [ ] Dashboards

### Phase 6: Production Orchestration (Week 6)
- [ ] Databricks Workflows
- [ ] Alerting
- [ ] Cost optimization

## Learning Objectives

By completing this project, you will understand:

✅ When to use Databricks Lakebase vs traditional databases
✅ How to stream events from applications to data platforms
✅ Medallion architecture (Bronze → Silver → Gold)
✅ dbt for SQL transformations and testing
✅ Unity Catalog for data governance
✅ Agent telemetry and evaluation
✅ End-to-end data + AI pipeline orchestration

## Cost Tracking

**Target:** $90-170 for full 6-week project

Monitor costs:
- Databricks: Usage dashboard
- Azure: Cost Management + Billing
- OpenAI: Usage dashboard

Set budget alerts at $50/month.

## Next Steps

1. Follow [SETUP_GUIDE.md](../SETUP_GUIDE.md) to create cloud services
2. Begin Phase 1 implementation
3. Track progress in this README

---

**Questions?** See [AI-TODO-APP-LEARNING-PROJECT.md](../AI-TODO-APP-LEARNING-PROJECT.md) for architecture details.
