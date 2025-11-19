"""Yahoo Finance service layer for MCP server.

This module provides the business logic for interacting with Yahoo Finance
through the yfinance library. It handles data retrieval, validation, and
formatting for all supported operations.
"""

import json
from datetime import datetime

import pandas as pd
import yfinance as yf
from requests import Session

from .exceptions import (
    DataNotAvailableError,
    InvalidParameterError,
    TickerNotFoundError,
    YFinanceAPIError,
)
from .models import (
    FrequencyType,
    HolderInfoType,
    IntervalType,
    OptionChainType,
    PeriodType,
    RecommendationInfoType,
)
from .utils import format_dataframe_dates, normalize_ticker


class YahooFinanceService:
    """Service class for Yahoo Finance operations.

    This class provides methods for retrieving stock data, financial
    information, and market data from Yahoo Finance.

    Attributes:
        session: Optional requests session for API calls
        verify: Whether to verify SSL certificates
        default_market: Default market for ticker normalization
    """

    def __init__(
        self,
        session: Session | None = None,
        verify: bool = True,
        default_market: str = "US",
    ):
        """Initialize the Yahoo Finance service.

        Args:
            session: Optional requests session for API calls
            verify: Whether to verify SSL certificates
            default_market: Default market for ticker normalization (e.g., "US", "BR", "UK")
        """
        self.session = session
        self.verify = verify
        self.default_market = default_market

    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """Get a yfinance Ticker object with validation.

        Args:
            symbol: Stock ticker symbol

        Returns:
            yfinance Ticker object

        Raises:
            TickerNotFoundError: If the ticker is invalid or not found
        """
        normalized_symbol = normalize_ticker(symbol, self.default_market)

        try:
            ticker = yf.Ticker(normalized_symbol, session=self.session)

            # Validate ticker by checking if it has any info
            if not ticker.info or len(ticker.info) == 0:
                raise TickerNotFoundError(normalized_symbol)

            return ticker
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), normalized_symbol)

    # ========================================================================
    # Pricing & Historical Data Methods
    # ========================================================================

    def get_current_stock_price(self, symbol: str) -> str:
        """Get the current stock price for a given ticker symbol.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "PETR4")

        Returns:
            JSON string with current price information
        """
        ticker = self._get_ticker(symbol)

        try:
            info = ticker.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")

            if current_price is None:
                raise DataNotAvailableError("current price", symbol)

            result = {
                "symbol": ticker.ticker,
                "price": current_price,
                "currency": info.get("currency", "USD"),
                "market_state": info.get("marketState", "UNKNOWN"),
                "timestamp": datetime.now().isoformat(),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_stock_price_by_date(self, symbol: str, date: str) -> str:
        """Get stock price for a specific date.

        Args:
            symbol: Stock ticker symbol
            date: Date in YYYY-MM-DD format

        Returns:
            JSON string with price information for the specified date
        """
        ticker = self._get_ticker(symbol)

        try:
            # Fetch a small range around the date to ensure we get data
            hist = ticker.history(start=date, end=date, interval="1d")

            if hist.empty:
                raise DataNotAvailableError(f"price data for date {date}", symbol)

            row = hist.iloc[0]
            result = {
                "symbol": ticker.ticker,
                "date": date,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "adj_close": float(row.get("Adj Close", row["Close"])),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_stock_price_date_range(
        self, symbol: str, start_date: str, end_date: str
    ) -> str:
        """Get stock prices for a date range.

        Args:
            symbol: Stock ticker symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            JSON string with price data for the date range
        """
        ticker = self._get_ticker(symbol)

        try:
            hist = ticker.history(start=start_date, end=end_date, interval="1d")

            if hist.empty:
                raise DataNotAvailableError(
                    f"price data for range {start_date} to {end_date}", symbol
                )

            hist = format_dataframe_dates(hist)
            result = {
                "symbol": ticker.ticker,
                "start_date": start_date,
                "end_date": end_date,
                "data": hist.to_dict(orient="index"),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_historical_stock_prices(
        self, symbol: str, period: PeriodType = "1mo", interval: IntervalType = "1d"
    ) -> str:
        """Get historical stock prices for a given period and interval.

        Args:
            symbol: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            JSON string with historical price data
        """
        ticker = self._get_ticker(symbol)

        try:
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                raise DataNotAvailableError(
                    f"historical data for period {period}", symbol
                )

            hist = format_dataframe_dates(hist)
            result = {
                "symbol": ticker.ticker,
                "period": period,
                "interval": interval,
                "data": hist.to_dict(orient="index"),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_dividends(self, symbol: str) -> str:
        """Get dividend history for a stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string with dividend history
        """
        ticker = self._get_ticker(symbol)

        try:
            dividends = ticker.dividends

            if dividends.empty:
                return json.dumps(
                    {
                        "symbol": ticker.ticker,
                        "message": "No dividend data available",
                        "dividends": [],
                    },
                    indent=2,
                )

            dividends_df = format_dataframe_dates(dividends.to_frame("amount"))
            result = {
                "symbol": ticker.ticker,
                "dividends": dividends_df.to_dict(orient="index"),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_stock_actions(self, symbol: str) -> str:
        """Get stock actions (splits and dividends) history.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string with stock actions history
        """
        ticker = self._get_ticker(symbol)

        try:
            actions = ticker.actions

            if actions.empty:
                return json.dumps(
                    {
                        "symbol": ticker.ticker,
                        "message": "No stock actions data available",
                        "actions": [],
                    },
                    indent=2,
                )

            actions_df = format_dataframe_dates(actions)
            result = {
                "symbol": ticker.ticker,
                "actions": actions_df.to_dict(orient="index"),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========================================================================
    # Company Info Methods
    # ========================================================================

    def get_stock_info(self, symbol: str) -> str:
        """Get comprehensive stock information.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string with detailed stock information
        """
        ticker = self._get_ticker(symbol)

        try:
            info = ticker.info

            if not info:
                raise DataNotAvailableError("company information", symbol)

            return json.dumps({"symbol": ticker.ticker, "info": info}, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========================================================================
    # Financial Statements Methods
    # ========================================================================

    def get_income_statement(
        self, symbol: str, freq: FrequencyType = "yearly"
    ) -> str:
        """Get income statement for a stock.

        Args:
            symbol: Stock ticker symbol
            freq: Frequency - 'yearly' or 'quarterly'

        Returns:
            JSON string with income statement data
        """
        ticker = self._get_ticker(symbol)

        try:
            if freq == "yearly":
                statement = ticker.financials
            else:
                statement = ticker.quarterly_financials

            if statement is None or statement.empty:
                raise DataNotAvailableError(f"{freq} income statement", symbol)

            # Convert column names (dates) to strings
            statement.columns = statement.columns.astype(str)

            result = {
                "symbol": ticker.ticker,
                "frequency": freq,
                "income_statement": statement.to_dict(),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_balance_sheet(self, symbol: str, freq: FrequencyType = "yearly") -> str:
        """Get balance sheet for a stock.

        Args:
            symbol: Stock ticker symbol
            freq: Frequency - 'yearly' or 'quarterly'

        Returns:
            JSON string with balance sheet data
        """
        ticker = self._get_ticker(symbol)

        try:
            if freq == "yearly":
                statement = ticker.balance_sheet
            else:
                statement = ticker.quarterly_balance_sheet

            if statement is None or statement.empty:
                raise DataNotAvailableError(f"{freq} balance sheet", symbol)

            # Convert column names (dates) to strings
            statement.columns = statement.columns.astype(str)

            result = {
                "symbol": ticker.ticker,
                "frequency": freq,
                "balance_sheet": statement.to_dict(),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_cashflow(self, symbol: str, freq: FrequencyType = "yearly") -> str:
        """Get cash flow statement for a stock.

        Args:
            symbol: Stock ticker symbol
            freq: Frequency - 'yearly' or 'quarterly'

        Returns:
            JSON string with cash flow data
        """
        ticker = self._get_ticker(symbol)

        try:
            if freq == "yearly":
                statement = ticker.cashflow
            else:
                statement = ticker.quarterly_cashflow

            if statement is None or statement.empty:
                raise DataNotAvailableError(f"{freq} cash flow statement", symbol)

            # Convert column names (dates) to strings
            statement.columns = statement.columns.astype(str)

            result = {
                "symbol": ticker.ticker,
                "frequency": freq,
                "cashflow": statement.to_dict(),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========================================================================
    # Holders & Ownership Methods
    # ========================================================================

    def get_holder_info(self, symbol: str, holder_type: HolderInfoType) -> str:
        """Get holder information for a stock.

        Args:
            symbol: Stock ticker symbol
            holder_type: Type of holder info (major_holders, institutional_holders, etc.)

        Returns:
            JSON string with holder information
        """
        ticker = self._get_ticker(symbol)

        try:
            holder_map = {
                "major_holders": ticker.major_holders,
                "institutional_holders": ticker.institutional_holders,
                "mutualfund_holders": ticker.mutualfund_holders,
                "insider_transactions": ticker.insider_transactions,
                "insider_purchases": ticker.insider_purchases,
                "insider_roster_holders": ticker.insider_roster_holders,
            }

            if holder_type not in holder_map:
                valid_types = list(holder_map.keys())
                raise InvalidParameterError("holder_type", holder_type, valid_types)

            data = holder_map[holder_type]

            if data is None or (isinstance(data, pd.DataFrame) and data.empty):
                return json.dumps(
                    {
                        "symbol": ticker.ticker,
                        "holder_type": holder_type,
                        "message": f"No {holder_type} data available",
                        "data": [],
                    },
                    indent=2,
                )

            # Convert DataFrame to dict
            if isinstance(data, pd.DataFrame):
                data_dict = data.to_dict(orient="records")
            else:
                data_dict = data

            result = {
                "symbol": ticker.ticker,
                "holder_type": holder_type,
                "data": data_dict,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(
                e, (InvalidParameterError, TickerNotFoundError)
            ):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========================================================================
    # Options Methods
    # ========================================================================

    def get_option_expiration_dates(self, symbol: str) -> str:
        """Get available option expiration dates for a stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string with list of expiration dates
        """
        ticker = self._get_ticker(symbol)

        try:
            dates = ticker.options

            if not dates:
                raise DataNotAvailableError("option expiration dates", symbol)

            result = {
                "symbol": ticker.ticker,
                "expiration_dates": list(dates),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_option_chain(
        self,
        symbol: str,
        expiration_date: str,
        option_type: OptionChainType = "both",
    ) -> str:
        """Get option chain for a specific expiration date.

        Args:
            symbol: Stock ticker symbol
            expiration_date: Expiration date (YYYY-MM-DD format)
            option_type: Type of options to retrieve (calls, puts, or both)

        Returns:
            JSON string with option chain data
        """
        ticker = self._get_ticker(symbol)

        try:
            opt = ticker.option_chain(expiration_date)

            result = {
                "symbol": ticker.ticker,
                "expiration_date": expiration_date,
            }

            if option_type in ("calls", "both"):
                if opt.calls is not None and not opt.calls.empty:
                    result["calls"] = opt.calls.to_dict(orient="records")
                else:
                    result["calls"] = []

            if option_type in ("puts", "both"):
                if opt.puts is not None and not opt.puts.empty:
                    result["puts"] = opt.puts.to_dict(orient="records")
                else:
                    result["puts"] = []

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========================================================================
    # News & Analysis Methods
    # ========================================================================

    def get_news(self, symbol: str) -> str:
        """Get recent news articles for a stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string with news articles
        """
        ticker = self._get_ticker(symbol)

        try:
            news = ticker.news

            if not news:
                return json.dumps(
                    {
                        "symbol": ticker.ticker,
                        "message": "No news available",
                        "news": [],
                    },
                    indent=2,
                )

            result = {
                "symbol": ticker.ticker,
                "news": news,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_recommendations(
        self,
        symbol: str,
        recommendation_type: RecommendationInfoType = "recommendations",
        months_back: int = 12,
    ) -> str:
        """Get analyst recommendations for a stock.

        Args:
            symbol: Stock ticker symbol
            recommendation_type: Type of recommendations (recommendations or upgrades_downgrades)
            months_back: Number of months of historical data to retrieve

        Returns:
            JSON string with recommendation data
        """
        ticker = self._get_ticker(symbol)

        try:
            if recommendation_type == "recommendations":
                data = ticker.recommendations
            else:
                data = ticker.upgrades_downgrades

            if data is None or data.empty:
                return json.dumps(
                    {
                        "symbol": ticker.ticker,
                        "recommendation_type": recommendation_type,
                        "message": f"No {recommendation_type} data available",
                        "data": [],
                    },
                    indent=2,
                )

            # Filter by months_back if data has dates
            if hasattr(data.index, "to_pydatetime"):
                cutoff_date = pd.Timestamp.now() - pd.DateOffset(months=months_back)
                data = data[data.index >= cutoff_date]

            # Format the data
            if isinstance(data.index, pd.DatetimeIndex):
                data = format_dataframe_dates(data)

            result = {
                "symbol": ticker.ticker,
                "recommendation_type": recommendation_type,
                "months_back": months_back,
                "data": data.to_dict(orient="index"),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_earning_dates(self, symbol: str, limit: int = 12) -> str:
        """Get upcoming and historical earnings dates.

        Args:
            symbol: Stock ticker symbol
            limit: Maximum number of dates to return

        Returns:
            JSON string with earnings dates
        """
        ticker = self._get_ticker(symbol)

        try:
            earnings_dates = ticker.earnings_dates

            if earnings_dates is None or earnings_dates.empty:
                raise DataNotAvailableError("earnings dates", symbol)

            # Limit the number of results
            earnings_dates = earnings_dates.head(limit)

            # Format dates
            if isinstance(earnings_dates.index, pd.DatetimeIndex):
                earnings_dates = format_dataframe_dates(earnings_dates)

            result = {
                "symbol": ticker.ticker,
                "limit": limit,
                "earnings_dates": earnings_dates.to_dict(orient="index"),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========================================================================
    # Bonus Methods
    # ========================================================================

    def get_stock_splits(self, symbol: str) -> str:
        """Get stock split history.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string with stock split history
        """
        ticker = self._get_ticker(symbol)

        try:
            splits = ticker.splits

            if splits.empty:
                return json.dumps(
                    {
                        "symbol": ticker.ticker,
                        "message": "No stock split data available",
                        "splits": [],
                    },
                    indent=2,
                )

            splits_df = format_dataframe_dates(splits.to_frame("ratio"))
            result = {
                "symbol": ticker.ticker,
                "splits": splits_df.to_dict(orient="index"),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_analyst_price_targets(self, symbol: str) -> str:
        """Get analyst price targets and estimates.

        Args:
            symbol: Stock ticker symbol

        Returns:
            JSON string with analyst price targets
        """
        ticker = self._get_ticker(symbol)

        try:
            info = ticker.info

            price_targets = {
                "symbol": ticker.ticker,
                "current_price": info.get("currentPrice"),
                "target_high_price": info.get("targetHighPrice"),
                "target_low_price": info.get("targetLowPrice"),
                "target_mean_price": info.get("targetMeanPrice"),
                "target_median_price": info.get("targetMedianPrice"),
                "number_of_analyst_opinions": info.get("numberOfAnalystOpinions"),
                "recommendation": info.get("recommendationKey"),
            }

            # Filter out None values
            price_targets = {k: v for k, v in price_targets.items() if v is not None}

            if len(price_targets) <= 1:  # Only symbol is present
                raise DataNotAvailableError("analyst price targets", symbol)

            return json.dumps(price_targets, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)
