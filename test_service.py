"""Quick test script to verify YahooFinanceService implementation."""

import sys
sys.path.insert(0, '/home/user/yfinance-mcp/src')

from mcp_yfinance.service import YahooFinanceService
from mcp_yfinance.exceptions import DataNotAvailableError, TickerNotFoundError

# Initialize service
service = YahooFinanceService(default_market="US")

print("Testing YahooFinanceService implementation...\n")
print("=" * 60)

# Test 1: Get current stock price (Method 1)
print("\n1. Testing get_current_stock_price('AAPL')...")
try:
    result = service.get_current_stock_price("AAPL")
    print("✓ Success! Sample output:")
    print(result[:200] + "..." if len(result) > 200 else result)
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Get news (Method 14)
print("\n2. Testing get_news('AAPL')...")
try:
    result = service.get_news("AAPL")
    print("✓ Success! Sample output:")
    print(result[:300] + "..." if len(result) > 300 else result)
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Get option expiration dates (Method 12)
print("\n3. Testing get_option_expiration_dates('AAPL')...")
try:
    result = service.get_option_expiration_dates("AAPL")
    print("✓ Success! Sample output:")
    print(result[:200] + "..." if len(result) > 200 else result)
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Get stock splits (Method 17)
print("\n4. Testing get_stock_splits('AAPL')...")
try:
    result = service.get_stock_splits("AAPL")
    print("✓ Success! Sample output:")
    print(result[:200] + "..." if len(result) > 200 else result)
except DataNotAvailableError:
    print("✓ Success! No stock splits available (expected for some stocks)")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Get analyst price targets (Method 18)
print("\n5. Testing get_analyst_price_targets('AAPL')...")
try:
    result = service.get_analyst_price_targets("AAPL")
    print("✓ Success! Sample output:")
    print(result[:300] + "..." if len(result) > 300 else result)
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Get holder info (Method 11)
print("\n6. Testing get_holder_info('AAPL', 'major_holders')...")
try:
    result = service.get_holder_info("AAPL", "major_holders")
    print("✓ Success! Sample output:")
    print(result[:300] + "..." if len(result) > 300 else result)
except Exception as e:
    print(f"✗ Error: {e}")

# Test 7: Error handling - invalid ticker
print("\n7. Testing error handling with invalid ticker...")
try:
    result = service.get_current_stock_price("INVALID_TICKER_XYZ123")
    print("✗ Should have raised an error!")
except TickerNotFoundError as e:
    print(f"✓ Success! Properly caught TickerNotFoundError: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")

print("\n" + "=" * 60)
print("Testing completed!")
