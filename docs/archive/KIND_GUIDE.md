# Kind (Kubernetes in Docker) Guide

Complete guide for testing OpsSage on a multi-node Kubernetes cluster using Kind.

## Overview

This guide covers deploying OpsSage to a local Kubernetes cluster created with Kind (Kubernetes in Docker). Kind creates a real Kubernetes cluster using Docker containers as nodes, perfect for testing Kubernetes deployments locally.

## Architecture

### Cluster Configuration

- **1 Control Plane Node**: Manages the cluster
- **3 Worker Nodes**: Run application workloads
  - Worker 1: Compute workload
  - Worker 2: Storage workload
  - Worker 3: Compute workload

### Port Mappings

| Service | Node Port | Host Port |
|---------|-----------|-----------|
| OpsSage Backend | 30800 | 8000 |
| OpsSage Dashboard | 30300 | 3000 |
| Kubernetes API | 6443 | 6443 |
| HTTP Ingress | 30080 | 30080 |
| HTTPS Ingress | 30443 | 30443 |

## Prerequisites

### Required Tools

1. **Docker** 20.10+
   ```bash
   docker --version
   ```

2. **Kind** 0.20+
   ```bash
   kind version
   # If not installed:
   # macOS: brew install kind
   # Linux: https://kind.sigs.k8s.io/docs/user/quick-start/
   ```

3. **kubectl** 1.28+
   ```bash
   kubectl version --client
   # If not installed:
   # macOS: brew install kubectl
   # Linux: https://kubernetes.io/docs/tasks/tools/
   ```

4. **Docker Images Built**
   ```bash
   docker-compose build backend dashboard
   ```

## Quick Start

### Automated Setup

```bash
# 1. Run development setup (if not done already)
./scripts/dev-setup.sh

# 2. Build Docker images
docker-compose build

# 3. Create Kind cluster
./scripts/kind-setup.sh

# 4. Deploy OpsSage
./scripts/kind-deploy.sh

# 5. Access services
# Backend:  http://localhost:8000
# Dashboard: http://localhost:3000
```

### Manual Setup

#### Step 1: Create Kind Cluster

```bash
# Create cluster with configuration
kind create cluster --config kind-config.yaml

# Verify cluster
kubectl cluster-info --context kind-opssage-cluster
kubectl get nodes
```

Expected output:
```
NAME                           STATUS   ROLES           AGE   VERSION
opssage-cluster-control-plane  Ready    control-plane   1m    v1.28.0
opssage-cluster-worker         Ready    <none>          1m    v1.28.0
opssage-cluster-worker2        Ready    <none>          1m    v1.28.0
opssage-cluster-worker3        Ready    <none>          1m    v1.28.0
```

#### Step 2: Build and Load Images

```bash
# Build images
docker-compose build backend dashboard

# Load images into Kind
kind load docker-image opssage-backend:latest --name opssage-cluster
kind load docker-image opssage-dashboard:latest --name opssage-cluster

# Verify images loaded
docker exec -it opssage-cluster-control-plane crictl images | grep opssage
```

#### Step 3: Create Kubernetes Resources

```bash
# Create namespace
kubectl apply -f deploy/kubernetes/namespace.yaml

# Create Google Cloud credentials secret
kubectl create secret generic google-credentials \
  --from-file=credentials.json=./credentials.json \
  --namespace=opssage

# Create ConfigMaps
kubectl apply -f deploy/kubernetes/configmap.yaml

# Create storage (PV and PVC)
kubectl apply -f deploy/kubernetes/storage.yaml

# Deploy backend
kubectl apply -f deploy/kubernetes/backend-deployment.yaml

# Deploy dashboard
kubectl apply -f deploy/kubernetes/dashboard-deployment.yaml
```

#### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods -n opssage

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=opssage-backend -n opssage --timeout=300s

# Check services
kubectl get svc -n opssage

# Check logs
kubectl logs -f -n opssage -l app=opssage-backend
```

## Accessing Services

### NodePort Access

Services are exposed via NodePort:

```bash
# Backend API
curl http://localhost:8000/api/v1/health

# Dashboard
open http://localhost:3000

