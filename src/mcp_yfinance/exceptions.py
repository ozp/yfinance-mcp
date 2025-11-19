"""Custom exceptions for MCP Yahoo Finance.

This module defines the exception hierarchy used throughout the application
for handling various error conditions.
"""

from typing import Any, Optional


class YFinanceMCPError(Exception):
    """Base exception for all MCP Yahoo Finance errors."""

    def __init__(self, message: str) -> None:
        """Initialize the base exception.

        Args:
            message: Error message describing the issue.
        """
        self.message = message
        super().__init__(self.message)


class TickerNotFoundError(YFinanceMCPError):
    """Raised when a ticker symbol is not found or invalid."""

    def __init__(self, ticker: str) -> None:
        """Initialize the ticker not found exception.

        Args:
            ticker: The ticker symbol that was not found.
        """
        self.ticker = ticker
        super().__init__(f"Ticker '{ticker}' not found or invalid")


class YFinanceAPIError(YFinanceMCPError):
    """Raised when the Yahoo Finance API returns an error."""

    def __init__(self, message: str, ticker: Optional[str] = None) -> None:
        """Initialize the API error exception.

        Args:
            message: Error message from the API.
            ticker: Optional ticker symbol related to the error.
        """
        self.ticker = ticker
        error_msg = f"Yahoo Finance API error: {message}"
        if ticker:
            error_msg += f" (ticker: {ticker})"
        super().__init__(error_msg)


class InvalidParameterError(YFinanceMCPError):
    """Raised when an invalid parameter is provided."""

    def __init__(self, param: str, value: Any, valid_values: Optional[list[Any]] = None) -> None:
        """Initialize the invalid parameter exception.

        Args:
            param: Name of the invalid parameter.
            value: The invalid value provided.
            valid_values: Optional list of valid values for the parameter.
        """
        self.param = param
        self.value = value
        self.valid_values = valid_values

        error_msg = f"Invalid value '{value}' for parameter '{param}'"
        if valid_values:
            error_msg += f". Valid values: {', '.join(map(str, valid_values))}"
        super().__init__(error_msg)


class DataNotAvailableError(YFinanceMCPError):
    """Raised when requested data is not available for a ticker."""

    def __init__(self, data_type: str, ticker: str) -> None:
        """Initialize the data not available exception.

        Args:
            data_type: Type of data that is not available.
            ticker: Ticker symbol for which data is not available.
        """
        self.data_type = data_type
        self.ticker = ticker
        super().__init__(f"{data_type} data not available for ticker '{ticker}'")
