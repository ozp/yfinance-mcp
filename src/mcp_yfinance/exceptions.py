"""Custom exceptions for MCP Yahoo Finance server.

This module defines a hierarchy of custom exceptions for handling
various error conditions when interacting with the Yahoo Finance API.
"""


class YFinanceMCPError(Exception):
    """Base exception for all MCP Yahoo Finance errors.

    All custom exceptions in this module inherit from this base class,
    allowing for easy catching of any MCP Yahoo Finance specific errors.
    """

    pass


class TickerNotFoundError(YFinanceMCPError):
    """Raised when a requested ticker symbol is not found.

    Attributes:
        ticker: The ticker symbol that was not found
        message: Error message
    """

    def __init__(self, ticker: str, message: str | None = None):
        """Initialize TickerNotFoundError.

        Args:
            ticker: The ticker symbol that was not found
            message: Optional custom error message
        """
        self.ticker = ticker
        self.message = message or f"Ticker '{ticker}' not found"
        super().__init__(self.message)


class YFinanceAPIError(YFinanceMCPError):
    """Raised when the Yahoo Finance API returns an error.

    Attributes:
        message: Error message
        ticker: Optional ticker symbol related to the error
    """

    def __init__(self, message: str, ticker: str | None = None):
        """Initialize YFinanceAPIError.

        Args:
            message: Error message from the API
            ticker: Optional ticker symbol related to the error
        """
        self.message = message
        self.ticker = ticker
        error_msg = f"Yahoo Finance API error: {message}"
        if ticker:
            error_msg += f" (ticker: {ticker})"
        super().__init__(error_msg)


class InvalidParameterError(YFinanceMCPError):
    """Raised when an invalid parameter value is provided.

    Attributes:
        param: The parameter name
        value: The invalid value provided
        valid_values: List of valid values for the parameter
        message: Error message
    """

    def __init__(
        self, param: str, value: any, valid_values: list[str] | None = None
    ):
        """Initialize InvalidParameterError.

        Args:
            param: The parameter name
            value: The invalid value provided
            valid_values: Optional list of valid values
        """
        self.param = param
        self.value = value
        self.valid_values = valid_values

        error_msg = f"Invalid value '{value}' for parameter '{param}'"
        if valid_values:
            error_msg += f". Valid values: {', '.join(valid_values)}"

        self.message = error_msg
        super().__init__(error_msg)


class DataNotAvailableError(YFinanceMCPError):
    """Raised when requested data is not available for a ticker.

    Attributes:
        data_type: The type of data that was requested
        ticker: The ticker symbol
        message: Error message
    """

    def __init__(self, data_type: str, ticker: str, message: str | None = None):
        """Initialize DataNotAvailableError.

        Args:
            data_type: The type of data that was requested
            ticker: The ticker symbol
            message: Optional custom error message
        """
        self.data_type = data_type
        self.ticker = ticker
        self.message = message or f"{data_type} not available for ticker '{ticker}'"
        super().__init__(self.message)