# API Documentation
open http://localhost:8000/docs
```

### Port Forwarding (Alternative)

```bash
# Forward backend
kubectl port-forward -n opssage svc/opssage-backend 8000:8000

# Forward dashboard
kubectl port-forward -n opssage svc/opssage-dashboard 3000:80
```

## Managing the Cluster

### View Resources

```bash
# All resources in opssage namespace
kubectl get all -n opssage

# Detailed pod information
kubectl get pods -n opssage -o wide

# Deployments
kubectl get deployments -n opssage

# Services
kubectl get svc -n opssage

# ConfigMaps and Secrets
kubectl get configmaps,secrets -n opssage

# Persistent Volumes
kubectl get pv,pvc -n opssage
```

### Logs and Debugging

```bash
# View logs
kubectl logs -f -n opssage -l app=opssage-backend
kubectl logs -f -n opssage -l app=opssage-dashboard

# Previous container logs
kubectl logs -n opssage <pod-name> --previous

# Describe resources
kubectl describe pod <pod-name> -n opssage
kubectl describe svc opssage-backend -n opssage

# Execute commands in pod
kubectl exec -it -n opssage <pod-name> -- bash
kubectl exec -it -n opssage <pod-name> -- python scripts/test_rag.py

# Get events
kubectl get events -n opssage --sort-by='.lastTimestamp'
```

### Scaling

```bash
# Scale backend
kubectl scale deployment opssage-backend --replicas=3 -n opssage

# Scale dashboard
kubectl scale deployment opssage-dashboard --replicas=2 -n opssage

# Verify scaling
kubectl get pods -n opssage -w
```

### Updates and Rollouts

```bash
# Update image
kubectl set image deployment/opssage-backend \
  backend=opssage-backend:v2 -n opssage

# Check rollout status
kubectl rollout status deployment/opssage-backend -n opssage

# Rollback
kubectl rollout undo deployment/opssage-backend -n opssage

# View rollout history
kubectl rollout history deployment/opssage-backend -n opssage
```

## Configuration Management

### ConfigMaps

Edit `deploy/kubernetes/configmap.yaml`:

```yaml
data:
  USE_REAL_KNOWLEDGE_ADAPTER: "true"
  CHROMADB_PATH: "/app/data/chromadb"
  LOG_LEVEL: "DEBUG"  # Change as needed
```

Apply changes:
```bash
kubectl apply -f deploy/kubernetes/configmap.yaml
kubectl rollout restart deployment/opssage-backend -n opssage
```

### Secrets

```bash
# Update Google credentials
kubectl create secret generic google-credentials \
  --from-file=credentials.json=./new-credentials.json \
  --namespace=opssage \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to use new secret
kubectl rollout restart deployment/opssage-backend -n opssage
```

## Storage

### Persistent Volumes

Kind uses hostPath for persistent volumes:

```bash
# View PV and PVC
kubectl get pv,pvc -n opssage

# PV is mounted from Kind node filesystem
docker exec opssage-cluster-worker ls -la /mnt/data/chromadb
```

### Backup Data

```bash
# Copy data from Kind node
docker cp opssage-cluster-worker:/mnt/data/chromadb ./backup/

# Restore data to Kind node
docker cp ./backup/chromadb opssage-cluster-worker:/mnt/data/
```

## Networking

### Service Types

OpsSage uses NodePort services for external access:

```yaml
spec:
  type: NodePort
  ports:
    - port: 8000        # Internal port
      targetPort: 8000  # Container port
      nodePort: 30800   # External port
```

### DNS Resolution

Pods can communicate using service DNS:

```bash
# From within a pod
kubectl exec -it -n opssage <pod-name> -- curl http://opssage-backend:8000/api/v1/health
```

### Network Policies (Optional)

Create network policies for security:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: opssage
spec:
  podSelector:
    matchLabels:
      app: opssage-backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: opssage-dashboard
      ports:
        - protocol: TCP
          port: 8000
```

## Monitoring

### Resource Usage

```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods -n opssage

# Detailed metrics
kubectl describe nodes
```

### Metrics Server (Optional)

```bash
# Install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch for Kind (disable TLS)
kubectl patch -n kube-system deployment metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

## Testing

### Smoke Tests

```bash
# Test backend health
curl http://localhost:8000/api/v1/health

