"""
Tests for data models and message contracts.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from sages.models import (
    AffectedComponents,
    AICAOutput,
    AlertInput,
    AlertMetadata,
    ContextualEnrichment,
    EnhancedContextPackage,
    EvidenceCollected,
    IncidentDiagnosticReport,
    PreliminaryAnalysis,
    PrimaryContextPackage,
    RCARAOutput,
    RecommendedRemediation,
    RetrievedKnowledge,
)


def test_alert_input_validation():
    """Test AlertInput model validation."""
    alert = AlertInput(
        alert_name="TestAlert",
        severity="critical",
        message="Test message",
        labels={"service": "test"},
        annotations={},
        firing_condition="test > 10",
    )

    assert alert.alert_name == "TestAlert"
    assert alert.severity == "critical"
    assert isinstance(alert.timestamp, datetime)


def test_primary_context_package():
    """Test PrimaryContextPackage model."""
    metadata = AlertMetadata(
        alert_name="TestAlert",
        severity="critical",
        firing_condition="cpu > 90",
        trigger_time="2025-01-01T00:00:00Z",
    )

    components = AffectedComponents(
        service="api", namespace="prod", pod="api-1", node="node-1"
    )

    evidence = EvidenceCollected(
        metrics=[{"cpu": 95.5}], logs=[{"message": "High CPU"}], events=[]
    )

    analysis = PreliminaryAnalysis(
        observations=["CPU usage high"],
        hypotheses=["Resource leak"],
        missing_information=["Memory usage"],
    )

    package = PrimaryContextPackage(
        alert_metadata=metadata,
        affected_components=components,
        evidence_collected=evidence,
        preliminary_analysis=analysis,
    )

    assert package.alert_metadata.alert_name == "TestAlert"
    assert len(package.preliminary_analysis.observations) == 1


def test_aica_output():
    """Test AICAOutput model."""
    metadata = AlertMetadata(
        alert_name="Test",
        severity="warning",
        firing_condition="x > 10",
        trigger_time="2025-01-01T00:00:00Z",
    )

    output = AICAOutput(
        primary_context_package=PrimaryContextPackage(
            alert_metadata=metadata,
            affected_components=AffectedComponents(),
            evidence_collected=EvidenceCollected(),
            preliminary_analysis=PreliminaryAnalysis(),
        )
    )

    assert output.primary_context_package.alert_metadata.alert_name == "Test"


def test_retrieved_knowledge_validation():
    """Test RetrievedKnowledge validation."""
    knowledge = RetrievedKnowledge(
        source_id="kb-001", excerpt="Test excerpt", relevance=0.85
    )

    assert knowledge.relevance == 0.85

    # Test relevance bounds
    with pytest.raises(ValidationError):
        RetrievedKnowledge(source_id="kb-002", excerpt="Test", relevance=1.5)


def test_enhanced_context_package():
    """Test EnhancedContextPackage model."""
    primary = PrimaryContextPackage(
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

    enrichment = ContextualEnrichment(
        failure_patterns=["Pattern 1"],
        possible_causes=["Cause 1"],
        related_incidents=["INC-001"],
        known_remediation_actions=["Action 1"],
    )

    enhanced = EnhancedContextPackage(
        primary_context_reference=primary,
        retrieved_knowledge=[
            RetrievedKnowledge(source_id="kb-001", excerpt="Test", relevance=0.9)
        ],
        knowledge_summary="Summary",
        contextual_enrichment=enrichment,
    )

    assert len(enhanced.retrieved_knowledge) == 1
    assert enhanced.contextual_enrichment.failure_patterns[0] == "Pattern 1"


def test_incident_diagnostic_report():
    """Test IncidentDiagnosticReport model."""
    remediation = RecommendedRemediation(
        short_term_actions=["Restart service"], long_term_actions=["Add monitoring"]
    )

    report = IncidentDiagnosticReport(
        root_cause="High CPU due to memory leak",
        reasoning_steps=["Step 1", "Step 2"],
        supporting_evidence=["Evidence 1"],
        confidence_score=0.85,
        recommended_remediation=remediation,
    )

    assert report.confidence_score == 0.85
    assert len(report.recommended_remediation.short_term_actions) == 1


def test_rcara_output():
    """Test RCARAOutput model."""
    output = RCARAOutput(
        incident_diagnostic_report=IncidentDiagnosticReport(
            root_cause="Test",
            reasoning_steps=["Step"],
            supporting_evidence=["Evidence"],
            confidence_score=0.7,
            recommended_remediation=RecommendedRemediation(),
        )
    )

    assert output.incident_diagnostic_report.confidence_score == 0.7
