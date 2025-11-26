"""
Tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient

from apis.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "OpsSage"


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data


def test_readiness_check(client):
    """Test the readiness check endpoint."""
    response = client.get("/api/v1/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "agents" in data


def test_list_incidents_empty(client):
    """Test listing incidents when none exist."""
    response = client.get("/api/v1/incidents")
    assert response.status_code == 200
    # Note: May have incidents from other tests if using shared state
    data = response.json()
    assert isinstance(data, list)


def test_get_nonexistent_incident(client):
    """Test getting a nonexistent incident."""
    response = client.get("/api/v1/incidents/nonexistent-id")
    assert response.status_code == 404


def test_delete_nonexistent_incident(client):
    """Test deleting a nonexistent incident."""
    response = client.delete("/api/v1/incidents/nonexistent-id")
    assert response.status_code == 404
