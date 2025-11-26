# Developer Guide

## Getting Started

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/opssage.git
cd opssage

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies including dev tools
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate

# Set up pre-commit hooks
uv run pre-commit install
```

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Model Configuration
WORKER_MODEL=gemini-2.5-flash
CRITIC_MODEL=gemini-2.5-pro

# Logging
LOG_LEVEL=INFO
```

## Code Style and Standards

### Python Style

We use Ruff for linting and formatting:

```bash
# Check code style
uv run ruff check sages tests

# Auto-fix issues
uv run ruff check --fix sages tests

# Format code
uv run ruff format sages tests
```

### Type Checking

We use mypy for static type checking:

```bash
uv run mypy sages
```

### Spell Checking

```bash
uv run codespell
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_models.py

# Run specific test
uv run pytest tests/test_models.py::test_alert_input_validation

# Run with coverage
uv run pytest --cov=sages --cov-report=html

# Run with verbose output
uv run pytest -v
```

### Writing Tests

Example test structure:

```python
import pytest
from sages.models import AlertInput

def test_alert_validation():
    """Test alert input validation."""
    alert = AlertInput(
        alert_name="TestAlert",
        severity="critical",
        message="Test",
        firing_condition="test > 10"
    )
    assert alert.alert_name == "TestAlert"

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await some_async_function()
    assert result is not None
```

### Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

```python
@pytest.fixture
def sample_alert() -> AlertInput:
    """Create a sample alert for testing."""
    return AlertInput(...)

@pytest.fixture
def context_store() -> ContextStore:
    """Create a fresh context store."""
    return ContextStore()
```

## Project Structure

```
sages/                   # Core agent package
├── __init__.py
├── agent.py              # Main agent entry point
├── configs.py           # Configuration
├── context_store.py     # Shared context store
├── logging.py           # Logging setup
├── models.py            # Pydantic models
├── orchestrator.py      # Pipeline orchestration
├── tools.py             # Capability adapters
├── utils.py             # Utility functions
├── validations.py       # Validation logic
└── subagents/
    ├── __init__.py
    ├── aica.py          # AICA agent
    ├── krea.py          # KREA agent
    └── rcara.py         # RCARA agent

apis/                    # FastAPI application
├── __init__.py
└── main.py             # API server and routes
```

## Adding New Features

### Adding a New Agent

1. Create agent file in `sages/subagents/`:

```python
"""
New Agent - Description
"""

from google.adk.agents import Agent
from google.adk.tools import agent_tool

from sages.configs import sage_configs
from sages.tools import some_tool

AGENT_SYSTEM_PROMPT = """Your agent prompt here..."""

def create_new_agent() -> Agent:
    """Create the new agent."""
    return Agent(
        name="new_agent",
        model=sage_configs.worker_model,
        description="Agent description",
        instruction=AGENT_SYSTEM_PROMPT,
        tools=[agent_tool(some_tool)],
        output_key="agent_output",
    )
```

2. Update orchestrator to include new agent
3. Add tests in `tests/test_new_agent.py`

### Adding a New Tool

1. Define abstract interface:

```python
class NewAdapter(ABC):
    @abstractmethod
    async def new_operation(self, param: str) -> dict[str, Any]:
        """Perform new operation."""
        pass
```

2. Implement mock version:

```python
class MockNewAdapter(NewAdapter):
    async def new_operation(self, param: str) -> dict[str, Any]:
        return {"result": f"Mock result for {param}"}
```

3. Create ADK tool wrapper:

```python
def new_tool(ctx: ToolContext, param: str) -> str:
    """
    Description of what this tool does.

    Args:
        param: Description of parameter

    Returns:
        JSON string with results
    """
    import asyncio
    import json

    adapter = MockNewAdapter()
    result = asyncio.run(adapter.new_operation(param))
    return json.dumps(result, indent=2)
```

4. Register tool with agent:

```python
from google.adk.tools import agent_tool

agent = Agent(
    name="agent",
    tools=[agent_tool(new_tool)],
    ...
)
```

### Adding New Models

1. Define Pydantic model in `sages/models.py`:

```python
class NewModel(BaseModel):
    """Description of model."""

    field1: str = Field(..., description="Field description")
    field2: int = Field(default=0, description="Field description")
```

2. Add validation tests:

```python
def test_new_model():
    model = NewModel(field1="test", field2=42)
    assert model.field1 == "test"
```

## API Development

### Adding New Endpoints

```python
@app.post("/api/v1/new-endpoint")
async def new_endpoint(data: InputModel) -> OutputModel:
    """
    Endpoint description.

    Args:
        data: Input data model

    Returns:
        Output data model
    """
    try:
        # Implementation
        result = process_data(data)
        return result
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### Testing API Endpoints

```python
from fastapi.testclient import TestClient
from apis.main import app

def test_new_endpoint():
    client = TestClient(app)
    response = client.post(
        "/api/v1/new-endpoint",
        json={"field": "value"}
    )
    assert response.status_code == 200
    assert response.json()["result"] == "expected"
```

## Debugging

### Local Development

```bash
# Run with debug logging
LOG_LEVEL=DEBUG uvicorn apis.main:app --reload

# Run with debugger
python -m debugpy --listen 5678 -m uvicorn apis.main:app --reload
```

### Debugging Agents

Enable verbose agent output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debugging Tests

```bash
# Run with print statements visible
uv run pytest -s

# Run with debugger on failure
uv run pytest --pdb
```

## Docker Development

### Building Images

```bash
# Build production image
docker build -t opssage:latest .

# Build dev image
docker build -f docker/Dockerfile.dev -t opssage:dev .
```

### Running Locally

```bash
# Run with environment file
docker run --env-file .env -p 8000:8000 opssage:latest

# Run with volume mount for development
docker run -v $(pwd):/app -p 8000:8000 opssage:dev
```

## Deployment

### Local Kubernetes

```bash
# Create local cluster (kind)
kind create cluster

# Build and load image
docker build -t opssage:latest .
kind load docker-image opssage:latest

# Install with Helm
helm install opssage ./deploy/helm
```

### Accessing Services

```bash
# Port forward to local
kubectl port-forward svc/opssage 8000:8000

# View logs
kubectl logs -f deployment/opssage

# Execute commands in pod
kubectl exec -it deployment/opssage -- /bin/bash
```

## CI/CD

### GitHub Actions

Workflows are defined in `.github/workflows/`:

- `ci.yaml`: Runs on every push/PR (lint, test, build)
- `cd.yaml`: Runs on master/tags (build, push, deploy)

### Local CI Testing

```bash
# Run linting locally
uv run ruff check sages tests
uv run mypy sages

# Run tests with coverage
uv run pytest --cov=sages

# Build Docker image
docker build -t opssage:test .
```

## Best Practices

### Code Organization

- Keep agents modular and focused
- Use dependency injection
- Prefer composition over inheritance
- Write comprehensive docstrings

### Error Handling

```python
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    # Handle gracefully
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Async/Await

```python
# Good: Use async/await for I/O operations
async def fetch_data():
    result = await external_api.get()
    return result

# Bad: Blocking I/O in async function
async def bad_fetch():
    result = requests.get(url)  # Blocks event loop!
    return result
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Test failures**: Check if dependencies are up to date (`uv sync`)
3. **Type errors**: Run `mypy` to identify issues
4. **Docker build fails**: Check Dockerfile and build context

### Getting Help

- Check existing issues on GitHub
- Review documentation in `docs/`
- Ask in project discussions
- Contact maintainers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run linting and tests
5. Submit pull request

See CONTRIBUTING.md for detailed guidelines.
