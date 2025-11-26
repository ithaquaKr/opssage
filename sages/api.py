"""
Backward compatibility module.
Re-exports FastAPI app from apis.main for existing code that imports from sages.api.

The actual API implementation has been moved to apis/main.py.
This module maintains backward compatibility for existing imports.
"""

from apis.main import app

__all__ = ["app"]
