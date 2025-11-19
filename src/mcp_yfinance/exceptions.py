"""Custom exceptions for MCP Yahoo Finance.

This module defines the exception hierarchy for error handling
throughout the MCP Yahoo Finance server.
"""

from typing import Any


class YFinanceMCPError(Exception):
    """Base exception for all MCP Yahoo Finance errors.

    This is the parent class for all custom exceptions in the
    MCP Yahoo Finance server.

    Attributes:
        message: Error message describing what went wrong
    """

    def __init__(self, message: str) -> None:
        """Initialize the base exception.

        Args:
            message: Error message
        """
        self.message = message
        super().__init__(self.message)


class TickerNotFoundError(YFinanceMCPError):
    """Exception raised when a ticker symbol is not found.

    This error indicates that the requested ticker symbol does not exist
    or is not available in Yahoo Finance.

    Attributes:
        ticker: The ticker symbol that was not found
        message: Error message
    """

    def __init__(self, ticker: str) -> None:
        """Initialize the ticker not found exception.

        Args:
            ticker: The ticker symbol that was not found
        """
        self.ticker = ticker
        message = f"Ticker '{ticker}' not found or unavailable"
        super().__init__(message)


class YFinanceAPIError(YFinanceMCPError):
    """Exception raised when Yahoo Finance API returns an error.

    This error indicates that the Yahoo Finance API request failed,
    either due to network issues, API limitations, or invalid requests.

    Attributes:
        ticker: Optional ticker symbol related to the error
        message: Error message
    """

    def __init__(self, message: str, ticker: str | None = None) -> None:
        """Initialize the API error exception.

        Args:
            message: Error message describing the API failure
            ticker: Optional ticker symbol related to the error
        """
        self.ticker = ticker
        if ticker:
            full_message = f"Yahoo Finance API error for '{ticker}': {message}"
        else:
            full_message = f"Yahoo Finance API error: {message}"
        super().__init__(full_message)


class InvalidParameterError(YFinanceMCPError):
    """Exception raised when an invalid parameter is provided.

    This error indicates that a function parameter has an invalid value
    that is not within the accepted range or set of values.

    Attributes:
        param: Parameter name
        value: The invalid value that was provided
        valid_values: List of valid values for this parameter
        message: Error message
    """

    def __init__(
        self,
        param: str,
        value: Any,
        valid_values: list[Any] | None = None,
    ) -> None:
        """Initialize the invalid parameter exception.

        Args:
            param: Name of the invalid parameter
            value: The invalid value that was provided
            valid_values: Optional list of valid values
        """
        self.param = param
        self.value = value
        self.valid_values = valid_values

        if valid_values:
            valid_str = ", ".join(str(v) for v in valid_values)
            message = (
                f"Invalid value '{value}' for parameter '{param}'. "
                f"Valid values are: {valid_str}"
            )
        else:
            message = f"Invalid value '{value}' for parameter '{param}'"

        super().__init__(message)


class DataNotAvailableError(YFinanceMCPError):
    """Exception raised when requested data is not available.

    This error indicates that the requested data type exists but is not
    available for the specified ticker symbol.

    Attributes:
        data_type: Type of data that was requested
        ticker: Ticker symbol for which data is unavailable
        message: Error message
    """

    def __init__(self, data_type: str, ticker: str) -> None:
        """Initialize the data not available exception.

        Args:
            data_type: Type of data that was requested (e.g., 'dividends', 'options')
            ticker: Ticker symbol for which data is unavailable
        """
        self.data_type = data_type
        self.ticker = ticker
        message = f"Data type '{data_type}' not available for ticker '{ticker}'"
        super().__init__(message)
