# Getting Started with OpsSage

This guide will walk you through setting up OpsSage from scratch. By the end, you'll have a running system that can analyze alerts and provide remediation recommendations.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Starting the System](#starting-the-system)
5. [First Alert](#first-alert)
6. [Next Steps](#next-steps)

---

## Prerequisites

### Required

- **Python 3.10+** (Python 3.13 recommended)
  ```bash
  python --version  # Check your version
  ```

- **uv Package Manager**
  ```bash
  # Install uv
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Verify installation
  uv --version
  ```

- **Google Cloud Account** with access to:
  - Vertex AI API
  - Gemini models

  [Create a Google Cloud account](https://cloud.google.com/free)

### Optional (for full stack)

- **Node.js 18+** (for web dashboard)
- **Docker & Docker Compose** (for containerized deployment)
- **kubectl & Helm** (for Kubernetes deployment)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ithaquaKr/opssage.git
cd opssage
```

### Step 2: Install Python Dependencies

```bash
# Install dependencies with uv
uv sync

# This creates a virtual environment at .venv and installs all packages
```

### Step 3: Verify Installation

```bash
# Activate the virtual environment
source .venv/bin/activate

# Check that packages are installed
uv pip list | grep fastapi
uv pip list | grep google-adk
```

---

## Configuration

### Step 1: Set Up Google Cloud Credentials

1. **Create a Service Account** in Google Cloud Console
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Grant roles: `Vertex AI User`, `AI Platform User`

2. **Download the JSON key file**
   - Click on the service account
   - Go to "Keys" tab
   - Add Key > Create new key > JSON
   - Save the file (e.g., `credentials.json`)

3. **Place credentials in your project**
   ```bash
   mkdir -p credentials
   mv ~/Downloads/credentials.json credentials/
   ```

### Step 2: Create Environment File

```bash
# Copy the example environment file
cp env.example .env
```

### Step 3: Edit Configuration

Open `.env` and configure:

```bash
# Required: Google Cloud Settings
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/opssage/credentials/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional: Application Settings
CHROMADB_PATH=./data/chromadb
LOG_LEVEL=INFO
USE_REAL_KNOWLEDGE_ADAPTER=true
```

**Important:** Use absolute paths for `GOOGLE_APPLICATION_CREDENTIALS`.

### Step 4: Verify Configuration

```bash
# Test Google Cloud authentication
export $(cat .env | xargs)
gcloud auth application-default print-access-token

# Should print an access token if configured correctly
```

---

## Starting the System

### Option 1: Quick Start (Backend Only)

Start just the API server for testing:

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Start the server
uvicorn apis.main:app --reload

# Or use the Makefile
make run
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Verify:** Visit http://localhost:8000 - you should see `{"status": "healthy"}`

### Option 2: With Web Dashboard

Start both backend and frontend:

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
uvicorn apis.main:app --reload
```

**Terminal 2 - Dashboard:**
```bash
cd dashboard
npm install  # First time only
npm run dev
```

**Access:**
- Dashboard: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 3: Docker Compose (Full Stack)

Start everything with one command:

```bash
# Build and start all services
make docker-up

# Or directly with docker-compose
docker-compose up -d
```

**Includes:**
- Backend API (port 8000)
- Dashboard (port 3000)
- ChromaDB (port 8001)
- Prometheus (port 9090)
- Grafana (port 3001)

**Check status:**
```bash
docker-compose ps
```

---

## First Alert

### Using the Web Dashboard

1. **Open the dashboard:** http://localhost:3000

2. **Navigate to "Alerts"** in the sidebar

3. **Fill in the alert form:**
   - Alert Name: `HighCPUUsage`
   - Severity: `critical`
   - Message: `CPU usage above 90% for 5 minutes`
   - Add labels:
     - service: `api-server`
     - namespace: `production`

4. **Click "Submit Alert"**

5. **View the analysis** - You'll be redirected to the incident detail page showing:
   - Root cause analysis
   - Evidence collected
   - Remediation recommendations

### Using the API

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "HighCPUUsage",
    "severity": "critical",
    "message": "CPU usage above 90% for 5 minutes",
    "labels": {
      "service": "api-server",
      "namespace": "production",
      "pod": "api-server-abc123"
    },
    "firing_condition": "cpu_usage > 90"
  }'
```

**Response:**
```json
{
  "incident_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "diagnostic_report": {
    "root_cause": "High CPU usage likely caused by...",
    "confidence_score": 0.75,
    "recommended_remediation": {
      "short_term_actions": ["Restart the pod", "..."],
      "long_term_actions": ["Optimize code", "..."]
    }
  }
}
```

### Using Python

```python
import requests

# Submit an alert
response = requests.post(
    "http://localhost:8000/api/v1/alerts",
    json={
        "alert_name": "HighMemoryUsage",
        "severity": "warning",
        "message": "Memory usage at 85%",
        "labels": {
            "service": "database",
            "namespace": "production"
        },
        "firing_condition": "memory_usage > 85"
    }
)

result = response.json()
print(f"Incident ID: {result['incident_id']}")
print(f"Root Cause: {result['diagnostic_report']['root_cause']}")
```

---

## Next Steps

### 1. Add Your Documentation

Upload your runbooks and playbooks so OpsSage can use them:

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@kubernetes-runbook.md" \
  -F "doc_type=playbook" \
  -F "category=kubernetes"

# Via Dashboard
# Navigate to "Documents" > Click "Upload" button
```

**Supported formats:** TXT, MD, PDF, DOCX, JSON

### 2. Explore the Dashboard

Visit http://localhost:3000 and explore:

- **Dashboard** - Overview of all incidents
- **Alerts** - Submit new alerts
- **Incidents** - View detailed analysis
- **Documents** - Manage knowledge base
- **Search** - Query your documentation

### 3. Integrate with Your Monitoring

Configure Prometheus AlertManager to send alerts to OpsSage:

```yaml
# alertmanager.yml
receivers:
  - name: 'opssage'
    webhook_configs:
      - url: 'http://opssage:8000/api/v1/alerts'
```

### 4. Review the Guides

- **[USER_GUIDE.md](USER_GUIDE.md)** - How to use all features
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - How the system works
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment
- **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete API docs

---

## Troubleshooting

### Issue: `ModuleNotFoundError`

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
uv sync
```

### Issue: Authentication errors with Google Cloud

**Solution:**
```bash
# Verify credentials path
cat .env | grep GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
gcloud auth application-default print-access-token

# Ensure service account has correct roles
gcloud projects get-iam-policy $GOOGLE_CLOUD_PROJECT
```

### Issue: Port already in use

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or use a different port
uvicorn apis.main:app --port 8080
```

### Issue: Dashboard can't connect to backend

**Solution:**
```bash
# Ensure backend is running
curl http://localhost:8000/api/v1/health

# Check proxy configuration
cat dashboard/vite.config.ts | grep proxy

# Restart dashboard
cd dashboard
npm run dev
```

### Issue: ChromaDB errors

**Solution:**
```bash
# Clear and recreate the database
rm -rf data/chromadb
mkdir -p data/chromadb

# Restart the server
make run
```

### Issue: No remediation suggestions

**Cause:** Empty knowledge base

**Solution:**
```bash
# Upload sample documentation
echo "# CPU Troubleshooting
High CPU usage can be caused by:
- Memory leaks
- Inefficient algorithms
- Too many requests

Solutions:
- Restart the service
- Scale horizontally
- Optimize code" > sample-runbook.md

curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@sample-runbook.md" \
  -F "doc_type=playbook"

# Submit alert again
```

---

## Testing the Installation

Run the test suite to verify everything is working:

```bash
# Activate environment
source .venv/bin/activate

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=sages --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Expected output:**
```
==================== test session starts ====================
collected 25 items

tests/test_api.py ........                             [ 32%]
tests/test_agents.py .......                           [ 60%]
tests/test_models.py .....                             [ 80%]
tests/test_rag.py .....                                [100%]

==================== 25 passed in 5.42s ====================
```

---

## Quick Reference

### Start Services

```bash
# Backend only
make run

# Docker Compose (full stack)
make docker-up

# Kubernetes
make kind-setup && make kind-deploy
```

### Stop Services

```bash
# Local (Ctrl+C in terminal)

# Docker Compose
make docker-down

# Kubernetes
make kind-teardown
```

### View Logs

```bash
# Local
tail -f logs/opssage.log

# Docker
docker logs -f opssage-backend

# Kubernetes
kubectl logs -f deployment/opssage -n opssage
```

### Common Commands

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List incidents
curl http://localhost:8000/api/v1/incidents

# List documents
curl http://localhost:8000/api/v1/documents/list

# Run tests
make test

# Format code
make format

# Clean up
make clean
```

---

## Getting Help

If you encounter issues:

1. **Check the logs** - Most errors are logged with details
2. **Review troubleshooting** - See section above
3. **Search documentation** - Check docs/ directory
4. **GitHub Issues** - https://github.com/ithaquaKr/opssage/issues
5. **Interactive API docs** - http://localhost:8000/docs

---

## What You've Learned

✅ How to install OpsSage
✅ How to configure Google Cloud credentials
✅ How to start the backend and dashboard
✅ How to submit your first alert
✅ How to view analysis results
✅ How to troubleshoot common issues

**Next:** Read the [USER_GUIDE.md](USER_GUIDE.md) to learn about all features in detail.

---

**Ready to deploy to production?** See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
