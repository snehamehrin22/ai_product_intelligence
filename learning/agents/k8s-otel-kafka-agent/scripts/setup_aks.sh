#!/bin/bash
set -e  # Exit on error

echo "========================================="
echo "AKS + ACR Setup Script (US-3)"
echo "========================================="
echo ""

# Variables (customize these)
RESOURCE_GROUP="rg-k8s-learning"
LOCATION="eastus"
ACR_NAME="acr$RANDOM"  # Must be globally unique
AKS_NAME="aks-learning"
NODE_SIZE="Standard_B2s"  # Cheapest ($30/month)
NODE_COUNT=2

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  ACR Name: $ACR_NAME"
echo "  AKS Name: $AKS_NAME"
echo "  Node Size: $NODE_SIZE"
echo "  Node Count: $NODE_COUNT"
echo ""
echo "Estimated cost: ~$2.78/day if left running"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Step 1: Create Resource Group
echo ""
echo "[1/6] Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --output table

# Step 2: Create Azure Container Registry
echo ""
echo "[2/6] Creating Azure Container Registry (ACR)..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --output table

echo ""
echo "ACR Login Server: $ACR_NAME.azurecr.io"

# Step 3: Build and push agent image to ACR
echo ""
echo "[3/6] Building and pushing agent image to ACR..."
cd ../agent-service
az acr build \
  --registry $ACR_NAME \
  --image agent:v1 \
  --file Dockerfile \
  .

echo ""
echo "Image pushed: $ACR_NAME.azurecr.io/agent:v1"

# Step 4: Create AKS cluster
echo ""
echo "[4/6] Creating AKS cluster (this takes ~15-20 minutes)..."
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --node-count $NODE_COUNT \
  --node-vm-size $NODE_SIZE \
  --attach-acr $ACR_NAME \
  --generate-ssh-keys \
  --enable-managed-identity \
  --output table

# Step 5: Get AKS credentials
echo ""
echo "[5/6] Getting AKS credentials..."
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --overwrite-existing

# Step 6: Update agent deployment YAML with ACR name
echo ""
echo "[6/6] Updating Kubernetes manifests with ACR name..."
cd ../k8s
sed -i.bak "s|<ACR_NAME>|$ACR_NAME|g" agent-deployment.yaml
rm agent-deployment.yaml.bak

echo ""
echo "========================================="
echo "✅ AKS Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Verify cluster: kubectl get nodes"
echo "  2. Deploy OTLP Collector: kubectl apply -f k8s/otel-collector-*.yaml"
echo "  3. Create OpenAI secret: kubectl create secret generic openai-key --from-literal=OPENAI_API_KEY=\$OPENAI_API_KEY"
echo "  4. Deploy agent: kubectl apply -f k8s/agent-*.yaml"
echo ""
echo "Cluster info:"
kubectl cluster-info
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "ACR Name: $ACR_NAME"
echo "AKS Name: $AKS_NAME"
echo ""
echo "⚠️  Remember to run cleanup_aks.sh when done to avoid charges!"
