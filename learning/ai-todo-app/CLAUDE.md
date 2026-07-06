# AI Todo App - Project Instructions

This file provides guidance for AI coding agents (like Claude Code) working on this project.

## Project Overview

Building a production-grade AI-powered todo app to learn the complete modern data + AI stack:
- **Frontend:** React
- **Backend:** FastAPI + Databricks (Lakebase)
- **AI Agent:** OpenAI + LangGraph
- **Data Pipeline:** Azure Event Hubs → Databricks → dbt (Phases 2+)

**Current Phase:** Phase 1 - Core App (Week 1)

## How to Work on This Project

### 1. Read the PRD

**Always start by reading `prd.json`** to understand:
- Current phase objectives
- User stories with acceptance criteria
- Technical decisions and constraints
- What's in scope vs out of scope

### 2. Check Progress

**Read `progress.txt`** to see:
- **Codebase Patterns section** (at the top) - patterns discovered by previous iterations
- Recent work completed
- Known issues or gotchas

### 3. Pick a User Story

- Choose the **highest priority** story where `passes: false`
- Priority order: P0 (critical) → P1 (important) → P2 (nice-to-have)
- Check `dependencies` array - only work on stories where dependencies are complete

### 4. Implement

- Follow acceptance criteria exactly
- Refer to `backend/CLAUDE.md` for backend-specific patterns
- Run quality checks before committing (see below)
- Update module CLAUDE.md files if you discover important patterns

### 5. Test & Commit

```bash
# Backend checks
cd backend
source .venv/bin/activate
black app/
ruff check app/ --fix
pytest

# If all pass, commit
git add .
git commit -m "feat: [US-X.X] - [Story Title]"
```

### 6. Update PRD & Progress

- Set `passes: true` for the completed story in `prd.json`
- Append to `progress.txt` with what you learned (see format below)

## Quality Requirements

### Before Every Commit:

- [ ] Code follows existing patterns
- [ ] Pydantic schemas validate all LLM output
- [ ] Environment variables are in .env (not hardcoded)
- [ ] Error handling is implemented
- [ ] Code is formatted (black)
- [ ] Linting passes (ruff)
- [ ] Tests pass (if tests exist)
- [ ] CLAUDE.md updated with new patterns (if applicable)

### Never Commit:

- ❌ `.env` files (use `.env.example` as template)
- ❌ API keys or secrets
- ❌ `__pycache__/` or `.venv/`
- ❌ Broken code that doesn't run
- ❌ Code without error handling

## Progress Report Format

When appending to `progress.txt`:

```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Pattern: [reusable pattern discovered]
  - Gotcha: [non-obvious issue encountered]
  - Context: [useful information about the codebase]
---
```

**Important:** If you discover a **general, reusable pattern**, add it to the **Codebase Patterns** section at the top of `progress.txt`.

## Key Architectural Patterns

### 1. Databricks as OLTP (Lakebase Pattern)

**Not just analytics** - Databricks is the primary transactional database.

```python
# Use Databricks SQL Connector for writes
connection = sql.connect(...)
cursor = connection.cursor()
cursor.execute("INSERT INTO main.todo_app.tasks ...")
connection.commit()
```

**Gotcha:** Connector is synchronous. Wrap in `asyncio.to_thread()` for FastAPI.

### 2. OpenAI Structured Output

**Always use `response_format` for guaranteed JSON:**

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},  # Forces valid JSON
    messages=[...]
)
```

**Why:** Prevents wrapper text and ensures parseable output.

### 3. Pydantic Validation (CRITICAL)

**Never trust raw LLM output. Always validate.**

```python
# schemas.py defines structure
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)

