#!/usr/bin/env python3
"""Test script for Session 2: Cache & Utilities"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_yfinance.cache import CacheManager, CACHE_TTL
from mcp_yfinance.utils import (
    normalize_ticker,
    MARKET_SUFFIXES,
    generate_cache_key,
    format_dataframe_dates,
    parse_docstring,
    generate_tool_schema,
)


def test_cache_operations():
    """Test cache manager operations."""
    print("=" * 60)
    print("Testing Cache Operations")
    print("=" * 60)

    # Initialize cache
    cache = CacheManager()
    print(f"✓ Cache initialized at: {cache.db_path}")

    # Test set and get
    test_data = {"symbol": "AAPL", "price": 234.56}
    cache.set("test_key", test_data, ttl=60)
    print(f"✓ Set cache: test_key = {test_data}")

    retrieved = cache.get("test_key")
    assert retrieved == test_data, "Retrieved data doesn't match"
    print(f"✓ Get cache: {retrieved}")

    # Test expiration
    cache.set("expire_key", {"data": "will expire"}, ttl=1)
    print("✓ Set expiring cache with TTL=1 second")
    time.sleep(2)
    expired_result = cache.get("expire_key")
    assert expired_result is None, "Expired entry should return None"
    print("✓ Expired entry correctly returns None")

    # Test stats
    stats = cache.get_stats()
    print(f"✓ Cache stats: {stats}")

    # Test clear
    count = cache.clear_all()
    print(f"✓ Cleared {count} entries")

    # Test cache TTL configuration
    print(f"\n✓ Cache TTL configurations loaded: {len(CACHE_TTL)} entries")
    print(f"  - current_price: {CACHE_TTL['current_price']}s")
    print(f"  - stock_info: {CACHE_TTL['stock_info']}s")
    print(f"  - option_chain: {CACHE_TTL['option_chain']}s")

    cache.close()
    print("\n✓ All cache tests passed!\n")


def test_ticker_normalization():
    """Test ticker normalization for multiple markets."""
    print("=" * 60)
    print("Testing Ticker Normalization (Multi-Market)")
    print("=" * 60)

    test_cases = [
        ("AAPL", "US", "AAPL"),
        ("PETR4", "BR", "PETR4.SA"),
        ("RELIANCE", "IN_NSE", "RELIANCE.NS"),
        ("INFY", "IN_BSE", "INFY.BO"),
        ("7203", "JP", "7203.T"),
        ("VOD", "UK", "VOD.L"),
        ("BMW", "DE", "BMW.DE"),
        ("BNP", "FR", "BNP.PA"),
        ("0700", "HK", "0700.HK"),
        ("BHP", "AU", "BHP.AX"),
        ("TD", "CA", "TD.TO"),
    ]

    for ticker, market, expected in test_cases:
        result = normalize_ticker(ticker, market)
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"✓ {market:8s} - {ticker:10s} -> {result}")

    # Test ticker with existing suffix
    result = normalize_ticker("AAPL.US", "US")
    assert result == "AAPL.US", "Ticker with suffix should remain unchanged"
    print(f"✓ Existing suffix preserved: AAPL.US -> {result}")

    # Test unsupported market
    try:
        normalize_ticker("TEST", "XX")
        assert False, "Should raise ValueError for unsupported market"
    except ValueError as e:
        print(f"✓ Unsupported market raises ValueError: {str(e)[:50]}...")

    print(f"\n✓ Supported markets: {', '.join(MARKET_SUFFIXES.keys())}")
    print("\n✓ All ticker normalization tests passed!\n")


def test_cache_key_generation():
    """Test cache key generation."""
    print("=" * 60)
    print("Testing Cache Key Generation")
    print("=" * 60)

    # Test consistent key generation
    key1 = generate_cache_key("get_stock_info", symbol="AAPL")
    key2 = generate_cache_key("get_stock_info", symbol="AAPL")
    assert key1 == key2, "Same parameters should generate same key"
    print(f"✓ Consistent keys: {key1}")

    # Test different parameters
    key3 = generate_cache_key("get_stock_info", symbol="GOOGL")
    assert key1 != key3, "Different parameters should generate different keys"
    print(f"✓ Different keys: {key3}")

    # Test with multiple parameters
    key4 = generate_cache_key(
        "get_historical_data",
        symbol="AAPL",
        period="1mo",
        interval="1d"
    )
    print(f"✓ Multi-param key: {key4}")

    print("\n✓ All cache key generation tests passed!\n")


def test_docstring_parsing():
    """Test docstring parsing."""
    print("=" * 60)
    print("Testing Docstring Parsing")
    print("=" * 60)

    test_docstring = """Get stock price information.

    Args:
        symbol: The stock ticker symbol.
        date: The date to query (optional).
        format: Output format type.

    Returns:
        Stock price data.
    """

    params = parse_docstring(test_docstring)
    assert "symbol" in params, "Should extract 'symbol' parameter"
    assert "date" in params, "Should extract 'date' parameter"
    assert "format" in params, "Should extract 'format' parameter"

    print(f"✓ Extracted parameters:")
    for name, desc in params.items():
        print(f"  - {name}: {desc}")

    print("\n✓ All docstring parsing tests passed!\n")


def test_tool_schema_generation():
    """Test MCP tool schema generation."""
    print("=" * 60)
    print("Testing Tool Schema Generation")
    print("=" * 60)

    def sample_tool(symbol: str, period: str = "1mo") -> str:
        """Get historical stock data.

        Args:
            symbol: Stock ticker symbol.
            period: Time period for data.

        Returns:
            Historical price data.
        """
        return "data"

    schema = generate_tool_schema(sample_tool)

    assert schema["name"] == "sample_tool", "Should extract function name"
    assert "symbol" in schema["inputSchema"]["properties"], "Should have 'symbol' parameter"
    assert "period" in schema["inputSchema"]["properties"], "Should have 'period' parameter"
    assert "symbol" in schema["inputSchema"]["required"], "'symbol' should be required"
    assert "period" not in schema["inputSchema"]["required"], "'period' should be optional"

    print(f"✓ Generated schema for '{schema['name']}':")
    print(f"  - Description: {schema['description']}")
    print(f"  - Parameters: {', '.join(schema['inputSchema']['properties'].keys())}")
    print(f"  - Required: {schema['inputSchema']['required']}")

    print("\n✓ All tool schema generation tests passed!\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SESSION 2: Cache & Utilities - Test Suite")
    print("=" * 60 + "\n")

    try:
        test_cache_operations()
        test_ticker_normalization()
        test_cache_key_generation()
        test_docstring_parsing()
        test_tool_schema_generation()

        print("=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nSession 2 implementation complete:")
        print("  ✓ cache.py - SQLite cache with TTL and thread-safety")
        print("  ✓ utils.py - Multi-market ticker normalization")
        print(f"  ✓ Supports {len(MARKET_SUFFIXES)} markets: {', '.join(list(MARKET_SUFFIXES.keys())[:5])}...")
        print("\nReady for integration!\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
