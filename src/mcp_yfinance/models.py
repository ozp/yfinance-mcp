"""Data models and type definitions for MCP Yahoo Finance.

This module contains Pydantic models and Enums used throughout the application.
All models support JSON serialization for MCP protocol compatibility.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


# Type aliases for Literal types
PeriodType = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
IntervalType = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
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


class Period(str, Enum):
    """Valid time periods for historical data queries."""

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
    """Valid time intervals for historical data."""

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
    """Valid frequencies for financial statements."""

    YEARLY = "yearly"
    QUARTERLY = "quarterly"


class HolderType(str, Enum):
    """Types of holder information available."""

    MAJOR_HOLDERS = "major_holders"
    INSTITUTIONAL_HOLDERS = "institutional_holders"
    MUTUALFUND_HOLDERS = "mutualfund_holders"
    INSIDER_TRANSACTIONS = "insider_transactions"
    INSIDER_PURCHASES = "insider_purchases"
    INSIDER_ROSTER_HOLDERS = "insider_roster_holders"


class OptionType(str, Enum):
    """Types of option contracts."""

    CALLS = "calls"
    PUTS = "puts"
    BOTH = "both"


class RecommendationType(str, Enum):
    """Types of analyst recommendations."""

    RECOMMENDATIONS = "recommendations"
    UPGRADES_DOWNGRADES = "upgrades_downgrades"


class Quote(BaseModel):
    """Stock quote data model."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    symbol: str = Field(..., description="Stock ticker symbol")
    price: float = Field(..., description="Current stock price")
    currency: Optional[str] = Field(None, description="Currency code")
    timestamp: Optional[datetime] = Field(None, description="Quote timestamp")


class Dividend(BaseModel):
    """Dividend payment data model."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    date: datetime = Field(..., description="Dividend payment date")
    amount: float = Field(..., description="Dividend amount per share")


class StockAction(BaseModel):
    """Stock corporate action data model."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    date: datetime = Field(..., description="Action date")
    action_type: str = Field(..., description="Type of action (split, dividend, etc.)")
    value: float = Field(..., description="Action value")


class HistoricalDataPoint(BaseModel):
    """Historical price data point."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    date: datetime = Field(..., description="Data point date")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    adj_close: Optional[float] = Field(None, description="Adjusted closing price")


class OptionContract(BaseModel):
    """Option contract data model."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    contract_symbol: str = Field(..., description="Option contract symbol")
    strike: float = Field(..., description="Strike price")
    last_price: float = Field(..., description="Last traded price")
    bid: Optional[float] = Field(None, description="Bid price")
    ask: Optional[float] = Field(None, description="Ask price")
    volume: Optional[int] = Field(None, description="Trading volume")
    open_interest: Optional[int] = Field(None, description="Open interest")
    implied_volatility: Optional[float] = Field(None, description="Implied volatility")
    expiration_date: datetime = Field(..., description="Expiration date")
    option_type: str = Field(..., description="Option type (call/put)")


class NewsArticle(BaseModel):
    """News article data model."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    title: str = Field(..., description="Article title")
    publisher: str = Field(..., description="Publisher name")
    link: str = Field(..., description="Article URL")
    published_date: Optional[datetime] = Field(None, description="Publication date")
    thumbnail: Optional[str] = Field(None, description="Thumbnail image URL")


class Recommendation(BaseModel):
    """Analyst recommendation data model."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    date: datetime = Field(..., description="Recommendation date")
    firm: str = Field(..., description="Analyst firm name")
    action: str = Field(..., description="Recommendation action")
    rating_before: Optional[str] = Field(None, description="Previous rating")
    rating_after: Optional[str] = Field(None, description="New rating")
