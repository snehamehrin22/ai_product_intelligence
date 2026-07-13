#!/bin/bash
set -e

echo "========================================="
echo "Complete Deployment Pipeline (US-8)"
echo "========================================="
echo ""
echo "This script will deploy the entire stack:"
echo "  1. AKS cluster + ACR"
echo "  2. OTLP Collector"
echo "  3. Agent service"
echo "  4. Azure Event Hubs"
echo "  5. OTLP Collector with Kafka exporter"
echo ""
echo "Estimated time: 25-30 minutes"
echo "Estimated cost: ~$2.78/day (don't forget cleanup!)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Step 1: Setup AKS and ACR
echo ""
echo "========================================="
echo "Step 1: AKS + ACR Setup"
echo "========================================="
./setup_aks.sh

# Step 2: Deploy OTLP Collector (initial version without Kafka)
echo ""
echo "========================================="
echo "Step 2: Deploy OTLP Collector"
echo "========================================="
cd ../k8s
kubectl apply -f otel-collector-configmap.yaml
kubectl apply -f otel-collector-deployment.yaml
kubectl apply -f otel-collector-service.yaml

echo ""
echo "Waiting for collector to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/otel-collector

# Step 3: Deploy Agent
echo ""
echo "========================================="
echo "Step 3: Deploy Agent"
echo "========================================="
echo ""
echo "Creating OpenAI API key secret..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable not set"
    echo "Run: export OPENAI_API_KEY='sk-proj-...'"
    exit 1
fi

kubectl create secret generic openai-key \
    --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "Deploying agent..."
kubectl apply -f agent-deployment.yaml
kubectl apply -f agent-service.yaml

echo ""
echo "Waiting for agent to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/agent

echo ""
echo "Waiting for LoadBalancer IP (this may take 2-3 minutes)..."
kubectl wait --for=jsonpath='{.status.loadBalancer.ingress[0].ip}' --timeout=300s service/agent-service

# Step 4: Test initial deployment
echo ""
echo "========================================="
echo "Step 4: Initial Testing"
echo "========================================="
AGENT_IP=$(kubectl get svc agent-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo ""
echo "Agent service IP: $AGENT_IP"
echo ""
echo "Testing health endpoint..."
curl -s http://$AGENT_IP/health | jq .

echo ""
echo "Testing agent processing..."
curl -s -X POST "http://$AGENT_IP/process" \
    -H "Content-Type: application/json" \
    -d '{"message": "Test deployment", "user_id": "deploy-test"}' | jq .

# Step 5: Setup Event Hubs
echo ""
echo "========================================="
echo "Step 5: Azure Event Hubs Setup"
echo "========================================="
cd ../scripts
./setup_eventhub.sh

# Step 6: Upgrade OTLP Collector with Kafka exporter
echo ""
echo "========================================="
echo "Step 6: Enable Kafka Exporter"
echo "========================================="
echo ""
echo "Updating OTLP Collector configuration..."

# Get Event Hubs details from secret
EVENTHUB_CONN=$(kubectl get secret eventhub-conn -o jsonpath='{.data.connection-string}' | base64 -d)
EVENTHUB_NAMESPACE=$(echo $EVENTHUB_CONN | sed -n 's/.*Endpoint=sb:\/\/\([^.]*\).*/\1/p')

if [ -z "$EVENTHUB_NAMESPACE" ]; then
    echo "❌ Could not extract Event Hubs namespace from secret"
    exit 1
fi

echo "Event Hubs namespace: $EVENTHUB_NAMESPACE"

# Update collector ConfigMap with Kafka exporter
cd ../k8s
cp otel-collector-configmap-with-kafka.yaml otel-collector-configmap-kafka-applied.yaml
sed -i.bak "s/\${EVENTHUB_BROKER}/$EVENTHUB_NAMESPACE.servicebus.windows.net:9093/g" otel-collector-configmap-kafka-applied.yaml
rm otel-collector-configmap-kafka-applied.yaml.bak

kubectl apply -f otel-collector-configmap-kafka-applied.yaml

# Update collector deployment to inject Event Hubs connection string
kubectl patch deployment otel-collector --patch '
spec:
  template:
    spec:
      containers:
      - name: otel-collector
        env:
        - name: EVENTHUB_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: eventhub-conn
              key: connection-string
'

echo ""
echo "Restarting collector with Kafka exporter..."
kubectl rollout restart deployment/otel-collector
kubectl rollout status deployment/otel-collector

# Step 7: Send test traces
echo ""
echo "========================================="
echo "Step 7: Generating Test Traces"
echo "========================================="
echo ""
echo "Sending 5 test requests to generate traces..."

for i in {1..5}; do
    echo "Request $i/5..."
    curl -s -X POST "http://$AGENT_IP/process" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"Test trace $i\", \"user_id\": \"e2e-test-$i\"}" > /dev/null
    sleep 2
done

echo "✅ Test traces sent"
echo ""

# Summary
echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "Agent endpoint: http://$AGENT_IP"
echo "Event Hubs namespace: $EVENTHUB_NAMESPACE"
echo ""
echo "Next steps:"
echo ""
echo "1. Configure Databricks notebook:"
echo "   - Open: databricks/ingest_traces_from_kafka.py"
echo "   - Set EVENTHUB_NAMESPACE = \"$EVENTHUB_NAMESPACE\""
echo "   - Get connection string: kubectl get secret eventhub-conn -o jsonpath='{.data.connection-string}' | base64 -d"
echo "   - Run all cells to start streaming ingestion"
echo ""
echo "2. Run validation:"
echo "   cd scripts"
echo "   ./validate_e2e.sh"
echo ""
echo "3. Check traces in Databricks:"
echo "   SELECT * FROM main.observability.agent_traces_k8s ORDER BY start_time DESC LIMIT 10"
echo ""
echo "⚠️  Don't forget to run cleanup_aks.sh when done!"
echo ""

# Save deployment info
cat > ../DEPLOYMENT_INFO.txt <<EOF
Deployment completed: $(date)

Agent Service IP: $AGENT_IP
Event Hubs Namespace: $EVENTHUB_NAMESPACE
Resource Group: rg-k8s-learning

Endpoints:
  Health: http://$AGENT_IP/health
  Process: http://$AGENT_IP/process

Kubernetes:
  kubectl get pods
  kubectl logs -l app=otel-collector
  kubectl logs -l app=agent

Event Hubs:
  Broker: $EVENTHUB_NAMESPACE.servicebus.windows.net:9093
  Topic: agent-traces

Databricks:
  Catalog: main
  Schema: observability
  Table: agent_traces_k8s

Cleanup:
  cd scripts
  ./cleanup_aks.sh
EOF

echo "Deployment info saved to: DEPLOYMENT_INFO.txt"
