# Event Flow Validation Guide

This guide explains how to validate that events and traces flow correctly through the AI Todo App's event instrumentation system.

## System Architecture

```
┌──────────────┐
│   Frontend   │
│  (React App) │
└──────┬───────┘
       │ 1. User interactions
       │ 2. X-Session-Id header
       ▼
┌──────────────┐
│   Backend    │
│  (FastAPI)   │
└──┬────────┬──┘
   │        │
   │        │ 3a. Platform events
   │        │    (task CRUD, agent messages)
   │        ▼
   │   ┌──────────────┐
   │   │   Zerobus    │
   │   │   Ingest     │
   │   └──────┬───────┘
   │          │ 4a. Stream ingestion
   │          ▼
   │   ┌──────────────┐
   │   │ Delta Lake   │
   │   │ platform_    │
   │   │ events       │
   │   └──────────────┘
   │
   │ 3b. Agent traces
   │    (OpenTelemetry spans)
   ▼
┌──────────────┐
│ OpenTelemetry│
│ Exporters    │
└──┬────────┬──┘
   │        │
   │        │ 4b. OTLP → Langfuse (real-time UI)
   │        │
   │        │ 4c. Zerobus → Delta Lake (long-term storage)
   │        ▼
   │   ┌──────────────┐
   │   │ Delta Lake   │
   │   │ agent_traces │
   │   └──────────────┘
   │
   ▼
JOIN on session_id
```

## Validation Strategy

We validate the event flow at **3 levels**:

### 1. **Unit Level** - Component Testing
- Test individual components in isolation
- Mock external dependencies (Zerobus, OpenAI)
- Validate schema compliance and data transformation

### 2. **Integration Level** - End-to-End Flow
- Test complete flow from API → Zerobus → Delta Lake
- Validate session_id propagation
- Verify event ordering and schema

### 3. **System Level** - Production Monitoring
- Query Delta Lake for event coverage
- Monitor latency and error rates
- Validate join key (session_id) coverage

---

## Validation Tests

### Test 1: Platform Event Flow

**Purpose:** Validate events flow from backend → Zerobus → Delta Lake

**Steps:**
1. Create task via API with unique `session_id`
2. Wait 5 seconds for Zerobus ingestion
3. Query Delta Lake for `task_created` event
4. Validate event schema and properties

**Run:**
```bash
cd backend
pytest tests/integration/test_event_flow.py::TestEventFlowValidation::test_task_created_event_in_delta_lake -v
```

**Expected Result:**
```
✓ Task created via API
✓ Event found in Delta Lake (platform_events table)
✓ event_id, event_name, session_id, user_id present
✓ properties contain task_id and other context
```

**Troubleshooting:**
- **Event not found:** Increase wait time or check Zerobus connection
- **Schema mismatch:** Verify Delta table matches expected schema
- **Null session_id:** Check X-Session-Id header is sent

---

### Test 2: Agent Trace Flow

**Purpose:** Validate traces flow from agent → OTel → Zerobus → Delta Lake

**Steps:**
1. Send agent message via API with unique `session_id`
2. Agent processes message (creates spans)
3. OpenTelemetry exports spans via ZerobusSpanExporter
4. Wait 5 seconds for ingestion
5. Query Delta Lake for traces

**Run:**
```bash
cd backend
pytest tests/integration/test_event_flow.py::TestEventFlowValidation::test_agent_trace_in_delta_lake -v
```

**Expected Result:**
```
✓ Agent message sent
✓ Traces found in Delta Lake (agent_traces table)
✓ trace_id, span_id, span_name, session_id present
✓ GenAI attributes present (model, tokens, etc.)
```

**Troubleshooting:**
- **Traces not found:** Check OpenAI API key is valid
- **GenAI attributes missing:** Verify OpenAIInstrumentor is enabled
- **Session_id null:** Check baggage propagation in telemetry.py

---

### Test 3: Session ID Join

**Purpose:** Validate events and traces can be joined via `session_id`

