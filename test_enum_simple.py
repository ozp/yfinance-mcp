"""Simple test to validate enum/literal schema generation without full dependencies."""

import sys
import typing
from enum import Enum
from pathlib import Path
from typing import Literal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_yfinance.utils import generate_tool_schema


# Define test types similar to models.py
PeriodType = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
IntervalType = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
FrequencyType = Literal["yearly", "quarterly"]


class Period(str, Enum):
    """Test enum."""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    ONE_YEAR = "1y"


# Define test functions with Literal and Enum parameters
def test_function_with_literal(
    symbol: str,
    period: PeriodType = "1mo",
    interval: IntervalType = "1d"
) -> str:
    """Test function with Literal types.

    Args:
        symbol: Stock ticker symbol.
        period: Time period for historical data.
        interval: Data interval.

    Returns:
        Test result.
    """
    return "test"


def test_function_with_enum(
    symbol: str,
    period: Period = Period.ONE_MONTH,
    freq: FrequencyType = "yearly"
) -> str:
    """Test function with Enum type.

    Args:
        symbol: Stock ticker symbol.
        period: Time period as enum.
        freq: Frequency type.

    Returns:
        Test result.
    """
    return "test"


def test_function_without_enum(symbol: str, limit: int = 10) -> str:
    """Test function without enum types.

    Args:
        symbol: Stock ticker symbol.
        limit: Maximum number of results.

    Returns:
        Test result.
    """
    return "test"


def main():
    """Run the test."""
    print("=" * 70)
    print("TESTING ENUM/LITERAL SCHEMA GENERATION")
    print("=" * 70)

    tests = [
        ("test_function_with_literal", test_function_with_literal, ["period", "interval"]),
        ("test_function_with_enum", test_function_with_enum, ["period", "freq"]),
        ("test_function_without_enum", test_function_without_enum, ["limit"]),
    ]

    total_tests = 0
    passed_tests = 0

    for func_name, func, param_names in tests:
        print(f"\n{'=' * 70}")
        print(f"Function: {func_name}")
        print(f"{'=' * 70}")

        schema = generate_tool_schema(func)

        for param_name in param_names:
            total_tests += 1
            param_schema = schema["inputSchema"]["properties"].get(param_name, {})

            print(f"\nParameter: {param_name}")
            print(f"  Type: {param_schema.get('type')}")

            # Check if this parameter SHOULD have enum values
            func_sig = typing.get_type_hints(func)
            param_type = func_sig.get(param_name)

            # Determine if enum should be present
            should_have_enum = False
            if param_type:
                if typing.get_origin(param_type) is typing.Literal:
                    should_have_enum = True
                elif isinstance(param_type, type) and issubclass(param_type, Enum):
                    should_have_enum = True

            if "enum" in param_schema:
                print(f"  ✓ Enum values: {param_schema['enum']}")
                if should_have_enum:
                    passed_tests += 1
            else:
                if should_have_enum:
                    print(f"  ✗ Enum values MISSING (expected for {param_type})")
                else:
                    print(f"  ⓘ No enum (expected for type: {param_schema.get('type')})")
                    passed_tests += 1  # This is correct - no enum needed

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total parameters tested: {total_tests}")
    print(f"Correct schema generation: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("\n✓ SUCCESS! All schemas are correctly generated!")
        print("  - Literal types have enum values ✓")
        print("  - Enum types have enum values ✓")
        print("  - Regular types don't have enum values ✓")
        return True
    else:
        print("\n✗ FAILURE! Some schemas are incorrect.")
        return False


if __name__ == "__main__":
    import json

    print("\nThis test validates the fix for Audit Issue #1:")
    print("  - Literal and Enum types should include 'enum' field in schema")
    print("  - Regular types should NOT have enum field\n")

    success = main()

    # Show a full schema example
    print(f"\n{'=' * 70}")
    print("EXAMPLE SCHEMA: test_function_with_literal")
    print(f"{'=' * 70}\n")
    schema = generate_tool_schema(test_function_with_literal)
    print(json.dumps(schema, indent=2))

    if success:
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED - Audit Issue #1 is FIXED!")
        print("=" * 70)
        print("\nThe Claude/LLM will now receive schemas with enum values,")
        print("allowing it to know which parameter values are valid!")
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("✗ TESTS FAILED")
        print("=" * 70)
        sys.exit(1)
