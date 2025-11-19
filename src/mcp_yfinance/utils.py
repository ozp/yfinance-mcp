"""Utility functions for MCP Yahoo Finance Server.

This module provides utility functions for ticker normalization,
data formatting, cache key generation, and MCP tool schema generation.
"""

import hashlib
import inspect
import re
from collections.abc import Callable
from typing import Any, get_args, get_origin, get_type_hints

import pandas as pd


# Market suffix mapping for ticker normalization
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
    "CN": ".SS",  # Shanghai Stock Exchange
    "ES": ".MC",  # Madrid Stock Exchange
    "IT": ".MI",  # Milan Stock Exchange
    "NL": ".AS",  # Amsterdam Stock Exchange
    "CH": ".SW",  # Swiss Exchange
    "SE": ".ST",  # Stockholm Stock Exchange
    "KR": ".KS",  # Korea Stock Exchange
    "TW": ".TW",  # Taiwan Stock Exchange
    "SG": ".SI",  # Singapore Exchange
    "MX": ".MX",  # Mexican Stock Exchange
    "AR": ".BA",  # Buenos Aires Stock Exchange
}


def normalize_ticker(ticker: str, market: str = "US") -> str:
    """Normalize a ticker symbol for a specific market.

    Adds the appropriate market suffix to the ticker if needed.
    If the ticker already has a suffix, it is returned as-is.

    Args:
        ticker: The ticker symbol to normalize
        market: Market code (e.g., "US", "BR", "UK"). Defaults to "US"

    Returns:
        Normalized ticker with appropriate market suffix

    Examples:
        >>> normalize_ticker("AAPL", "US")
        'AAPL'
        >>> normalize_ticker("PETR4", "BR")
        'PETR4.SA'
        >>> normalize_ticker("RELIANCE", "IN_NSE")
        'RELIANCE.NS'
        >>> normalize_ticker("AAPL.US", "BR")
        'AAPL.US'  # Already has a suffix, return as-is
    """
    ticker = ticker.strip().upper()

    # If ticker already contains a period (has a suffix), return as-is
    if "." in ticker:
        return ticker

    # Get the suffix for the market, default to empty string if not found
    suffix = MARKET_SUFFIXES.get(market.upper(), "")

    return ticker + suffix


def format_dataframe_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert DataFrame datetime index to ISO format strings.

    Args:
        df: DataFrame with datetime index

    Returns:
        DataFrame with datetime index converted to ISO strings
    """
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.copy()
        df.index = df.index.strftime("%Y-%m-%d")

    return df


def generate_cache_key(tool_name: str, **kwargs: Any) -> str:
    """Generate a consistent cache key from tool name and parameters.

    Args:
        tool_name: Name of the tool
        **kwargs: Tool parameters

    Returns:
        MD5 hash of the tool name and parameters
    """
    # Sort kwargs to ensure consistent ordering
    sorted_params = sorted(kwargs.items())
    key_string = f"{tool_name}:{sorted_params}"

    # Generate MD5 hash
    return hashlib.md5(key_string.encode()).hexdigest()


def parse_docstring(docstring: str | None) -> dict[str, str]:
    """Extract parameter descriptions from a Google-style docstring.

    Args:
        docstring: Function docstring

    Returns:
        Dictionary mapping parameter names to their descriptions
    """
    if not docstring:
        return {}

    param_descriptions = {}
    lines = docstring.split("\n")
    in_args_section = False
    current_param = None

    for line in lines:
        stripped = line.strip()

        # Check if we're entering the Args section
        if stripped.startswith("Args:"):
            in_args_section = True
            continue

        # Check if we're leaving the Args section
        if in_args_section and stripped and not stripped.startswith(" ") and ":" in stripped:
            if not stripped[0].isspace() and stripped != "Args:":
                in_args_section = False

        if in_args_section and ":" in stripped:
            # Parse parameter line like "symbol: Stock ticker symbol"
            match = re.match(r"(\w+):\s*(.+)", stripped)
            if match:
                param_name, description = match.groups()
                current_param = param_name
                param_descriptions[param_name] = description
            elif current_param:
                # Continuation of previous parameter description
                param_descriptions[current_param] += " " + stripped

    return param_descriptions


def generate_tool_schema(func: Callable) -> dict[str, Any]:
    """Generate MCP Tool schema from a function.

    Automatically extracts parameter types, descriptions, and
    generates the JSON schema expected by MCP.

    Args:
        func: Function to generate schema for

    Returns:
        MCP Tool schema dictionary
    """
    # Get function signature and type hints
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    param_docs = parse_docstring(func.__doc__)

    # Extract function description (first line of docstring)
    description = ""
    if func.__doc__:
        description = func.__doc__.split("\n\n")[0].strip()

    # Build input schema
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        # Get type information
        param_type = type_hints.get(param_name, str)

        # Determine JSON schema type
        schema_type = _python_type_to_json_schema(param_type)

        # Add to properties
        properties[param_name] = {
            "type": schema_type["type"],
            "description": param_docs.get(param_name, ""),
        }

        # Add enum if it's a Literal type
        if "enum" in schema_type:
            properties[param_name]["enum"] = schema_type["enum"]

        # Check if required (no default value)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "name": func.__name__,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }


def _python_type_to_json_schema(python_type: Any) -> dict[str, Any]:
    """Convert Python type to JSON Schema type.

    Args:
        python_type: Python type annotation

    Returns:
        JSON Schema type dictionary
    """
    # Handle Literal types (for enums)
    origin = get_origin(python_type)
    if origin is type(Literal):  # type: ignore
        args = get_args(python_type)
        return {"type": "string", "enum": list(args)}

    # Handle basic types
    type_mapping = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
    }

    # Check if it's a basic type
    if python_type in type_mapping:
        return type_mapping[python_type]

    # Handle Optional types (Union with None)
    if origin is type(Union):  # type: ignore
        args = get_args(python_type)
        # Filter out NoneType
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return _python_type_to_json_schema(non_none_args[0])

    # Default to string
    return {"type": "string"}


# Import typing constructs needed for type checking
from typing import Literal, Union  # noqa: E402
