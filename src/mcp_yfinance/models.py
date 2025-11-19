"""Data models and type definitions for MCP Yahoo Finance.

This module contains all Pydantic models, Enums, and type aliases used
throughout the MCP Yahoo Finance server.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================


class Period(str, Enum):
    """Valid time periods for historical data queries.

    Attributes:
        ONE_DAY: One day of data
        FIVE_DAYS: Five days of data
        ONE_MONTH: One month of data
        THREE_MONTHS: Three months of data
        SIX_MONTHS: Six months of data
        ONE_YEAR: One year of data
        TWO_YEARS: Two years of data
        FIVE_YEARS: Five years of data
        TEN_YEARS: Ten years of data
        YTD: Year to date
        MAX: Maximum available data
    """

    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YTD = "ytd"
    MAX = "max"


class Interval(str, Enum):
    """Valid intervals for historical data queries.

    Attributes:
        ONE_MINUTE: One minute intervals
        TWO_MINUTES: Two minute intervals
        FIVE_MINUTES: Five minute intervals
        FIFTEEN_MINUTES: Fifteen minute intervals
        THIRTY_MINUTES: Thirty minute intervals
        SIXTY_MINUTES: Sixty minute intervals
        NINETY_MINUTES: Ninety minute intervals
        ONE_HOUR: One hour intervals
        ONE_DAY: One day intervals
        FIVE_DAYS: Five day intervals
        ONE_WEEK: One week intervals
        ONE_MONTH: One month intervals
        THREE_MONTHS: Three month intervals
    """

    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


class Frequency(str, Enum):
    """Valid frequencies for financial statements.

    Attributes:
        YEARLY: Annual financial statements
        QUARTERLY: Quarterly financial statements
    """

    YEARLY = "yearly"
    QUARTERLY = "quarterly"


class HolderType(str, Enum):
    """Types of holder information available.

    Attributes:
        MAJOR_HOLDERS: Major shareholders summary
        INSTITUTIONAL_HOLDERS: Institutional holders details
        MUTUALFUND_HOLDERS: Mutual fund holders details
        INSIDER_TRANSACTIONS: Insider transaction history
        INSIDER_PURCHASES: Insider purchase history
        INSIDER_ROSTER_HOLDERS: Insider roster information
    """

    MAJOR_HOLDERS = "major_holders"
    INSTITUTIONAL_HOLDERS = "institutional_holders"
    MUTUALFUND_HOLDERS = "mutualfund_holders"
    INSIDER_TRANSACTIONS = "insider_transactions"
    INSIDER_PURCHASES = "insider_purchases"
    INSIDER_ROSTER_HOLDERS = "insider_roster_holders"


class OptionType(str, Enum):
    """Types of options contracts.

    Attributes:
        CALLS: Call options only
        PUTS: Put options only
        BOTH: Both calls and puts
    """

    CALLS = "calls"
    PUTS = "puts"
    BOTH = "both"


class RecommendationType(str, Enum):
    """Types of recommendation data available.

    Attributes:
        RECOMMENDATIONS: Analyst recommendations (upgrade/downgrade)
        RECOMMENDATIONS_SUMMARY: Summary of recommendations by rating
        UPGRADES_DOWNGRADES: Detailed upgrade/downgrade history
    """

    RECOMMENDATIONS = "recommendations"
    RECOMMENDATIONS_SUMMARY = "recommendations_summary"
    UPGRADES_DOWNGRADES = "upgrades_downgrades"


# ============================================================================
# Type Aliases
# ============================================================================

PeriodType = Literal[
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
]

IntervalType = Literal[
    "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"
]

FrequencyType = Literal["yearly", "quarterly"]

HolderInfoType = Literal[
    "major_holders",
    "institutional_holders",
    "mutualfund_holders",
    "insider_transactions",
    "insider_purchases",
    "insider_roster_holders",
]

OptionChainType = Literal["calls", "puts", "both"]

RecommendationInfoType = Literal[
    "recommendations", "recommendations_summary", "upgrades_downgrades"
]


# ============================================================================
# Pydantic Models
# ============================================================================


class Quote(BaseModel):
    """Real-time stock quote data.

    Attributes:
        symbol: Stock ticker symbol
        price: Current stock price
        change: Price change from previous close
        percent_change: Percentage change from previous close
        volume: Trading volume
        market_cap: Market capitalization
        timestamp: Quote timestamp
    """

    symbol: str
    price: float
    change: float | None = None
    percent_change: float | None = None
    volume: int | None = None
    market_cap: float | None = None
    timestamp: datetime | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Dividend(BaseModel):
    """Dividend payment record.

    Attributes:
        date: Payment date
        amount: Dividend amount per share
    """

    date: datetime
    amount: float

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StockAction(BaseModel):
    """Stock action event (split, dividend, etc.).

    Attributes:
        date: Action date
        action_type: Type of action (e.g., 'Dividend', 'Stock Split')
        value: Action value (split ratio or dividend amount)
    """

    date: datetime
    action_type: str
    value: float

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HistoricalDataPoint(BaseModel):
    """Single point of historical price data.

    Attributes:
        date: Data point date
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
        adj_close: Adjusted closing price
    """

    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OptionContract(BaseModel):
    """Options contract details.

    Attributes:
        contract_symbol: Option contract symbol
        strike: Strike price
        last_price: Last traded price
        bid: Bid price
        ask: Ask price
        change: Price change
        percent_change: Percentage change
        volume: Trading volume
        open_interest: Open interest
        implied_volatility: Implied volatility
        in_the_money: Whether option is in the money
        expiration: Expiration date
        last_trade_date: Last trade date
    """

    contract_symbol: str
    strike: float
    last_price: float
    bid: float
    ask: float
    change: float | None = None
    percent_change: float | None = None
    volume: int | None = None
    open_interest: int | None = None
    implied_volatility: float | None = None
    in_the_money: bool | None = None
    expiration: datetime | None = None
    last_trade_date: datetime | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NewsArticle(BaseModel):
    """News article metadata.

    Attributes:
        title: Article title
        publisher: Publisher name
        link: Article URL
        published: Publication timestamp
        summary: Article summary/description
        thumbnail: Thumbnail image URL
    """

    title: str
    publisher: str
    link: str
    published: datetime
    summary: str | None = None
    thumbnail: str | None = None

    @field_validator("link", "thumbnail")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        """Validate URL fields.

        Args:
            v: URL string to validate

        Returns:
            Validated URL or None
        """
        if v and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Recommendation(BaseModel):
    """Analyst recommendation record.

    Attributes:
        date: Recommendation date
        firm: Analyst firm name
        to_grade: New recommendation grade
        from_grade: Previous recommendation grade
        action: Recommendation action (upgrade/downgrade/init/maintain)
    """

    date: datetime
    firm: str
    to_grade: str | None = None
    from_grade: str | None = None
    action: str | None = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
