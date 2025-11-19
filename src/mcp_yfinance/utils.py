"""Utility functions for MCP Yahoo Finance server.

This module provides helper functions for ticker normalization,
data formatting, caching, and tool schema generation.
"""

import hashlib
import json
from typing import Callable, Any
import pandas as pd
from datetime import datetime


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
    "CN": ".SS",  # Shanghai Stock Exchange
    "KR": ".KS",  # Korea Stock Exchange
    "IT": ".MI",  # Milan
    "ES": ".MC",  # Madrid
    "NL": ".AS",  # Amsterdam
    "CH": ".SW",  # Switzerland
    "SE": ".ST",  # Stockholm
    "NO": ".OL",  # Oslo
    "DK": ".CO",  # Copenhagen
    "FI": ".HE",  # Helsinki
    "BE": ".BR",  # Brussels
    "NZ": ".NZ",  # New Zealand
    "SG": ".SI",  # Singapore
    "MY": ".KL",  # Malaysia
    "TH": ".BK",  # Thailand
    "ID": ".JK",  # Indonesia
    "PH": ".PS",  # Philippines
    "VN": ".VN",  # Vietnam
    "TW": ".TW",  # Taiwan
    "TR": ".IS",  # Istanbul
    "ZA": ".JO",  # Johannesburg
    "MX": ".MX",  # Mexico
    "AR": ".BA",  # Buenos Aires
    "CL": ".SN",  # Santiago
}


def normalize_ticker(ticker: str, market: str = "US") -> str:
    """Normalize ticker symbol for the specified market.

    Adds the appropriate market suffix to the ticker symbol if not already present.
    For example, 'PETR4' in the BR market becomes 'PETR4.SA'.

    Args:
        ticker: The base ticker symbol (e.g., 'AAPL', 'PETR4', 'RELIANCE')
        market: Market code (e.g., 'US', 'BR', 'UK', 'JP', 'IN_NSE')

    Returns:
        Normalized ticker with appropriate market suffix

    Raises:
        ValueError: If market is not supported

    Examples:
        >>> normalize_ticker("AAPL", "US")
        'AAPL'
        >>> normalize_ticker("PETR4", "BR")
        'PETR4.SA'
        >>> normalize_ticker("RELIANCE", "IN_NSE")
        'RELIANCE.NS'
        >>> normalize_ticker("7203", "JP")
        '7203.T'
    """
    if market not in MARKET_SUFFIXES:
        raise ValueError(
            f"Unsupported market: {market}. "
            f"Supported markets: {', '.join(MARKET_SUFFIXES.keys())}"
        )

    suffix = MARKET_SUFFIXES[market]

    # If ticker already has the suffix, return as-is
    if suffix and ticker.endswith(suffix):
        return ticker

    # If ticker has a different suffix, return as-is (user knows what they want)
    if "." in ticker:
        return ticker

    # Add the market suffix
    return ticker + suffix


