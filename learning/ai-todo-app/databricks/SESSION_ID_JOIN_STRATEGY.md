# Session ID Join Strategy

## Overview

`session_id` is the primary join key for combining **platform events** and **agent traces** in Delta Lake. This enables end-to-end analysis of user sessions, from UI interactions to backend agent processing.

## Data Flow

```
┌─────────────────┐
│   Frontend      │
│  (React App)    │
└────────┬────────┘
         │ 1. Generate session_id (crypto.randomUUID())
         │ 2. Store in sessionStorage
         │ 3. Send X-Session-Id header on all requests
         ▼
┌─────────────────┐
│   Backend       │
│  (FastAPI)      │
└────────┬────────┘
         │ 4. Extract session_id from header
         ├──────────────┬───────────────┐
         │              │               │
         ▼              ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Platform     │ │ OTel Baggage │ │ API Response │
│ Events       │ │ (Traces)     │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
         │              │
         │              │
         ▼              ▼
┌──────────────────────────────────┐
│      Databricks Delta Lake       │
│                                  │
│  platform_events    agent_traces │
│      (table)           (table)   │
└──────────────────────────────────┘
                 │
                 ▼
        ┌──────────────────┐
        │  Analytics &     │
        │  Dashboards      │
        └──────────────────┘
```

## Delta Lake Schema

### Platform Events Table

**Table:** `signaltogrowth.platform_events`

| Column           | Type      | Description                          |
|------------------|-----------|--------------------------------------|
| event_id         | STRING    | Primary key (UUID)                   |
| **session_id**   | STRING    | **Join key (UUID)**                  |
| user_id          | STRING    | User identifier                      |
| event_name       | STRING    | Event type (e.g., task_created)      |
| event_timestamp  | TIMESTAMP | Event occurrence time                |
| properties       | STRUCT    | Event-specific data (flexible)       |

**Example Event:**
```json
{
  "event_id": "evt-123",
  "session_id": "abc-123-session",
  "user_id": "test-user-001",
  "event_name": "agent_message_sent",
  "event_timestamp": "2026-07-06T12:00:00Z",
  "properties": {
    "message_text": "Buy milk tomorrow",
    "message_length": 18
  }
}
```

### Agent Traces Table

**Table:** `signaltogrowth.agent_traces`

| Column           | Type      | Description                                |
|------------------|-----------|--------------------------------------------|
| trace_id         | STRING    | Primary key (UUID)                         |
| **session_id**   | STRING    | **Join key (UUID, from OTel baggage)**     |
| span_id          | STRING    | Span identifier                            |
| parent_span_id   | STRING    | Parent span (for nested operations)        |
| span_name        | STRING    | Operation name (e.g., agent.process_message) |
| start_time       | TIMESTAMP | Span start time                            |
| end_time         | TIMESTAMP | Span end time                              |
| attributes       | STRUCT    | GenAI semantic conventions + custom attrs  |

**Example Trace:**
```json
{
  "trace_id": "trc-456",
  "session_id": "abc-123-session",
  "span_id": "spn-789",
  "parent_span_id": null,
  "span_name": "agent.process_message",
  "start_time": "2026-07-06T12:00:00.100Z",
  "end_time": "2026-07-06T12:00:02.500Z",
  "attributes": {
    "gen_ai_request_model": "gpt-4o-mini",
    "gen_ai_usage_total_tokens": 150,
    "gen_ai_usage_input_tokens": 100,
    "gen_ai_usage_output_tokens": 50,
    "agent_task_created": true,
    "user_id": "test-user-001"
  }
}
```

## Join Patterns

### 1. Basic Join (All Events + Traces for Session)

```sql
SELECT
    e.event_name,
    e.event_timestamp,
    e.properties,
    t.span_name,
    t.start_time,
    t.end_time,
    t.attributes
FROM signaltogrowth.platform_events e
LEFT JOIN signaltogrowth.agent_traces t
    ON e.session_id = t.session_id
WHERE e.session_id = 'abc-123-session'
ORDER BY e.event_timestamp, t.start_time;
```

