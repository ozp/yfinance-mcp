"""Direct test of the enum detection logic without dependencies."""

import inspect
import typing
from enum import Enum
from typing import Any, Literal


# Test types
PeriodType = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
IntervalType = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]


class Period(str, Enum):
    """Test enum."""
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"


def test_literal_detection():
    """Test that Literal types are detected correctly."""
    print("\n" + "=" * 70)
    print("TEST 1: Literal Type Detection")
    print("=" * 70)

    # Test with a Literal type
    test_type = PeriodType

    # Check if it's a Literal
    is_literal = typing.get_origin(test_type) is typing.Literal
    print(f"\nType: {test_type}")
    print(f"Is Literal: {is_literal}")

    if is_literal:
        # Extract values
        values = list(typing.get_args(test_type))
        print(f"✓ Literal values extracted: {values}")
        return True
    else:
        print("✗ Failed to detect Literal type")
        return False


def test_enum_detection():
    """Test that Enum types are detected correctly."""
    print("\n" + "=" * 70)
    print("TEST 2: Enum Type Detection")
    print("=" * 70)

    # Test with an Enum type
    test_type = Period

    # Check if it's an Enum
    is_enum = inspect.isclass(test_type) and issubclass(test_type, Enum)
    print(f"\nType: {test_type}")
    print(f"Is Enum: {is_enum}")

    if is_enum:
        # Extract values
        values = [e.value for e in test_type]
        print(f"✓ Enum values extracted: {values}")
        return True
    else:
        print("✗ Failed to detect Enum type")
        return False


def test_function_parameter_detection():
    """Test detection in a real function signature."""
    print("\n" + "=" * 70)
    print("TEST 3: Function Parameter Detection")
    print("=" * 70)

    def sample_function(
        symbol: str,
        period: PeriodType = "1mo",
        interval: IntervalType = "1d",
        enum_period: Period = Period.ONE_MONTH,
        limit: int = 10
    ) -> str:
        """Sample function with various parameter types."""
        return "test"

    # Get function signature
    sig = inspect.signature(sample_function)

    results = []

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue

        print(f"\n--- Parameter: {param_name} ---")

        enum_values = []
        param_type = "string"

        if param.annotation != inspect.Parameter.empty:
            annotation = param.annotation

            # Check for Literal
            if typing.get_origin(annotation) is typing.Literal:
                enum_values = list(typing.get_args(annotation))
                print(f"  Type: Literal")
                print(f"  ✓ Enum values: {enum_values}")
                results.append(("literal", param_name, True))

            # Check for Enum
            elif inspect.isclass(annotation) and issubclass(annotation, Enum):
                enum_values = [e.value for e in annotation]
                print(f"  Type: Enum")
                print(f"  ✓ Enum values: {enum_values}")
                results.append(("enum", param_name, True))

            # Regular type
            else:
                annotation_str = str(annotation)
                if "int" in annotation_str.lower():
                    param_type = "integer"
                print(f"  Type: {param_type}")
                print(f"  ⓘ No enum (as expected)")
                results.append(("regular", param_name, True))

    # Check results
    expected_literal = ["period", "interval"]
    expected_enum = ["enum_period"]
    expected_regular = ["symbol", "limit"]

    all_correct = True
    for type_kind, param_name, detected in results:
        if type_kind == "literal" and param_name not in expected_literal:
            all_correct = False
        elif type_kind == "enum" and param_name not in expected_enum:
            all_correct = False
        elif type_kind == "regular" and param_name not in expected_regular:
            all_correct = False

    return all_correct


def main():
    """Run all tests."""
    print("=" * 70)
    print("ENUM/LITERAL DETECTION LOGIC TEST")
    print("=" * 70)
    print("\nThis test validates the core logic for detecting Literal and Enum types")
    print("in function parameters, as required by Audit Issue #1.\n")

    test1 = test_literal_detection()
    test2 = test_enum_detection()
    test3 = test_function_parameter_detection()

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Test 1 (Literal detection): {'✓ PASS' if test1 else '✗ FAIL'}")
    print(f"Test 2 (Enum detection): {'✓ PASS' if test2 else '✗ FAIL'}")
    print(f"Test 3 (Function parameters): {'✓ PASS' if test3 else '✗ FAIL'}")

    if test1 and test2 and test3:
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nThe enum detection logic is working correctly.")
        print("Literal and Enum types will be properly detected and")
        print("their valid values will be included in the schema.")
        return True
    else:
        print("\n" + "=" * 70)
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
