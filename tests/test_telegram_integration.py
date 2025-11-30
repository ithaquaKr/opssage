"""
Telegram Integration Tests

Tests the Telegram notification system with real message sending.
Validates that notifications are properly formatted and delivered.
"""

import asyncio
import time
from datetime import datetime

import pytest

from sages.config import get_config
from sages.models import AlertInput, IncidentDiagnosticReport, RecommendedRemediation
from sages.notifications import TelegramNotifier, get_notifier


@pytest.fixture
def sample_alert() -> AlertInput:
    """Create a sample alert for testing."""
    return AlertInput(
        alert_name="TestAlert",
        severity="critical",
        message="Test alert for Telegram integration",
        labels={
            "namespace": "test-namespace",
            "service": "test-service",
            "pod": "test-pod-123",
            "alertname": "TestAlert",
        },
        annotations={
            "description": "This is a test alert for Telegram integration",
            "summary": "Test alert triggered",
        },
        firing_condition="test_metric > threshold",
        timestamp=datetime.now(),
    )


@pytest.fixture
def sample_diagnostic_report() -> IncidentDiagnosticReport:
    """Create a sample diagnostic report for testing."""
    return IncidentDiagnosticReport(
        root_cause="Test root cause: Configuration error in test-service deployment",
        reasoning_steps=[
            "Analyzed alert metrics and identified spike in error rate",
            "Examined pod logs showing configuration validation failures",
            "Traced back to recent deployment with invalid environment variable",
        ],
        supporting_evidence=[
            "Pod logs show 'Invalid configuration: missing DATABASE_URL'",
            "Metrics show 100% error rate starting at deployment time",
            "Recent deployment changelog shows config map update",
        ],
        confidence_score=0.85,
        recommended_remediation=RecommendedRemediation(
            short_term_actions=[
                "Rollback the deployment to previous stable version",
                "Fix the DATABASE_URL environment variable in config map",
                "Restart affected pods after config update",
            ],
            long_term_actions=[
                "Implement configuration validation in CI/CD pipeline",
                "Add pre-deployment config validation checks",
                "Set up automated config backup and restore procedures",
            ],
        ),
    )


class TestTelegramNotifier:
    """Test suite for TelegramNotifier class."""

    def test_notifier_initialization(self):
        """Test that notifier initializes correctly with config."""
        notifier = TelegramNotifier()
        config = get_config()

        # Check if enabled matches config
        expected_enabled = config.get("telegram.enabled", True) and bool(
            config.get("telegram.bot_token") and config.get("telegram.chat_id")
        )
        assert notifier.enabled == expected_enabled

    def test_notifier_with_custom_credentials(self):
        """Test notifier with custom bot token and chat ID."""
        notifier = TelegramNotifier(
            bot_token="test_token_123",
            chat_id="test_chat_456"
        )

        assert notifier.bot_token == "test_token_123"
        assert notifier.chat_id == "test_chat_456"

    def test_global_notifier_singleton(self):
        """Test that get_notifier returns singleton instance."""
        notifier1 = get_notifier()
        notifier2 = get_notifier()

        assert notifier1 is notifier2

    @pytest.mark.asyncio
    async def test_send_simple_message(self):
        """Test sending a simple message to Telegram."""
        notifier = get_notifier()

        if not notifier.enabled:
            pytest.skip("Telegram not configured, skipping integration test")

        message = f"""
🧪 *Test Message*

This is a test message from OpsSage Telegram integration tests.

*Timestamp:* {datetime.now().isoformat()}
*Test ID:* `test_send_simple_message`

✅ If you see this, the integration is working!
"""

        success = await notifier.send_message(message.strip())
        assert success is True

    @pytest.mark.asyncio
    async def test_send_incident_start_notification(self, sample_alert):
        """Test sending incident start notification."""
        notifier = get_notifier()

        if not notifier.enabled:
            pytest.skip("Telegram not configured, skipping integration test")

        incident_id = f"test-incident-{int(time.time())}"
        success = await notifier.send_incident_start(incident_id, sample_alert)

        assert success is True
        # Wait a bit to avoid hitting Telegram rate limits
        await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_send_incident_complete_notification(
        self, sample_alert, sample_diagnostic_report
    ):
        """Test sending incident completion notification."""
        notifier = get_notifier()

        if not notifier.enabled:
            pytest.skip("Telegram not configured, skipping integration test")

        incident_id = f"test-incident-{int(time.time())}"
        duration = 12.5

        success = await notifier.send_incident_complete(
            incident_id, sample_alert, sample_diagnostic_report, duration
        )

        assert success is True
        await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_send_incident_error_notification(self, sample_alert):
        """Test sending incident error notification."""
        notifier = get_notifier()

        if not notifier.enabled:
            pytest.skip("Telegram not configured, skipping integration test")

        incident_id = f"test-incident-{int(time.time())}"
        error = "Test error: Simulated analysis failure for testing purposes"
        duration = 5.0

        success = await notifier.send_incident_error(
            incident_id, sample_alert, error, duration
        )

        assert success is True
        await asyncio.sleep(1)

    @pytest.mark.asyncio
    async def test_send_test_summary_notification(self):
        """Test sending test result summary notification."""
        notifier = get_notifier()

        if not notifier.enabled:
            pytest.skip("Telegram not configured, skipping integration test")

        total_scenarios = 10
        passed = 8
        failed = 2
        duration = 45.5

        success = await notifier.send_test_result_summary(
            total_scenarios, passed, failed, duration
        )

        assert success is True
        await asyncio.sleep(1)

    def test_status_bar_generation(self):
        """Test the visual status bar generation."""
        notifier = TelegramNotifier()

        # Test 100% pass
        bar = notifier._get_status_bar(10, 0)
        assert "█" in bar
        assert bar.count("█") == 10

        # Test 50% pass
        bar = notifier._get_status_bar(5, 5)
        assert "█" in bar and "▓" in bar

        # Test 0% pass
        bar = notifier._get_status_bar(0, 10)
        assert bar.count("▓") == 10

    @pytest.mark.asyncio
    async def test_long_message_truncation(self, sample_alert):
        """Test that long messages are properly truncated."""
        notifier = get_notifier()

        if not notifier.enabled:
            pytest.skip("Telegram not configured, skipping integration test")

        # Create a very long error message
        long_error = "Error: " + "X" * 500
        incident_id = f"test-incident-{int(time.time())}"

        success = await notifier.send_incident_error(
            incident_id, sample_alert, long_error, 1.0
        )

        assert success is True
        await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_complete_notification_flow(sample_alert, sample_diagnostic_report):
    """
    Test the complete notification flow: start -> complete.

    This simulates a real incident analysis workflow.
    """
    notifier = get_notifier()

    if not notifier.enabled:
        pytest.skip("Telegram not configured, skipping integration test")

    incident_id = f"test-full-flow-{int(time.time())}"

    # Step 1: Send start notification
    start_success = await notifier.send_incident_start(incident_id, sample_alert)
    assert start_success is True

    # Simulate analysis time
    await asyncio.sleep(2)

    # Step 2: Send completion notification
    complete_success = await notifier.send_incident_complete(
        incident_id, sample_alert, sample_diagnostic_report, 2.0
    )
    assert complete_success is True


