#!/usr/bin/env bash
# Generates short-lived OAuth tokens for Path A (direct VS Code → ZeroBus).
# Tokens expire after 1 hour. Re-run this script and restart VS Code to refresh.
#
# Usage:
#   export DATABRICKS_CLIENT_ID="<your-service-principal-client-id>"
#   export DATABRICKS_CLIENT_SECRET="<your-secret>"
#   export DATABRICKS_WORKSPACE_ID="<your-workspace-id>"
#   export DATABRICKS_WORKSPACE_HOST="adb-<workspace-id>.<shard>.azuredatabricks.net"
#   source scripts/get-token.sh
#
# After sourcing, your shell will have OTEL_EXPORTER_OTLP_* vars set.
# Launch VS Code from this same terminal: `code .`

set -euo pipefail

WORKSPACE_ID="${DATABRICKS_WORKSPACE_ID:-}"
WORKSPACE_URL="${DATABRICKS_WORKSPACE_HOST:-}"
REGION="${DATABRICKS_REGION:-eastus}"
CATALOG="signaltogrowth_zerobus"
SCHEMA="bronze"
TABLE_PREFIX="copilot"

TOKEN_URL="https://${WORKSPACE_URL}/oidc/v1/token"
ZEROBUS_ENDPOINT="https://${WORKSPACE_ID}.zerobus.${REGION}.azuredatabricks.net:443"

if [[ -z "${DATABRICKS_CLIENT_ID:-}" || -z "${DATABRICKS_CLIENT_SECRET:-}" ]]; then
  echo "ERROR: Set DATABRICKS_CLIENT_ID and DATABRICKS_CLIENT_SECRET first."
  return 1 2>/dev/null || exit 1
fi

if [[ -z "$WORKSPACE_ID" || -z "$WORKSPACE_URL" ]]; then
  echo "ERROR: Set DATABRICKS_WORKSPACE_ID and DATABRICKS_WORKSPACE_HOST first."
  echo "  e.g. DATABRICKS_WORKSPACE_HOST=adb-1234567890123456.7.azuredatabricks.net"
  return 1 2>/dev/null || exit 1
fi

get_token() {
  local table_name="$1"
  local auth_details
  auth_details=$(cat <<EOF
[{
  "type": "unity_catalog_privileges",
  "privileges": ["USE CATALOG"],
  "object_type": "CATALOG",
  "object_full_path": "${CATALOG}"
},
{
  "type": "unity_catalog_privileges",
  "privileges": ["USE SCHEMA"],
  "object_type": "SCHEMA",
  "object_full_path": "${CATALOG}.${SCHEMA}"
},
{
  "type": "unity_catalog_privileges",
  "privileges": ["SELECT", "MODIFY"],
  "object_type": "TABLE",
  "object_full_path": "${CATALOG}.${SCHEMA}.${table_name}"
}]
EOF
)
  curl -s -X POST \
    -u "${DATABRICKS_CLIENT_ID}:${DATABRICKS_CLIENT_SECRET}" \
    -d "grant_type=client_credentials" \
    -d "scope=all-apis" \
    -d "resource=api://databricks/workspaces/${WORKSPACE_ID}/zerobusDirectWriteApi" \
    --data-urlencode "authorization_details=${auth_details}" \
    "${TOKEN_URL}" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4
}

echo "Generating tokens (this takes a few seconds)..."
TOKEN_SPANS=$(get_token "${TABLE_PREFIX}_otel_spans")
TOKEN_LOGS=$(get_token "${TABLE_PREFIX}_otel_logs")
TOKEN_METRICS=$(get_token "${TABLE_PREFIX}_otel_metrics")

if [[ -z "$TOKEN_SPANS" || -z "$TOKEN_LOGS" || -z "$TOKEN_METRICS" ]]; then
  echo "ERROR: Failed to get one or more tokens. Check your credentials."
  return 1 2>/dev/null || exit 1
fi

# Export OTel env vars — launch VS Code from this terminal after sourcing
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="${ZEROBUS_ENDPOINT}"
export OTEL_EXPORTER_OTLP_LOGS_ENDPOINT="${ZEROBUS_ENDPOINT}"
export OTEL_EXPORTER_OTLP_METRICS_ENDPOINT="${ZEROBUS_ENDPOINT}"
export OTEL_EXPORTER_OTLP_TRACES_HEADERS="authorization=Bearer ${TOKEN_SPANS},x-databricks-zerobus-table-name=${CATALOG}.${SCHEMA}.${TABLE_PREFIX}_otel_spans"
export OTEL_EXPORTER_OTLP_LOGS_HEADERS="authorization=Bearer ${TOKEN_LOGS},x-databricks-zerobus-table-name=${CATALOG}.${SCHEMA}.${TABLE_PREFIX}_otel_logs"
export OTEL_EXPORTER_OTLP_METRICS_HEADERS="authorization=Bearer ${TOKEN_METRICS},x-databricks-zerobus-table-name=${CATALOG}.${SCHEMA}.${TABLE_PREFIX}_otel_metrics"

echo ""
echo "✅ Tokens generated. Env vars set."
echo "   Tokens expire in ~1 hour."
echo ""
echo "Now launch VS Code from this terminal:"
echo "   code ."
echo ""
echo "VS Code settings (vscode/settings-path-a-direct.json) point to:"
echo "   ${ZEROBUS_ENDPOINT}"
