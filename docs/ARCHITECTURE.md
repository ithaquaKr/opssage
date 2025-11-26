# OpsSage Architecture

## Overview

OpsSage is a multi-agent system designed for incident analysis and remediation recommendations. It follows Google ADK (Agent Development Kit) best practices for building production-grade multi-agent systems.

## Design Principles

1. **Modular Agents**: Each agent has a single, well-defined responsibility
2. **Clear Message Contracts**: Structured communication using Pydantic models
3. **Shared Context Store**: Thread-safe storage for incident state
4. **Capability Adapters**: Abstract interfaces for external systems
5. **Secure Orchestration**: Controlled pipeline execution with error handling

## System Architecture

### High-Level Flow

```
┌─────────┐
│  Alert  │
└────┬────┘
     │
     ▼
┌────────────────────────────────────────────────────────┐
│              OpsSage Orchestrator                      │
│                                                        │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐      │
│  │  AICA    │ ──► │  KREA    │ ──► │  RCARA   │      │
│  │          │     │          │     │          │      │
│  │ Analyze  │     │ Enrich   │     │ Diagnose │      │
│  │ Alert    │     │ Context  │     │ & Plan   │      │
│  └────┬─────┘     └────┬─────┘     └────┬─────┘      │
│       │                │                │            │
│       ▼                ▼                ▼            │
│  ┌─────────────────────────────────────────┐         │
│  │      Shared Context Store               │         │
│  └─────────────────────────────────────────┘         │
└────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────┐
│ Diagnostic Report   │
└─────────────────────┘
```

### Agent Responsibilities

#### AICA (Alert Ingestion & Context Agent)

**Purpose**: Build primary context from raw alerts

**Inputs**:
- Raw alert data (name, severity, labels, annotations)

**Outputs**:
- Primary Context Package containing:
  - Alert metadata
  - Affected components (service, namespace, pod, node)
  - Evidence collected (metrics, logs, events)
  - Preliminary analysis (observations, hypotheses)

**Tools**:
- `metrics_query_tool`: Query monitoring metrics
- `log_search_tool`: Search application and system logs
- `event_lookup_tool`: Retrieve Kubernetes events

**Reasoning Approach**:
- Chain-of-thought reasoning to identify missing information
- Systematic evidence collection using available tools
- Temporal correlation analysis
- Anomaly detection

#### KREA (Knowledge Retrieval & Enrichment Agent)

**Purpose**: Enrich context with relevant domain knowledge

**Inputs**:
- Primary Context Package from AICA

**Outputs**:
- Enhanced Context Package containing:
  - Reference to primary context
  - Retrieved knowledge items with relevance scores
  - Knowledge summary
  - Contextual enrichment (patterns, causes, related incidents)

**Tools**:
- `vector_search_tool`: Semantic search in knowledge base
- `document_lookup_tool`: Retrieve specific documents
- `playbook_query_tool`: Search runbooks and playbooks

**Reasoning Approach**:
- Extract key concepts from primary context
- Query multiple knowledge sources
- Score relevance (0-1)
- Synthesize findings into enrichment

#### RCARA (Root Cause Analysis & Remediation Agent)

**Purpose**: Determine root cause and generate remediation plan

**Inputs**:
- Primary Context Package from AICA
- Enhanced Context Package from KREA

**Outputs**:
- Incident Diagnostic Report containing:
  - Root cause determination
  - Reasoning steps
  - Supporting evidence
  - Confidence score (0-1)
  - Remediation recommendations (short-term and long-term)

**Tools**:
- `verify_cluster_state_tool`: Validate current cluster state

**Reasoning Approach**:
1. Identify dominant failure signals
2. Map evidence to known patterns
3. Evaluate causal hypotheses
4. Select final root cause
5. Generate actionable remediation plan

## Data Flow

### Message Contracts

All communication between agents uses strongly-typed Pydantic models:

```python
# AICA Output
class AICAOutput(BaseModel):
    primary_context_package: PrimaryContextPackage

# KREA Output
class KREAOutput(BaseModel):
    enhanced_context_package: EnhancedContextPackage

# RCARA Output
class RCARAOutput(BaseModel):
    incident_diagnostic_report: IncidentDiagnosticReport
```

### Context Store

The shared context store maintains incident state throughout the analysis:

```python
class IncidentContext(BaseModel):
    incident_id: str
    alert_input: AlertInput
    primary_context: PrimaryContextPackage | None
    enhanced_context: EnhancedContextPackage | None
    diagnostic_report: IncidentDiagnosticReport | None
    status: str  # pending, analyzing, completed, failed
    created_at: datetime
    updated_at: datetime
```

## Tool Architecture

### Capability Adapters

Tools are implemented using the adapter pattern with abstract interfaces:

```python
class MetricsAdapter(ABC):
    @abstractmethod
    async def query_metrics(...) -> list[dict[str, Any]]:
        pass

class MockMetricsAdapter(MetricsAdapter):
    # Mock implementation for testing
    pass

class PrometheusAdapter(MetricsAdapter):
    # Production implementation
    pass
```

### Tool Registration

Tools are registered with agents using ADK's `@tool` decorator:

```python
from google.adk.tools import tool

aica = Agent(
    name="aica",
    tools=[
        tool(metrics_query_tool),
        tool(log_search_tool),
        tool(event_lookup_tool),
    ]
)
```

## Orchestration

The orchestrator coordinates the agent pipeline:

1. Create incident in context store
2. Run AICA → update context with primary context
3. Run KREA → update context with enhanced context
4. Run RCARA → update context with diagnostic report
5. Return final diagnostic report

Error handling at each stage:
- Exceptions caught and logged
- Incident status updated to "failed"
- Error propagated to caller

## Security Considerations

### Input Validation

- All inputs validated using Pydantic models
- Type checking enforced at runtime
- Invalid data rejected before processing

### Tool Safety

- Tools operate in read-only mode by default
- No automatic remediation without explicit approval
- Policy configuration controls remediation permissions

### Secrets Management

- Credentials stored in Kubernetes secrets
- Environment variable injection
- No secrets in code or logs

## Scalability

### Horizontal Scaling

- Stateless API servers
- Shared context store (can be replaced with Redis/database)
- Kubernetes HPA based on CPU/memory

### Performance Optimization

- Async/await throughout
- Parallel tool calls where possible
- Response caching (future enhancement)

### Resource Management

- Configurable resource limits
- Request/response size limits
- Timeout controls for agent execution

## Monitoring and Observability

### Metrics

- Request count and latency
- Agent execution time
- Tool call statistics
- Error rates

### Logging

- Structured logging (JSON)
- Request tracing
- Agent reasoning traces (optional)

### Health Checks

- Liveness probe: `/api/v1/health`
- Readiness probe: `/api/v1/readiness`

## Future Enhancements

1. **Persistence**: Replace in-memory context store with database
2. **Real Tool Adapters**: Implement Prometheus, Elasticsearch, etc.
3. **Auto-remediation**: Controlled automatic remediation with approval workflows
4. **Learning Loop**: Feedback mechanism to improve recommendations
5. **Multi-tenancy**: Support for multiple teams/environments
6. **Advanced Analytics**: Trend analysis, pattern recognition
7. **Integration Hub**: Webhooks, Slack, PagerDuty integrations
