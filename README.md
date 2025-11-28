# OpsSage

**AI-Powered Incident Analysis & Remediation System**

OpsSage is an intelligent system that automatically analyzes alerts, investigates incidents, and provides remediation recommendations for your infrastructure. It uses three AI agents working together to understand problems and suggest solutions.

---

## What Does It Do?

When an alert fires (high CPU, pod crash, etc.), OpsSage:

1. **Investigates** - Collects logs, metrics, and events related to the alert
2. **Analyzes** - Searches your documentation for similar issues
3. **Diagnoses** - Determines the root cause with reasoning
4. **Recommends** - Suggests both quick fixes and long-term solutions

All automatically, in seconds.

---

## Quick Example

**Input:** Alert about high CPU usage

**Output:**
```
Root Cause: Memory leak in api-server causing CPU spikes
Confidence: 85%

Quick Fixes:
- Restart the api-server pod
- Increase memory limits to 4Gi

Long-Term Solutions:
- Fix memory leak in application code
- Add memory profiling
- Set up automated alerts for memory growth
```

---

## How It Works

OpsSage uses three specialized AI agents:

```
Alert → AICA → KREA → RCARA → Solution
```

1. **AICA** (Alert Analysis) - Understands the alert and gathers evidence
2. **KREA** (Knowledge Search) - Finds relevant documentation and past incidents
3. **RCARA** (Root Cause) - Diagnoses the problem and suggests fixes

---

## Getting Started

### Prerequisites

- Python 3.10+ (Python 3.13 recommended)
- [uv](https://github.com/astral-sh/uv) package manager
- Google Cloud account (for AI models)

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/ithaquaKr/opssage.git
cd opssage

# 2. Install dependencies
uv sync

# 3. Set up credentials
cp env.example .env
# Edit .env and add your Google Cloud credentials

# 4. Start the server
source .venv/bin/activate
uvicorn apis.main:app --reload
```

The API will be available at `http://localhost:8000`

**See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.**

---

## Usage

### Web Dashboard (Recommended)

```bash
cd dashboard
npm install
npm run dev
```

Access the dashboard at `http://localhost:3000` to:
- Submit alerts through a form
- View all incidents and their analysis
- Upload documentation and runbooks
- Search your knowledge base

### API (For Integration)

Submit an alert:

```bash
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "alert_name": "HighCPUUsage",
    "severity": "critical",
    "message": "CPU usage above 90%",
    "labels": {
      "service": "api-server",
      "pod": "api-server-xyz"
    }
  }'
```

Get analysis results:

```bash
curl http://localhost:8000/api/v1/incidents/{incident_id}
```

---

## Key Features

### 1. Intelligent Analysis
- Automatic evidence collection from logs, metrics, and events
- Root cause analysis with reasoning steps
- Confidence scoring

### 2. Knowledge Base
- Upload your runbooks, playbooks, and documentation
- Semantic search finds relevant info automatically
- Supports TXT, MD, PDF, DOCX, JSON

### 3. Web Dashboard
- Modern React UI
- Real-time incident tracking
- Document management
- Search interface

### 4. Production Ready
- Docker and Kubernetes deployment
- Health checks and monitoring
- Horizontal scaling
- Prometheus metrics

---

## Deployment Options

### Development (Easiest)
```bash
# Local Python server
make run
```

### Docker Compose (Recommended for Testing)
```bash
# Complete stack with monitoring
make docker-up
```
Includes: Backend, Dashboard, ChromaDB, Prometheus, Grafana

### Kubernetes (Production)
```bash
# Deploy with Helm
helm install opssage ./deploy/helm
```

**See deployment guides:**
- [Docker Compose Guide](docs/DOCKER_COMPOSE.md)
- [Kubernetes Guide](docs/KUBERNETES.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | Detailed setup and first steps |
| [USER_GUIDE.md](USER_GUIDE.md) | How to use OpsSage |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and components |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Complete API documentation |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deployment options and configuration |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Contributing and extending OpsSage |

---

## Project Structure

```
opssage/
├── sages/              # Core AI agents and logic
│   ├── subagents/     # AICA, KREA, RCARA agents
│   ├── rag/           # Knowledge base and search
│   └── tools.py       # Tool adapters
├── apis/              # FastAPI backend
├── dashboard/         # React web UI
├── deploy/            # Kubernetes and Helm charts
├── tests/             # Test suite
└── docs/              # Documentation
```

---

## Common Tasks

### Add Documentation
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@runbook.md" \
  -F "doc_type=playbook"
```

### List Incidents
```bash
curl http://localhost:8000/api/v1/incidents
```

### Run Tests
```bash
uv run pytest
```

### Check Logs
```bash
# Local
tail -f logs/opssage.log

# Docker
docker logs opssage-backend

# Kubernetes
kubectl logs -f deployment/opssage
```

---

## Technology Stack

- **AI Framework**: Google ADK (Agent Development Kit)
- **AI Models**: Google Gemini (via Vertex AI)
- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Tailwind CSS
- **Knowledge Base**: ChromaDB (vector database)
- **Deployment**: Docker, Kubernetes, Helm

---

## Configuration

Key environment variables:

```bash
# Required
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional
CHROMADB_PATH=./data/chromadb
LOG_LEVEL=INFO
USE_REAL_KNOWLEDGE_ADAPTER=true
```

See [CONFIGURATION.md](docs/CONFIGURATION.md) for all options.

---

## Troubleshooting

### Server won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Verify credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Check dependencies
uv sync
```

### No analysis results
```bash
# Ensure knowledge base has documents
curl http://localhost:8000/api/v1/documents/list

# Upload sample documentation
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@sample-runbook.md" \
  -F "doc_type=playbook"
```

### Dashboard not connecting
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Verify proxy configuration in dashboard/vite.config.ts
```

---

## License

Apache License 2.0

---

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/ithaquaKr/opssage/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ithaquaKr/opssage/discussions)

---

## What's Next?

1. **[Get Started](GETTING_STARTED.md)** - Set up OpsSage
2. **[User Guide](USER_GUIDE.md)** - Learn to use the system
3. **[Upload Docs](docs/KNOWLEDGE_BASE.md)** - Add your runbooks
4. **[Deploy](docs/DEPLOYMENT.md)** - Run in production

---

**Built with ❤️ for SREs and DevOps teams**
