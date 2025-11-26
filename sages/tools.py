"""
Capability adapters (tools) for agents to interact with external systems.
Following ADK best practices for tool design.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

from google.adk.tools import ToolContext

# ============================================================================
# Tool Interfaces (Abstract Base Classes)
# ============================================================================


class MetricsAdapter(ABC):
    """Abstract interface for metrics querying."""

    @abstractmethod
    async def query_metrics(
        self,
        metric_name: str,
        labels: dict[str, str],
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Query metrics from monitoring system."""
        pass


class LogAdapter(ABC):
    """Abstract interface for log querying."""

    @abstractmethod
    async def search_logs(
        self,
        query: str,
        namespace: str,
        pod: str | None,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Search logs from logging system."""
        pass


class EventAdapter(ABC):
    """Abstract interface for Kubernetes event querying."""

    @abstractmethod
    async def lookup_events(
        self,
        namespace: str,
        resource_type: str | None,
        resource_name: str | None,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Look up Kubernetes events."""
        pass


class KnowledgeAdapter(ABC):
    """Abstract interface for knowledge retrieval."""

    @abstractmethod
    async def vector_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Perform vector similarity search on knowledge base."""
        pass

    @abstractmethod
    async def document_lookup(self, doc_id: str) -> dict[str, Any]:
        """Look up a specific document."""
        pass

    @abstractmethod
    async def playbook_query(self, keywords: list[str]) -> list[dict[str, Any]]:
        """Query runbooks and playbooks."""
        pass


class ClusterStateAdapter(ABC):
    """Abstract interface for cluster state verification."""

    @abstractmethod
    async def verify_cluster_state(
        self, namespace: str, resource_type: str, resource_name: str
    ) -> dict[str, Any]:
        """Verify current cluster state for a resource."""
        pass


# ============================================================================
# Mock Implementations (for testing and development)
# ============================================================================


class MockMetricsAdapter(MetricsAdapter):
    """Mock implementation of MetricsAdapter for testing."""

    async def query_metrics(
        self,
        metric_name: str,
        labels: dict[str, str],
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Return mock metrics data."""
        return [
            {
                "timestamp": start_time.isoformat(),
                "metric": metric_name,
                "labels": labels,
                "value": 85.5,
            },
            {
                "timestamp": (start_time + timedelta(minutes=1)).isoformat(),
                "metric": metric_name,
                "labels": labels,
                "value": 92.3,
            },
        ]


class MockLogAdapter(LogAdapter):
    """Mock implementation of LogAdapter for testing."""

    async def search_logs(
        self,
        query: str,
        namespace: str,
        pod: str | None,
        start_time: datetime,
        end_time: datetime,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return mock log data."""
        return [
            {
                "timestamp": start_time.isoformat(),
                "namespace": namespace,
                "pod": pod or "test-pod",
                "message": f"Sample log entry matching query: {query}",
                "level": "ERROR",
            },
            {
                "timestamp": (start_time + timedelta(seconds=30)).isoformat(),
                "namespace": namespace,
                "pod": pod or "test-pod",
                "message": "Connection timeout occurred",
                "level": "ERROR",
            },
        ]


class MockEventAdapter(EventAdapter):
    """Mock implementation of EventAdapter for testing."""

    async def lookup_events(
        self,
        namespace: str,
        resource_type: str | None,
        resource_name: str | None,
        start_time: datetime,
        end_time: datetime,
    ) -> list[dict[str, Any]]:
        """Return mock Kubernetes events."""
        return [
            {
                "timestamp": start_time.isoformat(),
                "namespace": namespace,
                "type": "Warning",
                "reason": "BackOff",
                "message": "Back-off restarting failed container",
                "involved_object": {
                    "kind": resource_type or "Pod",
                    "name": resource_name or "test-pod",
                },
            }
        ]


class MockKnowledgeAdapter(KnowledgeAdapter):
    """Mock implementation of KnowledgeAdapter for testing."""

    async def vector_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Return mock knowledge search results."""
        return [
            {
                "source_id": "kb-001",
                "title": "High CPU Usage Troubleshooting",
                "excerpt": "Common causes of high CPU include inefficient queries, memory leaks, and infinite loops.",
                "relevance": 0.85,
            },
            {
                "source_id": "kb-002",
                "title": "Container Restart Patterns",
                "excerpt": "Containers may restart due to OOM kills, application crashes, or liveness probe failures.",
                "relevance": 0.72,
            },
        ]

    async def document_lookup(self, doc_id: str) -> dict[str, Any]:
        """Return mock document."""
        return {
            "source_id": doc_id,
            "title": f"Document {doc_id}",
            "content": "Mock document content",
        }

    async def playbook_query(self, keywords: list[str]) -> list[dict[str, Any]]:
        """Return mock playbook results."""
        return [
            {
                "source_id": "playbook-001",
                "title": "High CPU Remediation Playbook",
                "steps": [
                    "Check current resource limits",
                    "Review recent deployments",
                    "Analyze application logs",
                ],
                "relevance": 0.88,
            }
        ]


class RealKnowledgeAdapter(KnowledgeAdapter):
    """Real implementation using vector store."""

    def __init__(self):
        """Initialize with lazy loading of vector store."""
        self._vector_store = None

    @property
    def vector_store(self):
        """Lazy load vector store on first access."""
        if self._vector_store is None:
            from sages.rag import get_vector_store

            self._vector_store = get_vector_store()
        return self._vector_store

    async def vector_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Perform vector similarity search on knowledge base."""
        results = self.vector_store.search(
            query=query, collection_name="documents", top_k=top_k
        )

        formatted_results = []
        for result in results:
            metadata = result["metadata"]
            formatted_results.append(
                {
                    "source_id": result["id"],
                    "title": metadata.get("filename", "Unknown"),
                    "excerpt": result["document"][:500],  # First 500 chars
                    "relevance": result["relevance"],
                    "metadata": metadata,
                }
            )

        return formatted_results

    async def document_lookup(self, doc_id: str) -> dict[str, Any]:
        """Look up a specific document."""
        doc = self.vector_store.get_document(
            document_id=doc_id, collection_name="documents"
        )

        if doc is None:
            return {
                "source_id": doc_id,
                "title": "Not Found",
                "content": "Document not found in knowledge base",
            }

        metadata = doc["metadata"]
        return {
            "source_id": doc["id"],
            "title": metadata.get("filename", "Unknown"),
            "content": doc["document"],
            "metadata": metadata,
        }

    async def playbook_query(self, keywords: list[str]) -> list[dict[str, Any]]:
        """Query runbooks and playbooks."""
        query = " ".join(keywords)
        results = self.vector_store.search(
            query=query, collection_name="playbooks", top_k=5
        )

        formatted_results = []
        for result in results:
            metadata = result["metadata"]
            formatted_results.append(
                {
                    "source_id": result["id"],
                    "title": metadata.get("filename", "Unknown"),
                    "content": result["document"],
                    "relevance": result["relevance"],
                    "metadata": metadata,
                }
            )

        return formatted_results


class MockClusterStateAdapter(ClusterStateAdapter):
    """Mock implementation of ClusterStateAdapter for testing."""

    async def verify_cluster_state(
        self, namespace: str, resource_type: str, resource_name: str
    ) -> dict[str, Any]:
        """Return mock cluster state."""
        return {
            "namespace": namespace,
            "kind": resource_type,
            "name": resource_name,
            "status": "Running",
            "ready": "2/2",
            "restarts": 3,
        }


# ============================================================================
# ADK Tool Wrappers
# ============================================================================


def metrics_query_tool(
    ctx: ToolContext,
    metric_name: str,
    labels: str,
    time_range_minutes: int = 15,
) -> str:
    """
    Query metrics from the monitoring system.

    Args:
        metric_name: Name of the metric to query (e.g., 'cpu_usage', 'memory_usage')
        labels: JSON string of label filters (e.g., '{"service": "api", "namespace": "prod"}')
        time_range_minutes: How many minutes back to query (default: 15)

    Returns:
        JSON string with metric results
    """
    import asyncio
    import json

    adapter = MockMetricsAdapter()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=time_range_minutes)
    labels_dict = json.loads(labels)

    results = asyncio.run(
        adapter.query_metrics(metric_name, labels_dict, start_time, end_time)
    )
    return json.dumps(results, indent=2)


def log_search_tool(
    ctx: ToolContext,
    query: str,
    namespace: str,
    pod: str = "",
    time_range_minutes: int = 15,
    limit: int = 100,
) -> str:
    """
    Search logs from the logging system.

    Args:
        query: Search query string
        namespace: Kubernetes namespace
        pod: Specific pod name (optional)
        time_range_minutes: How many minutes back to search (default: 15)
        limit: Maximum number of log entries to return (default: 100)

    Returns:
        JSON string with log results
    """
    import asyncio
    import json

    adapter = MockLogAdapter()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=time_range_minutes)

    results = asyncio.run(
        adapter.search_logs(query, namespace, pod or None, start_time, end_time, limit)
    )
    return json.dumps(results, indent=2)


def event_lookup_tool(
    ctx: ToolContext,
    namespace: str,
    resource_type: str = "",
    resource_name: str = "",
    time_range_minutes: int = 30,
) -> str:
    """
    Look up Kubernetes events.

    Args:
        namespace: Kubernetes namespace
        resource_type: Type of resource (e.g., 'Pod', 'Deployment')
        resource_name: Name of specific resource
        time_range_minutes: How many minutes back to look (default: 30)

    Returns:
        JSON string with event results
    """
    import asyncio
    import json

    adapter = MockEventAdapter()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=time_range_minutes)

    results = asyncio.run(
        adapter.lookup_events(
            namespace,
            resource_type or None,
            resource_name or None,
            start_time,
            end_time,
        )
    )
    return json.dumps(results, indent=2)


def vector_search_tool(
    ctx: ToolContext,
    query: str,
    top_k: int = 5,
    use_real: bool = True,
) -> str:
    """
    Search the knowledge base using vector similarity.

    Args:
        query: Search query describing the problem or topic
        top_k: Number of top results to return (default: 5)
        use_real: Use real vector store (True) or mock data (False)

    Returns:
        JSON string with knowledge base results
    """
    import asyncio
    import json
    import os

    # Check environment variable for adapter type
    use_real_adapter = os.getenv("USE_REAL_KNOWLEDGE_ADAPTER", "true").lower() == "true"

    if use_real_adapter and use_real:
        adapter = RealKnowledgeAdapter()
    else:
        adapter = MockKnowledgeAdapter()

    results = asyncio.run(adapter.vector_search(query, top_k))
    return json.dumps(results, indent=2)


def document_lookup_tool(
    ctx: ToolContext,
    doc_id: str,
    use_real: bool = True,
) -> str:
    """
    Look up a specific document by ID.

    Args:
        doc_id: Document identifier
        use_real: Use real vector store (True) or mock data (False)

    Returns:
        JSON string with document content
    """
    import asyncio
    import json
    import os

    use_real_adapter = os.getenv("USE_REAL_KNOWLEDGE_ADAPTER", "true").lower() == "true"

    if use_real_adapter and use_real:
        adapter = RealKnowledgeAdapter()
    else:
        adapter = MockKnowledgeAdapter()

    result = asyncio.run(adapter.document_lookup(doc_id))
    return json.dumps(result, indent=2)


def playbook_query_tool(
    ctx: ToolContext,
    keywords: str,
    use_real: bool = True,
) -> str:
    """
    Query runbooks and playbooks.

    Args:
        keywords: Comma-separated keywords to search for
        use_real: Use real vector store (True) or mock data (False)

    Returns:
        JSON string with playbook results
    """
    import asyncio
    import json
    import os

    use_real_adapter = os.getenv("USE_REAL_KNOWLEDGE_ADAPTER", "true").lower() == "true"

    if use_real_adapter and use_real:
        adapter = RealKnowledgeAdapter()
    else:
        adapter = MockKnowledgeAdapter()

    keyword_list = [k.strip() for k in keywords.split(",")]
    results = asyncio.run(adapter.playbook_query(keyword_list))
    return json.dumps(results, indent=2)


def verify_cluster_state_tool(
    ctx: ToolContext,
    namespace: str,
    resource_type: str,
    resource_name: str,
) -> str:
    """
    Verify the current state of a cluster resource.

    Args:
        namespace: Kubernetes namespace
        resource_type: Type of resource (e.g., 'Pod', 'Deployment')
        resource_name: Name of the resource

    Returns:
        JSON string with current resource state
    """
    import asyncio
    import json

    adapter = MockClusterStateAdapter()
    result = asyncio.run(
        adapter.verify_cluster_state(namespace, resource_type, resource_name)
    )
    return json.dumps(result, indent=2)
