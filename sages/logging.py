"""Logging setup for OpsSage."""
import logging


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup logging configuration for OpsSage.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


# Create default logger
sage_logger = logging.getLogger("OpsSage")
