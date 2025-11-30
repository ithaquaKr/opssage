# OpsSage Test Suite

Comprehensive testing for the OpsSage incident response system, including E2E scenarios and Telegram integration tests.

## Overview

The test suite includes:

1. **E2E Incident Tests** (`test_e2e_scenarios.py`) - Full pipeline tests with real incidents
2. **Telegram Integration Tests** (`test_telegram_integration.py`) - Notification system validation
3. **Scenario Definitions** (`test_scenarios.py`) - Reusable test scenarios

### E2E Pipeline Flow

**AICA** → **KREA** → **RCARA** → **Telegram Notification**

Each test scenario simulates a real Kubernetes incident and verifies:

- Alert ingestion and context extraction (AICA)
- Knowledge retrieval from RAG system (KREA)
- Root cause analysis and remediation suggestions (RCARA)
- Telegram notifications sent successfully

## Test Files

### 1. E2E Incident Scenarios (`test_e2e_scenarios.py`)

Tests complete incident analysis workflows with real scenarios.

**Scenarios** (defined in `test_scenarios.py`):

1. **Scenario 1**: Pod CrashLoopBackOff (Complexity: Low)

    - Misconfigured environment variable causing pod crashes

2. **Scenario 2**: Node CPU Exhaustion (Complexity: Medium)

    - Node resource saturation causing pod throttling

3. **Scenario 3**: Multi-Service Dependency Failure (Complexity: High)
    - Cascading auth service outage affecting dependent services

### 2. Telegram Integration Tests (`test_telegram_integration.py`)

Tests the Telegram notification system independently with real message delivery.

**Test Coverage:**

- Basic message sending with Markdown formatting
- Incident lifecycle notifications (start, complete, error)
- Test result summaries
- Message truncation for long content
- Concurrent notification handling
- Special character and emoji support
- Configuration validation
- Error handling when Telegram is disabled

## Running Tests

### Quick Start

```bash
# Run all tests (E2E + Telegram integration)
make test

# Run specific test files
pytest tests/test_e2e_scenarios.py -v -s
pytest tests/test_telegram_integration.py -v -s

# Run only E2E tests
pytest tests/test_e2e_scenarios.py -v

# Run only Telegram integration tests
pytest tests/test_telegram_integration.py -v
```

### Run Specific Tests

```bash
# Run a single test function
pytest tests/test_telegram_integration.py::test_send_simple_message -v -s

# Run all tests in a class
pytest tests/test_telegram_integration.py::TestTelegramNotifier -v

# Run tests with specific markers
pytest -m asyncio tests/ -v
```

### Using the Test Runner Script (E2E Only)

```bash
# Run all E2E scenarios with detailed output
python scripts/run_e2e_tests.py --verbose

# Run specific scenario
python scripts/run_e2e_tests.py --scenario scenario_1

# Save results to JSON
python scripts/run_e2e_tests.py --output results.json
```

## Prerequisites

### Required Configuration

1. **Configuration File**: Ensure `config.yaml` exists and is properly configured

    ```bash
    cp config.example.yaml config.yaml
    # Edit config.yaml with your settings
    ```

2. **Environment Variables**: Set required API keys

    ```bash
    export GEMINI_API_KEY="your-gemini-api-key"
    export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
    export TELEGRAM_CHAT_ID="your-telegram-chat-id"
    ```

3. **Python Dependencies**: Install test dependencies

    ```bash
    # Using uv (recommended)
    uv pip install -e ".[dev]"

    # Or using pip
    pip install -e ".[dev]"
    ```

### Setting Up Telegram Bot

To run Telegram integration tests, you need to:

