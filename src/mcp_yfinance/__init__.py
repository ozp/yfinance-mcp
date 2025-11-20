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

__version__ = "0.1.1"

# Lazy import of main to avoid requiring server dependencies during testing
__all__ = ["main", "__version__"]


def main():
    """Entry point for the CLI."""
    import asyncio
    from .server import main as async_main
    asyncio.run(async_main())


def __getattr__(name):
    """Lazy import for other attributes."""
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
