"""Configuration management for OpsSage.

Simple YAML-based configuration with environment variable substitution.
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from string import Template


class Config:
    """Simple configuration loader from YAML."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration loader.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and parse YAML config, substituting environment variables.

        Returns:
            Parsed configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path) as f:
            content = f.read()

        # Substitute environment variables (${VAR_NAME} syntax)
        template = Template(content)
        substituted = template.safe_substitute(os.environ)

        return yaml.safe_load(substituted)

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., 'models.worker_model')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config.get('models.worker_model')
            'gemini-1.5-flash'
            >>> config.get('system.port', 8000)
            8000
        """
        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default

        return value if value is not None else default

    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return self._config

    def __repr__(self) -> str:
        """String representation of config."""
        return f"Config(path={self.config_path})"


# Global config instance
_config_instance: Optional[Config] = None


def load_config(config_path: str = "config.yaml") -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file

    Returns:
        Config instance
    """
    global _config_instance
    _config_instance = Config(config_path)
    return _config_instance


def get_config() -> Config:
    """Get current configuration instance.

    Returns:
        Config instance (loads default if not already loaded)
    """
    if _config_instance is None:
        return load_config()
    return _config_instance
