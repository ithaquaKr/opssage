"""
Main agent entry point for OpsSage.
Exports the orchestrator and agents for the multi-agent system.
"""

from sages.orchestrator import create_orchestrator
from sages.subagents.aica import create_aica_agent
from sages.subagents.krea import create_krea_agent
from sages.subagents.rcara import create_rcara_agent

# Create agent instances
aica_agent = create_aica_agent()
krea_agent = create_krea_agent()
rcara_agent = create_rcara_agent()

# Create orchestrator
orchestrator = create_orchestrator()

# Export root agent (for compatibility with ADK tooling)
root_agent = aica_agent

__all__ = [
    "aica_agent",
    "krea_agent",
    "orchestrator",
    "rcara_agent",
    "root_agent",
]
