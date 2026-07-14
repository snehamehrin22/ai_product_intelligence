# OpenTelemetry Schema for AI Agents

This document defines the complete telemetry schema for AI agents using OpenTelemetry semantic conventions.

---

## Table of Contents

1. [Overview](#overview)
2. [Trace Structure](#trace-structure)
3. [Span Types](#span-types)
4. [Standard Attributes](#standard-attributes)
5. [Complete Example](#complete-example)
6. [Databricks Schema](#databricks-schema)
7. [Query Examples](#query-examples)

---

## Overview

Every user interaction with an AI agent generates a **trace** containing multiple **spans**. Each span represents one operation (LLM call, tool execution, reasoning step).

### Key Concepts

| Concept | Definition | Example |
|---------|-----------|---------|
| **Trace** | Complete user request journey | User asks to create GitHub issue |
| **Span** | Single operation within trace | One LLM API call |
| **Parent-Child** | Hierarchical relationship | Tool call spawns HTTP request |
| **Attributes** | Metadata key-value pairs | `gen_ai.usage.total_tokens: 200` |

---

## Trace Structure

```
Trace (trace_id: abc123)
├─ Span: agent.user_request (root)
│  ├─ Span: agent.reasoning
│  │  └─ Span: llm.chat
│  ├─ Span: tool.github_create_issue
│  │  └─ Span: http.post
│  ├─ Span: agent.reasoning
│  │  └─ Span: llm.chat
│  └─ Span: memory.write
```

**Fields every span has:**
- `trace_id` - Links all spans from same user request
- `span_id` - Unique ID for this span
- `parent_span_id` - Links to parent (null for root)
- `name` - Operation name (e.g., "llm.chat")
- `start_time_unix_nano` - Start timestamp (nanoseconds)
- `end_time_unix_nano` - End timestamp (nanoseconds)
- `duration_ms` - Calculated duration in milliseconds
- `attributes` - Key-value metadata
- `status` - OK, ERROR, or UNSET

---

## Span Types

### 1. User Request Span (Root)

**Name**: `agent.user_request`

**Purpose**: Top-level span representing entire user interaction.

**Attributes**:
```json
{
  "user.id": "user-123",
  "user.org_id": "org-acme",
  "user.session_id": "session-xyz",
  "request.input": "Create a GitHub issue...",
  "request.type": "command",
  "agent.name": "claude-code",
  "agent.version": "1.2.0",
  "agent.framework": "anthropic-sdk",
  "agent.task_completed": true,
  "agent.iterations": 3,
  "agent.stopped_reason": "task_complete"
}
```

---

### 2. Agent Reasoning Span

**Name**: `agent.reasoning`

**Purpose**: Represents agent deciding what to do next.

**Attributes**:
```json
{
  "agent.reasoning.step": 1,
  "agent.reasoning.strategy": "ReAct",
  "agent.reasoning.input": "User message text",
  "agent.reasoning.thought": "I need to call tool X",
  "agent.reasoning.decision": "call_tool",
  "agent.reasoning.next_tool": "github_create_issue",
  "agent.reasoning.confidence": 0.95
}
```

**Common strategies**:
- `ReAct` - Reasoning + Acting
- `Chain-of-Thought` - Step-by-step reasoning
- `Tree-of-Thought` - Branching exploration
- `Plan-and-Execute` - Plan first, then act

---

### 3. LLM Call Span

**Name**: `llm.chat` or `llm.completion`

**Purpose**: Represents call to LLM API (OpenAI, Anthropic, etc.)

**Attributes (GenAI Semantic Conventions)**:

```json
{
  // Model information
  "gen_ai.system": "openai",
  "gen_ai.request.model": "gpt-4o",
  "gen_ai.response.model": "gpt-4o-2024-08-06",
  "gen_ai.request.temperature": 0.2,
  "gen_ai.request.max_tokens": 2000,
  "gen_ai.request.top_p": 1.0,
  "gen_ai.request.frequency_penalty": 0.0,
  "gen_ai.request.presence_penalty": 0.0,

  // Token usage
  "gen_ai.usage.input_tokens": 450,
  "gen_ai.usage.output_tokens": 85,
  "gen_ai.usage.total_tokens": 535,

  // Response metadata
  "gen_ai.response.id": "chatcmpl-abc123",
  "gen_ai.response.finish_reason": "stop",
  "gen_ai.response.created": 1704067200,

  // Tool calls (if function calling)
  "gen_ai.tool_calls.count": 1,
  "gen_ai.tool_calls[0].id": "call_xyz",
  "gen_ai.tool_calls[0].name": "search_web",
  "gen_ai.tool_calls[0].arguments": "{\"query\": \"weather\"}",

  // Optional: Full content (for debugging)
  "gen_ai.system_instructions": "You are an AI assistant...",
  "gen_ai.prompt.0.role": "user",
  "gen_ai.prompt.0.content": "User message",
  "gen_ai.completion.0.role": "assistant",
  "gen_ai.completion.0.content": "Assistant response",

  // Cost tracking
  "cost.input_usd": 0.00225,
  "cost.output_usd": 0.00128,
  "cost.total_usd": 0.00353
}
```

**Finish reasons**:
- `stop` - Normal completion
- `length` - Hit max_tokens limit (truncated)
- `tool_calls` - LLM wants to call a tool
- `content_filter` - Blocked by safety filter
- `function_call` - (Deprecated, use tool_calls)

---

### 4. Tool Call Span

**Name**: `tool.{tool_name}` (e.g., `tool.github_create_issue`)

**Purpose**: Represents execution of an external tool.

**Attributes**:

```json
{
  // Tool metadata
  "tool.name": "github_create_issue",
  "tool.type": "mcp",
  "tool.description": "Creates a new GitHub issue",
  "tool.version": "1.0.0",

  // MCP-specific (if using Model Context Protocol)
  "mcp.server.name": "github",
  "mcp.server.version": "1.0.0",
  "mcp.server.transport": "stdio",
  "mcp.tool.name": "create_issue",

  // Input/output
  "tool.input.title": "Fix login bug",
  "tool.input.body": "Bug description",
  "tool.input.labels": "[\"bug\", \"priority:high\"]",
  "tool.input.repository": "acme/webapp",

  "tool.output.issue_number": 42,
  "tool.output.url": "https://github.com/acme/webapp/issues/42",
  "tool.output.status": "open",

  // Success/failure
  "tool.success": true,
  "tool.error": null,
  "tool.error_type": null,

  // Security
  "security.authenticated": true,
  "security.user_id": "user-123",
  "security.permission_granted": true,
  "security.policy_checked": true
}
```

**Tool types**:
- `mcp` - Model Context Protocol server
- `api` - External API call
- `database` - Database query
- `filesystem` - File read/write
- `web` - Web scraping
- `shell` - Shell command execution

---

### 5. HTTP Request Span

**Name**: `http.{method}` (e.g., `http.post`)

**Purpose**: Represents HTTP request (often child of tool call).

**Attributes (HTTP Semantic Conventions)**:

```json
{
  // Request
  "http.method": "POST",
  "http.url": "https://api.github.com/repos/acme/webapp/issues",
  "http.target": "/repos/acme/webapp/issues",
  "http.scheme": "https",
  "http.host": "api.github.com",
  "http.request.header.user-agent": "mcp-github-client/1.0.0",
  "http.request.header.content-type": "application/json",
  "http.request.body.size": 456,

  // Response
  "http.response.status_code": 201,
  "http.response.header.content-type": "application/json",
  "http.response.body.size": 1234,

  // Network
  "network.protocol.name": "https",
  "network.protocol.version": "1.1",
  "network.peer.address": "140.82.121.6",
  "network.peer.port": 443
}
```

---

### 6. Retrieval (RAG) Span

**Name**: `retrieval.query` or `retrieval.search`

**Purpose**: Searching vector database or knowledge base.

**Attributes**:

```json
{
  // Query
  "retrieval.query": "How do I deploy to Kubernetes?",
  "retrieval.query_type": "semantic_search",

  // Source
  "retrieval.source": "pinecone",
  "retrieval.index_name": "docs-embeddings",
  "retrieval.namespace": "production",

  // Results
  "retrieval.results_count": 5,
  "retrieval.top_score": 0.92,
  "retrieval.score_threshold": 0.7,

  // Vector metadata
  "retrieval.embedding_model": "text-embedding-ada-002",
  "retrieval.embedding_dimensions": 1536,

  // Performance
  "retrieval.latency_ms": 45,
  "retrieval.cache_hit": false
}
```

---

### 7. Memory Operation Span

**Name**: `memory.{operation}` (e.g., `memory.write`, `memory.read`)

**Purpose**: Reading/writing to agent memory or state.

**Attributes**:

```json
{
  // Operation
  "memory.operation": "write",
  "memory.store": "redis",
  "memory.key": "session:abc-xyz:history",

  // Data
  "memory.size_bytes": 456,
  "memory.ttl_seconds": 3600,
  "memory.content_type": "conversation_history",
  "memory.content_summary": "User requested GitHub issue creation",

  // Performance
  "memory.cache_hit": false,
  "memory.latency_ms": 12
}
```

---

### 8. Skill Execution Span

**Name**: `skill.{skill_name}` (e.g., `skill.commit_push_pr`)

**Purpose**: Executing a reusable agent workflow/skill.

**Attributes**:

```json
{
  "skill.name": "commit-push-pr",
  "skill.version": "1.0.0",
  "skill.description": "Commits, pushes, and creates PR",
  "skill.input.commit_message": "Fix login bug",
  "skill.steps_completed": 3,
  "skill.steps_total": 5,
  "skill.current_step": "creating_pr",
  "skill.success": true,
  "skill.output.pr_url": "https://github.com/acme/webapp/pull/123"
}
```

---

## Standard Attributes Reference

### Resource Attributes (Apply to all spans)

```json
{
  "service.name": "claude-code-agent",
  "service.version": "1.2.0",
  "deployment.environment": "production",
  "host.name": "snehamehrin-macbook",
  "os.type": "darwin",
  "os.version": "14.2.1",
  "process.pid": 12345,
  "telemetry.sdk.name": "opentelemetry",
  "telemetry.sdk.version": "1.22.0",
  "telemetry.sdk.language": "python"
}
```

---

### User Context Attributes

```json
{
  "user.id": "user-123",
  "user.email": "user@example.com",
  "user.name": "John Doe",
  "user.org_id": "org-acme",
  "user.session_id": "session-abc-xyz",
  "user.ip_address": "192.168.1.100"
}
```

---

### Security/Compliance Attributes

```json
{
  "security.user_id": "user-123",
  "security.org_id": "org-acme",
  "security.rbac_role": "admin",
  "security.authenticated": true,
  "security.permission_granted": true,
  "security.policy_checked": true,
  "security.pii_detected": false,
  "security.data_classification": "public",
  "security.audit_log_written": true
}
```

---

## Complete Example Trace

### Scenario: User asks Claude Code to create a GitHub issue

**User input**: "Create a GitHub issue titled 'Fix login bug' with priority high"

### Full Trace JSON

```json
{
  "trace_id": "f4e8b2a1c9d7e3f6a5b8c1d2e3f4a5b6",
  "resource": {
    "service.name": "claude-code-agent",
    "service.version": "1.2.0",
    "deployment.environment": "production",
    "host.name": "snehamehrin-macbook"
  },
  "spans": [
    {
      "span_id": "span-001",
      "parent_span_id": null,
      "trace_id": "f4e8b2a1c9d7e3f6a5b8c1d2e3f4a5b6",
      "name": "agent.user_request",
      "kind": "INTERNAL",
      "start_time_unix_nano": 1704067200000000000,
      "end_time_unix_nano": 1704067215234000000,
      "duration_ms": 15234,
      "attributes": {
        "user.id": "user-sneha-123",
        "user.session_id": "session-abc-xyz",
        "request.input": "Create a GitHub issue titled 'Fix login bug' with priority high",
        "agent.name": "claude-code",
        "agent.task_completed": true,
        "agent.iterations": 3
      },
      "status": {
        "code": "OK"
      }
    },
    {
      "span_id": "span-002",
      "parent_span_id": "span-001",
      "trace_id": "f4e8b2a1c9d7e3f6a5b8c1d2e3f4a5b6",
      "name": "agent.reasoning",
      "kind": "INTERNAL",
      "start_time_unix_nano": 1704067200050000000,
      "end_time_unix_nano": 1704067201823000000,
      "duration_ms": 1773,
      "attributes": {
        "agent.reasoning.step": 1,
        "agent.reasoning.strategy": "ReAct",
        "agent.reasoning.decision": "call_tool",
        "agent.reasoning.next_tool": "github_create_issue",
        "agent.reasoning.confidence": 0.95
      }
    },
    {
      "span_id": "span-003",
      "parent_span_id": "span-002",
      "trace_id": "f4e8b2a1c9d7e3f6a5b8c1d2e3f4a5b6",
      "name": "llm.chat",
      "kind": "CLIENT",
      "start_time_unix_nano": 1704067200100000000,
      "end_time_unix_nano": 1704067201800000000,
      "duration_ms": 1700,
      "attributes": {
        "gen_ai.system": "openai",
        "gen_ai.request.model": "gpt-4o",
        "gen_ai.usage.input_tokens": 450,
        "gen_ai.usage.output_tokens": 85,
        "gen_ai.usage.total_tokens": 535,
        "gen_ai.response.finish_reason": "stop",
        "cost.total_usd": 0.00353
      }
    },
    {
      "span_id": "span-004",
      "parent_span_id": "span-001",
      "trace_id": "f4e8b2a1c9d7e3f6a5b8c1d2e3f4a5b6",
      "name": "tool.github_create_issue",
      "kind": "CLIENT",
      "start_time_unix_nano": 1704067201900000000,
      "end_time_unix_nano": 1704067204567000000,
      "duration_ms": 2667,
      "attributes": {
        "tool.name": "github_create_issue",
        "tool.type": "mcp",
        "mcp.server.name": "github",
        "tool.input.title": "Fix login bug",
        "tool.output.issue_number": 42,
        "tool.success": true
      }
    },
    {
      "span_id": "span-005",
      "parent_span_id": "span-004",
      "trace_id": "f4e8b2a1c9d7e3f6a5b8c1d2e3f4a5b6",
      "name": "http.post",
      "kind": "CLIENT",
      "start_time_unix_nano": 1704067201950000000,
      "end_time_unix_nano": 1704067204500000000,
      "duration_ms": 2550,
      "attributes": {
        "http.method": "POST",
        "http.url": "https://api.github.com/repos/acme/webapp/issues",
        "http.response.status_code": 201
      }
    }
  ],
  "summary": {
    "total_duration_ms": 15234,
    "span_count": 5,
    "llm_call_count": 1,
    "tool_call_count": 1,
    "total_tokens": 535,
    "total_cost_usd": 0.00353
  }
}
```

---

## Databricks Schema

### Architecture: Multi-Agent, Multi-Provider Support

This schema is designed to handle:
- **Multiple agents** (todo agent, email agent, research agent, etc.)
- **Multiple LLM providers** (OpenAI, Anthropic, Cohere, Azure OpenAI, Bedrock, etc.)
- **Multiple use cases** (different teams, products, environments)
- **Schema evolution** (new attributes added over time without breaking changes)

```
┌─────────────────────────────────────────────────────────────┐
│ BRONZE LAYER (Universal, Schema-Agnostic)                    │
│ ✓ Single table for ALL agents, ALL providers                 │
│ ✓ Schema evolution handled automatically                     │
│ ✓ Raw OTLP protobuf OR flattened MAP<STRING, STRING>         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ SILVER LAYER (Normalized by Use Case)                        │
│ ├─ llm_traces (LLM calls, agent reasoning)                   │
│ ├─ tool_traces (tool usage, MCP calls)                       │
│ ├─ http_traces (API calls, latency)                          │
│ └─ custom_events (business-specific)                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ GOLD LAYER (Aggregated Metrics)                              │
│ ├─ llm_cost_daily (by provider, model, team)                 │
│ ├─ agent_performance_hourly (latency, success rate)          │
│ └─ tool_usage_summary (which tools used most)                │
└─────────────────────────────────────────────────────────────┘
```

---

### Bronze Layer: `raw.otlp_spans_json`

**Purpose**: Universal append-only table storing ALL telemetry from ALL agents and providers.

**Design decisions**:
- Uses `MAP<STRING, STRING>` for attributes (infinite schema flexibility)
- Never modified or deleted (audit trail)
- Partitioned by date and topic for performance
- Supports schema evolution without migrations

```sql
-- Create catalog and schema
CREATE CATALOG IF NOT EXISTS telemetry;
USE CATALOG telemetry;

CREATE SCHEMA IF NOT EXISTS raw;
USE SCHEMA raw;

-- Universal Bronze table for ALL agents
CREATE TABLE IF NOT EXISTS otlp_spans_json (
  -- Kafka metadata
  kafka_topic STRING NOT NULL COMMENT 'agent-traces, platform-events, custom-events',
  kafka_partition INT NOT NULL,
  kafka_offset BIGINT NOT NULL,
  kafka_timestamp TIMESTAMP NOT NULL,

  -- Message metadata
  ingestion_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  ingestion_date DATE NOT NULL GENERATED ALWAYS AS (CAST(ingestion_timestamp AS DATE)),

  -- Core OTLP fields (always present)
  trace_id STRING NOT NULL,
  span_id STRING NOT NULL,
  parent_span_id STRING,
  trace_state STRING,
  span_name STRING NOT NULL,
  span_kind STRING COMMENT 'INTERNAL, CLIENT, SERVER, PRODUCER, CONSUMER',
  start_time_unix_nano BIGINT NOT NULL,
  end_time_unix_nano BIGINT NOT NULL,

  -- Resource attributes (service-level, applies to all spans)
  -- Stored as MAP for schema flexibility
  resource_attributes MAP<STRING, STRING> COMMENT 'service.name, deployment.environment, etc.',

  -- Span attributes (ALL span-specific attributes)
  -- Stored as MAP to handle infinite schema evolution
  attributes MAP<STRING, STRING> COMMENT 'gen_ai.*, tool.*, agent.*, custom.*',

  -- Events (logs within span)
  events ARRAY<STRUCT<
    time_unix_nano: BIGINT,
    name: STRING,
    attributes: MAP<STRING, STRING>
  >> COMMENT 'Span events like tool.input, tool.output',

  -- Links (to other spans in different traces)
  links ARRAY<STRUCT<
    trace_id: STRING,
    span_id: STRING,
    trace_state: STRING,
    attributes: MAP<STRING, STRING>
  >>,

  -- Status
  status_code STRING COMMENT 'OK, ERROR, UNSET',
  status_message STRING,

  PRIMARY KEY (kafka_topic, kafka_partition, kafka_offset)
)
USING DELTA
PARTITIONED BY (ingestion_date, kafka_topic)
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.minReaderVersion' = '2',
  'delta.minWriterVersion' = '5'
);

-- Indexes for common queries
CREATE INDEX idx_trace_id ON otlp_spans_json (trace_id);
CREATE INDEX idx_service ON otlp_spans_json ((resource_attributes['service.name']));
CREATE INDEX idx_span_name ON otlp_spans_json (span_name);
```

**Why MAP<STRING, STRING>?**

✅ **Schema evolution**: New `gen_ai.*` attributes automatically captured without DDL changes
✅ **Multi-provider**: Works with ANY LLM provider's semantic conventions
✅ **Custom attributes**: Teams can add domain-specific attributes without coordination
✅ **No data loss**: Every attribute from OTLP is preserved
✅ **Future-proof**: When OpenTelemetry adds new conventions, they're already stored

---

### Silver Layer: `agent_traces.llm_traces`

**Purpose**: Typed, queryable table for LLM and agent-specific analysis.

**Design decisions**:
- Strongly-typed columns for common queries (fast)
- Derived from Bronze via streaming job
- Includes cost calculation logic
- Supports all LLM providers uniformly

```sql
-- Create schema for agent traces
CREATE SCHEMA IF NOT EXISTS agent_traces;
USE SCHEMA agent_traces;

-- Silver table for LLM/Agent traces specifically
CREATE TABLE IF NOT EXISTS llm_traces (
  -- Core identifiers
  trace_id STRING NOT NULL,
  span_id STRING NOT NULL,
  parent_span_id STRING,
  span_name STRING NOT NULL,

  -- Timing
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  duration_ms DOUBLE NOT NULL,

  -- Service info (extracted from resource_attributes MAP)
  service_name STRING NOT NULL COMMENT 'Which agent: todo-agent, email-agent, etc.',
  service_version STRING,
  deployment_environment STRING COMMENT 'production, staging, development',

  -- User context
  user_id STRING,
  user_org_id STRING,
  user_session_id STRING,

  -- Agent attributes
  agent_name STRING,
  agent_version STRING,
  agent_framework STRING,
  agent_task_completed BOOLEAN,
  agent_iterations INT,
  agent_stopped_reason STRING,

  -- Agent reasoning
  agent_reasoning_step INT,
  agent_reasoning_strategy STRING,
  agent_reasoning_decision STRING,
  agent_reasoning_confidence DOUBLE,

  -- GenAI semantic conventions (works for ALL providers)
  gen_ai_system STRING COMMENT 'openai, anthropic, cohere, azure, bedrock',
  gen_ai_request_model STRING,
  gen_ai_response_model STRING,
  gen_ai_request_temperature DOUBLE,
  gen_ai_request_max_tokens INT,
  gen_ai_usage_input_tokens INT,
  gen_ai_usage_output_tokens INT,
  gen_ai_usage_total_tokens INT,
  gen_ai_response_id STRING,
  gen_ai_response_finish_reason STRING,

  -- Cost (calculated dynamically based on provider + model)
  cost_input_usd DOUBLE,
  cost_output_usd DOUBLE,
  cost_total_usd DOUBLE,

  -- Status
  status_code STRING COMMENT 'OK, ERROR, UNSET',
  status_message STRING,

  -- Metadata
  ingestion_timestamp TIMESTAMP NOT NULL,
  ingestion_date DATE NOT NULL,

  PRIMARY KEY (trace_id, span_id)
)
USING DELTA
PARTITIONED BY (ingestion_date, service_name)
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

CREATE INDEX idx_user ON llm_traces (user_id);
CREATE INDEX idx_model ON llm_traces (gen_ai_request_model);
```

---

### Silver Layer: `agent_traces.tool_traces`

**Purpose**: Typed table for tool call analysis.

**Design decisions**:
- Common tool attributes as columns
- Tool-specific I/O stored as JSON for flexibility
- Supports any tool type (MCP, API, database, etc.)

```sql
CREATE TABLE IF NOT EXISTS tool_traces (
  -- Core identifiers
  trace_id STRING NOT NULL,
  span_id STRING NOT NULL,
  parent_span_id STRING,
  span_name STRING NOT NULL,

  -- Timing
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  duration_ms DOUBLE NOT NULL,

  -- Service context
  service_name STRING NOT NULL,
  deployment_environment STRING,
  user_id STRING,

  -- Common tool attributes
  tool_name STRING NOT NULL,
  tool_type STRING NOT NULL COMMENT 'mcp, api, database, filesystem, web, shell',
  tool_success BOOLEAN,
  tool_error_message STRING,
  tool_retry_count INT,

  -- MCP-specific (if applicable)
  mcp_server_name STRING,
  mcp_server_version STRING,

  -- Tool-specific I/O (stored as JSON for schema flexibility)
  tool_input JSON COMMENT 'Full input parameters as JSON',
  tool_output JSON COMMENT 'Full output response as JSON',

  -- Security
  security_authenticated BOOLEAN,
  security_permission_granted BOOLEAN,

  -- Status
  status_code STRING,
  status_message STRING,

  -- Metadata
  ingestion_timestamp TIMESTAMP NOT NULL,
  ingestion_date DATE NOT NULL,

  PRIMARY KEY (trace_id, span_id)
)
USING DELTA
PARTITIONED BY (ingestion_date, tool_type)
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true',
  'delta.autoOptimize.optimizeWrite' = 'true'
);
```

---

### Silver Layer: Streaming Transformation Example

**Purpose**: Shows how to materialize Silver from Bronze using Spark Structured Streaming.

```python
# databricks/silver_llm_traces_streaming.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.appName("SilverLLMTraces").getOrCreate()

# Read from Bronze (change data feed for incremental processing)
bronze_df = spark.readStream \
    .format("delta") \
    .option("readChangeFeed", "true") \
    .option("startingVersion", 0) \
    .table("telemetry.raw.otlp_spans_json")

# Filter to only LLM-related spans
llm_df = bronze_df.filter(
    (col("span_name").like("llm.%")) |
    (col("span_name").like("agent.%")) |
    (col("attributes")["gen_ai.system"].isNotNull())
)

# Define cost calculation UDF (handles all providers)
@udf(returnType=DoubleType())
def calculate_cost(provider, model, input_tokens, output_tokens, cost_type):
    """Calculate cost based on provider/model pricing."""
    pricing = {
        # OpenAI pricing
        ("openai", "gpt-4o-mini", "input"): 0.15,
        ("openai", "gpt-4o-mini", "output"): 0.60,
        ("openai", "gpt-4o", "input"): 2.50,
        ("openai", "gpt-4o", "output"): 10.00,
        # Anthropic pricing
        ("anthropic", "claude-3-5-sonnet-20241022", "input"): 3.00,
        ("anthropic", "claude-3-5-sonnet-20241022", "output"): 15.00,
        # Cohere pricing
        ("cohere", "command-r-plus", "input"): 2.50,
        ("cohere", "command-r-plus", "output"): 10.00,
        # Add more as needed
    }

    # Handle model variations (e.g., "claude-3-5-sonnet-20241022" vs "claude-3.5-sonnet")
    for (p, m, t), price in pricing.items():
        if provider == p and model.startswith(m[:20]) and cost_type == t:
            tokens = input_tokens if cost_type == "input" else output_tokens
            return (tokens / 1_000_000.0) * price

    return 0.0

# Transform to Silver schema
silver_df = llm_df.select(
    col("trace_id"),
    col("span_id"),
    col("parent_span_id"),
    col("span_name"),

    # Parse timestamps
    (col("start_time_unix_nano") / 1000).cast("timestamp").alias("start_time"),
    (col("end_time_unix_nano") / 1000).cast("timestamp").alias("end_time"),
    ((col("end_time_unix_nano") - col("start_time_unix_nano")) / 1000000.0).alias("duration_ms"),

    # Extract from resource_attributes MAP
    col("resource_attributes")["service.name"].alias("service_name"),
    col("resource_attributes")["service.version"].alias("service_version"),
    col("resource_attributes")["deployment.environment"].alias("deployment_environment"),

    # Extract user context from attributes MAP
    col("attributes")["user.id"].alias("user_id"),
    col("attributes")["user.org_id"].alias("user_org_id"),
    col("attributes")["user.session_id"].alias("user_session_id"),

    # Extract agent attributes
    col("attributes")["agent.name"].alias("agent_name"),
    col("attributes")["agent.version"].alias("agent_version"),
    col("attributes")["agent.framework"].alias("agent_framework"),
    col("attributes")["agent.task_completed"].cast("boolean").alias("agent_task_completed"),
    col("attributes")["agent.iterations"].cast("int").alias("agent_iterations"),
    col("attributes")["agent.stopped_reason"].alias("agent_stopped_reason"),

    # Extract reasoning attributes
    col("attributes")["agent.reasoning.step"].cast("int").alias("agent_reasoning_step"),
    col("attributes")["agent.reasoning.strategy"].alias("agent_reasoning_strategy"),
    col("attributes")["agent.reasoning.decision"].alias("agent_reasoning_decision"),
    col("attributes")["agent.reasoning.confidence"].cast("double").alias("agent_reasoning_confidence"),

    # Extract GenAI attributes (works for ALL providers)
    col("attributes")["gen_ai.system"].alias("gen_ai_system"),
    col("attributes")["gen_ai.request.model"].alias("gen_ai_request_model"),
    col("attributes")["gen_ai.response.model"].alias("gen_ai_response_model"),
    col("attributes")["gen_ai.request.temperature"].cast("double").alias("gen_ai_request_temperature"),
    col("attributes")["gen_ai.request.max_tokens"].cast("int").alias("gen_ai_request_max_tokens"),
    col("attributes")["gen_ai.usage.input_tokens"].cast("int").alias("gen_ai_usage_input_tokens"),
    col("attributes")["gen_ai.usage.output_tokens"].cast("int").alias("gen_ai_usage_output_tokens"),
    col("attributes")["gen_ai.usage.total_tokens"].cast("int").alias("gen_ai_usage_total_tokens"),
    col("attributes")["gen_ai.response.id"].alias("gen_ai_response_id"),
    col("attributes")["gen_ai.response.finish_reason"].alias("gen_ai_response_finish_reason"),

    # Status
    col("status_code"),
    col("status_message"),

    # Metadata
    col("ingestion_timestamp"),
    col("ingestion_date")
)

# Add cost calculation
silver_with_cost = silver_df.withColumn(
    "cost_input_usd",
    calculate_cost(
        col("gen_ai_system"),
        col("gen_ai_request_model"),
        col("gen_ai_usage_input_tokens"),
        col("gen_ai_usage_output_tokens"),
        lit("input")
    )
).withColumn(
    "cost_output_usd",
    calculate_cost(
        col("gen_ai_system"),
        col("gen_ai_request_model"),
        col("gen_ai_usage_input_tokens"),
        col("gen_ai_usage_output_tokens"),
        lit("output")
    )
).withColumn(
    "cost_total_usd",
    col("cost_input_usd") + col("cost_output_usd")
)

# Write to Silver table
query = silver_with_cost.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/mnt/checkpoints/silver_llm") \
    .option("mergeSchema", "true") \
    .partitionBy("ingestion_date", "service_name") \
    .trigger(processingTime="30 seconds") \
    .toTable("telemetry.agent_traces.llm_traces")

query.awaitTermination()
```

---

### Parsed, queryable trace data with all attributes (DEPRECATED - see above for production schema)

```sql
CREATE TABLE telemetry.agent_traces.parsed_traces (
  -- Core span identifiers
  trace_id STRING NOT NULL,
  span_id STRING NOT NULL,
  parent_span_id STRING,
  span_name STRING NOT NULL,
  span_kind STRING,

  -- Timing
  start_time_unix_nano BIGINT,
  end_time_unix_nano BIGINT,
  duration_ms DOUBLE,

  -- Service/resource attributes
  service_name STRING,
  service_version STRING,
  deployment_environment STRING,

  -- User context
  user_id STRING,
  user_org_id STRING,
  user_session_id STRING,

  -- Agent attributes
  agent_name STRING,
  agent_version STRING,
  agent_framework STRING,
  agent_task_completed BOOLEAN,
  agent_iterations INT,
  agent_stopped_reason STRING,

  -- Agent reasoning
  agent_reasoning_step INT,
  agent_reasoning_strategy STRING,
  agent_reasoning_decision STRING,
  agent_reasoning_confidence DOUBLE,

  -- GenAI semantic conventions (LLM calls)
  gen_ai_system STRING,
  gen_ai_request_model STRING,
  gen_ai_response_model STRING,
  gen_ai_request_temperature DOUBLE,
  gen_ai_request_max_tokens INT,
  gen_ai_usage_input_tokens INT,
  gen_ai_usage_output_tokens INT,
  gen_ai_usage_total_tokens INT,
  gen_ai_response_id STRING,
  gen_ai_response_finish_reason STRING,

  -- Tool calls
  tool_name STRING,
  tool_type STRING COMMENT 'mcp, api, database, filesystem, web, shell',
  tool_success BOOLEAN,
  tool_error STRING,
  tool_error_type STRING,

  -- MCP-specific
  mcp_server_name STRING,
  mcp_server_version STRING,
  mcp_tool_name STRING,

  -- HTTP attributes
  http_method STRING,
  http_url STRING,
  http_status_code INT,

  -- Retrieval (RAG)
  retrieval_query STRING,
  retrieval_source STRING,
  retrieval_results_count INT,
  retrieval_top_score DOUBLE,

  -- Memory operations
  memory_operation STRING COMMENT 'read, write, update, delete',
  memory_store STRING,
  memory_size_bytes BIGINT,

  -- Skills
  skill_name STRING,
  skill_version STRING,
  skill_success BOOLEAN,

  -- Security/compliance
  security_authenticated BOOLEAN,
  security_permission_granted BOOLEAN,
  security_pii_detected BOOLEAN,

  -- Cost tracking
  cost_input_usd DOUBLE,
  cost_output_usd DOUBLE,
  cost_total_usd DOUBLE,

  -- Status
  status_code STRING COMMENT 'OK, ERROR, UNSET',
  status_message STRING,

  -- Metadata
  ingestion_timestamp TIMESTAMP,
  ingestion_date DATE GENERATED ALWAYS AS (CAST(ingestion_timestamp AS DATE))
)
USING DELTA
PARTITIONED BY (ingestion_date, service_name)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

---

### Gold Layer: `agent_metrics_hourly`

Aggregated metrics for dashboards.

```sql
CREATE TABLE telemetry.agent_traces.agent_metrics_hourly (
  metric_hour TIMESTAMP NOT NULL,
  metric_date DATE GENERATED ALWAYS AS (CAST(metric_hour AS DATE)),

  -- Dimensions
  service_name STRING,
  deployment_environment STRING,
  user_org_id STRING,
  llm_model STRING,
  tool_name STRING,

  -- Request metrics
  total_requests BIGINT,
  successful_requests BIGINT,
  failed_requests BIGINT,
  success_rate DOUBLE,

  -- Performance metrics
  avg_duration_ms DOUBLE,
  p50_duration_ms DOUBLE,
  p95_duration_ms DOUBLE,
  p99_duration_ms DOUBLE,
  max_duration_ms DOUBLE,

  -- LLM metrics
  total_llm_calls BIGINT,
  total_tokens BIGINT,
  total_input_tokens BIGINT,
  total_output_tokens BIGINT,
  avg_tokens_per_call DOUBLE,

  -- Tool metrics
  total_tool_calls BIGINT,
  tool_success_rate DOUBLE,
  avg_tool_latency_ms DOUBLE,

  -- Cost metrics
  total_cost_usd DOUBLE,
  avg_cost_per_request_usd DOUBLE,

  -- Agent behavior metrics
  avg_iterations DOUBLE,
  avg_reasoning_confidence DOUBLE
)
USING DELTA
PARTITIONED BY (metric_date, service_name)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

---

## Query Examples

All queries work uniformly across **all agents** and **all LLM providers**.

### 1. Multi-Agent Cost Comparison

```sql
-- Compare costs across different agents (OpenAI, Anthropic, Cohere, etc.)
SELECT
  service_name as agent,
  gen_ai_system as provider,
  gen_ai_request_model as model,
  COUNT(*) as total_calls,
  SUM(gen_ai_usage_total_tokens) as total_tokens,
  SUM(cost_total_usd) as total_cost_usd,
  AVG(cost_total_usd) as avg_cost_per_call,
  AVG(duration_ms) as avg_latency_ms
FROM telemetry.agent_traces.llm_traces
WHERE ingestion_date >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY service_name, gen_ai_system, gen_ai_request_model
ORDER BY total_cost_usd DESC;
```

**Output example**:
```
agent              | provider  | model                      | total_calls | total_tokens | total_cost_usd | avg_cost_per_call | avg_latency_ms
-------------------|-----------|----------------------------|-------------|--------------|----------------|-------------------|----------------
todo-agent         | openai    | gpt-4o                     | 1,245       | 524,300      | $45.23         | $0.036            | 1,850
email-agent        | anthropic | claude-3-5-sonnet-20241022 | 892         | 412,100      | $38.15         | $0.043            | 2,120
research-agent     | openai    | gpt-4o-mini                | 3,421       | 1,234,500    | $8.94          | $0.003            | 950
```

---

### 2. Find all traces for a user (across all agents)

```sql
SELECT
  trace_id,
  service_name as agent,
  span_name,
  duration_ms,
  gen_ai_system as llm_provider,
  gen_ai_usage_total_tokens as tokens,
  tool_name,
  cost_total_usd,
  status_code
FROM telemetry.agent_traces.llm_traces
WHERE user_id = 'user-sneha-123'
  AND ingestion_date = CURRENT_DATE()
ORDER BY start_time;
```

---

### 2. Calculate cost per user

```sql
SELECT
  user_id,
  COUNT(DISTINCT trace_id) as total_requests,
  SUM(gen_ai_usage_total_tokens) as total_tokens,
  SUM(cost_total_usd) as total_cost_usd,
  AVG(cost_total_usd) as avg_cost_per_request
FROM telemetry.agent_traces.parsed_traces
WHERE cost_total_usd IS NOT NULL
  AND ingestion_date >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY user_id
ORDER BY total_cost_usd DESC;
```

---

### 3. Find slow tool calls

```sql
SELECT
  tool_name,
  mcp_server_name,
  COUNT(*) as call_count,
  AVG(duration_ms) as avg_duration_ms,
  MAX(duration_ms) as max_duration_ms,
  SUM(CASE WHEN tool_success THEN 1 ELSE 0 END) as success_count,
  AVG(CASE WHEN tool_success THEN 1.0 ELSE 0.0 END) as success_rate
FROM telemetry.agent_traces.parsed_traces
WHERE tool_name IS NOT NULL
  AND ingestion_date = CURRENT_DATE()
GROUP BY tool_name, mcp_server_name
ORDER BY avg_duration_ms DESC;
```

---

### 4. Agent reasoning analysis

```sql
SELECT
  agent_reasoning_strategy,
  agent_reasoning_step,
  COUNT(*) as occurrences,
  AVG(duration_ms) as avg_reasoning_time_ms,
  AVG(agent_reasoning_confidence) as avg_confidence
FROM telemetry.agent_traces.parsed_traces
WHERE span_name = 'agent.reasoning'
  AND ingestion_date >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY agent_reasoning_strategy, agent_reasoning_step
ORDER BY agent_reasoning_strategy, agent_reasoning_step;
```

---

### 5. LLM token usage by model

```sql
SELECT
  gen_ai_request_model,
  COUNT(*) as call_count,
  SUM(gen_ai_usage_input_tokens) as total_input_tokens,
  SUM(gen_ai_usage_output_tokens) as total_output_tokens,
  SUM(gen_ai_usage_total_tokens) as total_tokens,
  AVG(gen_ai_usage_total_tokens) as avg_tokens_per_call,
  SUM(cost_total_usd) as total_cost_usd
FROM telemetry.agent_traces.parsed_traces
WHERE gen_ai_request_model IS NOT NULL
  AND ingestion_date = CURRENT_DATE()
GROUP BY gen_ai_request_model
ORDER BY total_tokens DESC;
```

---

### 6. Find failed requests

```sql
SELECT
  trace_id,
  span_name,
  user_id,
  tool_name,
  tool_error,
  status_message,
  duration_ms,
  ingestion_timestamp
FROM telemetry.agent_traces.parsed_traces
WHERE status_code = 'ERROR'
  AND ingestion_date = CURRENT_DATE()
ORDER BY ingestion_timestamp DESC
LIMIT 50;
```

---

### 7. MCP server usage

```sql
SELECT
  mcp_server_name,
  mcp_tool_name,
  COUNT(*) as call_count,
  AVG(duration_ms) as avg_latency_ms,
  SUM(CASE WHEN tool_success THEN 1 ELSE 0 END) as successes,
  SUM(CASE WHEN NOT tool_success THEN 1 ELSE 0 END) as failures,
  AVG(CASE WHEN tool_success THEN 1.0 ELSE 0.0 END) as success_rate
FROM telemetry.agent_traces.parsed_traces
WHERE mcp_server_name IS NOT NULL
  AND ingestion_date >= CURRENT_DATE() - INTERVAL 7 DAYS
GROUP BY mcp_server_name, mcp_tool_name
ORDER BY call_count DESC;
```

---

### 8. Reconstruct complete trace

```sql
WITH trace_spans AS (
  SELECT
    trace_id,
    span_id,
    parent_span_id,
    span_name,
    duration_ms,
    start_time_unix_nano,
    gen_ai_usage_total_tokens,
    tool_name,
    tool_success
  FROM telemetry.agent_traces.parsed_traces
  WHERE trace_id = 'f4e8b2a1c9d7e3f6a5b8c1d2e3f4a5b6'
)
SELECT
  span_id,
  parent_span_id,
  span_name,
  duration_ms,
  gen_ai_usage_total_tokens,
  tool_name,
  tool_success
FROM trace_spans
ORDER BY start_time_unix_nano;
```

---

---

## Auto-Instrumentation vs Manual Instrumentation

### Auto-Instrumentation (Recommended)

**What it is**: Libraries that automatically wrap LLM API calls to create spans without manual code.

**Available libraries**:
```bash
# OpenAI
pip install opentelemetry-instrumentation-openai

# Anthropic
pip install opentelemetry-instrumentation-anthropic

# Universal (LiteLLM, LangChain, LlamaIndex)
pip install opentelemetry-instrumentation-litellm
pip install traceloop-sdk  # OpenLLMetry - supports all providers
```

**Setup example**:
```python
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

# One-time setup
OpenAIInstrumentor().instrument()
AnthropicInstrumentor().instrument()

# Now ALL calls are automatically traced:
from openai import OpenAI
from anthropic import Anthropic

openai_client = OpenAI()
anthropic_client = Anthropic()

# Both automatically generate spans with GenAI semantic conventions
response = openai_client.chat.completions.create(...)
response = anthropic_client.messages.create(...)
```

**Benefits**:
- ✅ Zero boilerplate per LLM call
- ✅ Automatic GenAI semantic conventions
- ✅ Token usage, costs, latency tracked automatically
- ✅ Works across all providers uniformly

---

### LLM Routing Support

When using **LLM routers** (LiteLLM, Portkey) that dynamically choose providers:

```python
from opentelemetry.instrumentation.litellm import LiteLLMInstrumentor
import litellm

# Instrument the router (not individual providers)
LiteLLMInstrumentor().instrument()

# Now ANY provider call through LiteLLM is traced:
response = litellm.completion(
    model="gpt-4o",  # OpenAI
    messages=[...]
)

response = litellm.completion(
    model="claude-3-5-sonnet-20241022",  # Anthropic
    messages=[...]
)

response = litellm.completion(
    model="command-r-plus",  # Cohere
    messages=[...]
)

# All generate uniform telemetry in Databricks
```

**Databricks queries work identically**:
```sql
-- Works for ALL providers, regardless of routing
SELECT
  gen_ai_system,  -- "openai", "anthropic", "cohere", etc.
  COUNT(*) as calls,
  SUM(cost_total_usd) as cost
FROM telemetry.agent_traces.llm_traces
GROUP BY gen_ai_system;
```

---

### Manual Instrumentation (Custom Attributes)

For **custom attributes** (agent reasoning, tool calls, etc.):

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def agent_process_message(message: str):
    with tracer.start_as_current_span("agent.process_message") as span:
        # Custom agent attributes
        span.set_attribute("agent.name", "todo-agent")
        span.set_attribute("agent.reasoning.strategy", "ReAct")

        # LLM call (auto-instrumented)
        response = openai_client.chat.completions.create(...)

        # Tool call (manual instrumentation)
        with tracer.start_as_current_span("tool.github_create_issue") as tool_span:
            tool_span.set_attribute("tool.name", "github_create_issue")
            tool_span.set_attribute("tool.type", "mcp")
            # ... tool execution
```

---

### Hybrid Approach (Best Practice)

**Recommendation**: Use auto-instrumentation for standard operations + manual for custom logic.

```python
# Auto-instrument all LLM providers
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

OpenAIInstrumentor().instrument()
AnthropicInstrumentor().instrument()

# Manually instrument agent-specific logic
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def agent_workflow(user_input: str):
    with tracer.start_as_current_span("agent.user_request") as span:
        # Custom attributes
        span.set_attribute("user.id", "user-123")
        span.set_attribute("agent.task_completed", True)

        # LLM call (auto-instrumented - no manual tracing needed)
        response = openai_client.chat.completions.create(...)

        # Tool call (manual - custom attributes)
        with tracer.start_as_current_span("tool.custom_api") as tool_span:
            tool_span.set_attribute("tool.name", "custom_api")
            # ... tool execution
```

---

## References

- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [HTTP Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/http/)
- [OpenTelemetry Trace Specification](https://opentelemetry.io/docs/specs/otel/trace/)
- [OpenTelemetry Auto-Instrumentation](https://opentelemetry.io/docs/instrumentation/python/automatic/)
- [LiteLLM Observability](https://docs.litellm.ai/docs/observability/opentelemetry)
- [OpenLLMetry (Universal Instrumentation)](https://github.com/traceloop/openllmetry)
- [Langfuse MCP Tracing](https://langfuse.com/docs/observability/features/mcp-tracing)
- [Arize Phoenix MCP](https://docs.arize.com/phoenix/mcp)
