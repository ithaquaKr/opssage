# Deployment Guide

This guide covers all deployment options for OpsSage, from local development to production Kubernetes.

---

## Table of Contents

1. [Deployment Options](#deployment-options)
2. [Local Development](#local-development)
3. [Docker Compose](#docker-compose)
4. [Kubernetes with Kind](#kubernetes-with-kind)
5. [Production Kubernetes](#production-kubernetes)
6. [Configuration](#configuration)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Deployment Options

| Option | Best For | Setup Time | Complexity |
|--------|----------|------------|------------|
| **Local** | Quick testing | 2 min | Low |
| **Docker Compose** | Full stack testing | 5 min | Medium |
| **Kind** | K8s testing | 10 min | Medium |
| **Kubernetes** | Production | 30 min | High |

---

## Local Development

### Quick Start

```bash
# Install dependencies
uv sync

# Set up environment
cp env.example .env
# Edit .env with your credentials

# Start backend
source .venv/bin/activate
uvicorn apis.main:app --reload

# Start dashboard (separate terminal)
cd dashboard
npm install && npm run dev
```

**Access:**
- Backend: http://localhost:8000
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

### When to Use

- ✅ Developing new features
- ✅ Quick testing
- ✅ Learning the system
- ❌ Production use
- ❌ Load testing
- ❌ Multi-user scenarios

---

## Docker Compose

### Overview

Complete stack with all dependencies in containers.

**Includes:**
- Backend API (port 8000)
- Web Dashboard (port 3000)
- ChromaDB vector database (port 8001)
- Prometheus monitoring (port 9090)
- Grafana dashboards (port 3001)
- Mock services for testing (ports 9091, 9092)

### Quick Start

```bash
# One-command setup
./scripts/dev-setup.sh

# Start all services
make docker-up

# Or directly
docker-compose up -d
```

### Detailed Setup

#### 1. Prerequisites

```bash
# Check Docker is installed
docker --version
docker-compose --version

# Ensure Docker is running
docker ps
```

#### 2. Configuration

```bash
# Create environment file
cp env.example .env

# Edit .env
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
CHROMADB_PATH=/app/data/chromadb
```

#### 3. Credentials

```bash
# Place your Google Cloud credentials
mkdir -p credentials
cp /path/to/your/credentials.json credentials/
```

#### 4. Start Services

```bash
# Build images
docker-compose build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### Service Management

```bash
# Stop services
docker-compose stop

# Start services
docker-compose start

# Restart specific service
docker-compose restart opssage-backend

# View logs for specific service
docker-compose logs -f opssage-backend

# Remove all containers and volumes
docker-compose down -v
```

### Access Services

```
Backend:    http://localhost:8000
Dashboard:  http://localhost:3000
ChromaDB:   http://localhost:8001
Prometheus: http://localhost:9090
Grafana:    http://localhost:3001 (admin/admin)
```

### Data Persistence

Data is persisted in Docker volumes:

```bash
# List volumes
docker volume ls | grep opssage

# Backup ChromaDB
docker run --rm -v opssage_chromadb_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/chromadb-backup.tar.gz /data

# Restore ChromaDB
docker run --rm -v opssage_chromadb_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/chromadb-backup.tar.gz -C /
```

### When to Use

- ✅ Full stack testing
- ✅ Demo environments
- ✅ Development with dependencies
- ✅ Integration testing
- ❌ Production (use Kubernetes)

---

## Kubernetes with Kind

### Overview

Test OpsSage on a real Kubernetes cluster locally using Kind (Kubernetes in Docker).

**Cluster Configuration:**
- 1 control plane node
- 3 worker nodes
- Multi-node scheduling
- Real Kubernetes features

### Quick Start

```bash
# Create Kind cluster
make kind-setup

# Deploy OpsSage
make kind-deploy

# Access services
# Backend:   http://localhost:30800
# Dashboard: http://localhost:30300
```

### Detailed Setup

#### 1. Prerequisites

```bash
# Install Kind
brew install kind  # macOS
# or
go install sigs.k8s.io/kind@latest

# Install kubectl
brew install kubectl

# Verify
kind version
kubectl version --client
```

#### 2. Create Cluster

```bash
# Create cluster with custom config
kind create cluster --config kind-config.yaml --name opssage-cluster

# Wait for nodes to be ready
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Verify cluster
kubectl get nodes
```

#### 3. Load Images

```bash
# Build Docker images
docker-compose build

# Load images to Kind
kind load docker-image opssage-backend:latest --name opssage-cluster
kind load docker-image opssage-dashboard:latest --name opssage-cluster
```

#### 4. Deploy Application

```bash
# Create namespace
kubectl apply -f deploy/kubernetes/namespace.yaml

# Create secrets (replace with your credentials)
kubectl create secret generic google-credentials \
  --from-file=credentials.json=./credentials/credentials.json \
  -n opssage

# Apply configuration
kubectl apply -f deploy/kubernetes/configmap.yaml

# Deploy storage
kubectl apply -f deploy/kubernetes/storage.yaml

# Deploy backend
kubectl apply -f deploy/kubernetes/backend-deployment.yaml

# Deploy dashboard
kubectl apply -f deploy/kubernetes/dashboard-deployment.yaml

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods --all -n opssage --timeout=300s
```

#### 5. Access Services

```bash
# Get service URLs
kubectl get svc -n opssage

# Access via NodePort
# Backend:   http://localhost:30800
# Dashboard: http://localhost:30300
```

### Management Commands

```bash
# View pods
kubectl get pods -n opssage

# View logs
kubectl logs -f deployment/opssage-backend -n opssage

# Scale deployment
kubectl scale deployment opssage-backend --replicas=3 -n opssage

# Port forward (alternative to NodePort)
kubectl port-forward svc/opssage-backend 8000:8000 -n opssage

# Execute commands in pod
kubectl exec -it deployment/opssage-backend -n opssage -- /bin/bash

# Delete deployment
kubectl delete namespace opssage

# Delete cluster
kind delete cluster --name opssage-cluster
```

### Testing Scenarios

#### Multi-Node Scheduling

```bash
# Deploy with 3 replicas
kubectl scale deployment opssage-backend --replicas=3 -n opssage

# View pod distribution
kubectl get pods -n opssage -o wide

# Should see pods on different nodes
```

#### Node Failure Simulation

```bash
# Stop a worker node
docker stop opssage-cluster-worker

# Watch pod rescheduling
kubectl get pods -n opssage -w

# Restart node
docker start opssage-cluster-worker
```

### When to Use

- ✅ Kubernetes feature testing
- ✅ Multi-node scenarios
- ✅ Helm chart validation
- ✅ Pre-production testing
- ❌ Production deployment

---

## Production Kubernetes

### Using Helm

#### 1. Prerequisites

```bash
# Install Helm
brew install helm

# Add repository (if published)
helm repo add opssage https://charts.opssage.io
helm repo update
```

#### 2. Prepare Configuration

Create `values-production.yaml`:

```yaml
# Production values
replicaCount: 3

image:
  repository: your-registry/opssage
  tag: "0.4.0"
  pullPolicy: IfNotPresent

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

googleCloud:
  projectId: "your-project-id"
  credentialsSecretName: "google-credentials"

storage:
  storageClass: "fast-ssd"
  size: "50Gi"

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: opssage.your-domain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: opssage-tls
      hosts:
        - opssage.your-domain.com

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

#### 3. Create Secrets

```bash
# Google Cloud credentials
kubectl create secret generic google-credentials \
  --from-file=credentials.json=./credentials/credentials.json \
  -n opssage

# Image pull secrets (if using private registry)
kubectl create secret docker-registry regcred \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password \
  -n opssage
```

#### 4. Install with Helm

```bash
# Install
helm install opssage ./deploy/helm \
  -f values-production.yaml \
  -n opssage \
  --create-namespace

# Verify deployment
helm status opssage -n opssage

# Watch pods come up
kubectl get pods -n opssage -w
```

#### 5. Upgrade Deployment

```bash
# Update image tag
helm upgrade opssage ./deploy/helm \
  -f values-production.yaml \
  --set image.tag=0.4.1 \
  -n opssage

# Rollback if needed
helm rollback opssage -n opssage
```

### Manual Kubernetes Deployment

#### 1. Customize Manifests

```bash
# Copy manifests
cp -r deploy/kubernetes deploy/production

# Edit for your environment
vim deploy/production/backend-deployment.yaml
```

#### 2. Apply Manifests

```bash
# Create namespace
kubectl apply -f deploy/production/namespace.yaml

# Create secrets
kubectl create secret generic google-credentials \
  --from-file=credentials.json=./credentials/credentials.json \
  -n opssage

# Apply configuration
kubectl apply -f deploy/production/configmap.yaml

# Deploy storage
kubectl apply -f deploy/production/storage.yaml

# Deploy application
kubectl apply -f deploy/production/backend-deployment.yaml
kubectl apply -f deploy/production/dashboard-deployment.yaml

# Create ingress
kubectl apply -f deploy/production/ingress.yaml
```

### Production Checklist

Before deploying to production:

- [ ] Set appropriate resource limits
- [ ] Configure autoscaling
- [ ] Set up ingress with TLS
- [ ] Configure persistent storage
- [ ] Set up monitoring and alerts
- [ ] Configure backup strategy
- [ ] Set up log aggregation
- [ ] Test disaster recovery
- [ ] Configure network policies
- [ ] Set up RBAC
- [ ] Enable authentication
- [ ] Configure rate limiting
- [ ] Test upgrade procedure
- [ ] Document runbooks

---

## Configuration

### Environment Variables

```bash
# Required
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional
CHROMADB_PATH=./data/chromadb
LOG_LEVEL=INFO
USE_REAL_KNOWLEDGE_ADAPTER=true
MAX_WORKERS=4
ENABLE_METRICS=true
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: opssage-config
  namespace: opssage
data:
  CHROMADB_PATH: "/data/chromadb"
  LOG_LEVEL: "INFO"
  USE_REAL_KNOWLEDGE_ADAPTER: "true"
```

### Resource Limits

**Development:**
```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Production:**
```yaml
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 4Gi
```

---

## Monitoring

### Prometheus Metrics

OpsSage exposes metrics at `/metrics`:

```bash
# View metrics
curl http://localhost:8000/metrics
```

**Key metrics:**
- `opssage_alerts_total` - Total alerts received
- `opssage_incidents_total` - Total incidents created
- `opssage_analysis_duration_seconds` - Analysis duration
- `opssage_agent_calls_total` - Agent invocations

### Grafana Dashboards

```bash
# Access Grafana
# Docker Compose: http://localhost:3001
# Login: admin/admin

# Import dashboard
# Use dashboard ID from docs/dashboards/
```

### Health Checks

```bash
# Liveness probe
curl http://localhost:8000/api/v1/health

# Readiness probe
curl http://localhost:8000/api/v1/readiness
```

---

## Troubleshooting

### Common Issues

#### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n opssage

# Check events
kubectl get events -n opssage --sort-by='.lastTimestamp'

# View logs
kubectl logs <pod-name> -n opssage
```

#### Image Pull Errors

```bash
# Verify image exists
docker images | grep opssage

# Check image pull secret
kubectl get secret regcred -n opssage

# Load image to Kind
kind load docker-image opssage-backend:latest --name opssage-cluster
```

#### Storage Issues

```bash
# Check PV/PVC status
kubectl get pv,pvc -n opssage

# Describe PVC
kubectl describe pvc chromadb-pvc -n opssage
```

#### Authentication Errors

```bash
# Verify secret exists
kubectl get secret google-credentials -n opssage

# Check secret content
kubectl get secret google-credentials -n opssage -o yaml

# Recreate secret
kubectl delete secret google-credentials -n opssage
kubectl create secret generic google-credentials \
  --from-file=credentials.json=./credentials/credentials.json \
  -n opssage
```

### Debug Mode

Enable debug logging:

```bash
# Docker Compose
docker-compose up  # Without -d to see logs

# Kubernetes
kubectl set env deployment/opssage-backend LOG_LEVEL=DEBUG -n opssage
```

---

## Next Steps

- **[Configuration Guide](CONFIGURATION.md)** - Detailed configuration options
- **[Security Guide](SECURITY.md)** - Security best practices
- **[Monitoring Guide](MONITORING.md)** - Complete monitoring setup
- **[Backup Guide](BACKUP.md)** - Backup and recovery procedures

---

**Need help?** Check [GitHub Issues](https://github.com/ithaquaKr/opssage/issues)
