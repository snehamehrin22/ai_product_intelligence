# Langfuse Setup Guide - Real-Time Agent Trace Visualization

This guide walks you through setting up Langfuse for visualizing AI agent traces in real-time.

## What is Langfuse?

Langfuse is an open-source LLM observability platform that provides:
- Real-time trace visualization for AI agents
- Token usage tracking and cost estimation
- Latency analysis and performance monitoring
- Session-based trace grouping
- Error highlighting and debugging tools

**Why Langfuse over LangSmith?**
- Open-source (self-hostable if needed)
- GenAI-focused interface (better for LLM apps)
- Native OTLP support (standards-based integration)
- Free tier: 50k traces/month (sufficient for development)

## Step 1: Create Langfuse Account

1. Go to **https://cloud.langfuse.com**
2. Click **"Sign Up"** (or "Sign In" if you have an account)
3. Create account with email or GitHub OAuth
4. Verify email if required

## Step 2: Create Project

1. After login, click **"New Project"** (or you'll be prompted to create one)
2. Project name: **"AI Todo App"** (or your preferred name)
3. Click **"Create Project"**
4. You'll be redirected to your project dashboard

## Step 3: Get API Keys

1. In Langfuse UI, navigate to **Settings → API Keys** (left sidebar)
2. You'll see two keys:
   - **Public Key** (starts with `pk-lf-...`)
   - **Secret Key** (starts with `sk-lf-...`)
3. Click **"Copy"** buttons to copy each key

## Step 4: Configure Backend

1. Open `backend/.env` file (create from `.env.example` if missing)
2. Add Langfuse credentials:

```bash
# Langfuse Configuration (Phase 2)
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

3. Save the file

**Security Note:** Never commit `.env` to git. The `.gitignore` already excludes it.

## Step 5: Test Connection

Run the test script to verify integration:

```bash
cd backend
source .venv/bin/activate
python scripts/test_langfuse_connection.py
```

**Expected Output:**

```
======================================================================
Testing Langfuse OTLP Integration
======================================================================

1. Checking Langfuse credentials...
✓ Langfuse public key: pk-lf-xxxxxxx...
✓ Langfuse host: https://cloud.langfuse.com

2. Initializing OpenTelemetry with Langfuse exporter...
✓ Langfuse OTLP exporter configured (endpoint: https://cloud.langfuse.com/api/public/otel)
✓ Telemetry initialized successfully

3. Creating test trace...
✓ Test trace created successfully

4. Waiting for trace export to Langfuse...
✓ Trace should now be visible in Langfuse UI

======================================================================
✅ SUCCESS: Langfuse integration test complete!
======================================================================
```

## Step 6: Verify Traces in Langfuse UI

1. Go back to Langfuse UI: **https://cloud.langfuse.com**
2. Click on **"Traces"** in left sidebar
3. Within 10 seconds, you should see a new trace:
   - **Name:** `test.langfuse_connection`
   - **Status:** ✓ (green checkmark)
   - **Attributes:** Click to expand and see GenAI conventions

**What You'll See:**

- **Trace Details:**
  - `span_name`: `test.langfuse_connection`
  - `duration`: ~100ms
  - `timestamp`: Current time

- **GenAI Attributes:**
  - `gen_ai.request.model`: `gpt-4o-mini`
  - `gen_ai.usage.input_tokens`: 50
  - `gen_ai.usage.output_tokens`: 100
  - `gen_ai.usage.total_tokens`: 150
  - `gen_ai.response.finish_reason`: `stop`

- **Custom Attributes:**
  - `test.purpose`: `langfuse_connection_validation`
  - `user_id`: `test-user-001`
  - `session_id`: `test-session-001`

## Step 7: Run Backend with Langfuse Enabled

Start the backend server:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

**Check logs for Langfuse initialization:**

```
INFO:app.telemetry:Configuring Langfuse OTLP exporter...
INFO:app.telemetry:✓ Langfuse OTLP exporter configured (endpoint: https://cloud.langfuse.com/api/public/otel)
INFO:app.telemetry:✓ OpenAI auto-instrumentation enabled
INFO:app.telemetry:✓ OpenTelemetry telemetry initialized
```

## Step 8: Generate Real Agent Traces

Use the AI agent to create tasks:

```bash
# Example: Send a chat message to create a task
curl -X POST "http://localhost:8000/agent/chat?message=Buy%20milk%20tomorrow&user_id=test-user-001" \
  -H "X-Session-Id: $(uuidgen)" \
  -H "accept: application/json"
```

**In Langfuse UI, you'll now see:**

1. **New traces appear within 10 seconds**
2. **Trace hierarchy:**
   - `agent.process_message` (parent span)
   - `agent.extract_task` (child span)
   - `openai.chat.completions` (OpenAI API call span)

3. **Rich attributes:**
   - Model: `gpt-4o-mini`
   - Tokens: Input, output, total counts
   - Latency: Per-span timing
   - Session ID: For grouping traces
   - Task created: Boolean flag
   - User ID: For filtering by user

## Using Langfuse UI Features

### Filter Traces

Use filters to narrow down traces:
- **User ID:** Show traces for specific user
- **Session ID:** See all traces in a session
- **Date Range:** Filter by time period
- **Model:** Filter by LLM model used
- **Status:** Show only errors or successes

### Analyze Token Usage

1. Click **"Usage"** in left sidebar
2. See token consumption over time
3. Group by: Model, User, Day, Session
4. Estimate costs based on OpenAI pricing

### Debug Errors

1. Traces with errors show red ❌ icon
2. Click trace to see error details:
   - Exception type
   - Error message
   - Stack trace (if recorded)
3. See which span failed in hierarchy

### Session Timeline View

1. Click on a trace
2. See **"Session"** tab
3. View all events and traces for that session_id
4. Understand complete user journey

## Architecture: How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Todo App Backend                     │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         OpenTelemetry SDK (app/telemetry.py)          │ │
│  │                                                       │ │
│  │  1. Trace agent execution with spans                 │ │
│  │  2. Add GenAI semantic conventions                   │ │
│  │  3. Export to multiple backends:                     │ │
│  │     - Langfuse (OTLP HTTP exporter)                  │ │
│  │     - Zerobus (custom exporter → Delta Lake)         │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ OTLP over HTTP
                         │ (JSON spans)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Langfuse Cloud (cloud.langfuse.com)            │
│                                                             │
│  Endpoint: /api/public/otel                                 │
│  Auth: Bearer pk-lf-...:sk-lf-...                           │
│                                                             │
│  ┌─────────────────┐      ┌─────────────────┐             │
│  │   Trace Store   │      │   Analytics     │             │
│  │   (PostgreSQL)  │──────│   Engine        │             │
│  └─────────────────┘      └─────────────────┘             │
│           │                        │                        │
│           └────────────────────────┘                        │
│                      │                                      │
│                      ▼                                      │
│            ┌──────────────────┐                             │
│            │   Web UI         │                             │
│            │   (React App)    │                             │
│            └──────────────────┘                             │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
                  ┌──────────────┐
                  │   Browser    │
                  │   (You)      │
                  └──────────────┘
```

**Key Points:**
1. **OTLP Standard:** Uses OpenTelemetry Protocol (not vendor-specific SDK)
2. **Dual Export:** Traces go to both Langfuse (real-time UI) and Zerobus (long-term storage)
3. **No Code Changes:** Instrumentation is automatic via OpenAI instrumentor
4. **Async Export:** Doesn't block agent execution (BatchSpanProcessor)

## GenAI Semantic Conventions

The app follows **OpenTelemetry GenAI conventions** for consistency:

| Attribute | Description | Example |
|-----------|-------------|---------|
| `gen_ai.system` | LLM provider | `openai` |
| `gen_ai.request.model` | Model name | `gpt-4o-mini` |
| `gen_ai.request.temperature` | Sampling temperature | `0.7` |
| `gen_ai.usage.input_tokens` | Prompt tokens | `100` |
| `gen_ai.usage.output_tokens` | Completion tokens | `50` |
| `gen_ai.usage.total_tokens` | Total tokens | `150` |
| `gen_ai.response.finish_reason` | Stop reason | `stop`, `length` |

**Custom Attributes (App-Specific):**
- `user_id`: User identifier
- `session_id`: Session UUID (join key)
- `agent.task_created`: Boolean flag
- `agent.needs_clarification`: Boolean flag

## Cost Monitoring

### Langfuse Free Tier
- **50,000 traces/month** (sufficient for development)
- Unlimited projects
- 30-day data retention
- Community support

### Paid Tier (if needed)
- **$49/month** (Team plan)
- 500,000 traces/month
- 90-day retention
- Priority support

### Token Cost Estimation

Langfuse can estimate OpenAI costs:
1. Go to **Settings → Billing**
2. Add OpenAI pricing (already pre-filled for common models)
3. View cost breakdown in **Usage** tab

**Example:**
- Model: `gpt-4o-mini`
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- Daily usage: 1M tokens → ~$0.75/day

## Troubleshooting

### Traces Not Appearing

**1. Check credentials:**
```bash
# Verify keys are set
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY
```

**2. Check backend logs:**
Look for telemetry initialization messages when starting backend.

**3. Check project selection in UI:**
Make sure you're viewing the correct project in Langfuse UI.

**4. Wait up to 10 seconds:**
OTLP export is asynchronous (batch processor flushes every few seconds).

### Errors in Telemetry Setup

**Error: "Langfuse credentials not found"**
- Cause: `.env` file missing keys
- Fix: Add `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` to `.env`

**Error: "Failed to export spans"**
- Cause: Invalid API keys or network issue
- Fix:
  1. Regenerate keys in Langfuse UI
  2. Check internet connectivity
  3. Verify firewall allows HTTPS to `cloud.langfuse.com`

**Error: "Module not found: langfuse"**
- Cause: Langfuse SDK not installed (shouldn't happen, we use OTLP)
- Note: We use OTLP exporter, not langfuse SDK directly

### High Trace Volume

If you exceed free tier:
1. **Enable sampling:**
   ```python
   # In telemetry.py
   from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

   provider = TracerProvider(
       resource=resource,
       sampler=TraceIdRatioBased(0.1)  # Sample 10% of traces
   )
   ```

2. **Filter specific spans:**
   Only export important spans (e.g., agent execution, not utility functions)

3. **Upgrade to paid tier** if needed

## Next Steps

After Langfuse setup:
1. ✅ **US-2.11 Complete:** Langfuse integration working
2. 🔜 **US-2.12:** End-to-end event flow validation
3. 🔜 **US-2.13:** Documentation and monitoring setup

## References

- **Langfuse Docs:** https://langfuse.com/docs
- **OpenTelemetry GenAI Conventions:** https://opentelemetry.io/docs/specs/semconv/gen-ai/
- **OTLP Specification:** https://opentelemetry.io/docs/specs/otlp/
- **Backend Telemetry Code:** `backend/app/telemetry.py`
- **Test Script:** `backend/scripts/test_langfuse_connection.py`

---

**Questions?** Check `backend/CLAUDE.md` for backend patterns or `SETUP_GUIDE.md` for full project setup.
