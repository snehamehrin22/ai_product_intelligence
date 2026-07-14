# K8s + OpenTelemetry + Kafka Deployment Walkthrough

**Date:** July 13, 2026
**Purpose:** Step-by-step record of deploying the complete observability pipeline to Azure

---

## Overview

This document captures the actual deployment process, including all problems encountered and solutions applied. This is a learning resource showing the real-world deployment experience.

**Architecture:**
```
Agent (AKS) → OTLP Collector (AKS) → Event Hubs (Kafka) → Databricks → Delta Lake
```

**Resources Created:**
- Resource Group: `rg-k8s-learning`
- Azure Container Registry: `acr8409.azurecr.io`
- AKS Cluster: `aks-learning` (2 nodes, Standard_D2s_v7)
- Location: `eastus`

---

## Phase 1: Prerequisites Installation

### Step 1.1: Install Azure CLI

**Why:** Azure CLI is needed to manage all Azure resources from the command line.

```bash
brew install azure-cli
```

**Result:** Installed version 2.88.0 with Python 3.14 dependencies (~320MB download)

**Verification:**
```bash
az --version
```

### Step 1.2: Install kubectl

**Why:** kubectl is the Kubernetes CLI for managing AKS clusters.

```bash
brew install kubectl
```

**Result:** Installed version 1.36.2

**Verification:**
```bash
kubectl version --client
```

### Step 1.3: Install Docker Desktop

**Why:** Needed to build Docker images locally (workaround for ACR Tasks limitation).

1. Downloaded Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Installed and started the application
3. Waited for Docker daemon to fully start (whale icon shows "Docker Desktop is running")

**Docker location:** `/Applications/Docker.app/Contents/Resources/bin/docker`

**Verification:**
```bash
/Applications/Docker.app/Contents/Resources/bin/docker --version
# Or add to PATH first:
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
docker --version
```

---

## Phase 2: Azure Authentication

### Step 2.1: Azure Login with Device Code

**Why:** Need to authenticate with Azure to create and manage resources.

```bash
az login --use-device-code
```

**Process:**
1. Command displays a device code (e.g., `BZB9YS8JP`)
2. Opens browser to https://microsoft.com/devicelogin
3. Enter the device code
4. Sign in with Azure account credentials
5. Return to terminal - login completes automatically

**Result:** Successfully logged into subscription:
- Subscription Name: "Azure subscription 1"
- Subscription ID: `84e5732e-6218-4d5d-97a8-adf4ad14e6d8`
- Account: mehrinsneha2291@gmail.com

**Note:** One tenant was blocked due to inactivity, but authentication succeeded with the active tenant.

---

## Phase 3: Azure Resource Provider Registration

### Step 3.1: Register Required Providers

**Why:** New Azure subscriptions don't have all resource providers enabled by default. These must be registered before creating resources.

**Problem Encountered:**
```
ERROR: (MissingSubscriptionRegistration) The subscription is not registered
to use namespace 'Microsoft.ContainerRegistry'
```

**Solution:** Register the required providers:

```bash
# Register ACR provider
az provider register --namespace Microsoft.ContainerRegistry --wait

# Register AKS provider
az provider register --namespace Microsoft.ContainerService --wait

# Register Event Hubs provider
az provider register --namespace Microsoft.EventHub --wait
```

**Verification:**
```bash
az provider show -n Microsoft.ContainerRegistry --query "registrationState"
az provider show -n Microsoft.ContainerService --query "registrationState"
az provider show -n Microsoft.EventHub --query "registrationState"
# All should return: "Registered"
```

**Time:** ~2-3 minutes for all three providers

---

## Phase 4: Resource Group and Container Registry

### Step 4.1: Create Resource Group

**Why:** Resource groups organize all Azure resources and share a lifecycle.

```bash
az group create \
  --name rg-k8s-learning \
  --location eastus
```

**Result:** Resource group created successfully

