"""Custom exceptions for MCP Yahoo Finance Server.

This module defines a hierarchy of custom exceptions used throughout
the MCP Yahoo Finance server for better error handling and reporting.
"""


class YFinanceMCPError(Exception):
    """Base exception for all MCP Yahoo Finance errors.

    All custom exceptions in this module inherit from this base class.
    """

    pass


class TickerNotFoundError(YFinanceMCPError):
    """Raised when a requested ticker symbol is not found.

    Attributes:
        ticker: The ticker symbol that was not found
    """

    def __init__(self, ticker: str):
        """Initialize the exception.

        Args:
            ticker: The ticker symbol that was not found
        """
        self.ticker = ticker
        super().__init__(f"Ticker '{ticker}' not found or has no data available")


class YFinanceAPIError(YFinanceMCPError):
    """Raised when the yfinance API returns an error.

    Attributes:
        message: Error message
        ticker: The ticker symbol related to the error (optional)
    """

    def __init__(self, message: str, ticker: str | None = None):
        """Initialize the exception.

        Args:
            message: Error message describing what went wrong
            ticker: The ticker symbol related to the error (optional)
        """
        self.ticker = ticker
        ticker_info = f" for ticker '{ticker}'" if ticker else ""
        super().__init__(f"Yahoo Finance API error{ticker_info}: {message}")


class InvalidParameterError(YFinanceMCPError):
    """Raised when an invalid parameter value is provided.

    Attributes:
        param: Parameter name
        value: The invalid value provided
        valid_values: List of valid values (optional)
    """

    def __init__(
        self, param: str, value: str, valid_values: list[str] | None = None
    ):
        """Initialize the exception.

        Args:
            param: Parameter name
            value: The invalid value provided
            valid_values: List of valid values for this parameter (optional)
        """
        self.param = param
        self.value = value
        self.valid_values = valid_values

        if valid_values:
            valid_str = ", ".join(valid_values)
            message = (
                f"Invalid value '{value}' for parameter '{param}'. "
                f"Valid values are: {valid_str}"
            )
        else:
            message = f"Invalid value '{value}' for parameter '{param}'"

        super().__init__(message)


class DataNotAvailableError(YFinanceMCPError):
    """Raised when requested data is not available for a ticker.

    Attributes:
        data_type: Type of data that is not available
        ticker: The ticker symbol
    """

    def __init__(self, data_type: str, ticker: str):
        """Initialize the exception.

        Args:
            data_type: Type of data that is not available
            ticker: The ticker symbol
        """
        self.data_type = data_type
        self.ticker = ticker
        super().__init__(
            f"Data type '{data_type}' is not available for ticker '{ticker}'"
        )
