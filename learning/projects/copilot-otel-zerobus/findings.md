# Copilot OTel → ZeroBus: Path B Findings

**Date:** 2026-08-17
**Environment:** personal Azure subscription, Databricks workspace `signaltogrowth` (eastus)
**Goal:** prove Path B — VS Code Copilot → OTel Collector hosted in AKS → ZeroBus → Delta

---

## 1. Status: PROVEN

Real VS Code Copilot telemetry was written into Unity Catalog Delta tables via ZeroBus, with the service-principal secret sourced from Azure Key Vault and **prompt/response content redacted at the collector** so it never reaches Delta.

Final counts: **17 spans, 18 logs, 171 metrics.**

Real Copilot spans captured:

```
copilot-chat | invoke_agent GitHub Copilot Chat  | 1
copilot-chat | chat gpt-4o-mini-2024-07-18       | 4
copilot-chat | chat mai-code-1.1-flash           | 3
copilot-chat | execute_tool read_file            | 6
copilot-chat | execute_tool manage_todo_list     | 1
```

**Chain verified:**

```
laptop → <COLLECTOR_LB_IP>:4318 (AKS LoadBalancer)
      → otel-collector pod (AKS aks-learning, eastus)
      → transform/derive + attributes/redact  (content stripped here)
      → oauth2client: KV secret → ZeroBus OAuth token via /oidc/v1/token
      → gRPC to <WORKSPACE_ID>.zerobus.eastus.azuredatabricks.net:443
      → signaltogrowth.agent_traces.copilot_otel_{spans,logs,metrics}
```

**The prior POC in this repo had never run.** The `signaltogrowth_zerobus` catalog did not exist and the `copilot-otel` namespace did not exist in AKS. Manifests and scripts were written but never executed.

---

## 2. ZeroBus table requirements

Three independent constraints, each discovered by hitting it.

### 2.1 Must NOT be in metastore default storage

```
Error Code: 4024
Unsupported table kind. Tables created in default storage are not supported.
```

A plain `CREATE TABLE` in a schema with no explicit managed location lands in metastore default storage (`abfss://unitycatalog@prd0lz…`). ZeroBus rejects it.

The location **is** an `abfss://` URL, so "has an abfss location" is *not* the requirement — the earlier README note was misleading. What matters is that it is not metastore *default* storage.

### 2.2 Must be a UC MANAGED table

```
Error Code: 4014
Unsupported table type: "External". Only UC Managed tables are supported.
```

Creating the table as EXTERNAL with an explicit `LOCATION` satisfies 2.1 but violates 2.2.

### 2.3 The only configuration satisfying both

A **MANAGED** table inside a **schema (or catalog) created with an explicit `MANAGED LOCATION`**:

```sql
CREATE SCHEMA signaltogrowth.agent_traces
  MANAGED LOCATION 'abfss://<CONTAINER>@<STORAGE_ACCOUNT>.dfs.core.windows.net/agent_traces';

-- then plain managed CREATE TABLE, no LOCATION clause
CREATE TABLE signaltogrowth.agent_traces.copilot_otel_spans ( ... ) USING DELTA ...;
```

Resulting location — managed, but under the schema's own storage root:

```
abfss://<CONTAINER>@<STORAGE_ACCOUNT>.dfs.core.windows.net/
  agent_traces/__unitystorage/schemas/<schema-id>/tables/<table-id>
```

**Gotcha:** `ALTER SCHEMA ... SET MANAGED LOCATION` is **not supported**:

```
[UC_COMMAND_NOT_SUPPORTED.NON_HMS_FEDERATED_ENTITY]
ALTER SCHEMA SET MANAGED LOCATION is only supported for Unity Catalog
federated Hive metastore entities
```

The managed location must be set **at schema creation time**. An existing schema must be dropped and recreated.

### 2.4 Metrics table must contain EVERY metric type column

```
Error Code: 4027
Field "exponential_histogram" found in the proto definition, but not in the table schema.
Field "summary" found in the proto definition, but not in the table schema.
Error Code: 4004
```

**ZeroBus validates the full OTel proto against the table schema.** Every metric type needs a column even if never emitted. `setup.sql` in this repo omitted `exponential_histogram` and `summary`; the reference DDL has both. Fixed with `ALTER TABLE ... ADD COLUMNS`, after which all 171 metrics landed.

---

## 3. Storage credential RBAC

Creating tables in the external location initially failed:

```
PERMISSION_DENIED: Request for user delegation key is not authorized.
```

