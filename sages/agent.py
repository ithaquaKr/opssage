from google.adk.agents import Agent

from sages.configs import sage_configs

sage_agent = Agent(
    name="sage",
    model=sage_configs.worker_model,
    description="The main OpsSage orchestrator. It executes a deterministic flow to analyze an alert.",
    instruction="",
    output_key="",
)

root_agent = sage_agent
