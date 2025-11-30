"""
Data models for message contracts between agents.
Following ADK best practices for structured communication.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# AICA (Alert Ingestion & Context Agent) - Output Models
# ============================================================================


class AlertMetadata(BaseModel):
    """Metadata about the alert that triggered the analysis."""

    alert_name: str = Field(..., description="Name of the alert rule")
    severity: str = Field(..., description="Alert severity level")
    firing_condition: str = Field(..., description="Condition that triggered the alert")
    trigger_time: str = Field(..., description="When the alert was triggered")


class AffectedComponents(BaseModel):
    """Components affected by the incident."""

    service: str | None = Field(None, description="Affected service name")
    namespace: str | None = Field(None, description="Kubernetes namespace")
    pod: str | None = Field(None, description="Affected pod name")
    node: str | None = Field(None, description="Affected node name")


class EvidenceCollected(BaseModel):
    """Evidence collected during initial analysis."""

    metrics: list[dict[str, Any]] = Field(
        default_factory=list, description="Metrics snapshots"
    )
    logs: list[dict[str, Any]] = Field(
        default_factory=list, description="Relevant log entries"
    )
    events: list[dict[str, Any]] = Field(
        default_factory=list, description="Kubernetes events"
    )


class PreliminaryAnalysis(BaseModel):
    """Initial analysis findings."""

    observations: list[str] = Field(
        default_factory=list, description="Key observations from evidence"
    )
    hypotheses: list[str] = Field(
        default_factory=list, description="Preliminary hypotheses about the issue"
    )
    missing_information: list[str] = Field(
        default_factory=list, description="Information gaps identified"
    )


class PrimaryContextPackage(BaseModel):
    """Output from AICA - Primary context about the incident."""

    alert_metadata: AlertMetadata
    affected_components: AffectedComponents
    evidence_collected: EvidenceCollected
    preliminary_analysis: PreliminaryAnalysis


class AICAOutput(BaseModel):
    """Complete output from AICA agent."""

    primary_context_package: PrimaryContextPackage


# ============================================================================
# KREA (Knowledge Retrieval & Enrichment Agent) - Output Models
# ============================================================================


class RetrievedKnowledge(BaseModel):
    """A single piece of retrieved knowledge."""

    source_id: str = Field(
        ..., description="Unique identifier for the knowledge source"
    )
    excerpt: str = Field(..., description="Relevant excerpt from the source")
    relevance: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")


class ContextualEnrichment(BaseModel):
    """Enriched context from knowledge retrieval."""

    failure_patterns: list[str] = Field(
        default_factory=list,
        description="Known failure patterns matching this incident",
    )
    possible_causes: list[str] = Field(
        default_factory=list, description="Possible root causes from knowledge base"
    )
    related_incidents: list[str] = Field(
        default_factory=list, description="Similar past incidents"
    )
    known_remediation_actions: list[str] = Field(
        default_factory=list, description="Known remediation strategies"
    )


class EnhancedContextPackage(BaseModel):
    """Output from KREA - Enhanced context with retrieved knowledge."""

    primary_context_reference: PrimaryContextPackage = Field(
        ..., description="Reference to the primary context from AICA"
    )
    retrieved_knowledge: list[RetrievedKnowledge] = Field(
        default_factory=list, description="Retrieved knowledge items"
    )
    knowledge_summary: str = Field("", description="Summary of retrieved knowledge")
    contextual_enrichment: ContextualEnrichment


class KREAOutput(BaseModel):
    """Complete output from KREA agent."""

    enhanced_context_package: EnhancedContextPackage


# ============================================================================
# RCARA (Root Cause Analysis & Remediation Agent) - Output Models
# ============================================================================


class RecommendedRemediation(BaseModel):
    """Remediation recommendations."""

    short_term_actions: list[str] = Field(
        default_factory=list,
        description="Immediate actions to resolve or mitigate the incident",
    )
    long_term_actions: list[str] = Field(
        default_factory=list,
        description="Long-term improvements to prevent recurrence",
    )


class IncidentDiagnosticReport(BaseModel):
    """Output from RCARA - Complete diagnostic and remediation plan."""

    root_cause: str = Field(..., description="Identified root cause of the incident")
    reasoning_steps: list[str] = Field(
        ..., description="Step-by-step reasoning that led to the conclusion"
    )
    supporting_evidence: list[str] = Field(
        ..., description="Evidence supporting the root cause determination"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in the analysis (0-1)"
    )
    recommended_remediation: RecommendedRemediation


class RCARAOutput(BaseModel):
    """Complete output from RCARA agent."""

    incident_diagnostic_report: IncidentDiagnosticReport


# ============================================================================
# Input Models
# ============================================================================


class AlertInput(BaseModel):
    """Input alert for the system."""

    alert_name: str = Field(..., description="Name of the alert")
    severity: str = Field(..., description="Severity level (critical, warning, info)")
    message: str = Field(..., description="Alert message/description")
    labels: dict[str, str] = Field(
        default_factory=dict, description="Alert labels (service, namespace, etc.)"
    )
    annotations: dict[str, str] = Field(
        default_factory=dict, description="Alert annotations"
    )
    firing_condition: str = Field(..., description="Condition that triggered the alert")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="When the alert fired"
    )


# ============================================================================
# Context Store Models
# ============================================================================


class IncidentContext(BaseModel):
    """Complete context for an incident, stored in shared context store."""

    incident_id: str = Field(..., description="Unique incident identifier")
    alert_input: AlertInput
    primary_context: PrimaryContextPackage | None = None
    enhanced_context: EnhancedContextPackage | None = None
    diagnostic_report: IncidentDiagnosticReport | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = Field(
        default="pending", description="Status: pending, analyzing, completed, failed"
    )