**Cause:** the Databricks Access Connector's managed identity had `Storage Blob Data Contributor` scoped to the **container**:

```
.../storageAccounts/<STORAGE_ACCOUNT>/blobServices/default/containers/<CONTAINER>
```

Requesting a **user delegation key is a storage-account-level operation**, so container-scoped RBAC is insufficient.

**Fix** — grant at storage account scope:

| Role | Scope |
|---|---|
| `Storage Blob Data Contributor` | storage account |
| `Storage Blob Delegator` | storage account |

Access Connector identity: `<ACCESS_CONNECTOR_PRINCIPAL_ID>` (system-assigned on `databricks-access-connector`, RG `Analytics`). Propagation was effectively immediate; allow 1–2 minutes.

**Also found:** `<STORAGE_ACCOUNT_NO_HNS>` (backing the `zerobusingest_externallocation` external location) has **HNS disabled**, so it cannot serve ADLS Gen2 / `abfss://` traffic. Only `<STORAGE_ACCOUNT>` has HNS enabled — that external location was never usable.

---

## 4. Service principal privilege chain

`oauth2client` requests these in its `authorization_details`. **All four levels must be granted or the token request fails.**

| Object | Privilege | Note |
|---|---|---|
| Catalog `signaltogrowth` | `USE_CATALOG` | pre-existing |
| Schema `agent_traces` | `USE_SCHEMA` | **was missing** — easy to overlook |
| Table `copilot_otel_spans` | `MODIFY`, `SELECT` | |
| Table `copilot_otel_logs` | `MODIFY`, `SELECT` | |

SP: `zerobus_ingest`

`setup.sql` grants only table-level privileges with a comment claiming catalog/schema `USE` was "already granted." That assumption breaks when the target catalog/schema changes, and the failure surfaces far downstream.

---

## 5. Corporate network findings (Zscaler / GlobalProtect)

Tested on a corporate-managed laptop.

| Host | Result |
|---|---|
| `dev.azure.com`, `management.azure.com` | reachable |
| `portal.azure.com`, `shell.azure.com` | reachable |
| `*.zerobus.*.azuredatabricks.net` | **reachable** (real IP, TLS + HTTP/2) |
| `adb-*.azuredatabricks.net` (workspace) | **BLOCKED** |
| `accounts.azuredatabricks.net` | **BLOCKED** |
| `*.hcp.*.azmk8s.io` (Kubernetes API) | **BLOCKED** |

**Block signature:** DNS returns a synthetic `100.64.x.x` address (Zscaler resolver at `100.64.0.1-3`); TCP connects; the TLS **Client Hello is reset with no Server Hello**. This is SNI-based policy blocking, *not* a certificate trust problem — a CA bundle does not help.

### The critical consequence

`/oidc/v1/token` lives on the blocked workspace host. Therefore:

- **Path A (direct Copilot → ZeroBus) cannot work from a laptop** — the token cannot be obtained.
- **A collector running on a laptop cannot work either** — `oauth2client`'s `token_url` is the same blocked host.
- **The OAuth exchange must happen in the cloud.** This is what makes Path B the only viable design, independent of any infrastructure preference.

### Notes

- Turning Zscaler off unblocked `*.azuredatabricks.net` but **not** `*.azmk8s.io`. GlobalProtect stayed running with traffic via `utun4` → `100.64.0.1`.
- Even with Zscaler off, TLS interception continued: Python `urllib` failed with `CERTIFICATE_VERIFY_FAILED: Basic Constraints of CA cert not marked critical`, while `curl` (system keychain) succeeded. **Use `curl` for Databricks API calls from a managed laptop.**
- **Workaround for the `azmk8s.io` block:** `az aks command invoke` runs kubectl server-side via `management.azure.com`. Worked reliably, required no security changes, and supports `--file` to upload manifests.
- `shell.azure.com` (Cloud Shell) is a fallback for reaching Databricks, since it runs inside Azure.

---

## 6. Copilot telemetry vocabulary

Derived from 204 trace dumps, 43 log dumps, 690 metric dumps in a local telemetry dump directory, cross-checked against live Delta rows.

### 6.1 Span types

| Span | Count in dumps | Distinct attribute keys |
|---|---|---|
| `execute_tool` | 265 | 15 |
| `permission` | 240 | 4 |
| `chat` | 239 | 36 |
| `invoke_agent` | 47 | 29 |
| `external_tool` | 1 | 3 |

