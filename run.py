#!/usr/bin/env python3
"""OpsSage - Multi-Agent Incident Response System.

Simple entry point that loads configuration and starts the API server.
"""
import sys
import uvicorn
from pathlib import Path

from sages.config import load_config
from sages.logging import setup_logging


def main():
    """Main entry point for OpsSage."""
    # Load configuration
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"

    if not Path(config_path).exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("💡 Create config.yaml from config.example.yaml:")
        print("   cp config.example.yaml config.yaml")
        sys.exit(1)

    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)

    # Setup logging
    log_level = config.get('system.log_level', 'INFO')
    setup_logging(log_level)

    # Get server configuration
    host = config.get('system.host', '0.0.0.0')
    port = config.get('system.port', 8000)

    # Print startup information
    print("=" * 60)
    print("🚀 OpsSage - Multi-Agent Incident Response System")
    print("=" * 60)
    print(f"📊 Dashboard:  http://localhost:3000")
    print(f"📚 API Docs:   http://localhost:{port}/docs")
    print(f"🔧 API Server: http://{host}:{port}")
    print("=" * 60)
    print()

    # Start server
    uvicorn.run(
        "apis.main:app",
        host=host,
        port=port,
        reload=False,
        log_level=log_level.lower()
    )


if __name__ == "__main__":
    main()
