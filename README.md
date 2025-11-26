# OpsSage

**Multi-Agent Incident Analysis & Remediation System**

OpsSage is an AI-powered advisory system for incident analysis and remediation recommendations in SRE workflows. It uses a multi-agent architecture built with Google ADK (Agent Development Kit) to provide comprehensive incident analysis through three specialized agents: AICA, KREA, and RCARA.

## Overview

OpsSage implements a deterministic multi-stage pipeline for incident analysis:

```
Alert → AICA → KREA → RCARA → Diagnostic Report
```

1. **AICA** (Alert Ingestion & Context Agent): Analyzes alerts and builds primary context
2. **KREA** (Knowledge Retrieval & Enrichment Agent): Enriches context with relevant knowledge
3. **RCARA** (Root Cause Analysis & Remediation Agent): Performs root cause analysis and generates remediation recommendations

## Features

- **Multi-Agent Architecture**: Modular agents with clear responsibilities following ADK best practices
- **Structured Message Contracts**: Type-safe communication between agents using Pydantic models
- **Shared Context Store**: Thread-safe storage for incident analysis state
- **Capability Adapters**: Pluggable tool interfaces for metrics, logs, events, and knowledge retrieval
- **RESTful API**: FastAPI-based server with health checks and incident management endpoints
- **Kubernetes-Native**: Helm charts and manifests for production deployment
- **Comprehensive Testing**: Unit tests, integration tests, and API tests
- **CI/CD Pipeline**: Automated testing, linting, and deployment via GitHub Actions

## Architecture

### Agent Pipeline

```mermaid
graph LR
    A[Alert] --> AICA[AICA Agent]
    AICA --> |Primary Context| KREA[KREA Agent]
    KREA --> |Enhanced Context| RCARA[RCARA Agent]
    RCARA --> |Diagnostic Report| Output[Remediation Plan]

    AICA -.-> M[Metrics API]
    AICA -.-> L[Logs API]
    AICA -.-> E[Events API]

    KREA -.-> V[Vector Store]
    KREA -.-> D[Docs]
    KREA -.-> P[Playbooks]
```

### Components

- **Agents** (`sages/subagents/`): AICA, KREA, RCARA agent implementations
- **Models** (`sages/models.py`): Pydantic models for message contracts
- **Tools** (`sages/tools.py`): Capability adapters for external systems
- **Context Store** (`sages/context_store.py`): Shared state management
- **Orchestrator** (`sages/orchestrator.py`): Coordinates agent pipeline
- **API** (`apis/`): FastAPI server for external access

## Quick Start

### Prerequisites

- Python 3.10+ (3.13 recommended)
- [uv](https://github.com/astral-sh/uv) for dependency management
- Google Cloud credentials (for Google ADK and Gemini models)

### Installation

```bash
# Clone the repository
git clone https://github.com/ithaquaKr/opssage.git
cd opssage

# Install dependencies using uv
uv sync

# Set up environment variables
cp env.example .env
# Edit .env with your Google Cloud credentials
```

### Running Locally

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the FastAPI server
uvicorn apis.main:app --reload

# The API will be available at http://localhost:8000
```

### Running with Docker

```bash
# Build the Docker image
docker build -t opssage:latest .

# Run the container
docker run -p 8000:8000 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json \
  opssage:latest
```

## Usage

### Ingesting an Alert

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
      "pod": "api-server-7d8f9b-xyz"
    },
    "firing_condition": "cpu_usage > 90"
  }'
```

### Response

```json
{
  "incident_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "diagnostic_report": {
    "root_cause": "Memory leak causing excessive CPU usage",
    "reasoning_steps": [...],
    "supporting_evidence": [...],
    "confidence_score": 0.85,
    "recommended_remediation": {
      "short_term_actions": [
        "Restart the affected pod",
        "Monitor CPU and memory usage"
      ],
      "long_term_actions": [
        "Fix memory leak in application code",
        "Implement better monitoring"
      ]
    }
  }
}
```

### Retrieving an Incident

```bash
curl http://localhost:8000/api/v1/incidents/{incident_id}
```

### Listing All Incidents

```bash
# List all incidents
curl http://localhost:8000/api/v1/incidents

# Filter by status
curl http://localhost:8000/api/v1/incidents?status=completed
```

## Development

### Project Structure

```
opssage/
├── sages/                  # Core agent package
│   ├── subagents/         # Agent implementations
│   │   ├── aica.py       # Alert Ingestion & Context Agent
│   │   ├── krea.py       # Knowledge Retrieval & Enrichment Agent
│   │   └── rcara.py      # Root Cause Analysis & Remediation Agent
│   ├── models.py          # Pydantic models for message contracts
│   ├── tools.py           # Capability adapters
│   ├── context_store.py   # Shared context store
│   ├── orchestrator.py    # Pipeline orchestration
│   └── configs.py        # Configuration
├── apis/                  # FastAPI application
│   └── main.py           # API server and routes
├── tests/                 # Test suite
├── deploy/               # Deployment configurations
│   └── helm/            # Helm charts
├── docker/              # Docker configurations
├── docs/                # Documentation
└── pyproject.toml       # Project metadata and dependencies
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=sages --cov-report=html

# Run specific test file
uv run pytest tests/test_models.py
```

### Linting and Formatting

```bash
# Run ruff linter
uv run ruff check sages tests

# Auto-fix issues
uv run ruff check --fix sages tests

# Format code
uv run ruff format sages tests

# Type checking
uv run mypy sages
```

## Deployment

### Kubernetes with Helm

```bash
# Install OpsSage using Helm
helm install opssage ./deploy/helm \
  --set image.tag=0.1.0 \
  --set googleCloud.projectId=your-project-id

# Upgrade deployment
helm upgrade opssage ./deploy/helm

# Uninstall
helm uninstall opssage
```

### Configuration

Key configuration options in `deploy/helm/values.yaml`:

- `replicaCount`: Number of replicas (default: 2)
- `resources`: CPU and memory limits
- `autoscaling`: HPA configuration
- `policy.allowAutoRemediate`: Enable/disable auto-remediation (default: false)
- `googleCloud`: Google Cloud configuration

**Important Policy Note**: By default, OpsSage requires manual approval for all remediation actions. To enable automatic remediation, update `policy.allowAutoRemediate` to `true` in your Helm values. However, this is not recommended for production environments without additional safeguards.

## API Documentation

Once the server is running, interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

- `GET /` - Health check
- `GET /api/v1/health` - Detailed health status
- `GET /api/v1/readiness` - Readiness probe
- `POST /api/v1/alerts` - Ingest an alert
- `GET /api/v1/incidents` - List incidents
- `GET /api/v1/incidents/{id}` - Get incident details
- `DELETE /api/v1/incidents/{id}` - Delete incident

## Extending OpsSage

### Adding New Tools

To add a new capability adapter:

1. Define an abstract interface in `sages/tools.py`:

```python
class NewAdapter(ABC):
    @abstractmethod
    async def new_operation(self, params) -> result:
        pass
```

2. Implement a mock version for testing
3. Create an ADK tool wrapper function
4. Add the tool to the appropriate agent(s)

### Adding New Agents

To add a new agent to the pipeline:

1. Create a new file in `sages/subagents/`
2. Define the agent's system prompt
3. Create agent instance with appropriate tools
4. Update `orchestrator.py` to include the new agent in the pipeline
5. Update models if new message contracts are needed

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please see the contributing guidelines for more information.

## Support

For issues and questions:

- GitHub Issues: <https://github.com/ithaquaKr/opssage/issues>
- Documentation: <https://github.com/ithaquaKr/opssage/docs>