`permission` spans (`permission.kind`, `permission.result`, `permission.tool_name`) are the **tool-approval funnel** — directly relevant to funnel analysis and absent from the short live session.

### 6.2 TWO COEXISTING VOCABULARIES

Two emitters use different names for the same concepts:

| Concept | `github.copilot` scope (CLI / agent host) | `copilot-chat` scope (VS Code ext) |
|---|---|---|
| turn count | `github.copilot.turn_count` | `copilot_chat.turn_count` |
| AIU billing | `github.copilot.nano_aiu` | `copilot_chat.copilot_usage_nano_aiu` |
| request id | `github.copilot.service_request_id` | `copilot_chat.server_request_id` |
| latency | `github.copilot.server_duration` | `copilot_chat.time_to_first_token` |

Scope → span mapping in the dumps:

```
github.copilot : execute_tool 265, permission 240, chat 183, invoke_agent 47, external_tool 1
copilot-chat   : chat 56
```

Scope versions seen: `github.copilot 1.0.70-0`, `github.copilot 1.0.73`, `copilot-chat 0.59.0`.

**Every silver column must `COALESCE` both.** A view reading only `copilot_chat.*` silently drops most traffic.

### 6.3 A SECOND TELEMETRY LAYER LIVES IN SPAN EVENTS

Not in `attributes` — in the `events ARRAY<STRUCT<... attributes VARIANT ...>>` column. Easy to miss entirely.

| Event | Count | Carries |
|---|---|---|
| `github.copilot.session.usage_info` | 167 | `current_tokens`, `messages_length`, `token_limit` → **context-window utilisation** |
| `github.copilot.hook.start` / `.end` | 111 each | `hook.type`, `hook.decision`, `hook.duration`, `hook.tool_names` → **guardrail enforcement** |
| `github.copilot.mcp.server.lifecycle` | 75 | server name, name_hash, state, transport, source, plugin_name |
| `github.copilot.user.message` | 45 | `agent_mode`, `interaction_id`, `source` |
| `github.copilot.skill.invoked` | 16 | skill name, path, invocation_trigger, source |
| `gen_ai.client.operation.exception` | 5 | `exception.type`, `exception.message` → **errors** |

VS Code scope also emits `turn_start`, `turn_end`, `user_message`, `tools_available` events (confirmed in live Delta rows).

### 6.4 Resource attributes

Only three: `service.name`, `service.version`, `session.id` (the last present in 31/204 files — `copilot-chat` scope only).

### 6.5 Attribute sparsity

Coverage is uneven and silver must tolerate NULLs:

- `gen_ai.request.temperature`, `top_p`, `max_tokens` — **23%** of chat spans
- `github.copilot.cost`, `nano_aiu`, `interaction_id`, `turn_id` — **70%**
- `gen_ai.usage.reasoning.output_tokens` — **67%**
- `gen_ai.tool.definitions` — **70%**

Any gold metric needs a denominator of *spans where the field was present*, not all spans, or averages silently skew.

Oddity: `gen_ai.response.model` appears at **115%** of chat spans — duplicate keys on some spans. Dedupe when modelling.

### 6.6 Pre-aggregated metrics (bonus)

Copilot emits OTel GenAI metrics directly — cheaper than deriving from spans:

| Metric | Type |
|---|---|
| `gen_ai.client.token.usage` | histogram |
| `gen_ai.client.operation.duration` | histogram |
| `gen_ai.client.operation.time_to_first_chunk` | histogram |
| `gen_ai.client.operation.time_per_output_chunk` | histogram |
| `copilot_chat.tool.call.count` | sum |
| `copilot_chat.tool.call.duration` | histogram |
| `copilot_chat.time_to_first_token` | histogram |
| `copilot_chat.agent.invocation.duration` | histogram |
| `copilot_chat.agent.turn.count` | histogram |
| `copilot_chat.session.count` | sum |

---

## 7. Identity and WAU

**`enduser.pseudo.id` exists** — this corrects an earlier assumption that no user identifier was available.

| | |
|---|---|
| Example value | `2be99fd08f3b01ec750ce6f5c4fb42a8` (32-char hex) |
| Stability | **stable across all 47 spans**, 1 distinct value for 1 user |
| Present on | **`invoke_agent` spans only** (100% of them) |
| Absent from | `chat` (239), `execute_tool` (265), `permission` (240), `external_tool` (1) |

**Implications:**