**Steps:**
1. Send agent message (creates both event and trace)
2. Wait 7 seconds for ingestion
3. Query Delta Lake with LEFT JOIN on session_id
4. Validate at least one successful join

**Run:**
```bash
cd backend
pytest tests/integration/test_event_flow.py::TestEventFlowValidation::test_session_id_join -v
```

**Expected Result:**
```
✓ Agent message sent
✓ Found joined records in Delta Lake
✓ session_id matches between events and traces
✓ At least one event has corresponding trace
```

**Troubleshooting:**
- **No joined records:** Check session_id in both tables
- **Join returns nulls:** Verify session_id propagation end-to-end
- **Session_id mismatch:** Check frontend generates and sends consistent ID

---

### Test 4: Event Ordering

**Purpose:** Validate events are ordered correctly by timestamp within session

**Steps:**
1. Create multiple tasks in sequence (same session_id)
2. Wait for ingestion
3. Query events ordered by event_timestamp ASC
4. Verify timestamps are increasing

**Run:**
```bash
cd backend
pytest tests/integration/test_event_flow.py::TestEventFlowValidation::test_event_ordering -v
```

**Expected Result:**
```
✓ Multiple tasks created
✓ Events found in Delta Lake
✓ Timestamps are monotonically increasing
✓ Events ordered correctly by timestamp
```

---

### Test 5: Schema Compliance

**Purpose:** Validate Delta Lake tables have expected schema

**Steps:**
1. Query platform_events and agent_traces tables
2. Inspect column names and types
3. Validate required columns exist

**Run:**
```bash
cd backend
pytest tests/integration/test_event_flow.py::TestEventSchemaCompliance -v
```

**Expected Result:**
```
✓ platform_events has required columns (event_id, event_name, session_id, etc.)
✓ agent_traces has required columns (trace_id, span_id, session_id, etc.)
✓ Schema matches expected structure
```

---

## Manual Validation with Query Script

For manual testing and debugging, use the query script:

### Query Recent Events

```bash
cd backend
python scripts/query_events.py events --limit 10
```

**Example Output:**
```
Event 1:
  ID: evt_123e4567-e89b-12d3-a456-426614174000
  Name: task_created
  Timestamp: 2026-07-07 10:01:17.891
  Session: sess_abc123-def456-789012
  User: test-user-001
  Properties:
    - task_id: task_456def-789ghi-012jkl
    - title: Buy milk
    - status: pending
```

### Query Events for Specific Session

```bash
python scripts/query_events.py events --session-id sess_abc123-def456-789012
```

### Query Agent Traces

```bash
python scripts/query_events.py traces --limit 10
```

**Example Output:**
```
Trace 1:
  Trace ID: 00112233445566778899aabbccddeeff
  Span ID: 0011223344556677
  Span Name: agent.process_message
  Session: sess_abc123-def456-789012
  Start: 2026-07-07 10:01:15.345
  Duration: 2778ms
  GenAI Attributes:
    - gen_ai.request.model: gpt-4o-mini
    - gen_ai.usage.total_tokens: 127
```

### Query Session Timeline (Joined View)

```bash
python scripts/query_events.py join --session-id sess_abc123-def456-789012
```

**Example Output:**
```
Timeline:
────────────────────────────────────────────────────────────────────────────────
📊 [2026-07-07 10:00:00] EVENT: session_started
     └─ user_agent: Mozilla/5.0...

📊 [2026-07-07 10:01:15] EVENT: agent_message_sent
     └─ message_text: Buy milk tomorrow

🔍 [2026-07-07 10:01:15] TRACE: agent.process_message
     └─ duration: 2778ms
     └─ tokens: 127

📊 [2026-07-07 10:01:17] EVENT: task_created
     └─ task_id: task_456def-789ghi-012jkl
```

---

## Validation Checklist

Use this checklist to validate event flow after setup or changes:

### ✅ **Backend Events**

- [ ] POST /tasks emits `task_created` event
- [ ] PUT /tasks/{id} emits `task_updated` event
- [ ] DELETE /tasks/{id} emits `task_deleted` event
- [ ] PATCH /tasks/{id}/complete emits `task_completed` event
- [ ] POST /agent/chat processes messages and creates tasks

