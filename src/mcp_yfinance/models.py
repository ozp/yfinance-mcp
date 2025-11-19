"""Data models for MCP Yahoo Finance Server.

This module defines all Enums, type aliases, and Pydantic models used
throughout the MCP Yahoo Finance server implementation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================


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
    """Valid interval values for historical data."""

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
    """Frequency for financial statements."""

    YEARLY = "yearly"
    QUARTERLY = "quarterly"


class HolderType(str, Enum):
    """Type of holder information to retrieve."""

    MAJOR = "major_holders"
    INSTITUTIONAL = "institutional_holders"
    MUTUAL_FUND = "mutualfund_holders"
    INSIDER_TRANSACTIONS = "insider_transactions"
    INSIDER_PURCHASES = "insider_purchases"
    INSIDER_ROSTER = "insider_roster_holders"


class OptionType(str, Enum):
    """Type of option chain to retrieve."""

    CALLS = "calls"
    PUTS = "puts"
    BOTH = "both"


class RecommendationType(str, Enum):
    """Type of recommendation information."""

    RECOMMENDATIONS = "recommendations"
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

RecommendationInfoType = Literal["recommendations", "upgrades_downgrades"]


# ============================================================================
# Pydantic Models
# ============================================================================


class Quote(BaseModel):
    """Real-time stock quote information.

    Attributes:
        symbol: Stock ticker symbol
        price: Current stock price
        currency: Currency of the price
        timestamp: Time of the quote
        volume: Trading volume
        market_cap: Market capitalization
    """

    symbol: str = Field(..., description="Stock ticker symbol")
    price: float = Field(..., description="Current stock price")
    currency: str | None = Field(None, description="Currency of the price")
    timestamp: datetime | None = Field(None, description="Time of the quote")
    volume: int | None = Field(None, description="Trading volume")
    market_cap: float | None = Field(None, description="Market capitalization")

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class Dividend(BaseModel):
    """Dividend payment information.

    Attributes:
        date: Payment date
        amount: Dividend amount per share
    """

    date: str = Field(..., description="Payment date (ISO format)")
    amount: float = Field(..., description="Dividend amount per share")


class StockAction(BaseModel):
    """Stock corporate action (split or dividend).

    Attributes:
        date: Action date
        action_type: Type of action (split or dividend)
        value: Action value/ratio
    """

    date: str = Field(..., description="Action date (ISO format)")
    action_type: str = Field(..., description="Type of action")
    value: float = Field(..., description="Action value or ratio")


class HistoricalDataPoint(BaseModel):
    """Single historical price data point.

    Attributes:
        date: Trading date
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
        adj_close: Adjusted closing price
    """

    date: str = Field(..., description="Trading date (ISO format)")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    adj_close: float | None = Field(None, description="Adjusted closing price")


class OptionContract(BaseModel):
    """Option contract details.

    Attributes:
        contract_symbol: Option contract identifier
        strike: Strike price
        last_price: Last traded price
        bid: Bid price
        ask: Ask price
        volume: Trading volume
        open_interest: Open interest
        implied_volatility: Implied volatility
    """

    contract_symbol: str = Field(..., description="Option contract identifier")
    strike: float = Field(..., description="Strike price")
    last_price: float | None = Field(None, description="Last traded price")
    bid: float | None = Field(None, description="Bid price")
    ask: float | None = Field(None, description="Ask price")
    volume: int | None = Field(None, description="Trading volume")
    open_interest: int | None = Field(None, description="Open interest")
    implied_volatility: float | None = Field(None, description="Implied volatility")


class NewsArticle(BaseModel):
    """News article information.

    Attributes:
        title: Article title
        publisher: News publisher
        link: Article URL
        publish_time: Publication timestamp
    """

    title: str = Field(..., description="Article title")
    publisher: str | None = Field(None, description="News publisher")
    link: str | None = Field(None, description="Article URL")
    publish_time: datetime | None = Field(None, description="Publication timestamp")

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class Recommendation(BaseModel):
    """Analyst recommendation.

    Attributes:
        date: Recommendation date
        firm: Analyst firm name
        to_grade: New rating
        from_grade: Previous rating
        action: Recommendation action
    """

    date: str = Field(..., description="Recommendation date")
    firm: str | None = Field(None, description="Analyst firm name")
    to_grade: str | None = Field(None, description="New rating")
    from_grade: str | None = Field(None, description="Previous rating")
    action: str | None = Field(None, description="Recommendation action")
