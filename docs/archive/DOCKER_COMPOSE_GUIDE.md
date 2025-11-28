# Docker Compose Guide

Complete guide for running OpsSage with Docker Compose for local development and testing.

## Overview

The Docker Compose setup provides a complete OpsSage environment with all dependencies:

- **Backend API**: OpsSage multi-agent system
- **Web Dashboard**: React-based UI
- **ChromaDB**: Vector database for RAG pipeline
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Mock Services**: Simulated metrics, logs, and events APIs

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Google Cloud credentials (for Gemini models)

### Initial Setup

```bash
# Run the automated setup script
./scripts/dev-setup.sh

# Or manually:
# 1. Copy environment file
cp env.example .env

# 2. Add Google Cloud credentials
# Place credentials.json in project root or credentials/ directory

# 3. Create data directories
mkdir -p data/chromadb
```

### Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f dashboard
```

### Access Services

- **Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ChromaDB**: http://localhost:8001
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Mock Metrics**: http://localhost:9091
- **Mock Logs**: http://localhost:9092

## Services

### Backend (opssage-backend)

OpsSage multi-agent system with FastAPI.

**Ports**: 8000
**Volumes**:
- `./credentials:/app/credentials:ro` - Google Cloud credentials
- `chromadb-data:/app/data/chromadb` - Vector database persistence
- `./sages:/app/sages` - Hot-reload source code
- `./apis:/app/apis` - Hot-reload API code

**Environment Variables**:
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to credentials
- `USE_REAL_KNOWLEDGE_ADAPTER` - Enable RAG pipeline
- `CHROMADB_PATH` - Vector database path

**Health Check**: http://localhost:8000/api/v1/health

### Dashboard (opssage-dashboard)

React-based web UI with Nginx.

**Ports**: 3000 → 80
**Health Check**: http://localhost:3000/health

### ChromaDB (chromadb)

Standalone vector database for testing.

**Ports**: 8001 → 8000
**Volume**: `chromadb-standalone:/chroma/chroma`
**Health Check**: http://localhost:8001/api/v1/heartbeat

### Prometheus (prometheus)

Metrics collection and monitoring.

**Ports**: 9090
**Volume**: `prometheus-data:/prometheus`
**Config**: `docker/prometheus/prometheus.yml`

**Targets**:
- OpsSage Backend
- Mock Services
- ChromaDB
- Self-monitoring

### Grafana (grafana)

Metrics visualization dashboard.

**Ports**: 3001 → 3000
**Volume**: `grafana-data:/var/lib/grafana`
**Default Credentials**: admin/admin
**Data Source**: Prometheus (auto-configured)

### Mock Services

Simulated infrastructure APIs for testing without real systems.

**Mock Metrics** (port 9091):
- Prometheus-compatible metrics API
- Random time series data
- Instant and range queries

**Mock Logs** (port 9092):
- Loki-compatible logs API
- Simulated log entries
- Multiple severity levels

## Common Operations

### Building Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build dashboard

# Build with no cache
docker-compose build --no-cache
```

### Managing Services

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart service
docker-compose restart backend

# Stop and remove volumes
docker-compose down -v

# View running services
docker-compose ps

# View resource usage
docker-compose stats
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash
docker-compose exec backend python scripts/test_rag.py

# View container details
docker-compose inspect backend
```

### Development Workflow

#### Backend Development

```bash
# Code changes are auto-reloaded via volume mounts
# Edit files in sages/ or apis/

# Restart backend after dependency changes
docker-compose restart backend

# View backend logs
docker-compose logs -f backend

# Test RAG pipeline
docker-compose exec backend python scripts/test_rag.py
```

#### Dashboard Development

```bash
# For live development, run locally:
cd dashboard
npm run dev

# Or rebuild and restart container:
docker-compose build dashboard
docker-compose up -d dashboard
```

### Testing with Mock Services

The mock services provide simulated infrastructure for testing:

```bash
# Query mock metrics
curl "http://localhost:9091/metrics/query?metric=cpu_usage"

# Query mock logs
curl "http://localhost:9092/logs/query?query=error&limit=10"

# Check health
curl http://localhost:9091/health
curl http://localhost:9092/health
```

### Monitoring with Prometheus & Grafana

1. **Access Grafana**: http://localhost:3001
2. **Login**: admin/admin
3. **Explore Metrics**:
   - Navigate to Explore
   - Select Prometheus data source
   - Query metrics: `up`, `process_cpu_seconds_total`, etc.

4. **Create Dashboards**:
   - Click '+' → Dashboard
   - Add panels with queries
   - Save dashboard

## Data Persistence

### Volumes

Docker Compose creates named volumes for data persistence:

- `chromadb-data`: Backend vector database
- `chromadb-standalone`: Standalone ChromaDB
- `prometheus-data`: Prometheus metrics
- `grafana-data`: Grafana dashboards

### Backup Data

```bash
# List volumes
docker volume ls | grep opssage

