"""Configuration for MCP Yahoo Finance Server.

This module provides configuration options for the MCP Yahoo Finance server,
including market selection and supported markets.
"""

import os

# Default market for ticker normalization
# Can be overridden via YFINANCE_DEFAULT_MARKET environment variable
DEFAULT_MARKET: str = os.getenv("YFINANCE_DEFAULT_MARKET", "US")

# Supported markets with their Yahoo Finance suffixes
SUPPORTED_MARKETS = [
    "US",  # United States (no suffix)
    "BR",  # Brazil (.SA)
    "UK",  # United Kingdom (.L)
    "DE",  # Germany (.DE)
    "FR",  # France (.PA)
    "JP",  # Japan (.T)
    "IN_NSE",  # India - National Stock Exchange (.NS)
    "IN_BSE",  # India - Bombay Stock Exchange (.BO)
    "HK",  # Hong Kong (.HK)
    "AU",  # Australia (.AX)
    "CA",  # Canada (.TO)
    "CN",  # China (.SS)
    "ES",  # Spain (.MC)
    "IT",  # Italy (.MI)
    "NL",  # Netherlands (.AS)
    "CH",  # Switzerland (.SW)
    "SE",  # Sweden (.ST)
    "KR",  # South Korea (.KS)
    "TW",  # Taiwan (.TW)
    "SG",  # Singapore (.SI)
    "MX",  # Mexico (.MX)
    "AR",  # Argentina (.BA)
]

# Cache directory
CACHE_DIR: str = os.getenv("YFINANCE_CACHE_DIR", str(os.path.expanduser("~/.mcp-yfinance")))
