# OpsSage Quick Start Guide

Get OpsSage up and running in 5 minutes!

## Prerequisites

- Python 3.10 or higher (3.13 recommended)
- [uv](https://github.com/astral-sh/uv) package manager
- Google Cloud credentials with access to Vertex AI and Gemini models

## Step 1: Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/opssage.git
cd opssage

# Install all dependencies
uv sync
```

## Step 2: Configure Environment

```bash
# Copy the example environment file
cp env.example .env

# Edit .env with your Google Cloud credentials
# Required variables:
# - GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
# - GOOGLE_CLOUD_PROJECT=your-project-id
```

## Step 3: Run the Server

```bash
# Activate the virtual environment
source .venv/bin/activate

# Start the API server
uvicorn apis.main:app --reload

# Or use the Makefile
make run
```

The API will be available at `http://localhost:8000`

## Step 4: Test the System

### Using curl

```bash
# Send a test alert
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
    "annotations": {
      "summary": "High CPU detected",
      "description": "CPU has been above threshold"
    },
    "firing_condition": "cpu_usage > 90"
  }'
```

### Using Python

```python
import requests

alert = {
    "alert_name": "HighCPUUsage",
    "severity": "critical",
    "message": "CPU usage above 90% for 5 minutes",
    "labels": {
        "service": "api-server",
        "namespace": "production",
        "pod": "api-server-abc123"
    },
    "firing_condition": "cpu_usage > 90"
}

response = requests.post(
    "http://localhost:8000/api/v1/alerts",
    json=alert
)

print(response.json())
```

## Step 5: View Results

The response will contain:
- Incident ID
- Root cause analysis
- Supporting evidence
- Remediation recommendations

Example response:

```json
{
  "incident_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "diagnostic_report": {
    "root_cause": "Memory leak causing excessive CPU usage",
    "reasoning_steps": [
      "Analyzed CPU metrics showing sustained high usage",
      "Correlated with memory growth pattern",
      "Found error logs indicating OOM conditions"
    ],
    "supporting_evidence": [
      "CPU usage at 95% for 10 minutes",
      "Memory usage increased from 2GB to 7.5GB",
      "OOMKilled events in pod logs"
    ],
    "confidence_score": 0.85,
    "recommended_remediation": {
      "short_term_actions": [
        "Restart the affected pod to free memory",
        "Increase memory limits temporarily",
        "Monitor for recurrence"
      ],
      "long_term_actions": [
        "Fix memory leak in application code",
        "Implement proper memory profiling",
        "Add memory usage alerts"
      ]
    }
  }
}
```

## Next Steps

### Explore the API

Visit the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Run Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov
```

### Development

```bash
# Format code
make format

# Run linting
make lint

# Clean up
make clean
```

### Docker Deployment

```bash
# Build Docker image
make docker-build

# Run in Docker
make docker-run
```

### Kubernetes Deployment

```bash
# Install with Helm
make helm-install

# View templates
make helm-template
```

## Troubleshooting

### Import Errors

Ensure the virtual environment is activated:
```bash
source .venv/bin/activate
```

### Authentication Errors

Check that your Google Cloud credentials are properly configured:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
gcloud auth application-default login
```

### Port Already in Use

Change the port:
```bash
uvicorn sages.api:app --port 8080
```

## Learn More

- **Full Documentation**: See [README.md](README.md)
- **Architecture**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Developer Guide**: See [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)

## Getting Help

- Check [GitHub Issues](https://github.com/yourusername/opssage/issues)
- Read the documentation in `docs/`
- Run `make help` to see all available commands
