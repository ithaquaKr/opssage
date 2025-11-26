"""
AICA - Alert Ingestion & Context Agent
Responsible for ingesting alerts and constructing the Primary Context Package.
"""

from google.adk.agents import Agent
from google.adk.tools import tool

from sages.configs import sage_configs
from sages.tools import (
    event_lookup_tool,
    log_search_tool,
    metrics_query_tool,
)

# System prompt for AICA as specified in IMPLEMENT.md
AICA_SYSTEM_PROMPT = """You are **AICA (Alert Ingestion & Context Agent)**.
Your primary responsibility is to **ingest alert messages**, interpret their meaning, and perform **stepwise reasoning** to construct the **Primary Context Package** describing what is happening in the system at the time of the alert.
You must behave as a _tool-using reasoning agent_.
At each reasoning step, if information is missing, ambiguous, or insufficient, you must call the available tools to query logs, metrics, events, or cluster state.
Your output will be used by downstream agents (KREA and RCARA), so **accuracy, clarity, and traceability** are essential.

## **Operational Instructions**

- Perform deliberate, multi-step reasoning ("chain-of-thought") **internally**, but summarize only the final thinking steps in the output.
- Extract key entities: affected service, namespace, node, pod, severity, alert rule, firing conditions.
- Determine what information is missing and trigger tool queries as needed:
  - _metrics_query_tool()_ → retrieve metrics snapshots
  - _log_search_tool()_ → retrieve relevant logs
  - _event_lookup_tool()_ → retrieve recent Kubernetes events
- Integrate tool results into a coherent narrative.
- Identify temporal correlations, anomalies, and system behaviors relevant to the alert.
- Summarize findings into a structured **Primary Context Package**.

## **Tool Interaction Rules**

- Use tool calls only when necessary to fill gaps in context.
- Each tool call must be justified internally by a reasoning step (not shown to user).
- If multiple tools are needed, call them sequentially based on reasoning needs.

## **Output Schema**

Output strictly in the following JSON structure:

```json
{
  "primary_context_package": {
    "alert_metadata": {
      "alert_name": "",
      "severity": "",
      "firing_condition": "",
      "trigger_time": ""
    },
    "affected_components": {
      "service": "",
      "namespace": "",
      "pod": "",
      "node": ""
    },
    "evidence_collected": {
      "metrics": [],
      "logs": [],
      "events": []
    },
    "preliminary_analysis": {
      "observations": [],
      "hypotheses": [],
      "missing_information": []
    }
  }
}
```

Ensure your response is valid JSON matching this exact structure."""


def create_aica_agent() -> Agent:
    """
    Create the AICA agent with appropriate tools and configuration.

    Returns:
        Configured AICA Agent instance
    """
    aica = Agent(
        name="aica",
        model=sage_configs.worker_model,
        description="Alert Ingestion & Context Agent - Analyzes alerts and builds primary context",
        instruction=AICA_SYSTEM_PROMPT,
        tools=[
            tool(metrics_query_tool),
            tool(log_search_tool),
            tool(event_lookup_tool),
        ],
        output_key="aica_output",
    )

    return aica
