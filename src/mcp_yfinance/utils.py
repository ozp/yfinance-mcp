"""Utility functions for MCP Yahoo Finance.

This module provides helper functions for ticker normalization, data formatting,
and other common operations.
"""

import hashlib
import json
from typing import Any, Callable

import pandas as pd


# Market suffix configuration for ticker normalization
MARKET_SUFFIXES = {
    "US": "",
    "BR": ".SA",
    "UK": ".L",
    "DE": ".DE",
    "FR": ".PA",
    "JP": ".T",
    "IN_NSE": ".NS",  # National Stock Exchange
    "IN_BSE": ".BO",  # Bombay Stock Exchange
    "HK": ".HK",
    "AU": ".AX",
    "CA": ".TO",
}


def normalize_ticker(ticker: str, market: str = "US") -> str:
    """Normalize ticker symbol for the specified market.

    Adds the appropriate market suffix to the ticker symbol if not already present.
    This ensures compatibility with Yahoo Finance's ticker naming conventions.

    Args:
        ticker: The base ticker symbol (e.g., "AAPL", "PETR4").
        market: Market identifier (default: "US"). Must be one of the keys in MARKET_SUFFIXES.

    Returns:
        Normalized ticker with market suffix if applicable.

    Examples:
        >>> normalize_ticker("AAPL", "US")
        'AAPL'
        >>> normalize_ticker("PETR4", "BR")
        'PETR4.SA'
        >>> normalize_ticker("RELIANCE", "IN_NSE")
        'RELIANCE.NS'
    """
    market = market.upper()
    suffix = MARKET_SUFFIXES.get(market, "")

    # If ticker already has the suffix, don't add it again
    if suffix and not ticker.endswith(suffix):
        return f"{ticker}{suffix}"

    return ticker


def format_dataframe_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert DataFrame datetime index to ISO format strings.

    Args:
        df: DataFrame with datetime index.

    Returns:
        DataFrame with index converted to ISO format strings.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = df.index.strftime("%Y-%m-%d")

    return df


def generate_cache_key(tool_name: str, **kwargs: Any) -> str:
    """Generate a consistent cache key from tool name and parameters.

    Args:
        tool_name: Name of the tool/function.
        **kwargs: Tool parameters to include in the cache key.

    Returns:
        SHA-256 hash of the tool name and sorted parameters.

    Examples:
        >>> generate_cache_key("get_stock_price", symbol="AAPL", date="2024-01-01")
        'a1b2c3d4...'
    """
    # Sort kwargs to ensure consistent key generation
    sorted_params = json.dumps(kwargs, sort_keys=True)
    key_string = f"{tool_name}:{sorted_params}"
    return hashlib.sha256(key_string.encode()).hexdigest()


def parse_docstring(docstring: str) -> dict[str, str]:
    """Extract parameter descriptions from a Google-style docstring.

    Args:
        docstring: Function docstring in Google style.

    Returns:
        Dictionary mapping parameter names to their descriptions.

    Examples:
        >>> parse_docstring("Get stock price.\\n\\nArgs:\\n    symbol: Ticker symbol.\\n")
        {'symbol': 'Ticker symbol.'}
    """
    if not docstring:
        return {}

    params = {}
    lines = docstring.split("\n")
    in_args_section = False
    current_param = None

    for line in lines:
        stripped = line.strip()

        # Check if we're entering the Args section
        if stripped == "Args:":
            in_args_section = True
            continue

        # Check if we're leaving the Args section
        if in_args_section and stripped and not line.startswith(" "):
            break

        # Parse parameter line
        if in_args_section and ":" in stripped:
            parts = stripped.split(":", 1)
            param_name = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
            params[param_name] = description
            current_param = param_name
        elif in_args_section and current_param and stripped:
            # Continuation of previous parameter description
            params[current_param] += f" {stripped}"

    return params


def generate_tool_schema(func: Callable) -> dict[str, Any]:
    """Auto-generate MCP Tool schema from function signature and docstring.

    Args:
        func: Function to generate schema for.

    Returns:
        MCP tool schema dictionary with name, description, and parameters.

    Examples:
        >>> def get_price(symbol: str) -> str:
        ...     '''Get stock price. Args: symbol: Ticker symbol.'''
        ...     pass
        >>> schema = generate_tool_schema(get_price)
        >>> schema['name']
        'get_price'
    """
    import inspect

    # Get function signature
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ""

    # Extract description (first line/paragraph)
    description_lines = []
    for line in doc.split("\n"):
        stripped = line.strip()
        if stripped == "Args:" or stripped == "Returns:":
            break
        if stripped:
            description_lines.append(stripped)

    description = " ".join(description_lines) or func.__name__

    # Parse parameter descriptions
    param_descriptions = parse_docstring(doc)

    # Build parameter schema
    parameters = {}
    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        param_schema: dict[str, Any] = {
            "type": "string",  # Default type
            "description": param_descriptions.get(param_name, ""),
        }

        # Add required flag if no default value
        if param.default == inspect.Parameter.empty:
            param_schema["required"] = True

        parameters[param_name] = param_schema

    return {
        "name": func.__name__,
        "description": description,
        "parameters": parameters,
    }