### ✅ **Frontend Events**

- [ ] App mount emits `session_started` event
- [ ] Agent chat emits `agent_message_sent` event
- [ ] Agent response emits `agent_message_received` event
- [ ] EventEmitter batches events (max 10 or 5 seconds)
- [ ] X-Session-Id header sent on all API requests

### ✅ **Delta Lake - Platform Events**

- [ ] signaltogrowth.platform_events table exists
- [ ] Events appear within 5 seconds of API call (Zerobus latency)
- [ ] All events have non-null session_id
- [ ] Event schema matches expected structure
- [ ] Properties field contains event-specific data

### ✅ **Delta Lake - Agent Traces**

- [ ] signaltogrowth.agent_traces table exists
- [ ] Traces appear within 10 seconds of agent execution
- [ ] All traces have non-null session_id
- [ ] GenAI attributes present (model, tokens, finish_reason)
- [ ] Trace hierarchy preserved (parent_span_id)

### ✅ **Session ID Propagation**

- [ ] Frontend generates session_id (crypto.randomUUID())
- [ ] Frontend stores session_id in sessionStorage
- [ ] Frontend sends X-Session-Id header
- [ ] Backend extracts session_id from header
- [ ] Backend includes session_id in events
- [ ] Backend propagates session_id to OTel baggage
- [ ] Session_id appears in both Delta tables

### ✅ **Join Validation**

- [ ] Can join platform_events and agent_traces on session_id
- [ ] >95% of events have matching session_id in traces (for agent interactions)
- [ ] Join query returns expected results
- [ ] Timeline query shows complete user journey

---

## Common Issues & Solutions

### Issue: Events not appearing in Delta Lake

**Symptoms:**
- API call succeeds but no event in Delta Lake
- Query returns empty result set

**Possible Causes:**
1. Zerobus not configured or connection failed
2. Wrong table name in query (check catalog.schema.table)
3. Ingestion delay (wait longer than 5 seconds)
4. Zerobus stream not flushed

**Solutions:**
```bash
# 1. Test Zerobus connection
cd backend
python scripts/test_zerobus_connection.py

# 2. Verify table exists
# In Databricks SQL:
SHOW TABLES IN signaltogrowth;
DESCRIBE TABLE signaltogrowth.platform_events;

# 3. Check recent events (ignore session filter)
SELECT COUNT(*) FROM signaltogrowth.platform_events
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR;

# 4. Check Zerobus publisher logs
# Look for "Published event to Zerobus" messages in backend logs
```

---

### Issue: Traces not appearing in Delta Lake

**Symptoms:**
- Agent executes but no traces in agent_traces table
- Traces visible in Langfuse but not Delta Lake

**Possible Causes:**
1. ZerobusSpanExporter not registered
2. OpenAI credentials invalid (agent execution fails)
3. Async export delay (BatchSpanProcessor)
4. Span exporter error (check logs)

**Solutions:**
```bash
# 1. Check telemetry setup logs
# Look for: "✓ Zerobus span exporter configured"
cd backend
uvicorn app.main:app --reload
# Check startup logs

# 2. Verify OpenAI credentials
echo $OPENAI_API_KEY
python -c "from openai import OpenAI; client = OpenAI(); print('✓ OpenAI connected')"

# 3. Check agent_traces table
SELECT COUNT(*) FROM signaltogrowth.agent_traces
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR;

# 4. Check span exporter errors
# grep "Failed to export spans" backend.log
```

---

### Issue: session_id null in events or traces

**Symptoms:**
- Events have null session_id
- Traces have null session_id
- Join returns no results

**Possible Causes:**
1. Frontend not generating session_id
2. Frontend not sending X-Session-Id header
3. Backend not extracting session_id from header
4. OTel baggage not propagated

