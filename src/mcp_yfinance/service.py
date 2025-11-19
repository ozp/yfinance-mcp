"""Yahoo Finance service layer for MCP server.

This module provides the YahooFinanceService class which implements
all business logic for fetching stock market data from Yahoo Finance.
"""

import json
from datetime import datetime
from typing import Any
import yfinance as yf
import pandas as pd
from requests import Session

from .models import PeriodType, IntervalType, FrequencyType
from .exceptions import (
    TickerNotFoundError,
    YFinanceAPIError,
    DataNotAvailableError,
    InvalidParameterError,
)
from .utils import normalize_ticker, format_dataframe_dates, dataframe_to_json_string


class YahooFinanceService:
    """Service class for interacting with Yahoo Finance API.

    This class provides methods for fetching various types of financial data
    including stock prices, company information, financial statements, and more.
    All methods return JSON-formatted strings for easy consumption by MCP clients.

    Attributes:
        session: Optional requests Session for API calls
        verify: Whether to verify SSL certificates
        default_market: Default market code for ticker normalization (e.g., 'US', 'BR', 'UK')
    """

    def __init__(
        self,
        session: Session | None = None,
        verify: bool = True,
        default_market: str = "US",
    ):
        """Initialize YahooFinanceService.

        Args:
            session: Optional requests Session for connection pooling
            verify: Whether to verify SSL certificates (default: True)
            default_market: Default market for ticker normalization (default: 'US')
        """
        self.session = session
        self.verify = verify
        self.default_market = default_market

    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """Get a yfinance Ticker object with validation.

        Args:
            symbol: Stock ticker symbol (will be normalized)

        Returns:
            yfinance Ticker object

        Raises:
            TickerNotFoundError: If ticker is invalid or not found
        """
        # Normalize ticker for the default market
        normalized_symbol = normalize_ticker(symbol, self.default_market)

        try:
            ticker = yf.Ticker(normalized_symbol, session=self.session)

            # Validate ticker exists by checking if info is available
            if not ticker.info or len(ticker.info) <= 1:
                raise TickerNotFoundError(normalized_symbol)

            return ticker
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), normalized_symbol)

    # ==================== PRICING & HISTORICAL DATA ====================

    def get_current_stock_price(self, symbol: str) -> str:
        """Get the current stock price for a given ticker symbol.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'PETR4' for BR market)

        Returns:
            JSON string containing current price information including:
            - symbol: Ticker symbol
            - price: Current price
            - currency: Price currency
            - market_time: Last market timestamp
            - volume: Current volume
            - market_cap: Market capitalization

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If price data is not available

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_current_stock_price("AAPL")
            >>> print(result)
            {
              "symbol": "AAPL",
              "price": 234.56,
              "currency": "USD",
              ...
            }
        """
        ticker = self._get_ticker(symbol)

        try:
            info = ticker.info

            if "currentPrice" not in info and "regularMarketPrice" not in info:
                raise DataNotAvailableError("Current price", symbol)

            # Get price from available fields
            price = info.get("currentPrice") or info.get("regularMarketPrice")

            result = {
                "symbol": symbol,
                "price": price,
                "currency": info.get("currency", "USD"),
                "market_time": info.get("regularMarketTime"),
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
                "previous_close": info.get("previousClose"),
                "open": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
            }

            return json.dumps(result, indent=2)

        except DataNotAvailableError:
            raise
        except Exception as e:
            raise YFinanceAPIError(f"Failed to fetch current price: {str(e)}", symbol)

    def get_stock_price_by_date(self, symbol: str, date: str) -> str:
        """Get the stock price for a specific date.

        Args:
            symbol: Stock ticker symbol
            date: Date in ISO format (YYYY-MM-DD)

        Returns:
            JSON string containing price data for the specified date including:
            - date: The requested date
            - open: Opening price
            - high: Highest price
            - low: Lowest price
            - close: Closing price
            - volume: Trading volume
            - adj_close: Adjusted closing price

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If no data available for the date
            InvalidParameterError: If date format is invalid

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_stock_price_by_date("AAPL", "2024-01-15")
            >>> print(result)
            {
              "date": "2024-01-15",
              "open": 150.00,
              ...
            }
        """
        ticker = self._get_ticker(symbol)

        try:
            # Validate date format
            try:
                target_date = pd.to_datetime(date)
            except Exception:
                raise InvalidParameterError(
                    "date", date, ["ISO format: YYYY-MM-DD"]
                )

            # Fetch data for a range around the target date
            # (to handle weekends/holidays)
            start_date = target_date - pd.Timedelta(days=7)
            end_date = target_date + pd.Timedelta(days=1)

            hist = ticker.history(start=start_date, end=end_date, interval="1d")

            if hist.empty:
                raise DataNotAvailableError(f"Price data for {date}", symbol)

            # Find the closest date
            hist.index = pd.to_datetime(hist.index)
            closest_idx = hist.index.get_indexer([target_date], method="nearest")[0]

            if closest_idx < 0 or closest_idx >= len(hist):
                raise DataNotAvailableError(f"Price data for {date}", symbol)

            row = hist.iloc[closest_idx]
            actual_date = hist.index[closest_idx]

            result = {
                "date": actual_date.strftime("%Y-%m-%d"),
                "requested_date": date,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "adj_close": float(row["Close"]),  # Adjusted close
            }

            return json.dumps(result, indent=2)

        except (DataNotAvailableError, InvalidParameterError):
            raise
        except Exception as e:
            raise YFinanceAPIError(
                f"Failed to fetch price for date {date}: {str(e)}", symbol
            )

    def get_stock_price_date_range(
        self, symbol: str, start_date: str, end_date: str
    ) -> str:
        """Get stock prices for a date range.

        Args:
            symbol: Stock ticker symbol
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)

        Returns:
            JSON string containing array of price data points, each with:
            - date: Trading date
            - open: Opening price
            - high: Highest price
            - low: Lowest price
            - close: Closing price
            - volume: Trading volume
            - adj_close: Adjusted closing price

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If no data available for the range
            InvalidParameterError: If date format is invalid

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_stock_price_date_range(
            ...     "AAPL", "2024-01-01", "2024-01-31"
            ... )
        """
        ticker = self._get_ticker(symbol)

        try:
            # Validate date formats
            try:
                pd.to_datetime(start_date)
                pd.to_datetime(end_date)
            except Exception:
                raise InvalidParameterError(
                    "date", f"{start_date} or {end_date}", ["ISO format: YYYY-MM-DD"]
                )

            hist = ticker.history(start=start_date, end=end_date, interval="1d")

            if hist.empty:
                raise DataNotAvailableError(
                    f"Price data for range {start_date} to {end_date}", symbol
                )

            # Convert to list of dictionaries
            hist = format_dataframe_dates(hist)
            result = []

            for date_str, row in hist.iterrows():
                result.append(
                    {
                        "date": date_str,
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"]),
                        "volume": int(row["Volume"]),
                        "adj_close": float(row["Close"]),
                    }
                )

            return json.dumps(result, indent=2)

        except (DataNotAvailableError, InvalidParameterError):
            raise
        except Exception as e:
            raise YFinanceAPIError(
                f"Failed to fetch price range: {str(e)}", symbol
            )

    def get_historical_stock_prices(
        self, symbol: str, period: PeriodType = "1mo", interval: IntervalType = "1d"
    ) -> str:
        """Get historical stock prices for a specified period and interval.

        Args:
            symbol: Stock ticker symbol
            period: Time period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval (e.g., '1m', '5m', '1h', '1d', '1wk', '1mo')

        Returns:
            JSON string containing array of historical price data points

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If no data available
            InvalidParameterError: If period or interval is invalid

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_historical_stock_prices("AAPL", period="1mo", interval="1d")
        """
        ticker = self._get_ticker(symbol)

        try:
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                raise DataNotAvailableError(
                    f"Historical data (period={period}, interval={interval})", symbol
                )

            # Convert to list of dictionaries
            hist = format_dataframe_dates(hist)
            result = []

            for date_str, row in hist.iterrows():
                data_point = {
                    "date": date_str,
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                }

                # Add optional fields if available
                if "Dividends" in row:
                    data_point["dividends"] = float(row["Dividends"])
                if "Stock Splits" in row:
                    data_point["stock_splits"] = float(row["Stock Splits"])

                result.append(data_point)

            return json.dumps(result, indent=2)

        except DataNotAvailableError:
            raise
        except Exception as e:
            raise YFinanceAPIError(
                f"Failed to fetch historical prices: {str(e)}", symbol
            )

    def get_dividends(self, symbol: str) -> str:
        """Get dividend history for a stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string containing array of dividend payments, each with:
            - date: Payment date
            - amount: Dividend amount per share

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If no dividend data available

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_dividends("AAPL")
        """
        ticker = self._get_ticker(symbol)

        try:
            dividends = ticker.dividends

            if dividends is None or dividends.empty:
                raise DataNotAvailableError("Dividend data", symbol)

            # Convert to list of dictionaries
            result = []
            for date, amount in dividends.items():
                result.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "amount": float(amount),
                    }
                )

            return json.dumps(result, indent=2)

        except DataNotAvailableError:
            raise
        except Exception as e:
            raise YFinanceAPIError(f"Failed to fetch dividends: {str(e)}", symbol)

    def get_stock_actions(self, symbol: str) -> str:
        """Get stock actions (splits, dividends) history.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string containing array of stock actions with:
            - date: Action date
            - dividends: Dividend amount (if applicable)
            - stock_splits: Split ratio (if applicable)

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If no action data available

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_stock_actions("AAPL")
        """
        ticker = self._get_ticker(symbol)

        try:
            actions = ticker.actions

            if actions is None or actions.empty:
                raise DataNotAvailableError("Stock actions data", symbol)

            # Convert to list of dictionaries
            result = []
            for date, row in actions.iterrows():
                action = {"date": date.strftime("%Y-%m-%d")}

                if "Dividends" in row and row["Dividends"] > 0:
                    action["dividends"] = float(row["Dividends"])

                if "Stock Splits" in row and row["Stock Splits"] > 0:
                    action["stock_splits"] = float(row["Stock Splits"])

                result.append(action)

            return json.dumps(result, indent=2)

        except DataNotAvailableError:
            raise
        except Exception as e:
            raise YFinanceAPIError(f"Failed to fetch stock actions: {str(e)}", symbol)

    # ==================== COMPANY INFORMATION ====================

    def get_stock_info(self, symbol: str) -> str:
        """Get comprehensive company and stock information.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string containing detailed company information including:
            - Basic info: name, sector, industry, website
            - Market data: market cap, price, volume
            - Financial metrics: P/E ratio, dividend yield, etc.
            - Company description and key statistics

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_stock_info("AAPL")
        """
        ticker = self._get_ticker(symbol)

        try:
            info = ticker.info

            if not info or len(info) <= 1:
                raise DataNotAvailableError("Stock information", symbol)

            # Return the full info dictionary as JSON
            # Clean up any non-serializable values
            clean_info = {}
            for key, value in info.items():
                try:
                    json.dumps(value)  # Test if serializable
                    clean_info[key] = value
                except (TypeError, ValueError):
                    clean_info[key] = str(value)

            return json.dumps(clean_info, indent=2)

        except DataNotAvailableError:
            raise
        except Exception as e:
            raise YFinanceAPIError(f"Failed to fetch stock info: {str(e)}", symbol)

    # ==================== FINANCIAL STATEMENTS ====================

    def get_income_statement(
        self, symbol: str, freq: FrequencyType = "yearly"
    ) -> str:
        """Get income statement for a stock.

        Args:
            symbol: Stock ticker symbol
            freq: Frequency - 'yearly' or 'quarterly' (default: 'yearly')

        Returns:
            JSON string containing income statement data with rows as financial
            line items and columns as time periods

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If income statement not available
            InvalidParameterError: If frequency is invalid

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_income_statement("AAPL", freq="yearly")
        """
        ticker = self._get_ticker(symbol)

        try:
            if freq == "yearly":
                income_stmt = ticker.income_stmt
            elif freq == "quarterly":
                income_stmt = ticker.quarterly_income_stmt
            else:
                raise InvalidParameterError("freq", freq, ["yearly", "quarterly"])

            if income_stmt is None or income_stmt.empty:
                raise DataNotAvailableError(f"Income statement ({freq})", symbol)

            # Convert to JSON with proper date formatting
            return dataframe_to_json_string(income_stmt.T, orient="index")

        except (DataNotAvailableError, InvalidParameterError):
            raise
        except Exception as e:
            raise YFinanceAPIError(
                f"Failed to fetch income statement: {str(e)}", symbol
            )

    def get_balance_sheet(self, symbol: str, freq: FrequencyType = "yearly") -> str:
        """Get balance sheet for a stock.

        Args:
            symbol: Stock ticker symbol
            freq: Frequency - 'yearly' or 'quarterly' (default: 'yearly')

        Returns:
            JSON string containing balance sheet data with rows as financial
            line items and columns as time periods

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If balance sheet not available
            InvalidParameterError: If frequency is invalid

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_balance_sheet("AAPL", freq="yearly")
        """
        ticker = self._get_ticker(symbol)

        try:
            if freq == "yearly":
                balance_sheet = ticker.balance_sheet
            elif freq == "quarterly":
                balance_sheet = ticker.quarterly_balance_sheet
            else:
                raise InvalidParameterError("freq", freq, ["yearly", "quarterly"])

            if balance_sheet is None or balance_sheet.empty:
                raise DataNotAvailableError(f"Balance sheet ({freq})", symbol)

            # Convert to JSON with proper date formatting
            return dataframe_to_json_string(balance_sheet.T, orient="index")

        except (DataNotAvailableError, InvalidParameterError):
            raise
        except Exception as e:
            raise YFinanceAPIError(
                f"Failed to fetch balance sheet: {str(e)}", symbol
            )

    def get_cashflow(self, symbol: str, freq: FrequencyType = "yearly") -> str:
        """Get cash flow statement for a stock.

        Args:
            symbol: Stock ticker symbol
            freq: Frequency - 'yearly' or 'quarterly' (default: 'yearly')

        Returns:
            JSON string containing cash flow statement data with rows as
            financial line items and columns as time periods

        Raises:
            TickerNotFoundError: If ticker symbol is not found
            YFinanceAPIError: If API request fails
            DataNotAvailableError: If cash flow statement not available
            InvalidParameterError: If frequency is invalid

        Examples:
            >>> service = YahooFinanceService()
            >>> result = service.get_cashflow("AAPL", freq="yearly")
        """
        ticker = self._get_ticker(symbol)

        try:
            if freq == "yearly":
                cashflow = ticker.cashflow
            elif freq == "quarterly":
                cashflow = ticker.quarterly_cashflow
            else:
                raise InvalidParameterError("freq", freq, ["yearly", "quarterly"])

            if cashflow is None or cashflow.empty:
                raise DataNotAvailableError(f"Cash flow statement ({freq})", symbol)

            # Convert to JSON with proper date formatting
            return dataframe_to_json_string(cashflow.T, orient="index")

        except (DataNotAvailableError, InvalidParameterError):
            raise
        except Exception as e:
            raise YFinanceAPIError(
                f"Failed to fetch cash flow statement: {str(e)}", symbol
            )
