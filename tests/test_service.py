"""Test script for YahooFinanceService - Session 3 methods.

This script tests the 10 methods implemented in Session 3:
- Pricing & Historical (6 methods)
- Company Info (1 method)
- Financial Statements (3 methods)
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.mcp_yfinance.exceptions import (
    TickerNotFoundError,
)
from src.mcp_yfinance.service import YahooFinanceService


def test_pricing_methods():
    """Test pricing and historical data methods."""
    print("\n" + "=" * 60)
    print("Testing Pricing & Historical Methods")
    print("=" * 60)

    service = YahooFinanceService(default_market="US")

    # Test 1: get_current_stock_price
    print("\n1. Testing get_current_stock_price('AAPL')...")
    try:
        result = service.get_current_stock_price("AAPL")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 2: get_stock_price_by_date
    print("\n2. Testing get_stock_price_by_date('AAPL', '2024-01-15')...")
    try:
        result = service.get_stock_price_by_date("AAPL", "2024-01-15")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 3: get_stock_price_date_range
    print("\n3. Testing get_stock_price_date_range('AAPL', '2024-01-01', '2024-01-05')...")
    try:
        result = service.get_stock_price_date_range("AAPL", "2024-01-01", "2024-01-05")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 4: get_historical_stock_prices
    print("\n4. Testing get_historical_stock_prices('AAPL', period='5d')...")
    try:
        result = service.get_historical_stock_prices("AAPL", period="5d", interval="1d")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 5: get_dividends
    print("\n5. Testing get_dividends('AAPL')...")
    try:
        result = service.get_dividends("AAPL")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 6: get_stock_actions
    print("\n6. Testing get_stock_actions('AAPL')...")
    try:
        result = service.get_stock_actions("AAPL")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")


def test_company_info():
    """Test company information method."""
    print("\n" + "=" * 60)
    print("Testing Company Info Method")
    print("=" * 60)

    service = YahooFinanceService(default_market="US")

    # Test 7: get_stock_info
    print("\n7. Testing get_stock_info('AAPL')...")
    try:
        result = service.get_stock_info("AAPL")
        print("✓ Success! Sample output:")
        print(result[:300] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")


def test_financial_statements():
    """Test financial statement methods."""
    print("\n" + "=" * 60)
    print("Testing Financial Statement Methods")
    print("=" * 60)

    service = YahooFinanceService(default_market="US")

    # Test 8: get_income_statement
    print("\n8. Testing get_income_statement('AAPL', freq='yearly')...")
    try:
        result = service.get_income_statement("AAPL", freq="yearly")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 9: get_balance_sheet
    print("\n9. Testing get_balance_sheet('AAPL', freq='yearly')...")
    try:
        result = service.get_balance_sheet("AAPL", freq="yearly")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test 10: get_cashflow
    print("\n10. Testing get_cashflow('AAPL', freq='yearly')...")
    try:
        result = service.get_cashflow("AAPL", freq="yearly")
        print("✓ Success! Sample output:")
        print(result[:200] + "...")
    except Exception as e:
        print(f"✗ Failed: {e}")


def test_market_normalization():
    """Test configurable market normalization."""
    print("\n" + "=" * 60)
    print("Testing Market Normalization")
    print("=" * 60)

    # Test US market (no suffix)
    print("\nTesting US market (AAPL)...")
    service_us = YahooFinanceService(default_market="US")
    try:
        service_us.get_current_stock_price("AAPL")
        print("✓ US market works!")
    except Exception as e:
        print(f"✗ Failed: {e}")

    # Test BR market (.SA suffix)
    print("\nTesting BR market (PETR4 -> PETR4.SA)...")
    service_br = YahooFinanceService(default_market="BR")
    try:
        service_br.get_current_stock_price("PETR4")
        print("✓ BR market works!")
    except Exception as e:
        print(f"✗ Failed: {e}")


def test_error_handling():
    """Test error handling."""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)

    service = YahooFinanceService(default_market="US")

    # Test invalid ticker
    print("\nTesting invalid ticker (INVALID_TICKER_XYZ)...")
    try:
        service.get_current_stock_price("INVALID_TICKER_XYZ")
        print("✗ Should have raised TickerNotFoundError")
    except TickerNotFoundError as e:
        print(f"✓ Correctly raised TickerNotFoundError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("YahooFinanceService Test Suite - Session 3")
    print("Testing 10 methods implemented in Service Layer Part 1")
    print("=" * 60)

    test_pricing_methods()
    test_company_info()
    test_financial_statements()
    test_market_normalization()
    test_error_handling()

    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)
