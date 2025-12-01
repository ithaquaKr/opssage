"""
Shared context store for incident analysis.
Implements thread-safe storage for incident contexts across agents.
Following ADK best practices for shared state management.

Now with database persistence support for incident data.
"""

import asyncio
import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from sages.db.database import get_db
from sages.db.models import IncidentModel
from sages.models import (
    AlertInput,
    EnhancedContextPackage,
    IncidentContext,
    IncidentDiagnosticReport,
    PrimaryContextPackage,
)

logger = logging.getLogger(__name__)


class ContextStore:
    """
    Thread-safe context store for managing incident analysis state.
    Provides atomic operations for updating incident contexts.

    Now persists all incident data to database for durability.
    """

    def __init__(self) -> None:
        """Initialize the context store with database support."""
        self._lock = asyncio.Lock()
        self._subscribers: dict[str, list[Callable[[IncidentContext], None]]] = {}

    def _model_to_context(self, model: IncidentModel) -> IncidentContext:
        """
        Convert database model to IncidentContext.

        Args:
            model: Database model instance

        Returns:
            IncidentContext instance
        """
        # Deserialize alert input
        alert_input = AlertInput(**model.alert_input)

        # Deserialize optional contexts
        primary_context = (
            PrimaryContextPackage(**model.primary_context)
            if model.primary_context
            else None
        )
        enhanced_context = (
            EnhancedContextPackage(**model.enhanced_context)
            if model.enhanced_context
            else None
        )
        diagnostic_report = (
            IncidentDiagnosticReport(**model.diagnostic_report)
            if model.diagnostic_report
            else None
        )

        return IncidentContext(
            incident_id=model.incident_id,
            alert_input=alert_input,
            primary_context=primary_context,
            enhanced_context=enhanced_context,
            diagnostic_report=diagnostic_report,
            created_at=model.created_at,
            updated_at=model.updated_at,
            status=model.status,
        )

    def _context_to_model_data(self, context: IncidentContext) -> dict:
        """
        Convert IncidentContext to database model data.

        Args:
            context: IncidentContext instance

        Returns:
            Dictionary of model data
        """
        # Serialize Pydantic models to dict
        model_data = {
            "incident_id": context.incident_id,
            "status": context.status,
            "created_at": context.created_at,
            "updated_at": context.updated_at,
            "alert_input": context.alert_input.model_dump(mode="json"),
            "primary_context": (
                context.primary_context.model_dump(mode="json")
                if context.primary_context
                else None
            ),
            "enhanced_context": (
                context.enhanced_context.model_dump(mode="json")
                if context.enhanced_context
                else None
            ),
            "diagnostic_report": (
                context.diagnostic_report.model_dump(mode="json")
                if context.diagnostic_report
                else None
            ),
            # Denormalized fields for quick access
            "alert_name": context.alert_input.alert_name,
            "severity": context.alert_input.severity,
            "namespace": context.alert_input.labels.get("namespace"),
            "service": context.alert_input.labels.get("service"),
            "root_cause": (
                context.diagnostic_report.root_cause
                if context.diagnostic_report
                else None
            ),
            "confidence_score": (
                context.diagnostic_report.confidence_score
                if context.diagnostic_report
                else None
            ),
        }
        return model_data

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

            # Persist to database
            with get_db() as db:
                model_data = self._context_to_model_data(context)
                incident = IncidentModel(**model_data)
                db.add(incident)
                db.commit()
                logger.info(f"Created incident {incident_id} in database")

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
            with get_db() as db:
                incident = (
                    db.query(IncidentModel)
                    .filter(IncidentModel.incident_id == incident_id)
                    .first()
                )
                if incident:
                    return self._model_to_context(incident)
                return None

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
            with get_db() as db:
                incident = (
                    db.query(IncidentModel)
                    .filter(IncidentModel.incident_id == incident_id)
                    .first()
                )
                if not incident:
                    raise KeyError(f"Incident {incident_id} not found")

                # Update database model
                incident.primary_context = primary_context.model_dump(mode="json")
                incident.updated_at = datetime.now(UTC)
                incident.status = "context_collected"
                db.commit()
                logger.debug(f"Updated primary context for incident {incident_id}")

                # Notify subscribers
                context = self._model_to_context(incident)
                await self._notify_subscribers(incident_id, context)

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
            with get_db() as db:
                incident = (
                    db.query(IncidentModel)
                    .filter(IncidentModel.incident_id == incident_id)
                    .first()
                )
                if not incident:
                    raise KeyError(f"Incident {incident_id} not found")

                # Update database model
                incident.enhanced_context = enhanced_context.model_dump(mode="json")
                incident.updated_at = datetime.now(UTC)
                incident.status = "context_enriched"
                db.commit()
                logger.debug(f"Updated enhanced context for incident {incident_id}")

                # Notify subscribers
                context = self._model_to_context(incident)
                await self._notify_subscribers(incident_id, context)

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
            with get_db() as db:
                incident = (
                    db.query(IncidentModel)
                    .filter(IncidentModel.incident_id == incident_id)
                    .first()
                )
                if not incident:
                    raise KeyError(f"Incident {incident_id} not found")

                # Update database model with diagnostic report
                incident.diagnostic_report = diagnostic_report.model_dump(mode="json")
                incident.updated_at = datetime.now(UTC)
                incident.status = "completed"
                # Update denormalized fields
                incident.root_cause = diagnostic_report.root_cause
                incident.confidence_score = diagnostic_report.confidence_score
                db.commit()
                logger.info(f"Updated diagnostic report for incident {incident_id}")

                # Notify subscribers
                context = self._model_to_context(incident)
                await self._notify_subscribers(incident_id, context)

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
            with get_db() as db:
                incident = (
                    db.query(IncidentModel)
                    .filter(IncidentModel.incident_id == incident_id)
                    .first()
                )
                if not incident:
                    raise KeyError(f"Incident {incident_id} not found")

                incident.status = status
                incident.updated_at = datetime.now(UTC)
                db.commit()
                logger.debug(f"Updated status for incident {incident_id} to {status}")

                # Notify subscribers
                context = self._model_to_context(incident)
                await self._notify_subscribers(incident_id, context)

    async def list_incidents(self, status: str | None = None) -> list[IncidentContext]:
        """
        List all incidents, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of incident contexts
        """
        async with self._lock:
            with get_db() as db:
                query = db.query(IncidentModel).order_by(
                    IncidentModel.created_at.desc()
                )
                if status:
                    query = query.filter(IncidentModel.status == status)

                incidents = query.all()
                return [self._model_to_context(inc) for inc in incidents]

    async def delete_incident(self, incident_id: str) -> None:
        """
        Delete an incident from the store.

        Args:
            incident_id: The incident ID to delete

        Raises:
            KeyError: If the incident_id does not exist
        """
        async with self._lock:
            with get_db() as db:
                incident = (
                    db.query(IncidentModel)
                    .filter(IncidentModel.incident_id == incident_id)
                    .first()
                )
                if not incident:
                    raise KeyError(f"Incident {incident_id} not found")

                db.delete(incident)
                db.commit()
                logger.info(f"Deleted incident {incident_id} from database")

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