### Step 4.2: Create Azure Container Registry (ACR)

**Why:** ACR stores Docker images that AKS will pull from.

```bash
az acr create \
  --resource-group rg-k8s-learning \
  --name acr8409 \
  --sku Basic \
  --location eastus
```

**Result:**
- Registry Name: `acr8409`
- Login Server: `acr8409.azurecr.io`
- SKU: Basic

**Note:** ACR names must be globally unique, lowercase alphanumeric only.

---

## Phase 5: Docker Image Build (Local Workaround)

### Step 5.1: ACR Tasks Limitation Discovered

**Original Plan:** Use `az acr build` to build image in Azure cloud

**Problem Encountered:**
```
ERROR: (TasksOperationsNotAllowed) ACR Tasks requests for the registry acr8409
and subscription 84e5732e-6218-4d5d-97a8-adf4ad14e6d8 are not permitted.
```

**Root Cause:** Azure subscription has ACR Tasks feature disabled (common with free/trial/new accounts)

**Workaround:** Build Docker image locally with Docker Desktop and push to ACR

### Step 5.2: Build Agent Image Locally

**Prerequisites:**
- Docker Desktop running
- Docker CLI available in PATH

```bash
# Navigate to agent-service directory
cd /path/to/agent-service

# Add Docker to PATH for this session
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"

# Build image with ACR tag
docker build -t acr8409.azurecr.io/agent:v1 .
```

**Build Process:**
1. Multi-stage build: builder stage installs dependencies
2. Runtime stage copies installed packages
3. Final image size optimized (minimal runtime dependencies)

**Time:** ~15 seconds (with local Docker cache)

**Result:** Image built successfully with ID `sha256:52b2662c...`

### Step 5.3: Login to ACR

**Why:** Need to authenticate Docker with ACR before pushing images.

```bash
az acr login --name acr8409
```

**Result:** `Login Succeeded`

**What this does:** Configures Docker credentials for `acr8409.azurecr.io`

### Step 5.4: Push Image to ACR

```bash
docker push acr8409.azurecr.io/agent:v1
```

**Result:**
- Image digest: `sha256:ea44b5a92384eba8c30c6cdd1d9e56349a737b8f71dbc12705936481baae2b65`
- Size: 1785 bytes (manifest)

**Verification:**
```bash
az acr repository list --name acr8409 --output table
az acr repository show-tags --name acr8409 --repository agent --output table
```

---

## Phase 6: AKS Cluster Creation

### Step 6.1: VM Size Quota Issue

**Original Plan:** Use `Standard_B2s` (cheapest, ~$30/month)

**Problem Encountered:**
```
ERROR: (BadRequest) The VM size of Standard_B2s is not allowed in your
subscription in location 'eastus'.
```

**Root Cause:** Subscription doesn't have quota/access to B-series VMs in eastus region

**Available Alternatives:** Subscription only allows D-series, E-series, F-series, and specialized VMs

**Solution:** Use `Standard_D2s_v7` (smallest available D-series)
- 2 vCPUs, 8 GB RAM
- More expensive than B2s but available in subscription
- Sufficient for learning/development

### Step 6.2: Create AKS Cluster

**Command:**
```bash
az aks create \
  --resource-group rg-k8s-learning \
  --name aks-learning \
  --node-count 2 \
  --node-vm-size Standard_D2s_v7 \
  --attach-acr acr8409 \
  --generate-ssh-keys \
  --location eastus
```

**Important Flags Explained:**
- `--node-count 2`: Two worker nodes for redundancy
- `--node-vm-size Standard_D2s_v7`: VM size (must be from allowed list)
- `--attach-acr acr8409`: Automatically configures AKS to pull from our ACR without additional auth
- `--generate-ssh-keys`: Creates SSH keys for node access (stored in `~/.ssh/`)
- `--location eastus`: Same region as other resources

