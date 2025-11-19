"""Yahoo Finance service layer for MCP integration.

This module provides the main YahooFinanceService class that wraps yfinance
functionality and returns JSON-formatted data suitable for MCP tools.
"""

import json
from datetime import datetime
from typing import Optional

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
    """Service class for interacting with Yahoo Finance API.

    This class provides methods to fetch stock data, financial statements,
    and other market information from Yahoo Finance.

    Attributes:
        session: Optional requests Session for connection pooling.
        verify: Whether to verify SSL certificates.
        default_market: Default market for ticker normalization.
    """

    def __init__(
        self,
        session: Optional[Session] = None,
        verify: bool = True,
        default_market: str = "US",
    ) -> None:
        """Initialize the Yahoo Finance service.

        Args:
            session: Optional requests Session for connection pooling.
            verify: Whether to verify SSL certificates (default: True).
            default_market: Default market for ticker normalization (default: "US").
        """
        self.session = session
        self.verify = verify
        self.default_market = default_market

    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """Get a yfinance Ticker object for the given symbol.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            yfinance Ticker object.

        Raises:
            TickerNotFoundError: If the ticker is invalid or not found.
        """
        try:
            normalized_symbol = normalize_ticker(symbol, self.default_market)
            ticker = yf.Ticker(normalized_symbol, session=self.session)

            # Verify ticker exists by checking if info is available
            if not ticker.info or len(ticker.info) <= 1:
                raise TickerNotFoundError(symbol)

            return ticker
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========== PRICING & HISTORICAL DATA (Methods 1-6) ==========

    def get_current_stock_price(self, symbol: str) -> str:
        """Get the current stock price for a given symbol.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "PETR4").

        Returns:
            JSON string with current price information.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            info = ticker.info
            current_price = info.get("currentPrice") or info.get("regularMarketPrice")

            if current_price is None:
                raise DataNotAvailableError("current price", symbol)

            result = {
                "symbol": symbol,
                "price": current_price,
                "currency": info.get("currency"),
                "market_time": info.get("regularMarketTime"),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_stock_price_by_date(self, symbol: str, date: str) -> str:
        """Get the stock price for a specific date.

        Args:
            symbol: Stock ticker symbol.
            date: Date in YYYY-MM-DD format.

        Returns:
            JSON string with price data for the specified date.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no data is available for the date.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")

            # Get historical data for the specific date
            hist = ticker.history(start=date, end=date, interval="1d")

            if hist.empty:
                raise DataNotAvailableError(f"price data for date {date}", symbol)

            # Convert to dictionary
            row = hist.iloc[0]
            result = {
                "symbol": symbol,
                "date": date,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            }

            if "Adj Close" in row:
                result["adj_close"] = float(row["Adj Close"])

            return json.dumps(result, indent=2)
        except ValueError as e:
            raise InvalidParameterError("date", date, ["YYYY-MM-DD format"])
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError, InvalidParameterError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_stock_price_date_range(self, symbol: str, start_date: str, end_date: str) -> str:
        """Get stock prices for a date range.

        Args:
            symbol: Stock ticker symbol.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.

        Returns:
            JSON string with price data for the date range.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no data is available for the range.
            InvalidParameterError: If date format is invalid.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            # Validate date formats
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")

            hist = ticker.history(start=start_date, end=end_date, interval="1d")

            if hist.empty:
                raise DataNotAvailableError(f"price data for range {start_date} to {end_date}", symbol)

            # Format dates in index
            hist = format_dataframe_dates(hist)

            # Convert to list of records
            data = []
            for date, row in hist.iterrows():
                record = {
                    "date": str(date),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                }
                if "Adj Close" in row:
                    record["adj_close"] = float(row["Adj Close"])
                data.append(record)

            result = {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "data": data,
            }

            return json.dumps(result, indent=2)
        except ValueError as e:
            raise InvalidParameterError("date", f"{start_date} or {end_date}", ["YYYY-MM-DD format"])
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError, InvalidParameterError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_historical_stock_prices(
        self, symbol: str, period: PeriodType = "1mo", interval: IntervalType = "1d"
    ) -> str:
        """Get historical stock prices for a given period and interval.

        Args:
            symbol: Stock ticker symbol.
            period: Time period (e.g., "1mo", "1y", "max").
            interval: Data interval (e.g., "1d", "1wk", "1mo").

        Returns:
            JSON string with historical price data.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no data is available.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                raise DataNotAvailableError(f"historical data for period {period}", symbol)

            # Format dates in index
            hist = format_dataframe_dates(hist)

            # Convert to list of records
            data = []
            for date, row in hist.iterrows():
                record = {
                    "date": str(date),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                }
                if "Adj Close" in row:
                    record["adj_close"] = float(row["Adj Close"])
                data.append(record)

            result = {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data": data,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_dividends(self, symbol: str) -> str:
        """Get dividend history for a stock.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            JSON string with dividend history.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no dividend data is available.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            dividends = ticker.dividends

            if dividends.empty:
                raise DataNotAvailableError("dividend", symbol)

            # Format dates
            dividends_df = dividends.to_frame(name="amount")
            dividends_df = format_dataframe_dates(dividends_df)

            # Convert to list of records
            data = [{"date": str(date), "amount": float(amount)} for date, amount in dividends_df.iterrows()]

            result = {
                "symbol": symbol,
                "dividends": data,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_stock_actions(self, symbol: str) -> str:
        """Get stock actions (splits and dividends) history.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            JSON string with stock actions history.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no actions data is available.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            actions = ticker.actions

            if actions.empty:
                raise DataNotAvailableError("stock actions", symbol)

            # Format dates
            actions = format_dataframe_dates(actions)

            # Convert to list of records
            data = []
            for date, row in actions.iterrows():
                record = {"date": str(date)}
                if "Dividends" in row and row["Dividends"] > 0:
                    record["dividend"] = float(row["Dividends"])
                if "Stock Splits" in row and row["Stock Splits"] > 0:
                    record["stock_split"] = float(row["Stock Splits"])
                data.append(record)

            result = {
                "symbol": symbol,
                "actions": data,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========== COMPANY INFO (Method 7) ==========

    def get_stock_info(self, symbol: str) -> str:
        """Get comprehensive stock information and metadata.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            JSON string with stock information.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            info = ticker.info

            # Return the full info dictionary
            result = {
                "symbol": symbol,
                "info": info,
            }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, TickerNotFoundError):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========== FINANCIAL STATEMENTS (Methods 8-10) ==========

    def get_income_statement(self, symbol: str, freq: FrequencyType = "yearly") -> str:
        """Get income statement for a stock.

        Args:
            symbol: Stock ticker symbol.
            freq: Frequency - "yearly" or "quarterly".

        Returns:
            JSON string with income statement data.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no income statement data is available.
            InvalidParameterError: If frequency is invalid.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            if freq == "yearly":
                income_stmt = ticker.financials
            elif freq == "quarterly":
                income_stmt = ticker.quarterly_financials
            else:
                raise InvalidParameterError("freq", freq, ["yearly", "quarterly"])

            if income_stmt is None or income_stmt.empty:
                raise DataNotAvailableError(f"{freq} income statement", symbol)

            # Convert to JSON-serializable format
            income_stmt = format_dataframe_dates(income_stmt.T)
            data = income_stmt.to_dict(orient="index")

            result = {
                "symbol": symbol,
                "frequency": freq,
                "income_statement": data,
            }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError, InvalidParameterError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_balance_sheet(self, symbol: str, freq: FrequencyType = "yearly") -> str:
        """Get balance sheet for a stock.

        Args:
            symbol: Stock ticker symbol.
            freq: Frequency - "yearly" or "quarterly".

        Returns:
            JSON string with balance sheet data.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no balance sheet data is available.
            InvalidParameterError: If frequency is invalid.
            YFinanceAPIError: If the API request fails.
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
                raise DataNotAvailableError(f"{freq} balance sheet", symbol)

            # Convert to JSON-serializable format
            balance_sheet = format_dataframe_dates(balance_sheet.T)
            data = balance_sheet.to_dict(orient="index")

            result = {
                "symbol": symbol,
                "frequency": freq,
                "balance_sheet": data,
            }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError, InvalidParameterError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_cashflow(self, symbol: str, freq: FrequencyType = "yearly") -> str:
        """Get cash flow statement for a stock.

        Args:
            symbol: Stock ticker symbol.
            freq: Frequency - "yearly" or "quarterly".

        Returns:
            JSON string with cash flow data.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no cash flow data is available.
            InvalidParameterError: If frequency is invalid.
            YFinanceAPIError: If the API request fails.
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
                raise DataNotAvailableError(f"{freq} cash flow", symbol)

            # Convert to JSON-serializable format
            cashflow = format_dataframe_dates(cashflow.T)
            data = cashflow.to_dict(orient="index")

            result = {
                "symbol": symbol,
                "frequency": freq,
                "cashflow": data,
            }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError, InvalidParameterError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========== HOLDERS & OWNERSHIP (Method 11) ==========

    def get_holder_info(self, symbol: str, holder_type: HolderInfoType) -> str:
        """Get holder and ownership information for a stock.

        Args:
            symbol: Stock ticker symbol.
            holder_type: Type of holder information to retrieve. Options:
                - "major_holders": Major shareholders overview
                - "institutional_holders": Institutional ownership details
                - "mutualfund_holders": Mutual fund ownership details
                - "insider_transactions": Insider trading activity
                - "insider_purchases": Insider purchase transactions
                - "insider_roster_holders": Current insider roster

        Returns:
            JSON string with holder information.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If holder data is not available.
            InvalidParameterError: If holder_type is invalid.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            # Map holder_type to ticker attribute
            holder_data = None

            if holder_type == "major_holders":
                holder_data = ticker.major_holders
            elif holder_type == "institutional_holders":
                holder_data = ticker.institutional_holders
            elif holder_type == "mutualfund_holders":
                holder_data = ticker.mutualfund_holders
            elif holder_type == "insider_transactions":
                holder_data = ticker.insider_transactions
            elif holder_type == "insider_purchases":
                holder_data = ticker.insider_purchases
            elif holder_type == "insider_roster_holders":
                holder_data = ticker.insider_roster_holders
            else:
                valid_types = [
                    "major_holders",
                    "institutional_holders",
                    "mutualfund_holders",
                    "insider_transactions",
                    "insider_purchases",
                    "insider_roster_holders",
                ]
                raise InvalidParameterError("holder_type", holder_type, valid_types)

            if holder_data is None or (isinstance(holder_data, pd.DataFrame) and holder_data.empty):
                raise DataNotAvailableError(f"{holder_type} data", symbol)

            # Convert DataFrame to JSON-serializable format
            if isinstance(holder_data, pd.DataFrame):
                # Format dates if present in index or columns
                holder_data = format_dataframe_dates(holder_data)

                # Convert to dictionary
                data = holder_data.to_dict(orient="records")
            else:
                data = holder_data

            result = {
                "symbol": symbol,
                "holder_type": holder_type,
                "data": data,
            }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError, InvalidParameterError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========== OPTIONS (Methods 12-13) ==========

    def get_option_expiration_dates(self, symbol: str) -> str:
        """Get available option expiration dates for a stock.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            JSON string with list of expiration dates.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no options data is available.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            expiration_dates = ticker.options

            if not expiration_dates:
                raise DataNotAvailableError("option expiration dates", symbol)

            result = {
                "symbol": symbol,
                "expiration_dates": list(expiration_dates),
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_option_chain(
        self, symbol: str, expiration_date: str, option_type: OptionChainType = "both"
    ) -> str:
        """Get option chain data for a specific expiration date.

        Args:
            symbol: Stock ticker symbol.
            expiration_date: Option expiration date (YYYY-MM-DD format).
            option_type: Type of options - "calls", "puts", or "both".

        Returns:
            JSON string with option chain data.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no options data is available.
            InvalidParameterError: If option_type or expiration_date is invalid.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            # Verify expiration date exists
            if expiration_date not in ticker.options:
                raise InvalidParameterError("expiration_date", expiration_date, list(ticker.options))

            # Get option chain
            opt_chain = ticker.option_chain(expiration_date)

            result = {
                "symbol": symbol,
                "expiration_date": expiration_date,
                "option_type": option_type,
            }

            # Process based on option_type
            if option_type == "calls":
                if opt_chain.calls.empty:
                    raise DataNotAvailableError("calls option chain", symbol)
                result["calls"] = opt_chain.calls.to_dict(orient="records")
            elif option_type == "puts":
                if opt_chain.puts.empty:
                    raise DataNotAvailableError("puts option chain", symbol)
                result["puts"] = opt_chain.puts.to_dict(orient="records")
            elif option_type == "both":
                if opt_chain.calls.empty and opt_chain.puts.empty:
                    raise DataNotAvailableError("option chain", symbol)
                result["calls"] = opt_chain.calls.to_dict(orient="records") if not opt_chain.calls.empty else []
                result["puts"] = opt_chain.puts.to_dict(orient="records") if not opt_chain.puts.empty else []
            else:
                raise InvalidParameterError("option_type", option_type, ["calls", "puts", "both"])

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError, InvalidParameterError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========== NEWS & ANALYSIS (Methods 14-16) ==========

    def get_news(self, symbol: str) -> str:
        """Get recent news articles for a stock.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            JSON string with news articles.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no news data is available.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            news = ticker.news

            if not news:
                raise DataNotAvailableError("news", symbol)

            # Format news data
            formatted_news = []
            for article in news:
                formatted_article = {
                    "title": article.get("title", ""),
                    "publisher": article.get("publisher", ""),
                    "link": article.get("link", ""),
                }

                # Handle timestamp conversion
                if "providerPublishTime" in article:
                    formatted_article["published_date"] = datetime.fromtimestamp(
                        article["providerPublishTime"]
                    ).isoformat()

                # Add thumbnail if available
                if "thumbnail" in article and article["thumbnail"]:
                    resolutions = article["thumbnail"].get("resolutions", [])
                    if resolutions:
                        formatted_article["thumbnail"] = resolutions[0].get("url", "")

                formatted_news.append(formatted_article)

            result = {
                "symbol": symbol,
                "news": formatted_news,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
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
            symbol: Stock ticker symbol.
            recommendation_type: Type of recommendations - "recommendations" or "upgrades_downgrades".
            months_back: Number of months of historical recommendations to retrieve.

        Returns:
            JSON string with analyst recommendations.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no recommendations data is available.
            InvalidParameterError: If recommendation_type is invalid.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            if recommendation_type == "recommendations":
                recommendations = ticker.recommendations
            elif recommendation_type == "upgrades_downgrades":
                recommendations = ticker.upgrades_downgrades
            else:
                raise InvalidParameterError(
                    "recommendation_type", recommendation_type, ["recommendations", "upgrades_downgrades"]
                )

            if recommendations is None or recommendations.empty:
                raise DataNotAvailableError(f"{recommendation_type} data", symbol)

            # Format dates in index
            recommendations = format_dataframe_dates(recommendations)

            # Filter by months_back if applicable
            if months_back and isinstance(recommendations.index, pd.Index):
                # Limit to requested number of records
                recommendations = recommendations.tail(months_back * 4)  # Approximate weekly recommendations

            # Convert to dictionary
            data = recommendations.to_dict(orient="records")

            result = {
                "symbol": symbol,
                "recommendation_type": recommendation_type,
                "months_back": months_back,
                "data": data,
            }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError, InvalidParameterError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_earning_dates(self, symbol: str, limit: int = 12) -> str:
        """Get upcoming and historical earnings dates for a stock.

        Args:
            symbol: Stock ticker symbol.
            limit: Maximum number of earnings dates to retrieve.

        Returns:
            JSON string with earnings dates.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no earnings date data is available.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            earnings_dates = ticker.earnings_dates

            if earnings_dates is None or earnings_dates.empty:
                raise DataNotAvailableError("earnings dates", symbol)

            # Format dates in index
            earnings_dates = format_dataframe_dates(earnings_dates)

            # Limit results
            if limit:
                earnings_dates = earnings_dates.head(limit)

            # Convert to dictionary
            data = earnings_dates.to_dict(orient="index")

            result = {
                "symbol": symbol,
                "limit": limit,
                "earnings_dates": data,
            }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    # ========== BONUS TOOLS (Methods 17-18) ==========

    def get_stock_splits(self, symbol: str) -> str:
        """Get stock split history for a stock.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            JSON string with stock split history.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no stock split data is available.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            splits = ticker.splits

            if splits.empty:
                raise DataNotAvailableError("stock splits", symbol)

            # Format dates
            splits_df = splits.to_frame(name="split_ratio")
            splits_df = format_dataframe_dates(splits_df)

            # Convert to list of records
            data = [{"date": str(date), "split_ratio": float(ratio)} for date, ratio in splits_df.iterrows()]

            result = {
                "symbol": symbol,
                "splits": data,
            }

            return json.dumps(result, indent=2)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)

    def get_analyst_price_targets(self, symbol: str) -> str:
        """Get analyst price targets and recommendations summary.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            JSON string with analyst price targets.

        Raises:
            TickerNotFoundError: If the ticker is invalid.
            DataNotAvailableError: If no analyst target data is available.
            YFinanceAPIError: If the API request fails.
        """
        ticker = self._get_ticker(symbol)

        try:
            info = ticker.info

            # Extract analyst price target information
            price_targets = {
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "target_high_price": info.get("targetHighPrice"),
                "target_low_price": info.get("targetLowPrice"),
                "target_mean_price": info.get("targetMeanPrice"),
                "target_median_price": info.get("targetMedianPrice"),
                "recommendation_mean": info.get("recommendationMean"),
                "recommendation_key": info.get("recommendationKey"),
                "number_of_analyst_opinions": info.get("numberOfAnalystOpinions"),
            }

            # Check if any target data is available
            if all(v is None for k, v in price_targets.items() if k != "current_price"):
                raise DataNotAvailableError("analyst price targets", symbol)

            result = {
                "symbol": symbol,
                "price_targets": price_targets,
            }

            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            if isinstance(e, (DataNotAvailableError, TickerNotFoundError)):
                raise
            raise YFinanceAPIError(str(e), symbol)
