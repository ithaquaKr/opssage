#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

CLUSTER_NAME="opssage-cluster"

echo -e "${YELLOW}=== Tearing down OpsSage Kind Cluster ===${NC}"

# Check if cluster exists
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo -e "${YELLOW}Cluster ${CLUSTER_NAME} does not exist${NC}"
    exit 0
fi

read -p "Are you sure you want to delete the cluster? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

echo -e "${GREEN}Deleting Kind cluster...${NC}"
kind delete cluster --name "${CLUSTER_NAME}"

echo -e "${GREEN}Cleaning up data directories...${NC}"
read -p "Do you want to delete local data directories? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ./data
    echo -e "${GREEN}Data directories deleted${NC}"
fi

echo -e "${GREEN}=== Teardown complete ===${NC}"