1. **WAU is computable** — `COUNT(DISTINCT enduser.pseudo.id)`.
2. It must be **propagated down** to `chat` / `execute_tool` / `permission` spans via `trace_id` or `conversation_id`, since only the root span carries it.
3. It is **pseudonymous** — a hash, not an email. You can count distinct users and track behaviour per user over time, but **cannot segment by team, role, or persona** without a separate mapping table or an injected `user.id`.

**Decision needed before enterprise rollout:** whether to inject a real identifier. Copilot honours `OTEL_RESOURCE_ATTRIBUTES`, so managed settings could push `user.id=<upn>`, or the gateway collector could stamp it from the authenticated sender. Either way it must be decided up front — it cannot be backfilled.

---

## 8. Redaction in the collector (implemented and verified)

Content is stripped **at the collector**, so prompts and code never reach Delta. Two processors, order matters — derive first, then delete.

```yaml
processors:
  transform/derive:
    error_mode: ignore
    trace_statements:
      - context: span
        statements:
          - 'set(attributes["ra.input_chars"], Len(attributes["gen_ai.input.messages"])) where attributes["gen_ai.input.messages"] != nil'
          - 'set(attributes["ra.output_chars"], Len(attributes["gen_ai.output.messages"])) where attributes["gen_ai.output.messages"] != nil'
          - 'set(attributes["ra.request_chars"], Len(attributes["copilot_chat.user_request"])) where attributes["copilot_chat.user_request"] != nil'
          - 'set(attributes["ra.reasoning_chars"], Len(attributes["copilot_chat.reasoning_content"])) where attributes["copilot_chat.reasoning_content"] != nil'
          - 'set(attributes["ra.tool_args_chars"], Len(attributes["gen_ai.tool.call.arguments"])) where attributes["gen_ai.tool.call.arguments"] != nil'
          - 'set(attributes["ra.tool_result_chars"], Len(attributes["gen_ai.tool.call.result"])) where attributes["gen_ai.tool.call.result"] != nil'
      # events carry content too — the attributes processor CANNOT reach these
      - context: spanevent
        statements:
          - 'set(attributes["ra.content_chars"], Len(attributes["content"])) where attributes["content"] != nil'
          - 'delete_key(attributes, "content")'
          - 'delete_key(attributes, "toolDefinitions")'
          - 'delete_key(attributes, "github.copilot.skill.content")'

  attributes/redact:
    actions:
      - {key: gen_ai.system_instructions, action: hash}   # prompt-version drift
      - {key: gen_ai.tool.definitions, action: hash}      # tool-set drift
      - {key: copilot_chat.user_request, action: hash}     # repeat-question detection
      - {key: gen_ai.input.messages, action: delete}
      - {key: gen_ai.output.messages, action: delete}
      - {key: gen_ai.tool.call.arguments, action: delete}
      - {key: gen_ai.tool.call.result, action: delete}
      - {key: copilot_chat.reasoning_content, action: delete}
      - {key: github.copilot.tool.parameters.file_path, action: delete}
      - {key: github.copilot.tool.parameters.command, action: delete}
      - {key: github.copilot.skill.content, action: delete}

service:
  pipelines:
    traces:
      processors: [transform/derive, attributes/redact, batch]
    logs:
      processors: [attributes/redact, batch]
```

### Verified result

Sent a span deliberately stuffed with content:

| Field | Result in Delta |
|---|---|
| `gen_ai.input.messages` | **deleted** → `NULL` |
| `gen_ai.output.messages` | **deleted** → `NULL` |
| `gen_ai.tool.call.result` | **deleted** → `NULL` |
| `...tool.parameters.file_path` | **deleted** → `NULL` |
| `copilot_chat.user_request` | **hashed** → `84e372888cc852236745efad942fd920…` |
| `gen_ai.system_instructions` | **hashed** → `40d5318c6a98ae43654503fef6ed4cc4…` |
| `ra.input_chars` / `output` / `request` | **41 / 31 / 21** — exact counts |
| `gen_ai.request.model` | `keep-me-model` — preserved |
| Event `content` | **deleted**, replaced with `ra.content_chars: 25` |

### Key learnings

1. **`action: hash` is SHA-256** (64 hex chars), not SHA-1. Sufficient for change-detection and dedup; no need for OTTL hashing.
2. **The `attributes` processor cannot touch span events.** The `context: spanevent` OTTL block is mandatory — the `user_message` event carries the raw prompt in a `content` attribute. This is the easiest thing to miss and would silently leak prompts.
3. Both OTTL functions used (`Len`, `delete_key`) exist in collector **0.111.0**.
4. `error_mode: ignore` means a failed statement drops that statement, not the span — appropriate here given sparse attributes.

