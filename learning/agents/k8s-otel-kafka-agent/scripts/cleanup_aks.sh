#!/bin/bash
set -e

echo "========================================="
echo "⚠️  CLEANUP: Delete AKS Resources"
echo "========================================="
echo ""
echo "This will DELETE:"
echo "  - AKS cluster"
echo "  - Azure Container Registry"
echo "  - Resource Group (and everything in it)"
echo "  - LoadBalancer public IPs"
echo ""
echo "This action CANNOT be undone!"
echo ""
read -p "Are you sure? Type 'delete' to confirm: " -r
echo

if [[ $REPLY != "delete" ]]; then
    echo "Aborted. No resources were deleted."
    exit 1
fi

RESOURCE_GROUP="rg-k8s-learning"

echo ""
echo "Deleting resource group: $RESOURCE_GROUP"
echo "This may take 5-10 minutes..."

az group delete \
  --name $RESOURCE_GROUP \
  --yes \
  --no-wait

echo ""
echo "✅ Cleanup initiated!"
echo ""
echo "Resources are being deleted in the background."
echo "Check status: az group show --name $RESOURCE_GROUP"
echo ""
echo "You can close this terminal. Deletion will continue."
