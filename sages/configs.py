from dataclasses import dataclass


@dataclass
class Configuration:
    critic_model: str = "gemini-2.5-pro"
    worker_model: str = "gemini-2.5-flash"
    max_search_iterations: int = 5
    # Log
    log_level: str = "INFO"


sage_configs = Configuration()
