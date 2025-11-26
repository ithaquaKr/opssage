"""
FastAPI server for OpsSage incident analysis system.
Provides REST API endpoints for alert ingestion and incident management.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sages.context_store import get_context_store
from sages.models import AlertInput, IncidentContext
from sages.orchestrator import create_orchestrator

logger = logging.getLogger(__name__)


# Initialize orchestrator on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    logger.info("Starting OpsSage API server")
    app.state.orchestrator = create_orchestrator()
    app.state.context_store = get_context_store()
    yield
    logger.info("Shutting down OpsSage API server")


# Create FastAPI app
app = FastAPI(
    title="OpsSage",
    description="Multi-Agent Incident Analysis & Remediation System",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "OpsSage",
        "version": "0.1.0",
    }


@app.post("/api/v1/alerts", response_model=dict)
async def ingest_alert(alert: AlertInput):
    """
    Ingest an alert and trigger incident analysis.

    Args:
        alert: The alert to analyze

    Returns:
        Dictionary with incident_id and status
    """
    try:
        logger.info(f"Received alert: {alert.alert_name}")

        # Run analysis asynchronously
        incident_id, diagnostic_report = await app.state.orchestrator.analyze_incident(
            alert
        )

        return {
            "incident_id": incident_id,
            "status": "completed",
            "diagnostic_report": diagnostic_report.model_dump(),
        }

    except Exception as e:
        logger.error(f"Error processing alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/incidents/{incident_id}", response_model=IncidentContext)
async def get_incident(incident_id: str):
    """
    Retrieve an incident by ID.

    Args:
        incident_id: The incident ID

    Returns:
        The incident context
    """
    incident = await app.state.context_store.get_incident(incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@app.get("/api/v1/incidents", response_model=list[IncidentContext])
async def list_incidents(status: str | None = None):
    """
    List all incidents, optionally filtered by status.

    Args:
        status: Optional status filter

    Returns:
        List of incidents
    """
    incidents = await app.state.context_store.list_incidents(status=status)
    return incidents


@app.delete("/api/v1/incidents/{incident_id}")
async def delete_incident(incident_id: str):
    """
    Delete an incident.

    Args:
        incident_id: The incident ID to delete

    Returns:
        Success message
    """
    try:
        await app.state.context_store.delete_incident(incident_id)
        return {"status": "deleted", "incident_id": incident_id}
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint for Kubernetes probes.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "components": {
            "orchestrator": "ok",
            "context_store": "ok",
        },
    }


@app.get("/api/v1/readiness")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes probes.

    Returns:
        Readiness status
    """
    return {
        "status": "ready",
        "agents": {
            "aica": "ready",
            "krea": "ready",
            "rcara": "ready",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