**Note:** Cannot use `--no-wait` flag when `--attach-acr` is specified. Command must complete synchronously.

**Time:** 10-15 minutes (running in background)

**Status:** In progress...

### Step 6.3: Get AKS Credentials (After Cluster Creation)

**When cluster is ready, run:**
```bash
az aks get-credentials \
  --resource-group rg-k8s-learning \
  --name aks-learning
```

**What this does:**
- Downloads kubeconfig and merges into `~/.kube/config`
- Sets current context to the new cluster

**Verification:**
```bash
kubectl get nodes
# Should show 2 nodes in Ready state
```

---

## Phase 7: Deploy OTLP Collector (TODO - After Cluster Ready)

### Step 7.1: Deploy Collector ConfigMap

```bash
cd k8s
kubectl apply -f otel-collector-configmap.yaml
```

### Step 7.2: Deploy Collector Service and Deployment

```bash
kubectl apply -f otel-collector-deployment.yaml
kubectl apply -f otel-collector-service.yaml
```

### Step 7.3: Verify Collector

```bash
kubectl get pods -l app=otel-collector
kubectl logs -l app=otel-collector
```

---

## Phase 8: Deploy Agent Service (TODO)

### Step 8.1: Create OpenAI Secret

```bash
kubectl create secret generic openai-key \
  --from-literal=OPENAI_API_KEY='sk-proj-...'
```

### Step 8.2: Deploy Agent

```bash
kubectl apply -f agent-deployment.yaml
kubectl apply -f agent-service.yaml
```

### Step 8.3: Wait for LoadBalancer IP

```bash
kubectl get svc agent-service -w
# Wait until EXTERNAL-IP appears (3-5 minutes)
```

### Step 8.4: Test Agent

```bash
AGENT_IP=$(kubectl get svc agent-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Health check
curl http://$AGENT_IP/health

# Test request
curl -X POST http://$AGENT_IP/process \
  -H "Content-Type: application/json" \
  -d '{"message": "Buy milk tomorrow", "user_id": "test-user-001"}'
```

---

## Phase 9: Setup Azure Event Hubs (TODO)

### Step 9.1: Run Event Hubs Setup Script

```bash
cd scripts
./setup_eventhub.sh
```

**What this creates:**
- Event Hubs namespace: `eh-k8s-learning-XXXXX`
- Event Hub topic: `agent-traces`
- Kubernetes secret with connection string

---

## Phase 10: Enable Kafka Exporter (TODO)

### Step 10.1: Update Collector ConfigMap

```bash
kubectl apply -f otel-collector-configmap-with-kafka.yaml
```

### Step 10.2: Restart Collector

```bash
kubectl rollout restart deployment/otel-collector
kubectl rollout status deployment/otel-collector
```

---

## Phase 11: Databricks Setup (TODO)

### Step 11.1: Configure Notebook

1. Open `databricks/ingest_traces_from_kafka.py`
2. Set `EVENTHUB_NAMESPACE` from setup_eventhub.sh output
3. Set `CONNECTION_STRING` from Kubernetes secret:
   ```bash
   kubectl get secret eventhub-conn -o jsonpath='{.data.connection-string}' | base64 -d
   ```

### Step 11.2: Run Ingestion

Run all cells in the notebook to start streaming ingestion.

---

## Phase 12: End-to-End Validation (TODO)

### Step 12.1: Run Validation Script

```bash
cd scripts
./validate_e2e.sh
```

### Step 12.2: Query Traces in Databricks

```sql
SELECT
  trace_id,
  span_name,
  gen_ai_model,
  gen_ai_total_tokens,
  duration_ms,
  start_time,
  session_id
FROM main.observability.agent_traces_k8s
ORDER BY start_time DESC
LIMIT 10;
```

---

## Key Learnings and Gotchas

### 1. ACR Tasks Limitation

**Problem:** ACR Tasks not available in subscription
**Lesson:** Always have Docker Desktop as backup for building images
**Workaround:** Build locally, push to ACR

