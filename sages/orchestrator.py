"""
Orchestration layer for the multi-agent incident analysis system.
Coordinates the flow between AICA, KREA, and RCARA agents.
"""

import json
import logging
import os
import uuid
from typing import Any

from google.adk import Runner
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.genai import types

from sages.config import get_config

# Set GOOGLE_API_KEY from config
config = get_config()
gemini_api_key = config.get("models.gemini_api_key")
if gemini_api_key and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = gemini_api_key

from sages.context_store import get_context_store
from sages.models import (
    AICAOutput,
    AlertInput,
    EnhancedContextPackage,
    IncidentDiagnosticReport,
    KREAOutput,
    PrimaryContextPackage,
    RCARAOutput,
)
from sages.notifications import get_notifier
from sages.subagents.aica import create_aica_agent
from sages.subagents.krea import create_krea_agent
from sages.subagents.rcara import create_rcara_agent

logger = logging.getLogger(__name__)


class IncidentOrchestrator:
    """
    Orchestrates the multi-agent incident analysis workflow.
    Coordinates AICA → KREA → RCARA pipeline.
    """

    def __init__(self) -> None:
        """Initialize the orchestrator with agent instances."""
        self.aica: Agent = create_aica_agent()
        self.krea: Agent = create_krea_agent()
        self.rcara: Agent = create_rcara_agent()
        self.context_store = get_context_store()
        self.notifier = get_notifier()

        # Setup session service and runners
        self.session_service = InMemorySessionService()
        self.aica_runner = Runner(
            app_name="agents",
            agent=self.aica,
            session_service=self.session_service,
        )
        self.krea_runner = Runner(
            app_name="agents",
            agent=self.krea,
            session_service=self.session_service,
        )
        self.rcara_runner = Runner(
            app_name="agents",
            agent=self.rcara,
            session_service=self.session_service,
        )

    async def analyze_incident(
        self, alert: AlertInput
    ) -> tuple[str, IncidentDiagnosticReport]:
        """
        Run the full incident analysis pipeline.

        Args:
            alert: The alert to analyze

        Returns:
            Tuple of (incident_id, diagnostic_report)

        Raises:
            Exception: If any stage of the analysis fails
        """
        import time

        # Create incident in context store
        incident_id = await self.context_store.create_incident(alert)
        logger.info(f"Created incident {incident_id} for alert {alert.alert_name}")

        # Send start notification
        start_time = time.time()
        await self.notifier.send_incident_start(incident_id, alert)

        try:
            # Stage 1: AICA - Alert Ingestion & Context
            await self.context_store.update_status(incident_id, "running_aica")
            primary_context = await self._run_aica(alert)
            await self.context_store.update_primary_context(
                incident_id, primary_context
            )
            logger.info(f"AICA completed for incident {incident_id}")

            # Stage 2: KREA - Knowledge Retrieval & Enrichment
            await self.context_store.update_status(incident_id, "running_krea")
            enhanced_context = await self._run_krea(primary_context)
            await self.context_store.update_enhanced_context(
                incident_id, enhanced_context
            )
            logger.info(f"KREA completed for incident {incident_id}")

            # Stage 3: RCARA - Root Cause Analysis & Remediation
            await self.context_store.update_status(incident_id, "running_rcara")
            diagnostic_report = await self._run_rcara(primary_context, enhanced_context)
            await self.context_store.update_diagnostic_report(
                incident_id, diagnostic_report
            )
            logger.info(f"RCARA completed for incident {incident_id}")

            # Send completion notification
            duration = time.time() - start_time
            await self.notifier.send_incident_complete(
                incident_id, alert, diagnostic_report, duration
            )

            return incident_id, diagnostic_report

        except Exception as e:
            logger.error(f"Error analyzing incident {incident_id}: {e}")
            await self.context_store.update_status(incident_id, "failed")

            # Send error notification
            duration = time.time() - start_time
            await self.notifier.send_incident_error(
                incident_id, alert, str(e), duration
            )

            raise

    async def _run_aica(self, alert: AlertInput) -> PrimaryContextPackage:
        """
        Run AICA agent to build primary context.

        Args:
            alert: The alert input

        Returns:
            Primary context package from AICA
        """
        # Prepare input for AICA
        alert_json = alert.model_dump_json(indent=2)
        prompt = f"""Analyze the following alert and build a comprehensive Primary Context Package.

Alert:
{alert_json}

Use the available tools to gather metrics, logs, and events as needed to build a complete picture of the incident."""

        # Create user message
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        # Create session and run AICA agent
        user_id = "sage_system"
        session_id = str(uuid.uuid4())
        await self.session_service.create_session(
            app_name="agents",
            user_id=user_id,
            session_id=session_id,
        )
        final_response = None

        async for event in self.aica_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            if event.is_final_response():
                final_response = event
                break

        if final_response is None or not final_response.content:
            raise ValueError("No final response received from AICA agent")

        # Extract text content from response
        response_text = ""
        for part in final_response.content.parts:
            if hasattr(part, 'text') and part.text:
                response_text += part.text

        # Parse and validate response
        output_data = self._extract_json_from_response(response_text)
        aica_output = AICAOutput.model_validate(output_data)

        return aica_output.primary_context_package

    async def _run_krea(
        self, primary_context: PrimaryContextPackage
    ) -> EnhancedContextPackage:
        """
        Run KREA agent to enrich context with knowledge.

        Args:
            primary_context: The primary context from AICA

        Returns:
            Enhanced context package from KREA
        """
        # Prepare input for KREA
        context_json = primary_context.model_dump_json(indent=2)
        prompt = f"""Enrich the following Primary Context Package with relevant knowledge from the knowledge base.

Primary Context Package:
{context_json}

Use the available tools to search for relevant documentation, playbooks, and past incidents.
Focus on retrieving actionable knowledge that will help with root cause analysis."""

        # Create user message
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        # Create session and run KREA agent
        user_id = "sage_system"
        session_id = str(uuid.uuid4())
        await self.session_service.create_session(
            app_name="agents",
            user_id=user_id,
            session_id=session_id,
        )
        final_response = None

        async for event in self.krea_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            if event.is_final_response():
                final_response = event
                break

        if final_response is None or not final_response.content:
            raise ValueError("No final response received from KREA agent")

        # Extract text content from response
        response_text = ""
        for part in final_response.content.parts:
            if hasattr(part, 'text') and part.text:
                response_text += part.text

        # Parse and validate response
        output_data = self._extract_json_from_response(response_text)
        krea_output = KREAOutput.model_validate(output_data)

        return krea_output.enhanced_context_package

    async def _run_rcara(
        self,
        primary_context: PrimaryContextPackage,
        enhanced_context: EnhancedContextPackage,
    ) -> IncidentDiagnosticReport:
        """
        Run RCARA agent to perform root cause analysis.

        Args:
            primary_context: The primary context from AICA
            enhanced_context: The enhanced context from KREA

        Returns:
            Incident diagnostic report from RCARA
        """
        # Prepare input for RCARA
        primary_json = primary_context.model_dump_json(indent=2)
        enhanced_json = enhanced_context.model_dump_json(indent=2)

        prompt = f"""Perform root cause analysis and generate remediation recommendations.

Primary Context Package:
{primary_json}

Enhanced Context Package:
{enhanced_json}

Use structured reasoning to identify the root cause and provide specific, actionable remediation recommendations."""

        # Create user message
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )

        # Create session and run RCARA agent
        user_id = "sage_system"
        session_id = str(uuid.uuid4())
        await self.session_service.create_session(
            app_name="agents",
            user_id=user_id,
            session_id=session_id,
        )
        final_response = None

        async for event in self.rcara_runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            if event.is_final_response():
                final_response = event
                break

        if final_response is None or not final_response.content:
            raise ValueError("No final response received from RCARA agent")

        # Extract text content from response
        response_text = ""
        for part in final_response.content.parts:
            if hasattr(part, 'text') and part.text:
                response_text += part.text

        # Parse and validate response
        output_data = self._extract_json_from_response(response_text)
        rcara_output = RCARAOutput.model_validate(output_data)

        return rcara_output.incident_diagnostic_report

    def _extract_json_from_response(self, response: str) -> dict[str, Any]:
        """
        Extract JSON from agent response, handling code blocks and other formatting.

        Args:
            response: The raw response from an agent

        Returns:
            Parsed JSON data

        Raises:
            ValueError: If JSON cannot be extracted or parsed
        """
        # Remove markdown code blocks if present
        content = response.strip()

        # Check for ```json blocks
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        # Check for ``` blocks
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()

        # Try to find JSON object boundaries
        if not content.startswith("{"):
            start = content.find("{")
            if start == -1:
                raise ValueError("No JSON object found in response")
            content = content[start:]

        if not content.endswith("}"):
            end = content.rfind("}")
            if end == -1:
                raise ValueError("No complete JSON object found in response")
            content = content[: end + 1]

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Content: {content}")
            raise ValueError(f"Invalid JSON in response: {e}") from e


def create_orchestrator() -> IncidentOrchestrator:
    """
    Create an instance of the incident orchestrator.

    Returns:
        Configured IncidentOrchestrator instance
    """
    return IncidentOrchestrator()