# Backup ChromaDB data
docker run --rm \
  -v opssage_chromadb-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/chromadb-$(date +%Y%m%d).tar.gz -C /data .

# Restore ChromaDB data
docker run --rm \
  -v opssage_chromadb-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/chromadb-20240115.tar.gz -C /data
```

### Clear Data

```bash
# Stop services and remove volumes
docker-compose down -v

# Or manually remove specific volume
docker volume rm opssage_chromadb-data
```

## Environment Configuration

### Environment Variables

Edit `.env` file or set in `docker-compose.yml`:

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/credentials.json

# RAG Pipeline
USE_REAL_KNOWLEDGE_ADAPTER=true
CHROMADB_PATH=/app/data/chromadb

# Logging
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

### Credentials

**Option 1**: Project root
```bash
# Place credentials.json in project root
./credentials.json
```

**Option 2**: Credentials directory
```bash
# Place in credentials directory
./credentials/credentials.json
```

The Docker Compose file mounts `./credentials` as read-only volume.

## Networking

All services run on the `opssage-network` bridge network.

### Service Communication

Services can communicate using service names:

- Backend → ChromaDB: `http://chromadb:8000`
- Dashboard → Backend: `http://backend:8000`
- Prometheus → Backend: `http://backend:8000`

### Port Mapping

| Service | Container Port | Host Port |
|---------|---------------|-----------|
| Backend | 8000 | 8000 |
| Dashboard | 80 | 3000 |
| ChromaDB | 8000 | 8001 |
| Prometheus | 9090 | 9090 |
| Grafana | 3000 | 3001 |
| Mock Metrics | 8080 | 9091 |
| Mock Logs | 8080 | 9092 |

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing credentials
#    - Add credentials.json file
# 2. Port already in use
#    - Stop other services on port 8000
# 3. Out of memory
#    - Increase Docker memory limit
```

### Dashboard Shows Connection Error

```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Check dashboard logs
docker-compose logs dashboard

# Verify proxy configuration
docker-compose exec dashboard cat /etc/nginx/conf.d/default.conf
```

### ChromaDB Connection Issues

```bash
# Check if ChromaDB is running
curl http://localhost:8001/api/v1/heartbeat

# Check backend logs for connection errors
docker-compose logs backend | grep -i chroma

# Restart ChromaDB
docker-compose restart chromadb
```

### Slow Performance

```bash
# Check resource usage
docker-compose stats

# Increase Docker resources in Docker Desktop settings

# Limit services
docker-compose up -d backend dashboard
```

### Permission Denied Errors

```bash
# Fix volume permissions
sudo chown -R $(id -u):$(id -g) data/

# Or recreate volumes
docker-compose down -v
docker-compose up -d
```

## Production Considerations

### Security

1. **Change Default Passwords**:
   ```yaml
   grafana:
     environment:
       - GF_SECURITY_ADMIN_PASSWORD=strong_password
   ```

2. **Use Secrets** (Docker Compose 3.1+):
   ```yaml
   secrets:
     google_credentials:
       file: ./credentials.json
   ```

3. **Limit Network Exposure**:
   ```yaml
   ports:
     - "127.0.0.1:8000:8000"  # Only localhost
   ```

### Resource Limits

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 4G
      reservations:
        cpus: '1.0'
        memory: 2G
```

### Health Checks

All services include health checks for monitoring:

```bash
# Check health status
docker-compose ps

# Services should show "healthy" status
```

## Integration with Kubernetes

After testing locally with Docker Compose, deploy to Kubernetes:

```bash
# Setup Kind cluster
./scripts/kind-setup.sh

# Build and load images
docker-compose build
kind load docker-image opssage-backend:latest
kind load docker-image opssage-dashboard:latest

# Deploy to Kind
./scripts/kind-deploy.sh
```

See [KIND_GUIDE.md](KIND_GUIDE.md) for details.

## Additional Resources

- [OpsSage README](../README.md)
- [RAG Guide](RAG_GUIDE.md)
- [Dashboard README](../dashboard/README.md)
- [Kind Guide](KIND_GUIDE.md)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Support

For issues:
- Check logs: `docker-compose logs`
- GitHub Issues: https://github.com/ithaquaKr/opssage/issues