### 2. VM Size Quota Restrictions

**Problem:** Standard_B2s not allowed in subscription/region
**Lesson:** Check available VM sizes before planning architecture
**Command to check:**
```bash
az vm list-skus --location eastus --size Standard_D --output table
```

### 3. Resource Provider Registration

**Problem:** New subscriptions don't have all providers enabled
**Lesson:** Always register required providers first
**Time cost:** 2-3 minutes per provider

### 4. Device Code Authentication

**Problem:** CLI authentication can timeout if not completed quickly
**Lesson:** Have browser ready before running `az login --use-device-code`
**Timeout:** ~2 minutes per attempt

### 5. Docker Desktop PATH

**Problem:** Docker CLI not in default PATH after installation
**Lesson:** Need to export PATH or use full path
**Solution:**
```bash
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

### 6. ACR Authentication with AKS

**Problem:** AKS needs credentials to pull from ACR
**Lesson:** Use `--attach-acr` flag during cluster creation
**Alternative:** Manual configuration with service principals (more complex)

---

## Cost Considerations

**Current Resources (if left running 24/7):**
- AKS nodes (2x Standard_D2s_v7): ~$120-150/month (higher than original B2s estimate)
- Public IPs (2): ~$6/month
- ACR (Basic): ~$5/month
- Event Hubs (Standard): ~$11/month

**Total:** ~$142-172/month if left running continuously

**Cost Saving Commands:**
```bash
# Stop AKS cluster when not in use (saves ~78%)
az aks stop -n aks-learning -g rg-k8s-learning

# Start when needed
az aks start -n aks-learning -g rg-k8s-learning

# Or delete everything when done learning
az group delete -n rg-k8s-learning --yes --no-wait
```

---

## Cleanup Commands

### Quick Cleanup (Delete Everything)

```bash
# Delete entire resource group (removes all resources)
az group delete -n rg-k8s-learning --yes --no-wait

# Verify deletion
az group list --query "[?name=='rg-k8s-learning']"
```

### Selective Cleanup (Keep Some Resources)

```bash
# Stop AKS only
az aks stop -n aks-learning -g rg-k8s-learning

# Delete AKS but keep ACR
az aks delete -n aks-learning -g rg-k8s-learning --yes --no-wait

# Delete Event Hubs
az eventhubs namespace delete -n <namespace> -g rg-k8s-learning
```

---

## Troubleshooting Commands

### Check Cluster Status

```bash
az aks show -n aks-learning -g rg-k8s-learning --query "powerState"
az aks list -g rg-k8s-learning -o table
```

### Check ACR Images

```bash
az acr repository list --name acr8409 --output table
az acr repository show-tags --name acr8409 --repository agent --output table
```

### Check Kubernetes Resources

```bash
# Pods
kubectl get pods --all-namespaces
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Services
kubectl get svc
kubectl describe svc <service-name>

# Events
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Check Azure Resource Providers

```bash
az provider list --query "[?registrationState=='Registered']" -o table
az provider show -n Microsoft.ContainerRegistry --query "registrationState"
```

---

## Next Steps (After Cluster Creation Completes)

1. ✅ Phase 7: Deploy OTLP Collector
2. ✅ Phase 8: Deploy Agent Service
3. ✅ Phase 9: Setup Event Hubs
4. ✅ Phase 10: Enable Kafka Exporter
5. ✅ Phase 11: Configure Databricks
6. ✅ Phase 12: Validate End-to-End

---

## References

- [Azure CLI Documentation](https://learn.microsoft.com/cli/azure/)
- [AKS Documentation](https://learn.microsoft.com/azure/aks/)
- [ACR Documentation](https://learn.microsoft.com/azure/container-registry/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Original Project README](./README.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)

---

**Document Status:** In Progress (AKS cluster creation pending)
**Last Updated:** July 13, 2026