# agent.py validates output
response_data = json.loads(llm_response)
validated = TaskCreate(**response_data)  # Raises ValidationError if invalid
```

**Single source of truth:** `schemas.py` defines all data structures.

### 4. Environment Configuration

**Use pydantic-settings for config management:**

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    databricks_host: str
    databricks_token: str
    openai_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

**Never hardcode credentials.**

## Common Issues & Solutions

### "Databricks connection refused"
- **Cause:** SQL Warehouse is auto-stopped
- **Fix:** Go to Databricks UI → SQL Warehouses → Start warehouse
- **Prevention:** Set auto-stop to 60+ minutes during development

### "Invalid token" error
- **Cause:** Personal Access Token expired or incorrect
- **Fix:** Regenerate in Databricks → User Settings → Developer → Access Tokens

### "FastAPI blocking on DB calls"
- **Cause:** Using synchronous Databricks connector in async route
- **Fix:** Wrap all DB calls in `asyncio.to_thread(db.function_name)`

### "OpenAI rate limit exceeded"
- **Cause:** Too many requests in short time
- **Fix:** Add retry logic with exponential backoff (tenacity library)
- **Prevention:** Use gpt-4o-mini, set max_tokens limits

## File Organization

```
ai-todo-app/
├── prd.json              # User stories, priorities, acceptance criteria
├── progress.txt          # Work log, learnings, patterns
├── CLAUDE.md            # This file - project instructions
├── README.md            # Project overview, setup instructions
│
├── backend/
│   ├── app/
│   │   ├── main.py      # FastAPI app, routes
│   │   ├── config.py    # Environment config
│   │   ├── schemas.py   # Pydantic models (SINGLE SOURCE OF TRUTH)
│   │   ├── db.py        # Databricks queries
│   │   ├── agent.py     # LangGraph agent
│   │   ├── events.py    # Event publishing (Phase 2+)
│   │   └── telemetry.py # OpenTelemetry (Phase 2+)
│   ├── tests/
│   ├── CLAUDE.md        # Backend-specific patterns
│   └── requirements.txt
│
├── frontend/            # React app (to be implemented)
├── databricks/          # Notebooks, dbt (Phase 3+)
└── eval/                # Agent evaluation (Phase 5)
```

## Development Workflow

### Setup (First Time)

```bash
# Backend
cd backend
/usr/local/bin/python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Test Databricks connection
python -c "from app.db import test_connection; test_connection()"
```

### Daily Development

```bash
# Activate venv
cd backend
source .venv/bin/activate

# Run backend
uvicorn app.main:app --reload

# In another terminal: Run tests
pytest

# Format & lint
black app/
ruff check app/ --fix
```

## Phase 1 Specific Notes

### What's In Scope:
- ✅ Todo CRUD API (FastAPI + Databricks)
- ✅ React UI for task management
- ✅ Basic AI agent (natural language → task creation)
- ✅ LangGraph with OpenAI function calling
- ✅ Pydantic validation throughout
- ✅ Local development

### What's Out of Scope (Later Phases):
- ❌ User authentication (hardcode test user for now)
- ❌ Event instrumentation (Phase 2)
- ❌ Azure Event Hubs (Phase 2)
- ❌ Data pipeline (Phase 3+)
- ❌ Agent evaluation (Phase 5)
- ❌ Production deployment (Phase 6)

## Success Criteria for Phase 1

✅ **Functional:**
- User can create, view, update, delete tasks via UI
- AI agent creates tasks from natural language (>80% success on simple cases)

✅ **Technical:**
- Backend connects to Databricks successfully
- API response times < 500ms for CRUD operations
- Agent response time < 3 seconds
- All tests pass

✅ **Learning:**
- Understand Databricks as OLTP vs traditional databases
- Understand OpenAI function calling
- Understand LangGraph basics

## Next Steps After Phase 1

Once all user stories in `prd.json` have `passes: true`:
1. Review learnings in `progress.txt`
2. Create Phase 2 PRD (Event Instrumentation)
3. Branch: `phase-2-event-instrumentation`

---

**Questions?** Refer to:
- `SETUP_GUIDE.md` - Cloud services setup
- `ACCESS_REQUIREMENTS.md` - What you need access to
- `backend/CLAUDE.md` - Backend-specific patterns
- `AI-TODO-APP-LEARNING-PROJECT.md` - Full architecture overview
