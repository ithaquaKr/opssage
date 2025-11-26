"""
Tests for capability adapters and tools.
"""

from datetime import datetime, timedelta

import pytest

from sages.tools import (
    MockClusterStateAdapter,
    MockEventAdapter,
    MockKnowledgeAdapter,
    MockLogAdapter,
    MockMetricsAdapter,
)


@pytest.mark.asyncio
async def test_mock_metrics_adapter():
    """Test the mock metrics adapter."""
    adapter = MockMetricsAdapter()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=15)

    results = await adapter.query_metrics(
        metric_name="cpu_usage",
        labels={"service": "api", "namespace": "prod"},
        start_time=start_time,
        end_time=end_time,
    )

    assert len(results) > 0
    assert results[0]["metric"] == "cpu_usage"
    assert "value" in results[0]


@pytest.mark.asyncio
async def test_mock_log_adapter():
    """Test the mock log adapter."""
    adapter = MockLogAdapter()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=15)

    results = await adapter.search_logs(
        query="error",
        namespace="prod",
        pod="api-pod",
        start_time=start_time,
        end_time=end_time,
        limit=100,
    )

    assert len(results) > 0
    assert results[0]["namespace"] == "prod"
    assert results[0]["pod"] == "api-pod"


@pytest.mark.asyncio
async def test_mock_event_adapter():
    """Test the mock event adapter."""
    adapter = MockEventAdapter()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=30)

    results = await adapter.lookup_events(
        namespace="prod",
        resource_type="Pod",
        resource_name="api-pod",
        start_time=start_time,
        end_time=end_time,
    )

    assert len(results) > 0
    assert results[0]["namespace"] == "prod"


@pytest.mark.asyncio
async def test_mock_knowledge_adapter_vector_search():
    """Test the mock knowledge adapter vector search."""
    adapter = MockKnowledgeAdapter()

    results = await adapter.vector_search(query="high cpu usage", top_k=5)

    assert len(results) > 0
    assert "source_id" in results[0]
    assert "relevance" in results[0]
    assert 0 <= results[0]["relevance"] <= 1


@pytest.mark.asyncio
async def test_mock_knowledge_adapter_document_lookup():
    """Test the mock knowledge adapter document lookup."""
    adapter = MockKnowledgeAdapter()

    result = await adapter.document_lookup(doc_id="kb-001")

    assert result["source_id"] == "kb-001"
    assert "content" in result


@pytest.mark.asyncio
async def test_mock_knowledge_adapter_playbook_query():
    """Test the mock knowledge adapter playbook query."""
    adapter = MockKnowledgeAdapter()

    results = await adapter.playbook_query(keywords=["cpu", "remediation"])

    assert len(results) > 0
    assert "steps" in results[0]


@pytest.mark.asyncio
async def test_mock_cluster_state_adapter():
    """Test the mock cluster state adapter."""
    adapter = MockClusterStateAdapter()

    result = await adapter.verify_cluster_state(
        namespace="prod", resource_type="Pod", resource_name="api-pod"
    )

    assert result["namespace"] == "prod"
    assert result["kind"] == "Pod"
    assert result["name"] == "api-pod"
    assert "status" in result
