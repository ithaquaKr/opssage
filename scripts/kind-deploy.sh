#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Deploying OpsSage to Kind Cluster ===${NC}"

CLUSTER_NAME="opssage-cluster"

# Check if cluster exists
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo -e "${RED}Error: Cluster ${CLUSTER_NAME} does not exist${NC}"
    echo "Run './scripts/kind-setup.sh' first"
    exit 1
fi

# Set kubeconfig to Kind cluster
export KUBECONFIG="$(kind get kubeconfig-path --name ${CLUSTER_NAME} 2>/dev/null || echo ~/.kube/config)"
kubectl cluster-info --context kind-${CLUSTER_NAME}

echo -e "${GREEN}Building Docker images...${NC}"
docker-compose build backend dashboard

echo -e "${GREEN}Loading images into Kind cluster...${NC}"
kind load docker-image opssage-backend:latest --name "${CLUSTER_NAME}"
kind load docker-image opssage-dashboard:latest --name "${CLUSTER_NAME}"

echo -e "${GREEN}Creating namespace...${NC}"
kubectl apply -f deploy/kubernetes/namespace.yaml

echo -e "${GREEN}Creating Google Cloud credentials secret...${NC}"
if [ -f "credentials.json" ] || [ -f "credentials/credentials.json" ]; then
    CREDS_FILE="credentials.json"
    if [ ! -f "$CREDS_FILE" ] && [ -f "credentials/credentials.json" ]; then
        CREDS_FILE="credentials/credentials.json"
    fi

    kubectl create secret generic google-credentials \
        --from-file=credentials.json=$CREDS_FILE \
        --namespace=opssage \
        --dry-run=client -o yaml | kubectl apply -f -
    echo -e "${GREEN}Credentials secret created${NC}"
else
    echo -e "${YELLOW}Warning: No credentials.json found. Creating dummy secret.${NC}"
    echo '{}' > /tmp/dummy-creds.json
    kubectl create secret generic google-credentials \
        --from-file=credentials.json=/tmp/dummy-creds.json \
        --namespace=opssage \
        --dry-run=client -o yaml | kubectl apply -f -
    rm /tmp/dummy-creds.json
fi

echo -e "${GREEN}Creating ConfigMaps...${NC}"
kubectl apply -f deploy/kubernetes/configmap.yaml

echo -e "${GREEN}Creating PersistentVolume and PersistentVolumeClaim...${NC}"
kubectl apply -f deploy/kubernetes/storage.yaml

echo -e "${GREEN}Deploying backend...${NC}"
kubectl apply -f deploy/kubernetes/backend-deployment.yaml

echo -e "${GREEN}Deploying dashboard...${NC}"
kubectl apply -f deploy/kubernetes/dashboard-deployment.yaml

echo -e "${GREEN}Waiting for deployments to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s \
    deployment/opssage-backend \
    deployment/opssage-dashboard \
    -n opssage

echo -e "${GREEN}=== Deployment complete ===${NC}"
echo ""
echo "Services:"
kubectl get svc -n opssage
echo ""
echo "Pods:"
kubectl get pods -n opssage -o wide
echo ""
echo "Access the application:"
echo "  Backend API:  http://localhost:8000"
echo "  Dashboard:    http://localhost:3000"
echo "  API Docs:     http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  kubectl get pods -n opssage"
echo "  kubectl logs -f -n opssage -l app=opssage-backend"
echo "  kubectl logs -f -n opssage -l app=opssage-dashboard"
echo "  kubectl describe pod <pod-name> -n opssage"
echo ""