# Submit test alert
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "TestAlert",
    "severity": "high",
    "message": "Test alert from Kind cluster",
    "labels": {"env": "test"},
    "firing_condition": "test > 0"
  }'

# List incidents
curl http://localhost:8000/api/v1/incidents

# Upload test document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@README.md" \
  -F "doc_type=general"
```

### Load Testing

```bash
# Install hey (HTTP load generator)
# macOS: brew install hey
# Linux: https://github.com/rakyll/hey

# Load test backend
hey -n 1000 -c 10 http://localhost:8000/api/v1/health

# Load test with POST
hey -n 100 -c 5 -m POST \
  -H "Content-Type: application/json" \
  -d '{"alert_name":"LoadTest","severity":"low","message":"Test","labels":{},"firing_condition":"test"}' \
  http://localhost:8000/api/v1/alerts
```

## Troubleshooting

### Cluster Issues

```bash
# Cluster not starting
kind get clusters
kind delete cluster --name opssage-cluster
kind create cluster --config kind-config.yaml

# Cannot access services
kubectl get svc -n opssage
kubectl describe svc opssage-backend -n opssage

# DNS issues
kubectl get pods -n kube-system
kubectl logs -n kube-system -l k8s-app=kube-dns
```

### Pod Issues

```bash
# Pod not starting
kubectl describe pod <pod-name> -n opssage
kubectl logs <pod-name> -n opssage

# Image pull errors
kind load docker-image opssage-backend:latest --name opssage-cluster

# Insufficient resources
kubectl describe nodes
docker update --cpus=4 --memory=8g opssage-cluster-worker
```

### Storage Issues

```bash
# PVC pending
kubectl describe pvc chromadb-pvc -n opssage

# Create directory in node
docker exec opssage-cluster-worker mkdir -p /mnt/data/chromadb
docker exec opssage-cluster-worker chmod 777 /mnt/data/chromadb
```

## Cleanup

### Remove OpsSage

```bash
# Delete all resources
kubectl delete namespace opssage

# Or use script
./scripts/kind-teardown.sh
```

### Delete Cluster

```bash
# Delete Kind cluster
kind delete cluster --name opssage-cluster

# Verify deletion
kind get clusters
docker ps | grep opssage
```

### Clean Up Data

```bash
# Remove local data
rm -rf ./data

# Remove Docker volumes
docker volume prune
```

## Advanced Topics

### Multi-Cluster Setup

```bash
# Create multiple clusters
kind create cluster --name opssage-dev --config kind-config-dev.yaml
kind create cluster --name opssage-prod --config kind-config-prod.yaml

# Switch context
kubectl config use-context kind-opssage-dev
kubectl config use-context kind-opssage-prod
```

### Ingress Controller

```bash
# Install Nginx Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Create Ingress
kubectl apply -f deploy/kubernetes/ingress.yaml
```

### Helm Deployment

```bash
# Install with Helm
helm install opssage ./deploy/helm \
  --namespace opssage \
  --create-namespace \
  --set image.tag=latest

# Upgrade
helm upgrade opssage ./deploy/helm -n opssage

# Uninstall
helm uninstall opssage -n opssage
```

## Comparison: Docker Compose vs Kind

| Feature | Docker Compose | Kind |
|---------|---------------|------|
| Use Case | Local development | Kubernetes testing |
| Setup Time | Fast (~1 min) | Moderate (~3 min) |
| Resources | Low | Medium |
| Kubernetes | No | Yes (full K8s) |
| Scaling | Manual | Automatic |
| Production-like | No | Yes |
| Learning Curve | Easy | Moderate |

## Best Practices

1. **Development**: Use Docker Compose
2. **Kubernetes Testing**: Use Kind
3. **CI/CD Testing**: Use Kind in GitHub Actions
4. **Production**: Use managed Kubernetes (GKE, EKS, AKS)

## Resources

- [Kind Documentation](https://kind.sigs.k8s.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [OpsSage Helm Charts](../deploy/helm/)

## Support

For issues:
- Check logs: `kubectl logs -n opssage <pod-name>`
- GitHub Issues: https://github.com/ithaquaKr/opssage/issues
