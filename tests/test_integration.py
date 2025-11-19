"""Integration tests for MCP Yahoo Finance project.

This module tests the integration of all components:
- Models and exceptions
- Cache and utilities
- Service layer with all 18 methods
- Server initialization
- Multi-market support
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")

    try:
        # Import modules directly, not through __init__ to avoid server dependencies
        from mcp_yfinance import models, exceptions, cache, utils, service
        print("✓ All core modules imported")

        # Test specific imports
        from mcp_yfinance.models import PeriodType, IntervalType, FrequencyType
        from mcp_yfinance.exceptions import (
            YFinanceMCPError,
            TickerNotFoundError,
            YFinanceAPIError,
            InvalidParameterError,
            DataNotAvailableError,
        )
        from mcp_yfinance.cache import CacheManager, CACHE_TTL
        from mcp_yfinance.utils import normalize_ticker, MARKET_SUFFIXES
        from mcp_yfinance.service import YahooFinanceService

        print("✓ All specific imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        print("  Note: This is expected if dependencies (mcp, yfinance) are not installed")
        return False


def test_market_suffixes():
    """Test that MARKET_SUFFIXES supports multiple countries."""
    print("\nTesting MARKET_SUFFIXES...")

    from mcp_yfinance.utils import MARKET_SUFFIXES

    required_markets = ["US", "BR", "UK", "DE", "FR", "JP", "IN_NSE", "HK", "AU", "CA"]

    for market in required_markets:
        if market in MARKET_SUFFIXES:
            print(f"✓ Market {market}: {MARKET_SUFFIXES[market]}")
        else:
            print(f"✗ Market {market} missing!")
            return False

    print(f"✓ Total markets supported: {len(MARKET_SUFFIXES)}")
    return True


def test_ticker_normalization():
    """Test ticker normalization for multiple markets."""
    print("\nTesting ticker normalization...")

    from mcp_yfinance.utils import normalize_ticker

    test_cases = [
        ("AAPL", "US", "AAPL"),           # US - no suffix
        ("PETR4", "BR", "PETR4.SA"),      # Brazil
        ("VODAFONE", "UK", "VODAFONE.L"),  # UK
        ("7203", "JP", "7203.T"),         # Japan
        ("RELIANCE", "IN_NSE", "RELIANCE.NS"),  # India NSE
    ]

    for ticker, market, expected in test_cases:
        result = normalize_ticker(ticker, market)
        if result == expected:
            print(f"✓ {ticker} ({market}) → {result}")
        else:
            print(f"✗ {ticker} ({market}) → {result} (expected {expected})")
            return False

    return True


def test_cache_operations():
    """Test cache set/get/expire operations."""
    print("\nTesting cache operations...")

    from mcp_yfinance.cache import CacheManager
    import tempfile
    import time

    # Create temporary cache
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        cache_path = f.name

    try:
        cache = CacheManager(db_path=cache_path)

        # Test set and get
        cache.set("test_key", "test_value", ttl=10)
        value = cache.get("test_key")
        if value == "test_value":
            print("✓ Cache set/get works")
        else:
            print(f"✗ Cache get failed: {value}")
            return False

        # Test expiration
        cache.set("expire_key", "expire_value", ttl=1)
        time.sleep(2)
        expired_value = cache.get("expire_key")
        if expired_value is None:
            print("✓ Cache expiration works")
        else:
            print(f"✗ Cache should be expired: {expired_value}")
            return False

        # Test cache key generation
        from mcp_yfinance.utils import generate_cache_key
        key1 = generate_cache_key("get_stock_info", symbol="AAPL")
        key2 = generate_cache_key("get_stock_info", symbol="MSFT")
        if key1 != key2:
            print("✓ Cache key generation creates unique keys")
        else:
            print("✗ Cache keys should be different")
            return False

        cache.close()
        return True
    finally:
        # Cleanup
        Path(cache_path).unlink(missing_ok=True)


def test_cache_ttl_configurations():
    """Test that cache TTL is configured for all tool types."""
    print("\nTesting cache TTL configurations...")

    from mcp_yfinance.cache import CACHE_TTL

    required_tool_types = [
        "current_price",
        "historical_data",
        "stock_info",
        "dividends",
        "stock_actions",
        "income_statement",
        "balance_sheet",
        "cashflow",
        "holder_info",
        "option_expiration_dates",
        "option_chain",
        "news",
        "recommendations",
        "earning_dates",
        "stock_splits",
        "analyst_price_targets",
        "default",
    ]

    missing = []
    for tool_type in required_tool_types:
        if tool_type in CACHE_TTL:
            print(f"✓ {tool_type}: {CACHE_TTL[tool_type]}s")
        else:
            missing.append(tool_type)
            print(f"✗ {tool_type}: missing")

    if missing:
        print(f"✗ Missing TTL configs: {missing}")
        return False

    return True


def test_service_methods():
    """Test that YahooFinanceService has all 18 methods."""
    print("\nTesting service methods...")

    from mcp_yfinance.service import YahooFinanceService

    service = YahooFinanceService(default_market="US")

    required_methods = [
        "get_current_stock_price",
        "get_stock_price_by_date",
        "get_stock_price_date_range",
        "get_historical_stock_prices",
        "get_dividends",
        "get_stock_actions",
        "get_stock_info",
        "get_income_statement",
        "get_balance_sheet",
        "get_cashflow",
        "get_holder_info",
        "get_option_expiration_dates",
        "get_option_chain",
        "get_news",
        "get_recommendations",
        "get_earning_dates",
        "get_stock_splits",
        "get_analyst_price_targets",
    ]

    missing = []
    for method_name in required_methods:
        if hasattr(service, method_name) and callable(getattr(service, method_name)):
            print(f"✓ {method_name}")
        else:
            missing.append(method_name)
            print(f"✗ {method_name} missing")

    if missing:
        print(f"✗ Missing methods: {missing}")
        return False

    print(f"✓ All 18 methods implemented")
    return True


def test_exceptions_hierarchy():
    """Test exception hierarchy and attributes."""
    print("\nTesting exception hierarchy...")

    from mcp_yfinance.exceptions import (
        YFinanceMCPError,
        TickerNotFoundError,
        YFinanceAPIError,
        InvalidParameterError,
        DataNotAvailableError,
    )

    # Test base exception
    base_error = YFinanceMCPError("Test error")
    if isinstance(base_error, Exception):
        print("✓ YFinanceMCPError is an Exception")
    else:
        print("✗ YFinanceMCPError should be an Exception")
        return False

    # Test TickerNotFoundError
    ticker_error = TickerNotFoundError("INVALID")
    if isinstance(ticker_error, YFinanceMCPError) and hasattr(ticker_error, "ticker"):
        print("✓ TickerNotFoundError has correct inheritance and attributes")
    else:
        print("✗ TickerNotFoundError missing attributes")
        return False

    # Test YFinanceAPIError
    api_error = YFinanceAPIError("API failed", ticker="AAPL")
    if isinstance(api_error, YFinanceMCPError) and hasattr(api_error, "ticker"):
        print("✓ YFinanceAPIError has correct inheritance and attributes")
    else:
        print("✗ YFinanceAPIError missing attributes")
        return False

    # Test InvalidParameterError
    param_error = InvalidParameterError("period", "invalid", ["1d", "1mo"])
    if isinstance(param_error, YFinanceMCPError) and hasattr(param_error, "param"):
        print("✓ InvalidParameterError has correct inheritance and attributes")
    else:
        print("✗ InvalidParameterError missing attributes")
        return False

    # Test DataNotAvailableError
    data_error = DataNotAvailableError("dividends", "AAPL")
    if isinstance(data_error, YFinanceMCPError) and hasattr(data_error, "data_type"):
        print("✓ DataNotAvailableError has correct inheritance and attributes")
    else:
        print("✗ DataNotAvailableError missing attributes")
        return False

    return True


def test_type_models():
    """Test Pydantic models and type literals."""
    print("\nTesting type models...")

    from mcp_yfinance.models import PeriodType, IntervalType, FrequencyType

    # These are TypedDict or Literal types, just verify they exist
    print(f"✓ PeriodType: {PeriodType}")
    print(f"✓ IntervalType: {IntervalType}")
    print(f"✓ FrequencyType: {FrequencyType}")

    return True


def test_file_structure():
    """Verify all required files exist."""
    print("\nTesting file structure...")

    project_root = Path(__file__).parent.parent

    required_files = [
        "src/mcp_yfinance/__init__.py",
        "src/mcp_yfinance/__main__.py",
        "src/mcp_yfinance/models.py",
        "src/mcp_yfinance/exceptions.py",
        "src/mcp_yfinance/cache.py",
        "src/mcp_yfinance/utils.py",
        "src/mcp_yfinance/service.py",
        "src/mcp_yfinance/server.py",
        "src/mcp_yfinance/config.py",
        "src/mcp_yfinance/py.typed",
        "pyproject.toml",
        "README.md",
        ".gitignore",
    ]

    missing = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            missing.append(file_path)
            print(f"✗ {file_path} missing")

    if missing:
        print(f"✗ Missing files: {missing}")
        return False

    return True


def test_pyproject_toml():
    """Verify pyproject.toml has all dependencies."""
    print("\nTesting pyproject.toml...")

    import tomli

    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)
    except ImportError:
        # tomli not available, use basic parsing
        import re
        with open(pyproject_path, "r") as f:
            content = f.read()

        required_deps = ["mcp", "yfinance", "pydantic", "pandas", "requests"]
        for dep in required_deps:
            if dep in content:
                print(f"✓ Dependency: {dep}")
            else:
                print(f"✗ Missing dependency: {dep}")
                return False

        return True

    # Full tomli parsing
    deps = data.get("project", {}).get("dependencies", [])
    print(f"✓ Found {len(deps)} dependencies")

    required_deps = ["mcp", "yfinance", "pydantic", "pandas", "requests"]
    for req_dep in required_deps:
        found = any(req_dep in dep for dep in deps)
        if found:
            print(f"✓ {req_dep}")
        else:
            print(f"✗ Missing: {req_dep}")
            return False

    return True


def test_version_export():
    """Test that __version__ is exported from __init__.py."""
    print("\nTesting version export...")

    try:
        from mcp_yfinance import __version__
        print(f"✓ Version: {__version__}")
        return True
    except ImportError as e:
        print(f"✗ Version import failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("MCP YAHOO FINANCE - INTEGRATION TESTS")
    print("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Market Suffixes", test_market_suffixes),
        ("Ticker Normalization", test_ticker_normalization),
        ("Cache Operations", test_cache_operations),
        ("Cache TTL Configurations", test_cache_ttl_configurations),
        ("Service Methods (18 tools)", test_service_methods),
        ("Exception Hierarchy", test_exceptions_hierarchy),
        ("Type Models", test_type_models),
        ("pyproject.toml", test_pyproject_toml),
        ("Version Export", test_version_export),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"✗ Test {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
