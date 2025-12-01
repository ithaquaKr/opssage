"""
SQLAlchemy database models for OpsSage.
Stores incident data with full context for persistence.
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class IncidentModel(Base):
    """
    Database model for storing incident analysis data.

    Stores all incident information including alert input, analysis contexts,
    and diagnostic reports with full JSON serialization.
    """

    __tablename__ = "incidents"

    # Primary key
    incident_id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Status and timestamps
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Alert input (stored as JSON)
    alert_input: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # AICA output - Primary context (stored as JSON)
    primary_context: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # KREA output - Enhanced context (stored as JSON)
    enhanced_context: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # RCARA output - Diagnostic report (stored as JSON)
    diagnostic_report: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    # Denormalized fields for quick filtering/searching
    alert_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    namespace: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    service: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Root cause analysis (for quick access)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<IncidentModel(incident_id={self.incident_id!r}, "
            f"status={self.status!r}, alert_name={self.alert_name!r})>"
        )
