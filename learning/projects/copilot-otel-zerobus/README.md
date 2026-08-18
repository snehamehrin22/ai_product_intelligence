# Copilot OTel → ZeroBus

Sends VS Code Copilot telemetry (traces, logs, metrics) straight to Databricks Delta Lake via ZeroBus.
Two paths to compare — same destination, different routing.

```
PATH A (direct)
VS Code ──OTLP gRPC──► ZeroBus endpoint ──► Delta Lake

PATH B (via K8s collector)
VS Code ──OTLP HTTP──► OTel Collector (K8s) ──OTLP gRPC──► ZeroBus endpoint ──► Delta Lake
```

**Databricks workspace:** set via `DATABRICKS_WORKSPACE_HOST` — this POC ran on an
East US workspace. All workspace IDs, service principal IDs and Azure resource
identifiers in this project are placeholders; fill in your own.

**Target tables:**
- `signaltogrowth_zerobus.bronze.copilot_otel_spans`
- `signaltogrowth_zerobus.bronze.copilot_otel_logs`
- `signaltogrowth_zerobus.bronze.copilot_otel_metrics`

---

## Step 1 — Create Databricks tables

Run `databricks/setup.sql` in your Databricks SQL Editor.
(Reuses the existing `signaltogrowth_zerobus` catalog and service principal from ai-todo-app.)

---

## Step 2 — Path A: Direct to ZeroBus

ZeroBus only supports OTLP gRPC. Auth headers can't go in VS Code settings.json —
they must be env vars. The token script handles this.

```bash
export DATABRICKS_CLIENT_ID="<your-service-principal-client-id>"
export DATABRICKS_CLIENT_SECRET="<your-secret>"
export DATABRICKS_WORKSPACE_ID="<your-workspace-id>"
export DATABRICKS_WORKSPACE_HOST="adb-<workspace-id>.<shard>.azuredatabricks.net"
source scripts/get-token.sh
# tokens are now in OTEL_EXPORTER_OTLP_* env vars — valid for ~1 hour

code .   # launch VS Code from this terminal so it inherits the env vars
```

In VS Code Settings (JSON), add the contents of `vscode/settings-path-a-direct.json`.

Use Copilot normally. After ~5 seconds, check:
```sql
SELECT time, name, service_name, attributes
FROM signaltogrowth_zerobus.bronze.copilot_otel_spans
ORDER BY time DESC
LIMIT 20;
```

---

## Step 3 — Path B: Via K8s OTel Collector

The collector handles OAuth token refresh automatically — no manual token generation needed.

```bash
export DATABRICKS_CLIENT_ID="<your-service-principal-client-id>"
export DATABRICKS_CLIENT_SECRET="<your-secret>"
bash scripts/deploy.sh
# prints the collector's external IP when ready
```

Update `otlpEndpoint` in `vscode/settings-path-b-collector.json` with the external IP,
then copy its contents into VS Code Settings (JSON).

Use Copilot normally. Same query as above to verify data lands.

---

## What's different between Path A and Path B?

| | Path A (direct) | Path B (collector) |
|---|---|---|
| Hops | 0 | 1 (collector) |
| Token management | Manual (1hr expiry) | Auto-refresh via OAuth2 extension |
| Batching | VS Code default | Configurable (currently 5s / 50 spans) |
| Enrichment | None | Can add resource attributes in collector |
| Infra | None | AKS pod |

---

## Troubleshooting

**No data in spans table after using Copilot:**
- Path A: check that VS Code was launched from the terminal after `source scripts/get-token.sh`
- Path A: tokens expire after 1 hour — re-source and relaunch VS Code
- Path B: check collector logs: `kubectl logs -n copilot-otel -l app=otel-collector`
- Verify `github.copilot.chat.otel.enabled` is `true` in VS Code settings

**Error 4024 from ZeroBus:**
Tables must have `abfss://` storage locations. Re-run `setup.sql` to recreate them properly.

**Collector pod crashlooping:**
Check secret exists: `kubectl get secret zerobus-creds -n copilot-otel`
