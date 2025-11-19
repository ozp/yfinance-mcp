"""Test script to validate enum/literal schema generation.

This script validates that the generate_tool_schema function correctly
detects Literal and Enum types and adds the 'enum' field to the schema.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_yfinance.service import YahooFinanceService
from mcp_yfinance.utils import generate_tool_schema


def test_enum_schema_generation():
    """Test that schemas correctly include enum values for Literal and Enum types."""
    print("=" * 70)
    print("TESTING ENUM/LITERAL SCHEMA GENERATION")
    print("=" * 70)

    service = YahooFinanceService()

    # Test methods that use Literal types
    test_methods = [
        ("get_historical_stock_prices", ["period", "interval"]),
        ("get_income_statement", ["freq"]),
        ("get_balance_sheet", ["freq"]),
        ("get_cashflow", ["freq"]),
        ("get_holder_info", ["holder_type"]),
        ("get_option_chain", ["option_type"]),
        ("get_recommendations", ["recommendation_type"]),
    ]

    print("\nTesting schema generation for methods with Literal/Enum parameters:\n")

    total_tests = 0
    passed_tests = 0

    for method_name, param_names in test_methods:
        method = getattr(service, method_name)
        schema = generate_tool_schema(method)

        print(f"\n{'=' * 70}")
        print(f"Method: {method_name}")
        print(f"{'=' * 70}")

        for param_name in param_names:
            total_tests += 1
            param_schema = schema["inputSchema"]["properties"].get(param_name, {})

            print(f"\nParameter: {param_name}")
            print(f"  Type: {param_schema.get('type')}")

            if "enum" in param_schema:
                print(f"  ✓ Enum values found: {param_schema['enum']}")
                passed_tests += 1
            else:
                print(f"  ✗ Enum values MISSING (this is a problem!)")

            if "description" in param_schema:
                print(f"  Description: {param_schema['description'][:80]}...")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total parameters tested: {total_tests}")
    print(f"Parameters with enum values: {passed_tests}")
    print(f"Parameters missing enum values: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("\n✓ SUCCESS! All Literal/Enum parameters have enum values in their schemas!")
        print("  The Claude/LLM will now know which values are valid for each parameter.")
        return True
    else:
        print("\n✗ FAILURE! Some parameters are missing enum values.")
        print("  This means the LLM won't know which values are valid.")
        return False


def test_specific_schema_example():
    """Show a specific example of a generated schema."""
    print(f"\n{'=' * 70}")
    print("EXAMPLE: get_historical_stock_prices schema")
    print(f"{'=' * 70}\n")

    service = YahooFinanceService()
    method = getattr(service, "get_historical_stock_prices")
    schema = generate_tool_schema(method)

    import json
    print(json.dumps(schema, indent=2))


if __name__ == "__main__":
    print("\nThis test validates that the fix for Audit Issue #1 is working correctly.")
    print("Issue: Literal and Enum types should include 'enum' field in JSON schema")
    print("       so that the LLM knows which values are valid.\n")

    # Run the test
    success = test_enum_schema_generation()

    # Show a specific example
    test_specific_schema_example()

    # Exit with appropriate code
    if success:
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED - Audit Issue #1 is FIXED!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("✗ TESTS FAILED - Audit Issue #1 is NOT fixed")
        print("=" * 70)
        sys.exit(1)