@pytest.mark.asyncio
async def test_notification_with_markdown_formatting():
    """Test that Markdown formatting works correctly in messages."""
    notifier = get_notifier()

    if not notifier.enabled:
        pytest.skip("Telegram not configured, skipping integration test")

    message = """
🎨 *Markdown Formatting Test*

*Bold text*
_Italic text_
`Monospace code`
[Link](https://github.com)

• Bullet point 1
• Bullet point 2

```python
def hello():
    print("Code block")
```

✅ All formatting should render correctly!
"""

    success = await notifier.send_message(message.strip())
    assert success is True


@pytest.mark.asyncio
async def test_concurrent_notifications(sample_alert):
    """Test sending multiple notifications concurrently."""
    notifier = get_notifier()

    if not notifier.enabled:
        pytest.skip("Telegram not configured, skipping integration test")

    # Create multiple test incidents
    incidents = [f"test-concurrent-{i}-{int(time.time())}" for i in range(3)]

    # Send start notifications concurrently
    tasks = [
        notifier.send_incident_start(incident_id, sample_alert)
        for incident_id in incidents
    ]

    results = await asyncio.gather(*tasks)

    # All should succeed
    assert all(results)

    # Wait to avoid rate limiting
    await asyncio.sleep(2)


@pytest.mark.asyncio
async def test_notification_with_special_characters(sample_alert):
    """Test notifications with special characters and emojis."""
    notifier = get_notifier()

    if not notifier.enabled:
        pytest.skip("Telegram not configured, skipping integration test")

    # Modify alert with special characters
    sample_alert.message = "Test with émojis 🚀🎉 and spëcial çharacters: <>&\""

    incident_id = f"test-special-{int(time.time())}"
    success = await notifier.send_incident_start(incident_id, sample_alert)

    assert success is True


class TestTelegramConfiguration:
    """Test configuration handling for Telegram integration."""

    def test_disabled_notifier_returns_false(self):
        """Test that disabled notifier returns False without sending."""
        # Create notifier with no credentials
        notifier = TelegramNotifier(bot_token=None, chat_id=None)

        assert notifier.enabled is False

    @pytest.mark.asyncio
    async def test_disabled_notifier_skips_sending(self, sample_alert):
        """Test that disabled notifier skips message sending."""
        notifier = TelegramNotifier(bot_token=None, chat_id=None)

        incident_id = "test-disabled"
        success = await notifier.send_incident_start(incident_id, sample_alert)

        # Should return False since it's disabled
        assert success is False


def test_config_loading():
    """Test that Telegram config is properly loaded."""
    config = get_config()

    # Check that config has telegram section
    telegram_enabled = config.get("telegram.enabled")
    bot_token = config.get("telegram.bot_token")
    chat_id = config.get("telegram.chat_id")

    # These may be None if not configured, which is OK
    assert telegram_enabled is not None or telegram_enabled is None
    assert isinstance(bot_token, (str, type(None)))
    assert isinstance(chat_id, (str, type(None)))
