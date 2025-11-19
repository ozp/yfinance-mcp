"""CLI entry point for MCP Yahoo Finance Server.

This module allows the package to be run as a module:
    python -m mcp_yfinance
"""

import asyncio

from .server import main

if __name__ == "__main__":
    asyncio.run(main())