def format_dataframe_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convert DataFrame datetime index/columns to ISO format strings.

    Args:
        df: DataFrame with datetime index or columns

    Returns:
        DataFrame with datetime converted to ISO strings

    Examples:
        >>> df = pd.DataFrame({'value': [1, 2]},
        ...                   index=pd.DatetimeIndex(['2024-01-01', '2024-01-02']))
        >>> formatted = format_dataframe_dates(df)
        >>> formatted.index[0]
        '2024-01-01T00:00:00'
    """
    df = df.copy()

    # Convert datetime index to ISO strings
    if isinstance(df.index, pd.DatetimeIndex):
        df.index = df.index.strftime("%Y-%m-%dT%H:%M:%S")

    # Convert datetime columns to ISO strings
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

    return df


def generate_cache_key(tool_name: str, **kwargs) -> str:
    """Generate a consistent cache key from tool name and parameters.

    Args:
        tool_name: Name of the tool/method
        **kwargs: Tool parameters

    Returns:
        SHA-256 hash of the serialized parameters

    Examples:
        >>> generate_cache_key("get_stock_info", symbol="AAPL")
        'a1b2c3...'
        >>> generate_cache_key("get_historical_data", symbol="GOOGL", period="1mo")
        'd4e5f6...'
    """
    # Sort kwargs for consistency
    sorted_params = sorted(kwargs.items())
    key_string = f"{tool_name}:{json.dumps(sorted_params, sort_keys=True)}"
    return hashlib.sha256(key_string.encode()).hexdigest()


def parse_docstring(docstring: str) -> dict[str, str]:
    """Extract parameter descriptions from a Google-style docstring.

    Args:
        docstring: Function docstring in Google style

    Returns:
        Dictionary mapping parameter names to their descriptions

    Examples:
        >>> doc = '''Get stock info.
        ...
        ... Args:
        ...     symbol: Stock ticker symbol
        ...     market: Market code
        ... '''
        >>> parse_docstring(doc)
        {'symbol': 'Stock ticker symbol', 'market': 'Market code'}
    """
    if not docstring:
        return {}

    params = {}
    in_args_section = False

    for line in docstring.split("\n"):
        line = line.strip()

        # Check if we're entering the Args section
        if line.startswith("Args:"):
            in_args_section = True
            continue

        # Check if we're leaving the Args section
        if in_args_section and line.endswith(":") and not line.startswith(" "):
            break

        # Parse parameter lines
        if in_args_section and ":" in line:
            parts = line.split(":", 1)
            param_name = parts[0].strip()
            param_desc = parts[1].strip() if len(parts) > 1 else ""
            params[param_name] = param_desc

    return params


def generate_tool_schema(func: Callable) -> dict[str, Any]:
    """Generate MCP Tool schema from a function's signature and docstring.

    Args:
        func: Function to generate schema for

    Returns:
        MCP Tool schema dictionary with name, description, and inputSchema

    Examples:
        >>> def get_price(symbol: str, market: str = "US") -> str:
        ...     '''Get stock price.
        ...
        ...     Args:
        ...         symbol: Stock ticker symbol
        ...         market: Market code
        ...     '''
        ...     pass
        >>> schema = generate_tool_schema(get_price)
        >>> schema['name']
        'get_price'
    """
    import inspect

    # Get function name
    name = func.__name__

    # Get docstring
    doc = inspect.getdoc(func) or ""
    description = doc.split("\n\n")[0] if doc else f"Execute {name}"

    # Get parameter info from docstring
    param_descriptions = parse_docstring(doc)

    # Get function signature
    sig = inspect.signature(func)

    # Build input schema
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        # Get parameter type
        param_type = "string"  # Default
        if param.annotation != inspect.Parameter.empty:
            annotation_str = str(param.annotation)
            if "int" in annotation_str:
                param_type = "integer"
            elif "float" in annotation_str:
                param_type = "number"
            elif "bool" in annotation_str:
                param_type = "boolean"

        properties[param_name] = {
            "type": param_type,
            "description": param_descriptions.get(param_name, f"{param_name} parameter"),
        }

        # Check if parameter is required (no default value)
        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    input_schema = {
        "type": "object",
        "properties": properties,
    }

    if required:
        input_schema["required"] = required

    return {
        "name": name,
        "description": description,
        "inputSchema": input_schema,
    }


def dataframe_to_json_string(df: pd.DataFrame, orient: str = "records") -> str:
    """Convert DataFrame to JSON string with proper formatting.

    Args:
        df: DataFrame to convert
        orient: JSON orientation ('records', 'index', 'columns')

    Returns:
        Formatted JSON string

    Examples:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> json_str = dataframe_to_json_string(df)
        >>> 'a' in json_str
        True
    """
    # Format dates if present
    df = format_dataframe_dates(df)

    # Convert to JSON
    return json.dumps(json.loads(df.to_json(orient=orient)), indent=2)
