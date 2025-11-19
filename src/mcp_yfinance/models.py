"""Data models and types for MCP Yahoo Finance server.

This module contains all Enums, type aliases, and Pydantic models used
throughout the MCP Yahoo Finance server for type safety and data validation.
"""

from enum import Enum
from typing import Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Enums (inherit from str for JSON serialization)

class Period(str, Enum):
    """Valid period values for historical data requests."""

    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YEAR_TO_DATE = "ytd"
    MAX = "max"


class Interval(str, Enum):
    """Valid interval values for historical data requests."""

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
    """Valid frequency values for financial statements."""

    YEARLY = "yearly"
    QUARTERLY = "quarterly"


class HolderType(str, Enum):
    """Valid holder information types."""

    MAJOR_HOLDERS = "major_holders"
    INSTITUTIONAL_HOLDERS = "institutional_holders"
    MUTUALFUND_HOLDERS = "mutualfund_holders"
    INSIDER_TRANSACTIONS = "insider_transactions"
    INSIDER_PURCHASES = "insider_purchases"
    INSIDER_ROSTER_HOLDERS = "insider_roster_holders"


class OptionType(str, Enum):
    """Valid option chain types."""

    CALLS = "calls"
    PUTS = "puts"
    BOTH = "both"


class RecommendationType(str, Enum):
    """Valid recommendation information types."""

    RECOMMENDATIONS = "recommendations"
    RECOMMENDATIONS_SUMMARY = "recommendations_summary"
    UPGRADES_DOWNGRADES = "upgrades_downgrades"


# Type aliases for Literal types

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
    "recommendations",
    "recommendations_summary",
    "upgrades_downgrades",
]


# Pydantic Models

class Quote(BaseModel):
    """Real-time stock quote information.

    Attributes:
        symbol: Stock ticker symbol
        price: Current stock price
        currency: Price currency (e.g., 'USD', 'BRL')
        timestamp: Quote timestamp
        volume: Trading volume
        market_cap: Market capitalization (optional)
    """

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    symbol: str
    price: float
    currency: str | None = None
    timestamp: datetime | None = None
    volume: int | None = None
    market_cap: float | None = None


class Dividend(BaseModel):
    """Dividend payment information.

    Attributes:
        date: Dividend payment date
        amount: Dividend amount per share
    """

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    date: datetime
    amount: float


class StockAction(BaseModel):
    """Stock action (split, dividend, capital gain) information.

    Attributes:
        date: Action date
        action_type: Type of action (e.g., 'Dividends', 'Stock Splits', 'Capital Gains')
        value: Action value
    """

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    date: datetime
    action_type: str
    value: float


class HistoricalDataPoint(BaseModel):
    """Single historical price data point.

    Attributes:
        date: Trading date
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
        adj_close: Adjusted closing price (optional)
    """

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float | None = None


class OptionContract(BaseModel):
    """Option contract information.

    Attributes:
        contract_symbol: Option contract identifier
        strike: Strike price
        expiration: Expiration date
        option_type: 'call' or 'put'
        last_price: Last traded price
        bid: Bid price
        ask: Ask price
        volume: Trading volume
        open_interest: Open interest
        implied_volatility: Implied volatility (optional)
    """

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    contract_symbol: str
    strike: float
    expiration: datetime
    option_type: str
    last_price: float
    bid: float
    ask: float
    volume: int | None = None
    open_interest: int | None = None
    implied_volatility: float | None = None


class NewsArticle(BaseModel):
    """News article information.

    Attributes:
        title: Article title
        publisher: Publisher name
        link: Article URL
        published_at: Publication timestamp
        thumbnail: Thumbnail URL (optional)
        summary: Article summary (optional)
    """

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    title: str
    publisher: str
    link: str
    published_at: datetime | None = None
    thumbnail: str | None = None
    summary: str | None = None


class Recommendation(BaseModel):
    """Analyst recommendation information.

    Attributes:
        date: Recommendation date
        firm: Analyst firm name
        to_grade: New recommendation grade
        from_grade: Previous recommendation grade (optional)
        action: Recommendation action (e.g., 'upgrade', 'downgrade', 'init')
    """

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    date: datetime
    firm: str
    to_grade: str
    from_grade: str | None = None
    action: str | None = None
