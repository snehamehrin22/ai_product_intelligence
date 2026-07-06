# Backend Module - AI Todo App

## Overview

FastAPI backend that:
- Provides REST API for todo CRUD operations
- Runs LangGraph AI agent for natural language task management
- Connects to Databricks as primary database (Lakebase pattern)
- Publishes events to Azure Event Hubs (Phase 2+)
- Instruments agent traces with OpenTelemetry (Phase 2+)

## Architecture Patterns

### Database: Lakebase (Databricks as OLTP)

**Key Pattern:** Use Databricks SQL Connector for transactional operations, not just analytics.

```python
from databricks import sql

# Connection is synchronous (not async)
connection = sql.connect(
    server_hostname=os.getenv("DATABRICKS_HOST"),
    http_path=os.getenv("DATABRICKS_HTTP_PATH"),
    access_token=os.getenv("DATABRICKS_TOKEN")
)

# Execute queries
cursor = connection.cursor()
cursor.execute("INSERT INTO main.todo_app.tasks ...")
connection.commit()
```

**Gotchas:**
- Databricks SQL Connector is **synchronous**, not async
- Wrap DB calls in `asyncio.to_thread()` to avoid blocking FastAPI
- Use connection pooling for production (not single connection)
- Delta Lake provides ACID transactions, so commit/rollback works

### OpenAI Structured Output

**Key Pattern:** Use `response_format={"type": "json_object"}` for guaranteed JSON.

```python
from openai import OpenAI

response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},  # Forces valid JSON
    messages=[...]
)

data = json.loads(response.choices[0].message.content)
```

**Why:** Prevents Claude-style wrapper text ("Here is the JSON...") and truncation.

### Pydantic Validation (CRITICAL)

**Always validate LLM output with Pydantic schemas.**

```python
# schemas.py
from pydantic import BaseModel, Field

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    due_date: datetime | None = None

# agent.py
response = llm.invoke(...)
validated = TaskCreateRequest(**json.loads(response))
```

**Never trust raw LLM text.** Schema validation catches hallucinations.

## Code Organization

```
backend/
├── app/
│   ├── main.py          # FastAPI app, routes
│   ├── config.py        # Environment config (pydantic-settings)
│   ├── schemas.py       # Pydantic models (single source of truth)
│   ├── db.py            # Databricks connector, queries
│   ├── agent.py         # LangGraph agent runtime
│   ├── events.py        # Event Hubs publisher (Phase 2+)
│   └── telemetry.py     # OpenTelemetry setup (Phase 2+)
└── tests/
    └── test_api.py
```

## Development Workflow

### Setup

```bash
# From backend/ directory
/usr/local/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy .env.example to .env and fill in credentials
cp .env.example .env

# Test Databricks connection
python -c "from app.db import test_connection; test_connection()"
```

### Running

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Format code
black app/
ruff check app/ --fix
```

## API Endpoints (Phase 1)

```
POST   /tasks          - Create task
GET    /tasks          - List tasks (with filters)
GET    /tasks/{id}     - Get task by ID
PUT    /tasks/{id}     - Update task
DELETE /tasks/{id}     - Delete task

POST   /agent/chat     - Send message to AI agent (streaming)
```

## Environment Variables

See `.env.example` for all required variables.

**Critical:**
- `DATABRICKS_HOST` - Must include `https://`
- `DATABRICKS_HTTP_PATH` - From SQL Warehouse connection details
- `DATABRICKS_TOKEN` - Personal Access Token (do NOT commit)
- `OPENAI_API_KEY` - Starts with `sk-proj-`

## Common Issues

### "Connection refused" to Databricks
- **Cause:** SQL Warehouse is stopped
- **Fix:** Go to Databricks UI → SQL Warehouses → Start your warehouse

### "Invalid token" error
- **Cause:** PAT expired or incorrect
- **Fix:** Regenerate token in Databricks → User Settings → Access Tokens

### "Table not found"
- **Cause:** Schema/table doesn't exist yet
- **Fix:** Run SQL setup script in SETUP_GUIDE.md

### Async DB calls blocking FastAPI
- **Cause:** Using synchronous Databricks connector in async route
- **Fix:** Wrap in `asyncio.to_thread()`

```python
@app.get("/tasks")
async def get_tasks():
    tasks = await asyncio.to_thread(db.get_all_tasks)
    return tasks
```

## Learnings & Patterns

(Add discoveries here as you build)

---

**Next:** See `app/main.py` for entry point, `app/db.py` for database patterns.