### 2. Agent Performance Analysis (Latency Metrics)

Join `agent_message_sent` events with `agent.process_message` traces to measure end-to-end latency.

```sql
SELECT
    e.session_id,
    e.properties.message_text as user_message,
    e.event_timestamp as request_time,
    t.end_time as response_time,
    TIMESTAMPDIFF(MILLISECOND, e.event_timestamp, t.end_time) as latency_ms,
    t.attributes.gen_ai_usage_total_tokens as tokens_used,
    t.attributes.agent_task_created as task_created
FROM signaltogrowth.platform_events e
INNER JOIN signaltogrowth.agent_traces t
    ON e.session_id = t.session_id
WHERE e.event_name = 'agent_message_sent'
    AND t.span_name = 'agent.process_message'
    AND e.event_timestamp BETWEEN t.start_time AND t.end_time
ORDER BY e.event_timestamp DESC
LIMIT 100;
```

### 3. Token Usage Attribution (Cost per Task)

Join `task_created` events with `agent.extract_task` traces to attribute LLM costs.

```sql
SELECT
    e.properties.task_id as task_id,
    e.properties.title as task_title,
    e.event_timestamp as created_at,
    SUM(t.attributes.gen_ai_usage_total_tokens) as total_tokens,
    SUM(t.attributes.gen_ai_usage_input_tokens) as input_tokens,
    SUM(t.attributes.gen_ai_usage_output_tokens) as output_tokens,
    COUNT(DISTINCT t.span_id) as llm_calls
FROM signaltogrowth.platform_events e
INNER JOIN signaltogrowth.agent_traces t
    ON e.session_id = t.session_id
WHERE e.event_name = 'task_created'
    AND t.span_name LIKE 'agent.%'
    AND e.event_timestamp BETWEEN t.start_time AND t.end_time
GROUP BY e.properties.task_id, e.properties.title, e.event_timestamp
ORDER BY total_tokens DESC;
```

### 4. Error Analysis (Failed Operations)

Join failed task events with exception spans for debugging.

```sql
SELECT
    e.session_id,
    e.event_name,
    e.event_timestamp,
    e.properties as event_details,
    t.span_name,
    t.attributes.exception_type as error_type,
    t.attributes.exception_message as error_message,
    t.attributes.exception_stacktrace as stacktrace
FROM signaltogrowth.platform_events e
INNER JOIN signaltogrowth.agent_traces t
    ON e.session_id = t.session_id
WHERE t.attributes.exception_type IS NOT NULL
    AND e.event_timestamp BETWEEN t.start_time AND t.end_time
ORDER BY e.event_timestamp DESC
LIMIT 50;
```

### 5. User Journey Analysis (Session Timeline)

Visualize complete user interaction flow for a session.

```sql
WITH session_events AS (
    SELECT
        session_id,
        event_timestamp as timestamp,
        'event' as type,
        event_name as name,
        properties as details
    FROM signaltogrowth.platform_events
    WHERE session_id = 'abc-123-session'
),
session_traces AS (
    SELECT
        session_id,
        start_time as timestamp,
        'trace' as type,
        span_name as name,
        STRUCT(
            TIMESTAMPDIFF(MILLISECOND, start_time, end_time) as duration_ms,
            attributes.gen_ai_usage_total_tokens as tokens
        ) as details
    FROM signaltogrowth.agent_traces
    WHERE session_id = 'abc-123-session'
)
SELECT * FROM (
    SELECT * FROM session_events
    UNION ALL
    SELECT * FROM session_traces
)
ORDER BY timestamp;
```

## Implementation Checklist

✅ **Frontend**
- [x] Generate session_id with `crypto.randomUUID()`
- [x] Store in `sessionStorage` for persistence across page refreshes
- [x] Send `X-Session-Id` header on all API requests

✅ **Backend**
- [x] Extract session_id from `request.headers.get('X-Session-Id')`
- [x] Include session_id in all platform events (Zerobus)
- [x] Propagate session_id to OTel trace context via baggage
- [x] Ensure session_id in all event and trace payloads