### Tradeoff accepted

This is a **single redacted pipeline**: content is gone permanently, not hidden. Eval work requiring prompt/response text is not possible from these tables. The alternative — a fan-out with a second exporter to a restricted `*_raw` table — was considered and deferred.

---

## 9. Querying VARIANT in Databricks

`attributes` is a native `VARIANT` column, not text.

### The dotted-key trap

Every OTel key contains dots, and the `:` path operator treats dots as nesting:

```sql
attributes:gen_ai.request.model                 -- NULL  (wrong)
attributes:['gen_ai.request.model']::string     -- correct
variant_get(attributes, '$[\'gen_ai.request.model\']', 'string')  -- also correct
```

**Bracket notation always.**

### Exploration

```sql
-- every key across every row, with inferred types
SELECT schema_of_variant_agg(attributes) FROM ...copilot_otel_spans;

-- single row's shape
SELECT schema_of_variant(attributes), typeof(attributes) FROM ...;

-- long format, one row per key
SELECT key, value::string FROM ...copilot_otel_spans, LATERAL variant_explode(attributes);

-- nested: resource is a STRUCT whose attributes are VARIANT
SELECT resource.attributes:['service.name']::string FROM ...;

-- events
SELECT e.name, e.attributes FROM ...copilot_otel_spans s
LATERAL VIEW OUTER explode(s.events) t AS e;
```

**Warning:** `variant_explode` over spans with content returns enormous results (one query returned 550 KB from 16 spans before redaction was enabled).

---

## 10. Analytics schema design

### Layers

```
BRONZE (raw, tight ACL)        SILVER (redacted, broad)          GOLD
copilot_otel_spans        →    fct_agent_turns              →    WAU / adoption
copilot_otel_logs              fct_llm_calls                     cost per user/repo
copilot_otel_metrics           fct_tool_calls                    tool success rates
                               fct_permissions                   approval funnel
                               dim_users                         context pressure
```

### Silver tables — one per span type, because the grain differs

| Table | Grain | Core content |
|---|---|---|
| `fct_agent_turns` | one `invoke_agent` span = one user turn | `user_pseudo_id`, session, conversation, turn #, repo/branch/commit, org, agent type+version, mode, rolled-up tokens + cost, duration, finish reason, MCP servers & skills in context |
| `fct_llm_calls` | one `chat` span = one model call | model requested vs served, provider, tokens (in/out/cache read/cache create/reasoning), cost, nano_aiu, TTFT, server duration, temperature/top_p/max_tokens, finish reason, context used vs limit |
| `fct_tool_calls` | one `execute_tool` span | tool name + type, duration, status, error type, file extension / path depth |
| `fct_permissions` | one `permission` span | permission kind, **result**, tool name — the approval funnel |
| `dim_users` | one `user_pseudo_id` | first seen, last seen, active days |

`external_tool` is 1 span in 204 files — fold into `fct_tool_calls`.

### Three design rules

1. **Propagate `enduser.pseudo.id` down** from `invoke_agent` via `trace_id` / `conversation_id` — no other span type has it.
2. **`COALESCE` the two vocabularies** (§6.2) on every column, or most traffic is dropped.
3. **Content never enters silver** — collector redaction (§8) already guarantees this; silver consumes `ra.*_chars` and the SHA-256 hashes.

### Redaction mapping

| Original | Silver replacement |
|---|---|
| `gen_ai.input.messages` / `output.messages` | `ra.input_chars`, `ra.output_chars` |
| `gen_ai.system_instructions` | SHA-256 in place — prompt-version drift |
| `gen_ai.tool.definitions` | SHA-256 in place — tool-set drift |
| `copilot_chat.user_request` | SHA-256 in place + `ra.request_chars` — repeat detection |
| `copilot_chat.reasoning_content` | `ra.reasoning_chars` |
| `gen_ai.tool.call.arguments` / `.result` | `ra.tool_args_chars`, `ra.tool_result_chars` |
| `...tool.parameters.file_path` / `.command` | dropped (extension/depth derivation not yet implemented) |

---

## 11. Failure modes seen in a separate reference implementation

Source details omitted deliberately. Kept here as a checklist of mistakes worth
avoiding in any ZeroBus + OTel setup.

