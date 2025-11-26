"""
Tests for the shared context store.
"""

import pytest

from sages.context_store import ContextStore
from sages.models import (
    AffectedComponents,
    AlertInput,
    AlertMetadata,
    EvidenceCollected,
    PreliminaryAnalysis,
    PrimaryContextPackage,
)


@pytest.mark.asyncio
async def test_create_incident(sample_alert: AlertInput):
    """Test creating an incident."""
    store = ContextStore()
    incident_id = await store.create_incident(sample_alert)

    assert incident_id is not None
    incident = await store.get_incident(incident_id)
    assert incident is not None
    assert incident.alert_input.alert_name == sample_alert.alert_name
    assert incident.status == "pending"


@pytest.mark.asyncio
async def test_update_primary_context(sample_alert: AlertInput):
    """Test updating primary context."""
    store = ContextStore()
    incident_id = await store.create_incident(sample_alert)

    primary_context = PrimaryContextPackage(
        alert_metadata=AlertMetadata(
            alert_name="Test",
            severity="critical",
            firing_condition="test",
            trigger_time="2025-01-01T00:00:00Z",
        ),
        affected_components=AffectedComponents(),
        evidence_collected=EvidenceCollected(),
        preliminary_analysis=PreliminaryAnalysis(),
    )

    await store.update_primary_context(incident_id, primary_context)

    incident = await store.get_incident(incident_id)
    assert incident is not None
    assert incident.primary_context is not None
    assert incident.status == "context_collected"


@pytest.mark.asyncio
async def test_update_nonexistent_incident():
    """Test updating a nonexistent incident."""
    store = ContextStore()

    primary_context = PrimaryContextPackage(
        alert_metadata=AlertMetadata(
            alert_name="Test",
            severity="info",
            firing_condition="test",
            trigger_time="2025-01-01T00:00:00Z",
        ),
        affected_components=AffectedComponents(),
        evidence_collected=EvidenceCollected(),
        preliminary_analysis=PreliminaryAnalysis(),
    )

    with pytest.raises(KeyError):
        await store.update_primary_context("nonexistent-id", primary_context)


@pytest.mark.asyncio
async def test_list_incidents(sample_alert: AlertInput):
    """Test listing incidents."""
    store = ContextStore()

    id1 = await store.create_incident(sample_alert)
    await store.create_incident(sample_alert)

    incidents = await store.list_incidents()
    assert len(incidents) == 2

    # Test filtering by status
    await store.update_status(id1, "completed")
    completed = await store.list_incidents(status="completed")
    assert len(completed) == 1
    assert completed[0].incident_id == id1


@pytest.mark.asyncio
async def test_delete_incident(sample_alert: AlertInput):
    """Test deleting an incident."""
    store = ContextStore()
    incident_id = await store.create_incident(sample_alert)

    await store.delete_incident(incident_id)

    incident = await store.get_incident(incident_id)
    assert incident is None


@pytest.mark.asyncio
async def test_subscribe_to_updates(sample_alert: AlertInput):
    """Test subscribing to incident updates."""
    store = ContextStore()
    incident_id = await store.create_incident(sample_alert)

    updates = []

    def callback(context):
        updates.append(context.status)

    store.subscribe(incident_id, callback)

    await store.update_status(incident_id, "processing")
    await store.update_status(incident_id, "completed")

    # Note: Updates list will contain the statuses from update calls
    assert len(updates) >= 2
