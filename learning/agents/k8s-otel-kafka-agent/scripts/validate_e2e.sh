#!/bin/bash
set -e

echo "========================================="
echo "End-to-End Validation (US-8)"
echo "========================================="
echo ""

# Get agent service external IP
echo "[1/5] Getting agent service external IP..."
AGENT_IP=$(kubectl get svc agent-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$AGENT_IP" ]; then
    echo "❌ Agent service IP not found. Is the LoadBalancer ready?"
    echo "Check: kubectl get svc agent-service"
    exit 1
fi

echo "✅ Agent IP: $AGENT_IP"
echo ""

# Test health endpoint
echo "[2/5] Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://$AGENT_IP/health)

if [ "$HEALTH_RESPONSE" -ne 200 ]; then
    echo "❌ Health check failed. HTTP status: $HEALTH_RESPONSE"
    exit 1
fi

echo "✅ Health check passed"
echo ""

# Send test agent request
echo "[3/5] Sending test agent request..."
TEST_MESSAGE="Remind me to buy milk tomorrow"
echo "Test message: \"$TEST_MESSAGE\""
echo ""

AGENT_RESPONSE=$(curl -s -X POST "http://$AGENT_IP/process" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"$TEST_MESSAGE\", \"user_id\": \"test-user-001\"}" | jq .)

echo "Agent response:"
echo "$AGENT_RESPONSE"
echo ""

# Check OTLP Collector logs
echo "[4/5] Checking OTLP Collector logs for traces..."
echo ""

kubectl logs -l app=otel-collector --tail=50 | grep -E "(Span|trace_id|span_id)" || echo "No trace logs found yet (may take a few seconds)"
echo ""

# Instructions for Databricks validation
echo "[5/5] Databricks Validation"
echo "========================================="
echo ""
echo "To verify traces reached Delta Lake:"
echo ""
echo "1. Open the Databricks notebook: databricks/ingest_traces_from_kafka.py"
echo "2. Configure Event Hubs connection details from setup_eventhub.sh output"
echo "3. Run all cells to start streaming ingestion"
echo "4. Wait 30-60 seconds for initial batch"
echo "5. Run the query cell to check for traces:"
echo ""
echo "   SELECT"
echo "     trace_id,"
echo "     span_name,"
echo "     gen_ai_model,"
echo "     gen_ai_total_tokens,"
echo "     duration_ms,"
echo "     start_time,"
echo "     session_id"
echo "   FROM main.observability.agent_traces_k8s"
echo "   ORDER BY start_time DESC"
echo "   LIMIT 10"
echo ""
echo "Expected: 2 spans (agent.process_message, agent.extract_task)"
echo ""
echo "========================================="
echo "✅ Local validation complete!"
echo ""
echo "Next steps:"
echo "  1. Verify traces in Databricks (see above)"
echo "  2. Send more test requests to generate data"
echo "  3. Query traces by session_id for correlation"
echo ""
echo "Test commands:"
echo "  curl -X POST http://$AGENT_IP/process \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"message\": \"Schedule meeting for next week\", \"user_id\": \"test-user-002\"}'"
echo ""