1. **A copy-pasted DDL file creates the wrong table.** The logs script carried the spans
   schema *and* the spans table name under `CREATE OR REPLACE`. Run in the documented
   order, it **silently overwrites the spans table and never creates the logs table**.
   Lesson: `CREATE OR REPLACE` plus copy-paste is a data-loss combination — prefer
   `CREATE TABLE IF NOT EXISTS`, and assert the table name matches the file.
2. **Per-environment config files that are effectively identical.** Only the Key Vault
   name differed across dev/qa/prod; catalog, schema, workspace and subscription were
   the same, so selecting `prod` still wrote to the dev sandbox catalog — contradicting
   the documented per-environment catalogs. Lesson: diff env files against each other in
   CI; identical values across environments is a bug, not a convenience.
3. **A DDL script that cannot run standalone** — it inherited `DECLARE`/`SET VARIABLE`
   session state from earlier scripts, and the README referenced a schema-creation
   script that did not exist.
4. **Receiver was gRPC-only** (`grpc: 0.0.0.0:4317`). Copilot's default is **HTTP on
   4318**, so telemetry silently goes nowhere unless clients are forced to `otlp-grpc`
   or an `http:` block is added.
5. **`debug` exporter with `verbosity: detailed`** on all pipelines. On a shared
   collector at volume this prints every payload and buries the host in log I/O.
   (This POC used `verbosity: basic`.)
6. **No inbound authentication.** The config authenticated *outbound* to Databricks but
   accepted *anything* inbound. A shared collector needs `bearertokenauth` on the
   receiver.
7. **Missing table properties** — `otel.schemaVersion = 'v2'` and
   `delta.checkpointPolicy = 'classic'`.
8. **Protocol worth verifying.** That setup used `otlphttp/*` exporters; this POC used
   `otlp/*` (gRPC) successfully.
9. **No redaction of any kind.** With `captureContent` enabled, full prompts, responses,
   system prompts and tool results land in Delta. See §10 for the approach used here.
10. Minor drift: a config key set in every env file but referenced nowhere; a README
    example naming a different Key Vault than the real config; a secret name misspelled
    and inconsistently capitalised versus its sibling key. All three are the kind of
    thing a config-schema check catches for free.

### Two testable predictions for that rollout

- **Plain managed tables in a sandbox schema.** If the target schema/catalog has no
  explicit `MANAGED LOCATION`, the pipeline **will fail with Error 4024** exactly as this
  POC did (§2). Directly testable.
- **Managed laptops likely cannot reach `/oidc/v1/token`** (§5). If so, a laptop-side
  collector loader cannot work for any developer regardless of config, and a working demo
  machine must have had a network exception.

---

## 12. Databricks Apps cannot host the collector

Investigated as the closest Databricks-native hosting option.

- Apps **cannot be made public**; anonymous access and SSO bypass are not supported. Every request requires an `Authorization: Bearer <Databricks OAuth token>`, enforced at ingress before app code runs.
- Those tokens **expire in 1 hour**. Copilot can only send **static headers**, so ingestion would silently 401 an hour after setup.
- No non-expiring credential is accepted — even a notebook's own token must be exchanged for an audience-scoped token first.
- Token auth applies only to apps exposing `/api/` routes; OTLP posts to `/v1/traces`, `/v1/logs`, `/v1/metrics`.
- Single port over HTTPS ingress — no gRPC, cannot serve 4317 + 4318 together.
- Fixed ceiling of 2 vCPU / 8 GB per app.

**The structural point:** the collector's job is converting a *static* client credential into a *rotating* Databricks OAuth token. That adapter cannot live inside Databricks — which is precisely why ZeroBus exists as an API for external writers.

Sources:
- https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/auth
- https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/connect-local

---

## 13. Copilot OTel export reference

Copilot Chat emits OpenTelemetry natively — no custom instrumentation.

| Setting | Default | Notes |
|---|---|---|
| `github.copilot.chat.otel.enabled` | `false` | |
| `github.copilot.chat.otel.exporterType` | `otlp-http` | `otlp-http`, `otlp-grpc`, `console`, `file` |
| `github.copilot.chat.otel.otlpEndpoint` | `http://localhost:4318` | |
| `github.copilot.chat.otel.captureContent` | `false` | prompts, responses, tool args/results |
| `github.copilot.chat.otel.maxAttributeSizeChars` | `0` | 0 = unlimited |
| `github.copilot.chat.otel.dbSpanExporter.enabled` | `false` | local SQLite |

Precedence: **managed policy > environment variable > user setting > default.**

Settings used in this POC:

