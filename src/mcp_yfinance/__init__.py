"""MCP Yahoo Finance Server.

A Model Context Protocol (MCP) server that provides comprehensive access
to Yahoo Finance data for AI assistants and other MCP clients.

Features:
- 18 comprehensive tools for stock data retrieval
- Multi-market support (US, BR, UK, JP, and more)
- Intelligent caching with configurable TTL
- Type-safe with Pydantic models
- Thread-safe SQLite cache

Example:
    Run the server with uvx:

    $ uvx mcp-yfinance

    Or configure market:

    $ YFINANCE_DEFAULT_MARKET=BR uvx mcp-yfinance
"""

__version__ = "0.1.0"

from .server import main

__all__ = ["main"]
