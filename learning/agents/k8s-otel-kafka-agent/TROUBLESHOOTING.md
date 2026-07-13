# Troubleshooting Guide

Common issues and solutions for the K8s + OTLP + Kafka learning project.

## Table of Contents
- [AKS / Kubernetes Issues](#aks--kubernetes-issues)
- [OTLP Collector Issues](#otlp-collector-issues)
- [Agent Issues](#agent-issues)
- [Event Hubs / Kafka Issues](#event-hubs--kafka-issues)
- [Databricks Issues](#databricks-issues)
- [Cost Management](#cost-management)

---

## AKS / Kubernetes Issues

### "az command not found"

**Problem:** Azure CLI not installed.

**Solution:**
```bash
# macOS
brew install azure-cli

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### "kubectl command not found"

**Problem:** kubectl not installed.

**Solution:**
```bash
# macOS
brew install kubectl

# Linux
az aks install-cli
```

### "Error: This account has no subscriptions"

**Problem:** Not logged into Azure CLI.

**Solution:**
```bash
az login
az account list
az account set --subscription "Your Subscription Name"
```

### "LoadBalancer IP pending forever"

**Problem:** Azure LoadBalancer not provisioning.

**Check:**
```bash
kubectl get svc agent-service -o yaml
kubectl describe svc agent-service
```

**Solution:**
- Wait 3-5 minutes (Azure can be slow)
- Check quota limits in Azure portal
- Verify AKS cluster has network access to provision public IPs

### "Pods stuck in Pending"

**Check:**
```bash
kubectl get pods
kubectl describe pod <pod-name>
```

**Common causes:**
- Insufficient resources: Check node capacity
- Image pull errors: Check ACR authentication
- ConfigMap/Secret missing: Verify dependencies

**Solution:**
```bash
# Check nodes
kubectl get nodes
kubectl describe node <node-name>

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

### "ImagePullBackOff" error

**Problem:** AKS can't pull image from ACR.

**Solution:**
```bash
# Verify ACR attachment
az aks show -n aks-learning -g rg-k8s-learning --query "servicePrincipalProfile"

# Reattach ACR
az aks update -n aks-learning -g rg-k8s-learning --attach-acr <acr-name>

# Manual authentication (dev only)
az acr login --name <acr-name>
```

---

## OTLP Collector Issues

### "Connection refused" from agent to collector

**Problem:** Agent can't connect to collector at `otel-collector:4317`.

**Check:**
```bash
# Verify collector is running
kubectl get pods -l app=otel-collector
kubectl logs -l app=otel-collector

# Verify service exists
kubectl get svc otel-collector
```

**Solution:**
```bash
# Restart collector
kubectl rollout restart deployment/otel-collector

# Check DNS from agent pod
kubectl exec -it <agent-pod-name> -- nslookup otel-collector
```

### "No traces in collector logs"

**Problem:** Collector not receiving traces from agent.

**Check:**
```bash
kubectl logs -l app=otel-collector --tail=100 | grep -i span
```

**Solution:**
- Verify agent has correct `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable
- Check agent logs for connection errors
- Verify collector ConfigMap has OTLP receiver enabled on port 4317

### "Context deadline exceeded" in collector

**Problem:** Kafka exporter timing out.

**Check:**
```bash
kubectl logs -l app=otel-collector | grep -i "deadline\|timeout"
```

**Solution:**
- Verify Event Hubs connection string is correct in secret
- Check network connectivity from AKS to Event Hubs
- Verify Event Hubs namespace is not paused
- Check Event Hubs firewall rules (should allow Azure services)

---

## Agent Issues

### "OPENAI_API_KEY environment variable is required"

**Problem:** OpenAI secret not created or mounted incorrectly.

**Solution:**
```bash
# Create secret
kubectl create secret generic openai-key \
  --from-literal=OPENAI_API_KEY='sk-proj-...'

# Verify secret exists
kubectl get secret openai-key

# Check pod environment
kubectl exec -it <agent-pod-name> -- env | grep OPENAI
```

### "Agent returns 500 error"

**Check logs:**
```bash
kubectl logs -l app=agent --tail=50
```

**Common causes:**
- OpenAI API key invalid or expired
- OpenAI rate limit exceeded
- OTLP endpoint unreachable (non-fatal, but logged)

**Solution:**
- Regenerate OpenAI API key and update secret
- Add retry logic with exponential backoff
- Ignore OTLP warnings if collector isn't critical

### "Health endpoint returns 200 but /process fails"

**Problem:** Agent running but LLM calls failing.

**Check:**
```bash
curl -v -X POST http://<agent-ip>/process \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "user_id": "test"}'
```

**Solution:**
- Check OpenAI API key balance: https://platform.openai.com/usage
- Verify network access to api.openai.com
- Check for rate limiting (429 errors in logs)

---

## Event Hubs / Kafka Issues

### "Connection refused" to Event Hubs

**Problem:** OTLP Collector can't connect to Event Hubs.

**Check:**
```bash
# Verify Event Hubs exists
az eventhubs namespace show -n <namespace> -g rg-k8s-learning

# Check connection string format
kubectl get secret eventhub-conn -o jsonpath='{.data.connection-string}' | base64 -d
```

**Solution:**
- Verify connection string starts with `Endpoint=sb://`
- Check Event Hubs namespace status (should be Active)
- Verify firewall rules allow Azure services
- Use port 9093 for Kafka protocol (not 9092)

### "SASL authentication failed"

**Problem:** Invalid Event Hubs connection string.

**Solution:**
- Regenerate connection string from Azure portal
- Update Kubernetes secret:
  ```bash
  kubectl delete secret eventhub-conn
  kubectl create secret generic eventhub-conn \
    --from-literal=connection-string="Endpoint=sb://..."
  ```
- Restart collector: `kubectl rollout restart deployment/otel-collector`

### "No data in Event Hubs"

**Check:**
```bash
# View Event Hubs metrics in Azure portal
# Or check with Azure CLI
az eventhubs eventhub show \
  -n agent-traces \
  --namespace-name <namespace> \
  -g rg-k8s-learning \
  --query "{incoming:incomingMessages,outgoing:outgoingMessages}"
```

**Solution:**
- Verify collector has Kafka exporter configured
- Check collector logs for export errors
- Send test trace and watch collector logs in real-time:
  ```bash
  kubectl logs -f -l app=otel-collector
  ```

---

## Databricks Issues

### "Cannot connect to SQL endpoint"

**Problem:** Databricks SQL Warehouse not running or connection details incorrect.

**Solution:**
- Go to Databricks → SQL Warehouses
- Start your warehouse if stopped
- Verify connection details in notebook:
  - `EVENTHUB_NAMESPACE`
  - `CONNECTION_STRING`

### "Event Hubs connection timeout"

**Problem:** Databricks can't reach Event Hubs.

**Solution:**
- Verify Event Hubs firewall allows Databricks workspace IP
- Or set firewall to "Allow from all networks" (dev only)
- Check connection string format and credentials

### "Schema not found: main.observability"

**Problem:** Target schema doesn't exist.

**Solution:**
```sql
CREATE SCHEMA IF NOT EXISTS main.observability;
```

### "No data appearing in Delta table"

**Check:**
```sql
-- Check if streaming query is running
SELECT * FROM system.streaming.queries WHERE name LIKE '%agent_traces%';

-- Check checkpoint path
LIST '/mnt/checkpoints/agent_traces_k8s';

-- Check for errors in stream
DESCRIBE HISTORY main.observability.agent_traces_k8s;
```

**Solution:**
- Verify Event Hubs has incoming messages
- Check notebook cell output for streaming errors
- Restart streaming query (stop and rerun cells)
- Check OTLP JSON schema matches parsing logic

### "JSON parsing errors"

**Problem:** OTLP JSON structure doesn't match expected schema.

**Solution:**
- Check collector logs for actual JSON structure
- Update `from_json` schema in notebook to match
- Use `df.printSchema()` to debug parsed structure
- Enable `option("mergeSchema", "true")` for schema evolution

---

## Cost Management

### "My Azure bill is higher than expected"

**Problem:** Resources running 24/7.

**Costs per hour (Standard_B2s nodes):**
- AKS nodes: ~$0.0412/hour per node
- Public IPs: ~$0.004/hour each
- Event Hubs: ~$0.015/hour (Standard tier)

**Solution:**
```bash
# Stop AKS cluster (IMPORTANT!)
az aks stop -n aks-learning -g rg-k8s-learning

# Start when needed
az aks start -n aks-learning -g rg-k8s-learning

# Or delete everything
cd scripts
./cleanup_aks.sh
```

### "I forgot to clean up"

**Quick cleanup:**
```bash
# Delete entire resource group (nuclear option)
az group delete -n rg-k8s-learning --yes --no-wait

# Verify deletion
az group list --query "[?name=='rg-k8s-learning']"
```

---

## Debugging Commands

### Quick status check
```bash
# Cluster health
kubectl get nodes
kubectl get pods --all-namespaces

# Services and IPs
kubectl get svc

# Recent events
kubectl get events --sort-by=.metadata.creationTimestamp --all-namespaces

# Resource usage
kubectl top nodes
kubectl top pods
```

### Collector debugging
```bash
# Live logs
kubectl logs -f -l app=otel-collector

# Recent errors
kubectl logs -l app=otel-collector --tail=100 | grep -i error

# Exec into collector (for testing)
kubectl exec -it <collector-pod> -- /bin/sh
```

### Agent debugging
```bash
# Live logs
kubectl logs -f -l app=agent

# Check environment
kubectl exec -it <agent-pod> -- env

# Test from inside pod
kubectl exec -it <agent-pod> -- wget -O- http://localhost:8080/health
```

### Network debugging
```bash
# DNS from pod
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup otel-collector

# Port connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- telnet otel-collector 4317
```

---

## Getting Help

If you're stuck:
1. Check this guide first
2. Review logs: `kubectl logs <pod-name>`
3. Check events: `kubectl describe <resource> <name>`
4. Search Azure docs: https://learn.microsoft.com/azure/
5. OpenTelemetry docs: https://opentelemetry.io/docs/

## Learning Resources

- **Kubernetes**: https://kubernetes.io/docs/tutorials/
- **OTLP**: https://opentelemetry.io/docs/specs/otlp/
- **Event Hubs Kafka**: https://learn.microsoft.com/azure/event-hubs/event-hubs-for-kafka-ecosystem-overview
- **Databricks Streaming**: https://docs.databricks.com/structured-streaming/
