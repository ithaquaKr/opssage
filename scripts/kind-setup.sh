#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== OpsSage Kind Cluster Setup ===${NC}"

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo -e "${RED}Error: kind is not installed${NC}"
    echo "Install it from: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    echo "Install it from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

CLUSTER_NAME="opssage-cluster"

# Check if cluster already exists
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo -e "${YELLOW}Cluster ${CLUSTER_NAME} already exists${NC}"
    read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deleting existing cluster...${NC}"
        kind delete cluster --name "${CLUSTER_NAME}"
    else
        echo -e "${GREEN}Using existing cluster${NC}"
        exit 0
    fi
fi

# Create data directory for persistent volumes
echo -e "${GREEN}Creating data directories...${NC}"
mkdir -p ./data/chromadb

# Create Kind cluster
echo -e "${GREEN}Creating Kind cluster with multi-node configuration...${NC}"
kind create cluster --config kind-config.yaml

# Wait for cluster to be ready
echo -e "${GREEN}Waiting for cluster to be ready...${NC}"
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Display cluster info
echo -e "${GREEN}Cluster nodes:${NC}"
kubectl get nodes -o wide

# Load local images into Kind (if they exist)
echo -e "${GREEN}Loading Docker images into Kind cluster...${NC}"

if docker images | grep -q "opssage-backend"; then
    echo "Loading opssage-backend image..."
    kind load docker-image opssage-backend:latest --name "${CLUSTER_NAME}"
else
    echo -e "${YELLOW}opssage-backend image not found. Build it first with 'docker-compose build backend'${NC}"
fi

if docker images | grep -q "opssage-dashboard"; then
    echo "Loading opssage-dashboard image..."
    kind load docker-image opssage-dashboard:latest --name "${CLUSTER_NAME}"
else
    echo -e "${YELLOW}opssage-dashboard image not found. Build it first with 'docker-compose build dashboard'${NC}"
fi

echo -e "${GREEN}=== Kind cluster setup complete ===${NC}"
echo ""
echo "Cluster name: ${CLUSTER_NAME}"
echo "Kubeconfig: $(kind get kubeconfig --name ${CLUSTER_NAME} | grep server)"
echo ""
echo "Next steps:"
echo "  1. Build Docker images: docker-compose build"
echo "  2. Load images into Kind: kind load docker-image <image-name> --name ${CLUSTER_NAME}"
echo "  3. Deploy OpsSage: ./scripts/kind-deploy.sh"
echo ""
echo "To delete the cluster: kind delete cluster --name ${CLUSTER_NAME}"
