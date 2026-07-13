#!/bin/bash
set -e

echo "========================================="
echo "Azure Event Hubs Setup (US-6)"
echo "========================================="
echo ""

# Variables
RESOURCE_GROUP="rg-k8s-learning"
NAMESPACE_NAME="eh-k8s-learning-$RANDOM"
EVENTHUB_NAME="agent-traces"
LOCATION="eastus"

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Namespace: $NAMESPACE_NAME"
echo "  Event Hub: $EVENTHUB_NAME"
echo "  Location: $LOCATION"
echo ""

# Step 1: Create Event Hubs namespace
echo "[1/4] Creating Event Hubs namespace..."
az eventhubs namespace create \
  --name $NAMESPACE_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard \
  --output table

# Step 2: Create Event Hub (topic)
echo ""
echo "[2/4] Creating Event Hub (topic): $EVENTHUB_NAME..."
az eventhubs eventhub create \
  --name $EVENTHUB_NAME \
  --namespace-name $NAMESPACE_NAME \
  --resource-group $RESOURCE_GROUP \
  --partition-count 2 \
  --output table

# Step 3: Get connection string
echo ""
echo "[3/4] Getting connection string..."
CONNECTION_STRING=$(az eventhubs namespace authorization-rule keys list \
  --resource-group $RESOURCE_GROUP \
  --namespace-name $NAMESPACE_NAME \
  --name RootManageSharedAccessKey \
  --query primaryConnectionString \
  --output tsv)

BROKER_ENDPOINT="${NAMESPACE_NAME}.servicebus.windows.net:9093"

echo ""
echo "========================================="
echo "✅ Event Hubs Setup Complete!"
echo "========================================="
echo ""
echo "Configuration for OTLP Collector:"
echo ""
echo "  Broker: $BROKER_ENDPOINT"
echo "  Topic: $EVENTHUB_NAME"
echo ""
echo "Connection String (save this securely):"
echo "$CONNECTION_STRING"
echo ""

# Step 4: Create Kubernetes secret
echo "[4/4] Creating Kubernetes secret for Event Hubs..."
kubectl create secret generic eventhub-conn \
  --from-literal=connection-string="$CONNECTION_STRING" \
  --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "✅ Kubernetes secret 'eventhub-conn' created!"
echo ""
echo "Next steps:"
echo "  1. Update otel-collector-configmap.yaml with Kafka exporter"
echo "  2. Redeploy collector: kubectl apply -f k8s/otel-collector-configmap.yaml"
echo "  3. Restart collector: kubectl rollout restart deployment/otel-collector"
echo ""
echo "Save these values:"
echo "  NAMESPACE: $NAMESPACE_NAME"
echo "  BROKER: $BROKER_ENDPOINT"
echo "  TOPIC: $EVENTHUB_NAME"