```json
{
  "github.copilot.chat.otel.enabled": true,
  "github.copilot.chat.otel.exporterType": "otlp-http",
  "github.copilot.chat.otel.otlpEndpoint": "http://<COLLECTOR_LB_IP>:4318",
  "github.copilot.chat.otel.captureContent": true
}
```

`captureContent: true` was safe here **only because the collector redacts** (§8).

### Fleet rollout

Enterprise-managed settings deliver a `telemetry` block via MDM (Windows registry / macOS preferences), server-managed settings, or `managed-settings.json`. **Managed values always win.** Managed exporter headers deliberately bypass env vars so the auth token cannot leak into subprocess tools.

Per-signal routing is possible via `OTEL_EXPORTER_OTLP_{TRACES,LOGS,METRICS}_HEADERS` — Copilot is *not* limited to one header set for all signals.

Sources:
- https://code.visualstudio.com/docs/agents/guides/monitoring-agents
- https://github.blog/changelog/2026-07-08-enterprise-managed-opentelemetry-export-for-vs-code-and-cli/

---

## 14. Architecture recommendation for enterprise rollout

### Why laptop-local (`load-collector.ps1`) is not viable

1. **The OIDC endpoint is blocked from laptops** (§5). The token exchange cannot happen there. Disqualifying on its own.
2. **Windows-only.** `.exe` + `.ps1` excludes macOS developers from the dataset entirely.
3. **No denominator.** No way to tell who has the collector running, so a low number cannot be distinguished from "collector wasn't running." Every adoption/acceptance rate has an unknowable denominator — fatal for a measurement programme.
4. **Credential distribution.** Every laptop needs `az login`, Key Vault read, and the Databricks SP secret in process memory.
5. **Silent gaps.** Laptop asleep, terminal closed, VPN off → no data, no error.
6. **No redaction.** Content redaction must happen somewhere central, or every laptop's config becomes a governance surface.

### Gateway model

```
Copilot on laptops ─┐
AgentOS apps ───────┼──→ one gateway collector ──→ ZeroBus ──→ UC tables
ROKAI ──────────────┘     (holds the SP credential,
future apps ──────────     authenticates senders, redacts content)
```

Developer effort: zero. No clone, no binary, no `az login`, no Key Vault access, no `localhost`.

### Hosting: AKS is not required

| | Container Apps | AKS | Single VM |
|---|---|---|---|
| Cluster to manage | no | yes | no |
| OS patching | no | node pools | yours |
| HA / replicas | yes | yes | no |
| gRPC + HTTP | yes | yes | yes |
| Managed identity → Key Vault | yes | yes | yes |
| Ops weight | **low** | high | medium |

**Azure Container Apps** provides every property the gateway needs without introducing Kubernetes. AKS is justified only if it is already the standard platform for internal DAI services.

### Requirements for a shared endpoint

1. One stable hostname with TLS
2. OTLP on **both** HTTP 4318 and gRPC 4317
3. Reachable from laptops on VPN, Azure workloads, Databricks jobs, on-prem
4. **Per-producer authentication** (`bearertokenauth`) — otherwise anything on the network can inject rows into the metrics being reported on
5. **Gateway-stamped `service.name`** from authenticated identity, not client-supplied
6. **Central redaction** (§8) so content policy is enforced in one place
7. HA: 2+ replicas plus a persistent sending queue (`sending_queue` + `file_storage`) so a ZeroBus outage buffers rather than drops
8. Sampling policy defined before volume becomes a problem
9. **A decision on user identity** (§7) — pseudonymous only, or inject `user.id`

### Shared vs per-app tables

Use **three shared tables discriminated by `service_name`**. The DDL already clusters by `(time, service_name, trace_id)`, which only makes sense for shared tables. Per-app tables would need a separate `oauth2client` extension, exporter and pipeline per producer — unmaintainable by the fourth.

`attributes VARIANT` means Copilot spans and the AgentOS event vocabulary both land without schema migration, joinable on `session_id` + `invocation_id`.

---

## 15. Working configuration

### Azure

| | |
|---|---|
| Subscription | `<AZURE_SUBSCRIPTION_ID>` (tenant `<TENANT_ID>`) |
| AKS | `aks-learning` / `rg-k8s-learning`, eastus, 2 × `Standard_D2s_v7`, k8s 1.35.6 |
| Key Vault | `<KEY_VAULT_NAME>` (RBAC-enabled), secret `zerobus-client-secret` |
| CSI addon | `azure-keyvault-secrets-provider`, identity clientId `<ADDON_CLIENT_ID>`, objectId `<ADDON_OBJECT_ID>` |
| KV role for addon identity | `Key Vault Secrets User` at vault scope |
| Collector image | `otel/opentelemetry-collector-contrib:0.111.0` |
| LoadBalancer | `<COLLECTOR_LB_IP>` — ports 4317, 4318, 13133 |