✅ **Delta Lake**
- [x] platform_events table has `session_id` column (STRING)
- [x] agent_traces table has `session_id` column (STRING)
- [x] Both tables have indexes on session_id for efficient joins

✅ **Testing**
- [x] End-to-end test validates session_id propagation
- [x] Test queries verify session_id in Delta tables
- [x] Documentation provides example join queries

## Monitoring & Validation

### Query to Validate Session ID Coverage

Check what percentage of events/traces have session_id populated:

```sql
-- Platform events coverage
SELECT
    COUNT(*) as total_events,
    COUNT(session_id) as events_with_session_id,
    ROUND(100.0 * COUNT(session_id) / COUNT(*), 2) as coverage_pct
FROM signaltogrowth.platform_events
WHERE event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 DAY;

-- Agent traces coverage
SELECT
    COUNT(*) as total_traces,
    COUNT(session_id) as traces_with_session_id,
    ROUND(100.0 * COUNT(session_id) / COUNT(*), 2) as coverage_pct
FROM signaltogrowth.agent_traces
WHERE start_time >= CURRENT_TIMESTAMP - INTERVAL 1 DAY;
```

### Sample Sessions for Testing

Query to find recent sessions with both events and traces:

```sql
SELECT
    e.session_id,
    COUNT(DISTINCT e.event_id) as event_count,
    COUNT(DISTINCT t.span_id) as trace_count,
    MIN(e.event_timestamp) as session_start,
    MAX(e.event_timestamp) as session_end
FROM signaltogrowth.platform_events e
LEFT JOIN signaltogrowth.agent_traces t
    ON e.session_id = t.session_id
WHERE e.event_timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 DAY
GROUP BY e.session_id
HAVING COUNT(DISTINCT e.event_id) > 0
    AND COUNT(DISTINCT t.span_id) > 0
ORDER BY session_start DESC
LIMIT 10;
```

## Troubleshooting

### Issue: Events have session_id but traces don't

**Cause:** OTel baggage not propagated in agent endpoint

**Fix:** Ensure `set_session_id()` is called before processing agent message
```python
# In main.py /agent/chat endpoint
session_id = request.headers.get('X-Session-Id')
if session_id:
    set_session_id(session_id)  # Propagate to OTel baggage
```

### Issue: Traces have session_id but events don't

**Cause:** Frontend not sending X-Session-Id header

**Fix:** Check eventEmitter.js and api.js configuration
```javascript
// In api.js
headers['X-Session-Id'] = sessionStorage.getItem('session_id');
```

### Issue: session_id changes mid-session

**Cause:** sessionStorage cleared or regenerated

**Fix:** Only generate session_id once, on initial load
```javascript
// In eventEmitter.js
if (!sessionStorage.getItem('session_id')) {
    sessionStorage.setItem('session_id', crypto.randomUUID());
}
```

## Best Practices

1. **Always validate session_id exists before querying**
   - Add `WHERE session_id IS NOT NULL` to joins
   - Monitor null session_id rate as data quality metric

2. **Use time-based filters for large tables**
   - Add date filters before joining (e.g., `event_timestamp >= CURRENT_DATE - 7`)
   - This prevents full table scans

3. **Consider session duration for joins**
   - Events and traces should be within reasonable time window
   - Add `BETWEEN start_time - INTERVAL 1 MINUTE AND end_time + INTERVAL 1 MINUTE`

4. **Index both tables on session_id**
   - Already configured in setup_zerobus_catalog_tables.sql
   - Verify with `DESCRIBE DETAIL signaltogrowth.platform_events`

## References

- Frontend implementation: `frontend/src/services/eventEmitter.js`
- Backend implementation: `backend/app/main.py`
- OTel baggage propagation: `backend/app/telemetry.py`
- E2E tests: `backend/tests/test_session_id_e2e.py`
- Delta table setup: `databricks/setup_zerobus_catalog_tables.sql`