**Solutions:**
```bash
# 1. Check frontend sessionStorage
# Open browser DevTools → Application → Session Storage
# Look for key: "session_id"

# 2. Check network request headers
# DevTools → Network → Select API call → Headers
# Look for: X-Session-Id: <uuid>

# 3. Check backend extraction
# In main.py, verify:
session_id = request.headers.get('X-Session-Id')

# 4. Check OTel baggage
# In telemetry.py, verify:
from opentelemetry import baggage
baggage.set_baggage("session_id", session_id)

# 5. Query for null session_id
SELECT COUNT(*) FROM signaltogrowth.platform_events
WHERE session_id IS NULL
AND event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 DAY;
```

---

### Issue: Low join coverage (<95%)

**Symptoms:**
- Many events don't have corresponding traces
- Join returns fewer results than expected

**Possible Causes:**
1. Not all events trigger agent execution
2. Agent execution failures (OpenAI errors)
3. Trace export failures
4. Mismatched session_id

**Solutions:**
```sql
-- 1. Check session_id coverage
SELECT
    (SELECT COUNT(DISTINCT session_id) FROM signaltogrowth.agent_traces) * 100.0 /
    NULLIF((SELECT COUNT(DISTINCT session_id) FROM signaltogrowth.platform_events), 0) as coverage_pct;

-- 2. Find events without traces
SELECT e.session_id, e.event_name, e.event_timestamp
FROM signaltogrowth.platform_events e
LEFT JOIN signaltogrowth.agent_traces t ON e.session_id = t.session_id
WHERE t.session_id IS NULL
AND e.event_timestamp >= CURRENT_DATE
LIMIT 20;

-- 3. Check agent execution rate
SELECT
    COUNT(*) as total_events,
    COUNT(DISTINCT CASE WHEN event_name IN ('agent_message_sent', 'agent_message_received') THEN session_id END) as agent_sessions
FROM signaltogrowth.platform_events
WHERE event_timestamp >= CURRENT_DATE;
```

**Note:** It's normal for some events (like `session_started`, `page_viewed`) to not have traces. Only events that trigger agent execution will have corresponding traces.

---

## Performance Benchmarks

Expected performance metrics:

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| **Event ingestion latency** | <3s | <5s | >10s |
| **Trace export latency** | <5s | <10s | >15s |
| **API response time (with event)** | <100ms | <200ms | >500ms |
| **Session ID coverage** | >98% | >95% | <90% |
| **Event delivery rate** | >99% | >95% | <90% |
| **Join query latency** | <2s | <5s | >10s |

**Monitor these metrics in production:**
```sql
-- Event ingestion latency (estimate)
SELECT
    event_name,
    AVG(TIMESTAMPDIFF(SECOND, event_timestamp, CURRENT_TIMESTAMP)) as avg_latency_sec
FROM signaltogrowth.platform_events
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR
GROUP BY event_name;

-- Session ID coverage
SELECT
    COUNT(*) as total_events,
    COUNT(session_id) as events_with_session,
    ROUND(100.0 * COUNT(session_id) / COUNT(*), 2) as coverage_pct
FROM signaltogrowth.platform_events
WHERE event_timestamp >= CURRENT_DATE;
```

---

## Example Event Payloads

See `docs/example_events.json` for complete examples of:
- Platform events (task_created, agent_message_sent, etc.)
- Agent traces (with GenAI semantic conventions)
- Schema documentation
- Example SQL queries

---

## Next Steps

After validating event flow:
1. ✅ **US-2.12 Complete:** Event flow validated
2. 🔜 **US-2.13:** Complete documentation and monitoring setup
3. 🔜 **Phase 3:** Build dbt transformations on Delta Lake

---

## References

- **Integration Tests:** `backend/tests/integration/test_event_flow.py`
- **Query Script:** `backend/scripts/query_events.py`
- **Example Events:** `docs/example_events.json`
- **Session ID Strategy:** `databricks/SESSION_ID_JOIN_STRATEGY.md`
- **Zerobus Setup:** `databricks/ZEROBUS_SETUP_GUIDE.md`
- **Telemetry Setup:** `backend/app/telemetry.py`