### Secret flow (no secret on any laptop or in any manifest)

```
Key Vault ──▶ Secrets Store CSI Driver ──▶ K8s Secret "zerobus-creds"
          ──▶ deployment secretKeyRef ──▶ DATABRICKS_CLIENT_SECRET env var
```

`SecretProviderClass` used `useVMManagedIdentity: "true"` with the addon's `userAssignedIdentityID`, and `secretObjects` to sync into `zerobus-creds`.

**Gotcha:** the CSI driver only syncs to a Kubernetes Secret when a pod actually **mounts** the volume. The deployment needs a `volume` + `volumeMount` referencing the `SecretProviderClass`, even though the value is consumed via `secretKeyRef`.

`DATABRICKS_CLIENT_ID` was passed as a literal — not sensitive.

### Deviations from the original repo manifests

| | Original | This POC |
|---|---|---|
| Catalog | `signaltogrowth_zerobus` | `signaltogrowth` |
| Schema | `bronze` | `agent_traces` (with `MANAGED LOCATION`) |
| Secret source | `kubectl --from-literal` in `deploy.sh` | Key Vault via CSI driver |
| Client ID | K8s secret | literal env value |
| Processors | `batch` only | `transform/derive`, `attributes/redact`, `batch` |
| Debug verbosity | — | `basic` |
| Metrics table | missing 2 columns | `exponential_histogram`, `summary` added |

Workspace ID, region, service principal, receivers and exporters were unchanged and correct.

---

## 16. Known gaps

1. **Public LoadBalancer with no receiver auth.** Anyone who found `<COLLECTOR_LB_IP>:4318` could write rows. Acceptable for a timeboxed POC; add `bearertokenauth` or delete the Service for anything longer-lived.
2. **`replicas: 1`** — single point of failure, no sending queue, so a ZeroBus outage drops data.
3. **`az aks command invoke` records the command string** in the cluster's run-command history. Not an issue here (the secret came from Key Vault), but never pass secrets via `--command`.
4. **Collector image `0.111.0`** is roughly two years old. Worked fine; use a current release for anything real.
5. **Silver views not built** — the schema in §10 is designed but not implemented.
6. **`permission` and `external_tool` spans never captured live** — the session didn't trigger them. Their handling is inferred from dumps only.
7. **File path derivation not implemented** — `file_path` and `command` are deleted outright rather than reduced to extension / depth / hash.
8. **Storage credential grants widened** to storage-account scope (§3). Correct for the requirement but broader than container scope; flag in any security review.
9. **Eval capability sacrificed** — single redacted pipeline means no prompt/response content is retained anywhere (§8).

---

## 17. Cost, teardown and environment traps

Roughly **$0.25/hour** while running (2 × D2s_v7 + LoadBalancer + disks); about **$175/month** if left on. This POC ran ~1h15 (~$0.30). Cluster stopped at the end.

```bash
# stop compute, preserve everything (restart ~5 min)
az aks stop --name aks-learning --resource-group rg-k8s-learning

# optional: remove the public endpoint
kubectl delete svc otel-collector -n copilot-otel
```

### Traps encountered getting the environment usable

1. **Subscription was `Disabled`** (Free Trial, `spendingLimit: On`) and required **Reactivate** in the portal. `az account list` reported `Enabled` while ARM still reported `Disabled` — **ARM's view governs writes.** Test with an actual write, not the account listing.
2. **`Microsoft.KeyVault` was not registered** on the subscription; needed `az provider register` (~90 s) before a vault could be created. Freshly reactivated subscriptions may need others too.
3. **AKS was in `provisioningState: Failed`** after being deallocated while the subscription was disabled. `az aks start` refuses on a Failed cluster; **`az aks update`** reconciles it first (Azure's own error message says so).
4. **Portal sign-in bounced** with *"Selected user account does not exist in tenant"* — the browser resumes the last-used directory. Fix: incognito window plus a tenant-pinned URL (`https://portal.azure.com/#@<tenant-id>`).
5. **`az aks stop`/`start` return exit code 0 even on failure** — always check the printed output or re-query state.
