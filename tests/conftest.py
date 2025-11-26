"""
Pytest configuration and fixtures for OpsSage tests.
"""

from datetime import datetime

import pytest

from sages.context_store import ContextStore
from sages.models import AlertInput


@pytest.fixture
def sample_alert() -> AlertInput:
    """Create a sample alert for testing."""
    return AlertInput(
        alert_name="HighCPUUsage",
        severity="critical",
        message="CPU usage above 90% for 5 minutes",
        labels={
            "service": "api-server",
            "namespace": "production",
            "pod": "api-server-7d8f9b-xyz",
            "node": "node-1",
        },
        annotations={
            "summary": "High CPU usage detected",
            "description": "The CPU usage has been above 90% for the last 5 minutes",
        },
        firing_condition="cpu_usage > 90",
        timestamp=datetime.utcnow(),
    )


@pytest.fixture
def context_store() -> ContextStore:
    """Create a fresh context store for testing."""
    return ContextStore()
