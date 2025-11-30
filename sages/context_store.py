"""
Shared context store for incident analysis.
Implements thread-safe storage for incident contexts across agents.
Following ADK best practices for shared state management.
"""

import asyncio
import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from sages.models import (
    AlertInput,
    EnhancedContextPackage,
    IncidentContext,
    IncidentDiagnosticReport,
    PrimaryContextPackage,
)


class ContextStore:
    """
    Thread-safe context store for managing incident analysis state.
    Provides atomic operations for updating incident contexts.
    """

    def __init__(self) -> None:
        """Initialize the context store with an empty dictionary and lock."""
        self._store: dict[str, IncidentContext] = {}
        self._lock = asyncio.Lock()
        self._subscribers: dict[str, list[Callable[[IncidentContext], None]]] = {}

    async def create_incident(self, alert: AlertInput) -> str:
        """
        Create a new incident from an alert.

        Args:
            alert: The alert that triggered the incident

        Returns:
            The unique incident_id for the created incident
        """
        async with self._lock:
            incident_id = str(uuid.uuid4())
            context = IncidentContext(
                incident_id=incident_id,
                alert_input=alert,
                status="pending",
            )
            self._store[incident_id] = context
            await self._notify_subscribers(incident_id, context)
            return incident_id

    async def get_incident(self, incident_id: str) -> IncidentContext | None:
        """
        Retrieve an incident context by ID.

        Args:
            incident_id: The incident ID to retrieve

        Returns:
            The incident context, or None if not found
        """
        async with self._lock:
            return self._store.get(incident_id)

    async def update_primary_context(
        self, incident_id: str, primary_context: PrimaryContextPackage
    ) -> None:
        """
        Update the primary context for an incident (from AICA).

        Args:
            incident_id: The incident ID
            primary_context: The primary context package from AICA

        Raises:
            KeyError: If the incident_id does not exist
        """
        async with self._lock:
            if incident_id not in self._store:
                raise KeyError(f"Incident {incident_id} not found")

            incident = self._store[incident_id]
            incident.primary_context = primary_context
            incident.updated_at = datetime.now(UTC)
            incident.status = "context_collected"
            await self._notify_subscribers(incident_id, incident)

    async def update_enhanced_context(
        self, incident_id: str, enhanced_context: EnhancedContextPackage
    ) -> None:
        """
        Update the enhanced context for an incident (from KREA).

        Args:
            incident_id: The incident ID
            enhanced_context: The enhanced context package from KREA

        Raises:
            KeyError: If the incident_id does not exist
        """
        async with self._lock:
            if incident_id not in self._store:
                raise KeyError(f"Incident {incident_id} not found")

            incident = self._store[incident_id]
            incident.enhanced_context = enhanced_context
            incident.updated_at = datetime.now(UTC)
            incident.status = "context_enriched"
            await self._notify_subscribers(incident_id, incident)

    async def update_diagnostic_report(
        self, incident_id: str, diagnostic_report: IncidentDiagnosticReport
    ) -> None:
        """
        Update the diagnostic report for an incident (from RCARA).

        Args:
            incident_id: The incident ID
            diagnostic_report: The diagnostic report from RCARA

        Raises:
            KeyError: If the incident_id does not exist
        """
        async with self._lock:
            if incident_id not in self._store:
                raise KeyError(f"Incident {incident_id} not found")

            incident = self._store[incident_id]
            incident.diagnostic_report = diagnostic_report
            incident.updated_at = datetime.now(UTC)
            incident.status = "completed"
            await self._notify_subscribers(incident_id, incident)

    async def update_status(self, incident_id: str, status: str) -> None:
        """
        Update the status of an incident.

        Args:
            incident_id: The incident ID
            status: The new status

        Raises:
            KeyError: If the incident_id does not exist
        """
        async with self._lock:
            if incident_id not in self._store:
                raise KeyError(f"Incident {incident_id} not found")

            incident = self._store[incident_id]
            incident.status = status
            incident.updated_at = datetime.now(UTC)
            await self._notify_subscribers(incident_id, incident)

    async def list_incidents(self, status: str | None = None) -> list[IncidentContext]:
        """
        List all incidents, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of incident contexts
        """
        async with self._lock:
            incidents = list(self._store.values())
            if status:
                incidents = [i for i in incidents if i.status == status]
            return incidents

    async def delete_incident(self, incident_id: str) -> None:
        """
        Delete an incident from the store.

        Args:
            incident_id: The incident ID to delete

        Raises:
            KeyError: If the incident_id does not exist
        """
        async with self._lock:
            if incident_id not in self._store:
                raise KeyError(f"Incident {incident_id} not found")

            del self._store[incident_id]
            if incident_id in self._subscribers:
                del self._subscribers[incident_id]

    def subscribe(
        self, incident_id: str, callback: Callable[[IncidentContext], None]
    ) -> None:
        """
        Subscribe to updates for a specific incident.

        Args:
            incident_id: The incident ID to subscribe to
            callback: Function to call when the incident is updated
        """
        if incident_id not in self._subscribers:
            self._subscribers[incident_id] = []
        self._subscribers[incident_id].append(callback)

    async def _notify_subscribers(
        self, incident_id: str, context: IncidentContext
    ) -> None:
        """
        Notify all subscribers of an incident update.

        Args:
            incident_id: The incident ID
            context: The updated context
        """
        if incident_id in self._subscribers:
            for callback in self._subscribers[incident_id]:
                callback(context)


# Global singleton instance
_context_store: ContextStore | None = None


def get_context_store() -> ContextStore:
    """
    Get the global context store singleton.

    Returns:
        The global ContextStore instance
    """
    global _context_store
    if _context_store is None:
        _context_store = ContextStore()
    return _context_store