1. **Create a Telegram Bot**:

    - Open Telegram and search for [@BotFather](https://t.me/botfather)
    - Send `/newbot` and follow the prompts
    - Copy the bot token provided

2. **Get Your Chat ID**:

    - Start a chat with your bot
    - Send any message to it
    - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
    - Find your `chat_id` in the JSON response

3. **Configure OpsSage**:

    ```yaml
    # config.yaml
    telegram:
        enabled: true
        bot_token: ${TELEGRAM_BOT_TOKEN}
        chat_id: ${TELEGRAM_CHAT_ID}
    ```

### Optional Setup

- **Knowledge Base**: Upload relevant runbooks/documentation for better E2E test results

    ```bash
    make upload-doc DOC=path/to/runbook.pdf
    ```

## What Gets Validated

Each test verifies:

- ✅ Diagnostic report structure is complete
- ✅ Root cause is identified (min 10 characters)
- ✅ Confidence score is valid (0.0 to 1.0)
- ✅ Reasoning steps provided (min 2 steps)
- ✅ Supporting evidence included
- ✅ Short-term and long-term remediation actions suggested
- ✅ Telegram notification sent successfully

## Test Output

Tests send Telegram notifications with:

- **Start**: When test begins
- **Complete**: When analysis finishes (includes diagnostic report)
- **Error**: If test fails

Check your Telegram chat to see real-time notifications!

## Example Test Run

```bash
$ make test

================================ test session starts =================================
tests/test_e2e_scenarios.py::test_scenario_1_crashloopbackoff PASSED
tests/test_e2e_scenarios.py::test_scenario_2_node_cpu_exhaustion PASSED
tests/test_e2e_scenarios.py::test_scenario_3_multi_service_failure PASSED

================================ 3 passed in 45.23s ==================================
```

## Test Output Examples

### E2E Test Output

```bash
$ pytest tests/test_e2e_scenarios.py -v

tests/test_e2e_scenarios.py::test_scenario_1_crashloopbackoff PASSED
tests/test_e2e_scenarios.py::test_scenario_2_cpu_exhaustion PASSED
tests/test_e2e_scenarios.py::test_scenario_3_dependency_failure PASSED

3 passed in 45.23s
```

### Telegram Integration Test Output

```bash
$ pytest tests/test_telegram_integration.py -v

tests/test_telegram_integration.py::TestTelegramNotifier::test_send_simple_message PASSED
tests/test_telegram_integration.py::TestTelegramNotifier::test_send_incident_start_notification PASSED
tests/test_telegram_integration.py::TestTelegramNotifier::test_send_incident_complete_notification PASSED
tests/test_telegram_integration.py::test_complete_notification_flow PASSED

4 passed in 12.45s
```

### Telegram Notifications

When running tests, you'll receive notifications in your Telegram chat:

**Start Notification:**

```
🚨 Incident Analysis Started

Incident ID: test-incident-1234567890
Alert: TestAlert
Severity: CRITICAL
Namespace: test-namespace
Service: test-service

Message: Test alert for Telegram integration

⏳ Analysis in progress...
```

**Completion Notification:**

```
✅ Incident Analysis Complete

Incident ID: test-incident-1234567890
Alert: TestAlert
Duration: 12.5s

🎯 Root Cause (Confidence: 85%):
Test root cause: Configuration error in test-service deployment

🔧 Immediate Actions:
  • Rollback the deployment to previous stable version
  • Fix the DATABASE_URL environment variable in config map
  • Restart affected pods after config update

📊 Analysis Steps: 3
📝 Evidence Items: 3
```

## Test Structure

### Test Organization

```
tests/
├── README.md                      # This file
├── test_e2e_scenarios.py          # End-to-end incident analysis tests
├── test_telegram_integration.py   # Telegram notification tests
└── test_scenarios.py              # Test scenario definitions
```

### Test Fixtures

Both test files use pytest fixtures for:

- `orchestrator` - The incident orchestrator instance
- `sample_alert` - Pre-configured alert for testing
- `sample_diagnostic_report` - Sample analysis results
- `result_collector` - Collects test results for reporting

## Troubleshooting

### Common Issues

**Telegram notifications not working**

- ✅ Check `config.yaml` telegram settings
- ✅ Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment variables
- ✅ Ensure bot has been started with `/start` command
- ✅ Check bot token is valid (test with `getMe` API)

**GEMINI_API_KEY errors**

- ✅ Ensure API key is valid and set
- ✅ Check API quota hasn't been exceeded
- ✅ Verify API key has proper permissions

**Tests timeout**

- ✅ Increase timeout in pytest configuration
- ✅ Check network connectivity to Gemini API
- ✅ Verify Telegram API is accessible

**RAG returns no results**

- ✅ Upload relevant documents first using `make upload-doc`
- ✅ Check ChromaDB is running (`docker ps | grep chroma`)
- ✅ Verify knowledge base path in config.yaml

**Test skipped with "Telegram not configured"**

- ℹ️ This is expected if Telegram credentials are not set
- ℹ️ Set up Telegram bot (see "Setting Up Telegram Bot" above)
- ℹ️ Or run only E2E tests: `pytest tests/test_e2e_scenarios.py`

### Debugging Tips

```bash
# Run tests with verbose output
pytest tests/ -v -s

# Run tests with detailed logging
pytest tests/ -v -s --log-cli-level=DEBUG

# Run only fast tests (skip integration tests)
pytest tests/ -v -m "not asyncio"

# Run with coverage report
pytest tests/ --cov=sages --cov-report=html
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
    test:
        runs-on: ubuntu-latest

        steps:
            - uses: actions/checkout@v3

            - name: Set up Python
              uses: actions/setup-python@v4
              with:
                  python-version: "3.13"

            - name: Install dependencies
              run: |
                  pip install uv
                  uv pip install -e ".[dev]"

            - name: Run tests
              env:
                  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
                  TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
                  TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
              run: |
                  pytest tests/ -v --cov=sages
```

## Writing New Tests

### Adding E2E Scenarios

1. Add scenario definition to `test_scenarios.py`
2. Create test function in `test_e2e_scenarios.py`
3. Follow existing pattern for consistency

### Adding Telegram Tests

1. Add test to `test_telegram_integration.py`
2. Use `@pytest.mark.asyncio` for async tests
3. Skip test if Telegram not configured:

    ```python
    if not notifier.enabled:
        pytest.skip("Telegram not configured")
    ```

### Example Custom Test

```python
@pytest.mark.asyncio
async def test_custom_scenario():
    """Test custom incident scenario."""
    # Create alert
    alert = AlertInput(
        alert_name="CustomAlert",
        severity="warning",
        message="Custom test message",
        labels={"namespace": "custom"},
        annotations={},
        firing_condition="custom_metric > 0",
        timestamp=datetime.now(),
    )

    # Run analysis
    orchestrator = create_orchestrator()
    incident_id, report = await orchestrator.analyze_incident(alert)

    # Validate results
    assert report.root_cause
    assert report.confidence_score > 0.5
```
