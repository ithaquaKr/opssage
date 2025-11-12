from pydantic import BaseModel, Field


class AlertData(BaseModel):
    """A simplified model for a single alert from Alertmanager."""

    startsAt: str = Field(..., description="Timestamp of when the alert started.")
    status: str = Field(..., description="Current status (e.g., 'firing', 'resolved').")
    labels: dict[str, str] = Field(
        ...,
        description="Key-value pairs identifying the alert source (e.g., 'alertname', 'instance').",
    )
    annotations: dict[str, str] = Field(
        ...,
        description="Key-value pairs with descriptive information (e.g., 'summary', 'description').",
    )


class AlertPayload(BaseModel):
    """The full payload structure expected from Alertmanager."""

    version: str
    status: str
    alerts: list[AlertData]
    receiver: str
    groupKey: str


class AnalysisReport(BaseModel):
    """Structured output from the OpsSage system."""

    alert_name: str = Field(..., description="The primary name of the alert.")
    severity: str = Field(
        ...,
        description="The determined severity (e.g., 'Critical', 'Warning', 'Info').",
    )
    analysis_summary: str = Field(
        ...,
        description="A concise summary of the root cause based on alert data and knowledge retrieval.",
    )
    resolution_steps: str = Field(
        ..., description="Actionable steps or commands suggested to resolve the issue."
    )
    knowledge_sources: list[str] = Field(
        default_factory=list,
        description="List of knowledge base documents or URLs used for grounding.",
    )
