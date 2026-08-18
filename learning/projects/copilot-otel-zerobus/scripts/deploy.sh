#!/usr/bin/env bash
# Deploys the OTel Collector to your AKS cluster (Path B).
# Run from the project root: bash scripts/deploy.sh
#
# Prerequisites:
#   - kubectl configured for your AKS cluster
#   - DATABRICKS_CLIENT_ID and DATABRICKS_CLIENT_SECRET env vars set
#   - workspace host / ID filled into k8s/otel-collector-deployment.yaml

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

: "${DATABRICKS_CLIENT_ID:?Set DATABRICKS_CLIENT_ID (service principal application ID)}"
: "${DATABRICKS_CLIENT_SECRET:?Set DATABRICKS_CLIENT_SECRET}"

echo "==> Creating namespace..."
kubectl apply -f "${PROJECT_ROOT}/k8s/namespace.yaml"

echo "==> Creating ZeroBus credentials secret..."
kubectl create secret generic zerobus-creds \
  --namespace copilot-otel \
  --from-literal=client-id="${DATABRICKS_CLIENT_ID}" \
  --from-literal=client-secret="${DATABRICKS_CLIENT_SECRET}" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Applying collector config..."
kubectl apply -f "${PROJECT_ROOT}/k8s/otel-collector-configmap.yaml"

echo "==> Deploying collector..."
kubectl apply -f "${PROJECT_ROOT}/k8s/otel-collector-deployment.yaml"

echo "==> Exposing collector service..."
kubectl apply -f "${PROJECT_ROOT}/k8s/otel-collector-service.yaml"

echo ""
echo "==> Waiting for external IP (may take 1-2 minutes on AKS)..."
kubectl get svc otel-collector -n copilot-otel --watch &
WATCH_PID=$!
sleep 60
kill $WATCH_PID 2>/dev/null || true

echo ""
echo "==> Collector external IP:"
kubectl get svc otel-collector -n copilot-otel -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
echo ""
echo ""
echo "Update vscode/settings-path-b-collector.json with the IP above,"
echo "then copy its contents into VS Code Settings (JSON)."
