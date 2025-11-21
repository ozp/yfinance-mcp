"""Test script to verify the reported errors with get_news and get_stock_price_by_date."""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_yfinance.service import YahooFinanceService


def test_get_news():
    """Test get_news to see if it returns empty structures."""
    print("=" * 80)
    print("TEST 1: get_news - Checking for empty structures")
    print("=" * 80)

    service = YahooFinanceService(default_market="US")

    try:
        result = service.get_news("AAPL")
        data = json.loads(result)

        print(f"\n✓ Function executed successfully")
        print(f"Symbol: {data.get('symbol')}")
        print(f"Number of news articles: {len(data.get('news', []))}")

        if data.get('news'):
            print("\nFirst 3 articles:")
            for i, article in enumerate(data['news'][:3]):
                print(f"\n  Article {i+1}:")
                print(f"    Title: {article.get('title', 'EMPTY')[:80]}")
                print(f"    Publisher: {article.get('publisher', 'EMPTY')}")
                print(f"    Link: {article.get('link', 'EMPTY')[:60]}")

                # Check if fields are empty
                if not article.get('title') or not article.get('link'):
                    print(f"    ⚠️  WARNING: Empty fields detected!")
        else:
            print("\n⚠️  WARNING: No news articles returned!")
            print("This confirms the reported issue - news structure is empty")

        return len(data.get('news', [])) > 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_get_stock_price_by_date():
    """Test get_stock_price_by_date with a valid historical date."""
    print("\n" + "=" * 80)
    print("TEST 2: get_stock_price_by_date - Testing with multiple dates")
    print("=" * 80)

    service = YahooFinanceService(default_market="US")

    # Test multiple dates including weekends
    test_dates = [
        ("2024-12-20", "Regular trading day"),
        ("2025-09-09", "Recent date from user test"),
        ("2025-01-18", "Weekend - Saturday (should fallback to Friday)"),
    ]

    success_count = 0
    for test_date, description in test_dates:
        print(f"\n  Testing {test_date} ({description})...")
        try:
            result = service.get_stock_price_by_date("AAPL", test_date)
            data = json.loads(result)

            print(f"    ✓ Success!")
            print(f"      Requested: {data.get('requested_date')}")
            print(f"      Actual: {data.get('actual_date')}")
            print(f"      Close: ${data.get('close'):.2f}" if data.get('close') else "      Close: None")

            if data.get('requested_date') != data.get('actual_date'):
                print(f"      ℹ️  Fallback used (weekend/holiday)")

            success_count += 1

        except Exception as e:
            error_msg = str(e)
            print(f"    ✗ Failed: {error_msg}")

    print(f"\n  Result: {success_count}/{len(test_dates)} dates succeeded")
    return success_count > 0


def test_workaround_date_range():
    """Test if the workaround using date_range works."""
    print("\n" + "=" * 80)
    print("TEST 3: Workaround - Using get_stock_price_date_range")
    print("=" * 80)

    service = YahooFinanceService(default_market="US")

    test_date = "2024-12-20"

    try:
        result = service.get_stock_price_date_range("AAPL", test_date, test_date)
        data = json.loads(result)

        print(f"\n✓ Workaround executed successfully")
        print(f"Symbol: {data.get('symbol')}")
        print(f"Start date: {data.get('start_date')}")
        print(f"End date: {data.get('end_date')}")
        print(f"Data points: {len(data.get('data', []))}")

        if data.get('data'):
            first_point = data['data'][0]
            print(f"\nData for {first_point.get('date')}:")
            print(f"  Close price: ${first_point.get('close')}")
            print(f"  Volume: {first_point.get('volume'):,}" if first_point.get('volume') else "  Volume: None")

        return len(data.get('data', [])) > 0

    except Exception as e:
        print(f"\n✗ Workaround also failed: {e}")
        return False


def test_current_version():
    """Check yfinance version."""
    print("\n" + "=" * 80)
    print("ENVIRONMENT CHECK")
    print("=" * 80)

    try:
        import yfinance as yf
        print(f"\nyfinance version: {yf.__version__}")

        import requests
        print(f"requests version: {requests.__version__}")

        import pandas as pd
        print(f"pandas version: {pd.__version__}")

    except Exception as e:
        print(f"\nError checking versions: {e}")


if __name__ == "__main__":
    print("REAL-WORLD TEST FOR REPORTED ERRORS")
    print(f"Test date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check environment first
    test_current_version()

    # Run tests
    news_works = test_get_news()
    date_works = test_get_stock_price_by_date()
    workaround_works = test_workaround_date_range()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"\n1. get_news:                {'✓ WORKS' if news_works else '✗ BROKEN'}")
    print(f"2. get_stock_price_by_date: {'✓ WORKS' if date_works else '✗ BROKEN'}")
    print(f"3. Workaround (date_range): {'✓ WORKS' if workaround_works else '✗ BROKEN'}")

    if not news_works or not date_works:
        print("\n⚠️  ISSUES CONFIRMED - Corrections needed!")
        sys.exit(1)
    else:
        print("\n✓ All tests passed - No issues found!")
        sys.exit(0)
