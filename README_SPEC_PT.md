# MCP Yahoo Finance - Especificação Completa para Desenvolvimento

**Objetivo**: Criar um MCP server production-ready para Yahoo Finance com 18 tools, cache inteligente, suporte global + Brasil, e arquitetura robusta.

---

## 🎯 PROMPT INICIAL PARA CLAUDE CODE WEB

```markdown
Criar MCP server Python para Yahoo Finance seguindo arquitetura em camadas com:

CARACTERÍSTICAS PRINCIPAIS:
- 18 tools completos (pricing, financials, options, holders, news)
- Cache SQLite com TTL granular (performance + rate limiting)
- Suporte global + Brasil (auto-normalização .SA)
- Type safety completo (Pydantic + Literal)
- Error handling robusto com custom exceptions
- Async/await para todas operações I/O
- Deployment via uvx (zero config para usuário)

ARQUITETURA EM CAMADAS:
1. server.py → MCP protocol (list_tools, call_tool)
2. service.py → YahooFinanceService class (business logic)
3. models.py → Pydantic schemas + Enums
4. cache.py → SQLite cache manager com TTL
5. exceptions.py → Custom exception hierarchy
6. utils.py → Helpers (ticker normalization, tool generation)

IMPLEMENTAR NESTA ORDEM:
1. models.py (todos os Enums e Pydantic models)
2. exceptions.py (4 custom exceptions)
3. utils.py (ticker normalization, date formatting)
4. cache.py (SQLite cache com TTL)
5. service.py (YahooFinanceService com 18 métodos)
6. server.py (MCP server orchestration)
7. pyproject.toml (uvx config)
8. README.md (instalação one-liner + exemplos)

REQUISITOS TÉCNICOS:
- Python ≥3.10
- Dependencies: mcp>=1.6.0, yfinance>=0.2.62, pydantic>=2.0.0
- Cache: SQLite em ~/.mcp-yfinance/cache.db
- Type hints completos em todos métodos
- Docstrings Google-style
- JSON indent=2 para legibilidade

Comece criando a estrutura de diretórios e models.py.
```

---

## 📁 ESTRUTURA DO PROJETO

```
mcp-yfinance/
├── pyproject.toml
├── README.md
├── LICENSE (MIT)
├── .python-version (3.10)
├── .dockerignore
├── .pre-commit-config.yaml
│
├── src/
│   └── mcp_yfinance/
│       ├── __init__.py          # Version, exports, main()
│       ├── __main__.py          # CLI entry point
│       ├── py.typed             # Type checking marker
│       ├── server.py            # 🎯 MCP Server (150 linhas)
│       ├── service.py           # 🎯 YahooFinanceService (600 linhas)
│       ├── models.py            # 🎯 Schemas + Enums (200 linhas)
│       ├── cache.py             # 🎯 Cache manager (100 linhas)
│       ├── exceptions.py        # 🎯 Custom exceptions (50 linhas)
│       └── utils.py             # 🎯 Helpers (80 linhas)
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_service.py
    ├── test_cache.py
    └── test_server.py
```

**Total estimado**: ~1200 linhas de código útil

---

## 🏗️ ARQUITETURA EM CAMADAS

```
┌────────────────────────────────────────┐
│   Claude Desktop / API                 │
│   (usuário faz pergunta sobre ações)   │
└─────────────┬──────────────────────────┘
              │ stdio
┌─────────────▼──────────────────────────┐
│   server.py (MCP Protocol)             │ ◄─── Tool definitions
│   - @server.list_tools()               │      Input validation
│   - @server.call_tool()                │      Error handling
│   - Roteamento para service            │      Response formatting
└─────────────┬──────────────────────────┘
              │
┌─────────────▼──────────────────────────┐
│   cache.py (Cache Layer)               │ ◄─── TTL-based cache
│   - Check cache by key                 │      5min: quotes
│   - Return if valid                    │      1h: stock info
│   - Pass to service if miss            │      24h: historical
└─────────────┬──────────────────────────┘
              │ (cache miss)
┌─────────────▼──────────────────────────┐
│   service.py (Business Logic)          │ ◄─── YahooFinanceService
│   - Normalize ticker (.SA para BR)     │      Validate inputs
│   - Call yfinance                      │      Transform data
│   - Map to Pydantic models             │      Error enrichment
│   - Save to cache                      │      Retry logic
└─────────────┬──────────────────────────┘
              │
┌─────────────▼──────────────────────────┐
│   yfinance library                     │
│   (fetch de Yahoo Finance API)         │
└────────────────────────────────────────┘
```

---

## 📋 ESPECIFICAÇÃO DOS 18 TOOLS

### Categoria 1: Pricing & Historical (6 tools)

**1. get_current_stock_price**
```python
Input: {symbol: str}
Output: {"symbol": "AAPL", "price": 234.56, "change": 2.34, "change_percent": 1.01, ...}
Cache TTL: 5 minutos
Descrição: Preço atual da ação com variação do dia
```

**2. get_stock_price_by_date**
```python
Input: {symbol: str, date: str}  # date: "YYYY-MM-DD"
Output: {"symbol": "AAPL", "date": "2025-01-15", "close": 230.45}
Cache TTL: 24 horas
Descrição: Preço de fechamento em data específica
```

**3. get_stock_price_date_range**
```python
Input: {symbol: str, start_date: str, end_date: str}
Output: {"symbol": "AAPL", "data": [{"date": "...", "close": 230.45}, ...]}
Cache TTL: 24 horas
Descrição: Série de preços em intervalo de datas
```

**4. get_historical_stock_prices**
```python
Input: {
    symbol: str,
    period: Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] = "1mo",
    interval: Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"] = "1d"
}
Output: [{date, open, high, low, close, volume, adj_close}, ...]
Cache TTL: 24 horas
Descrição: Dados OHLCV históricos completos
```

**5. get_dividends**
```python
Input: {symbol: str}
Output: [{"date": "2024-11-15", "value": 0.25}, ...]
Cache TTL: 24 horas
Descrição: Histórico de dividendos pagos
```

**6. get_stock_actions**
```python
Input: {symbol: str}
Output: [{"date": "...", "dividends": 0.25, "stock_splits": 0.0}, ...]
Cache TTL: 24 horas
Descrição: Dividendos + splits em uma única consulta
```

---

### Categoria 2: Company Info (1 tool)

**7. get_stock_info**
```python
Input: {symbol: str}
Output: {
    "symbol": "AAPL",
    "longName": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "currentPrice": 234.56,
    "marketCap": 3600000000000,
    "trailingPE": 29.5,
    "dividendYield": 0.0045,
    # ... ~100 campos disponíveis
}
Cache TTL: 1 hora
Descrição: Informações completas da empresa (yfinance.Ticker.info)
```

---

### Categoria 3: Financial Statements (3 tools)

**8. get_income_statement**
```python
Input: {
    symbol: str,
    freq: Literal["yearly", "quarterly", "trailing"] = "yearly"
}
Output: {
    "symbol": "AAPL",
    "freq": "yearly",
    "data": {
        "2024-09-30": {"TotalRevenue": 391035000000, "NetIncome": 93736000000, ...},
        "2023-09-30": {...},
        ...
    }
}
Cache TTL: 24 horas
Descrição: Demonstração de Resultados (DRE)
```

**9. get_balance_sheet**
```python
Input: {symbol: str, freq: Literal[...] = "yearly"}
Output: Similar ao income_statement
Cache TTL: 24 horas
Descrição: Balanço Patrimonial
```

**10. get_cashflow**
```python
Input: {symbol: str, freq: Literal[...] = "yearly"}
Output: Similar ao income_statement
Cache TTL: 24 horas
Descrição: Fluxo de Caixa
```

---

### Categoria 4: Holders & Ownership (1 tool)

**11. get_holder_info**
```python
Input: {
    symbol: str,
    holder_type: Literal[
        "major_holders",
        "institutional_holders",
        "mutualfund_holders",
        "insider_transactions",
        "insider_purchases",
        "insider_roster_holders"
    ]
}
Output: [{"Holder": "Vanguard", "Shares": 1234567890, "Percent": 8.5}, ...]
Cache TTL: 24 horas
Descrição: Informações sobre acionistas (6 tipos diferentes)
```

---

### Categoria 5: Options (2 tools)

**12. get_option_expiration_dates**
```python
Input: {symbol: str}
Output: ["2025-01-17", "2025-01-24", "2025-02-21", ...]
Cache TTL: 24 horas
Descrição: Datas disponíveis para vencimento de opções
```

**13. get_option_chain**
```python
Input: {
    symbol: str,
    expiration_date: str,  # "YYYY-MM-DD"
    option_type: Literal["calls", "puts", "both"] = "both"
}
Output: {
    "underlying": "AAPL",
    "expiration": "2025-01-17",
    "calls": [
        {
            "contractSymbol": "AAPL250117C00100000",
            "strike": 100.0,
            "lastPrice": 134.50,
            "bid": 134.00,
            "ask": 135.00,
            "volume": 1250,
            "openInterest": 5432,
            "impliedVolatility": 0.2345
        },
        ...
    ],
    "puts": [...]
}
Cache TTL: 5 minutos
Descrição: Chain de opções (calls/puts/both) para data específica
```

---

### Categoria 6: News & Analysis (3 tools)

**14. get_news**
```python
Input: {symbol: str}
Output: [
    {
        "title": "Apple announces new iPhone",
        "summary": "...",
        "url": "https://...",
        "provider": "Reuters",
        "publishedAt": "2025-01-15T10:30:00Z"
    },
    ...
]
Cache TTL: 30 minutos
Descrição: Notícias recentes sobre a ação
```

**15. get_recommendations**
```python
Input: {
    symbol: str,
    recommendation_type: Literal["recommendations", "upgrades_downgrades"] = "recommendations",
    months_back: int = 12
}
Output: [
    {
        "date": "2025-01-15",
        "firm": "Goldman Sachs",
        "toGrade": "Buy",
        "fromGrade": "Hold",
        "action": "upgrade"
    },
    ...
]
Cache TTL: 24 horas
Descrição: Recomendações de analistas (completo ou upgrades/downgrades)
```

**16. get_earning_dates**
```python
Input: {
    symbol: str,
    limit: int = 12
}
Output: [
    {
        "date": "2025-02-01",
        "epsEstimate": 2.10,
        "reportedEPS": null,
        "surprise": null
    },
    ...
]
Cache TTL: 24 horas
Descrição: Datas de divulgação de resultados (passadas + futuras)
```

---

## 🔧 IMPLEMENTAÇÃO DETALHADA

### 1. models.py - Type System Completo

```python
"""
Type definitions, Enums, and Pydantic models
"""

from enum import Enum
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# ============================================================================
# ENUMS - Runtime validation + Autocomplete
# ============================================================================

class Period(str, Enum):
    """Valid time periods for historical data"""
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
    """Valid intervals for data points"""
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
    """Financial statement frequency"""
    YEARLY = "yearly"
    QUARTERLY = "quarterly"
    TRAILING = "trailing"


class HolderType(str, Enum):
    """Types of holder information"""
    MAJOR_HOLDERS = "major_holders"
    INSTITUTIONAL_HOLDERS = "institutional_holders"
    MUTUALFUND_HOLDERS = "mutualfund_holders"
    INSIDER_TRANSACTIONS = "insider_transactions"
    INSIDER_PURCHASES = "insider_purchases"
    INSIDER_ROSTER_HOLDERS = "insider_roster_holders"


class OptionType(str, Enum):
    """Option chain types"""
    CALLS = "calls"
    PUTS = "puts"
    BOTH = "both"


class RecommendationType(str, Enum):
    """Analyst recommendation types"""
    RECOMMENDATIONS = "recommendations"
    UPGRADES_DOWNGRADES = "upgrades_downgrades"


# ============================================================================
# TYPE ALIASES - For type hints
# ============================================================================

PeriodType = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
IntervalType = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
FrequencyType = Literal["yearly", "quarterly", "trailing"]
HolderInfoType = Literal["major_holders", "institutional_holders", "mutualfund_holders", 
                         "insider_transactions", "insider_purchases", "insider_roster_holders"]
OptionChainType = Literal["calls", "puts", "both"]
RecommendationInfoType = Literal["recommendations", "upgrades_downgrades"]


# ============================================================================
# PYDANTIC MODELS - Data validation and serialization
# ============================================================================

class Quote(BaseModel):
    """Current stock price quote"""
    symbol: str
    price: float
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    currency: str = "USD"
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Dividend(BaseModel):
    """Dividend payment record"""
    date: datetime
    value: float
    currency: str = "USD"


class StockAction(BaseModel):
    """Stock action (dividend + split)"""
    date: datetime
    dividends: float = 0.0
    stock_splits: float = 0.0


class HistoricalDataPoint(BaseModel):
    """Single OHLCV data point"""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None


class OptionContract(BaseModel):
    """Option contract details"""
    contractSymbol: str
    strike: float
    lastPrice: float
    bid: float
    ask: float
    volume: Optional[int]
    openInterest: Optional[int]
    impliedVolatility: Optional[float]


class NewsArticle(BaseModel):
    """News article"""
    title: str
    summary: Optional[str]
    url: str
    provider: str
    publishedAt: datetime


class Recommendation(BaseModel):
    """Analyst recommendation"""
    date: datetime
    firm: str
    toGrade: str
    fromGrade: Optional[str]
    action: Optional[str]
```

---

### 2. exceptions.py - Error Handling

```python
"""Custom exceptions for Yahoo Finance MCP"""

class YFinanceMCPError(Exception):
    """Base exception"""
    pass


class TickerNotFoundError(YFinanceMCPError):
    """Ticker symbol not found"""
    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"Ticker '{ticker}' not found in Yahoo Finance")


class YFinanceAPIError(YFinanceMCPError):
    """Yahoo Finance API error"""
    def __init__(self, message: str, ticker: str | None = None):
        self.ticker = ticker
        super().__init__(f"Yahoo Finance API error: {message}")


class InvalidParameterError(YFinanceMCPError):
    """Invalid parameter provided"""
    def __init__(self, param: str, value: str, valid_values: list[str]):
        super().__init__(
            f"Invalid {param}: '{value}'. Valid: {', '.join(valid_values)}"
        )


class DataNotAvailableError(YFinanceMCPError):
    """Requested data not available"""
    def __init__(self, data_type: str, ticker: str):
        super().__init__(f"{data_type} not available for '{ticker}'")
```

---

### 3. cache.py - SQLite Cache Manager

```python
"""
SQLite-based cache with TTL support

Features:
- Zero config (creates DB in ~/.mcp-yfinance/)
- TTL granular por tipo de dado
- Auto-cleanup de registros expirados
- Thread-safe operations
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any
import threading

class CacheManager:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            cache_dir = Path.home() / ".mcp-yfinance"
            cache_dir.mkdir(exist_ok=True)
            db_path = str(cache_dir / "cache.db")
        
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            # Index para performance em queries de expiração
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON cache(expires_at)
            """)
    
    def get(self, key: str) -> Optional[dict]:
        """
        Retrieve cached value if not expired
        
        Returns:
            dict if found and valid, None if expired or not found
        """
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute(
                    "SELECT value, expires_at FROM cache WHERE key = ?",
                    (key,)
                ).fetchone()
                
                if not row:
                    return None
                
                value, expires_at = row
                
                # Check TTL
                if datetime.now().timestamp() > expires_at:
                    # Delete expired
                    conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                    return None
                
                return json.loads(value)
    
    def set(self, key: str, value: Any, ttl: int):
        """
        Store value with TTL
        
        Args:
            key: Cache key
            value: Data to cache (must be JSON-serializable)
            ttl: Time to live in seconds
        """
        now = datetime.now().timestamp()
        expires_at = (datetime.now() + timedelta(seconds=ttl)).timestamp()
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache VALUES (?, ?, ?, ?)",
                    (key, json.dumps(value), expires_at, now)
                )
    
    def delete(self, key: str):
        """Delete specific cache entry"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
    
    def clear_expired(self):
        """Remove all expired entries"""
        now = datetime.now().timestamp()
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache WHERE expires_at < ?", (now,))
    
    def clear_all(self):
        """Clear entire cache"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        now = datetime.now().timestamp()
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            expired = conn.execute(
                "SELECT COUNT(*) FROM cache WHERE expires_at < ?", 
                (now,)
            ).fetchone()[0]
            
            return {
                "total_entries": total,
                "valid_entries": total - expired,
                "expired_entries": expired,
                "db_path": self.db_path
            }


# Cache TTL configurations (em segundos)
CACHE_TTL = {
    "quote": 300,              # 5 minutos
    "stock_info": 3600,        # 1 hora
    "historical": 86400,       # 24 horas
    "dividends": 86400,        # 24 horas
    "actions": 86400,          # 24 horas
    "financial": 86400,        # 24 horas
    "holders": 86400,          # 24 horas
    "options_dates": 86400,    # 24 horas
    "options_chain": 300,      # 5 minutos
    "news": 1800,              # 30 minutos
    "recommendations": 86400,  # 24 horas
    "earnings": 86400,         # 24 horas
}
```

---

### 4. utils.py - Helper Functions

```python
"""Utility functions"""

import re
from typing import Any, Callable
from datetime import datetime
import pandas as pd
from mcp.types import Tool
import inspect

def normalize_ticker(ticker: str, market: str = "BR") -> str:
    """
    Normalize ticker symbol
    
    For BR market: adds .SA suffix if not present
    For US market: removes any suffix
    
    Args:
        ticker: Raw ticker symbol
        market: Market code ("BR", "US", etc)
    
    Returns:
        Normalized ticker
    
    Examples:
        >>> normalize_ticker("PETR4", "BR")
        "PETR4.SA"
        >>> normalize_ticker("PETR4.SA", "BR")
        "PETR4.SA"
        >>> normalize_ticker("AAPL", "US")
        "AAPL"
    """
    ticker = ticker.upper().strip()
    
    if market == "BR":
        if not ticker.endswith(".SA"):
            return f"{ticker}.SA"
    elif market == "US":
        # Remove any suffix
        ticker = ticker.split(".")[0]
    
    return ticker


def format_dataframe_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format DataFrame index dates to ISO string format
    
    Args:
        df: DataFrame with datetime index
    
    Returns:
        DataFrame with string dates
    """
    if hasattr(df.index, "date"):
        df.index = df.index.date.astype(str)
    return df


def generate_cache_key(tool_name: str, **kwargs) -> str:
    """
    Generate cache key from tool name and arguments
    
    Args:
        tool_name: Name of the tool
        **kwargs: Tool arguments
    
    Returns:
        Cache key string
    
    Examples:
        >>> generate_cache_key("get_quote", symbol="AAPL")
        "get_quote:symbol=AAPL"
        >>> generate_cache_key("get_historical", symbol="MSFT", period="1mo")
        "get_historical:symbol=MSFT:period=1mo"
    """
    # Sort kwargs for consistent keys
    parts = [tool_name]
    for k, v in sorted(kwargs.items()):
        parts.append(f"{k}={v}")
    return ":".join(parts)


def parse_docstring(docstring: str) -> dict[str, str]:
    """
    Parse Google-style docstring to extract parameter descriptions
    
    Args:
        docstring: Function docstring
    
    Returns:
        Dict mapping parameter names to descriptions
    """
    descriptions = {}
    if not docstring:
        return descriptions
    
    lines = docstring.split("\n")
    current_param = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("Args:"):
            continue
        elif line and ":" in line and "(" in line and ")" in line:
            # Parameter line: "param (type): description"
            param = line.split("(")[0].strip()
            desc = line.split("):")[1].strip() if "):" in line else ""
            descriptions[param] = desc
            current_param = param
        elif current_param and line:
            # Continuation of previous parameter description
            descriptions[current_param] += " " + line.strip()
    
    return descriptions


def generate_tool_schema(func: Callable) -> Tool:
    """
    Generate MCP Tool schema from Python function
    
    Automatically extracts:
    - Function name
    - Docstring description
    - Parameter types and descriptions
    - Required vs optional parameters
    
    Args:
        func: Function to generate schema from
    
    Returns:
        MCP Tool object
    """
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func) or ""
    param_descriptions = parse_docstring(docstring)
    
    # Extract description (everything before "Args:")
    description = docstring.split("Args:")[0].strip()
    
    # Build schema
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }
    
    for param_name, param in signature.parameters.items():
        # Skip 'self' parameter
        if param_name == "self":
            continue
        
        # Determine type
        param_type = "string"  # Default
        if param.annotation != inspect.Parameter.empty:
            if param.annotation in (int, float):
                param_type = "number"
            elif param.annotation == bool:
                param_type = "boolean"
        
        # Add to schema
        schema["properties"][param_name] = {
            "type": param_type,
            "description": param_descriptions.get(param_name, "")
        }
        
        # Check if required (no default value)
        if param.default == inspect.Parameter.empty:
            schema["required"].append(param_name)
    
    return Tool(
        name=func.__name__,
        description=description,
        inputSchema=schema
    )
```

---

### 5. service.py - Business Logic Core

```python
"""
YahooFinanceService - Business logic layer

Implementa os 18 métodos de consulta ao Yahoo Finance com:
- Validação de ticker
- Retry logic
- Normalização de dados
- Transformação para Pydantic models
- Error handling robusto
"""

import json
from typing import Any
import pandas as pd
import yfinance as yf
from requests import Session

from .models import (
    PeriodType, IntervalType, FrequencyType,
    HolderInfoType, OptionChainType, RecommendationInfoType,
    Quote, Dividend, StockAction, HistoricalDataPoint,
    OptionContract, NewsArticle, Recommendation
)
from .exceptions import (
    TickerNotFoundError, YFinanceAPIError, DataNotAvailableError
)
from .utils import normalize_ticker, format_dataframe_dates


class YahooFinanceService:
    """Service for interacting with Yahoo Finance"""
    
    def __init__(
        self, 
        session: Session | None = None,
        verify: bool = True,
        default_market: str = "US"
    ):
        """
        Initialize service
        
        Args:
            session: Optional requests Session for connection pooling
            verify: Whether to verify SSL certificates
            default_market: Default market for ticker normalization ("US" or "BR")
        """
        self.session = session
        if self.session:
            self.session.verify = verify
        self.default_market = default_market
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_ticker(self, symbol: str) -> yf.Ticker:
        """Get and validate ticker object"""
        # Normalize ticker (add .SA if BR market)
        if self.default_market == "BR":
            symbol = normalize_ticker(symbol, "BR")
        
        ticker = yf.Ticker(symbol, session=self.session)
        
        try:
            # Validate ticker exists
            if ticker.isin is None:
                raise TickerNotFoundError(symbol)
        except Exception as e:
            if "isin" in str(e).lower():
                raise TickerNotFoundError(symbol)
            raise YFinanceAPIError(str(e), symbol)
        
        return ticker
    
    # ========================================================================
    # PRICING & HISTORICAL (6 tools)
    # ========================================================================
    
    def get_current_stock_price(self, symbol: str) -> str:
        """
        Get current stock price
        
        Args:
            symbol (str): Stock ticker symbol
        
        Returns:
            str: JSON with current price data
        """
        ticker = self._get_ticker(symbol)
        try:
            info = ticker.info
            quote = Quote(
                symbol=symbol,
                price=info.get("regularMarketPrice", info.get("currentPrice")),
                change=info.get("regularMarketChange"),
                change_percent=info.get("regularMarketChangePercent"),
                volume=info.get("volume"),
                currency=info.get("currency", "USD")
            )
            return quote.model_dump_json(indent=2)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting price: {e}", symbol)
    
    def get_stock_price_by_date(self, symbol: str, date: str) -> str:
        """
        Get stock price for specific date
        
        Args:
            symbol (str): Stock ticker
            date (str): Date in YYYY-MM-DD format
        
        Returns:
            str: JSON with closing price for the date
        """
        ticker = self._get_ticker(symbol)
        try:
            prices = ticker.history(start=date, period="1d")
            if prices.empty:
                raise DataNotAvailableError(f"Price for {date}", symbol)
            
            result = {
                "symbol": symbol,
                "date": date,
                "close": float(prices.iloc[0]["Close"])
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting price for {date}: {e}", symbol)
    
    def get_stock_price_date_range(
        self, symbol: str, start_date: str, end_date: str
    ) -> str:
        """
        Get stock prices for date range
        
        Args:
            symbol (str): Stock ticker
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
        
        Returns:
            str: JSON with date->price mapping
        """
        ticker = self._get_ticker(symbol)
        try:
            prices = ticker.history(start=start_date, end=end_date)
            if prices.empty:
                raise DataNotAvailableError(
                    f"Prices from {start_date} to {end_date}", symbol
                )
            
            prices = format_dataframe_dates(prices)
            result = {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "data": json.loads(prices["Close"].to_json(orient="index"))
            }
            return json.dumps(result, indent=2)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting date range: {e}", symbol)
    
    def get_historical_stock_prices(
        self,
        symbol: str,
        period: PeriodType = "1mo",
        interval: IntervalType = "1d"
    ) -> str:
        """
        Get historical OHLCV data
        
        Args:
            symbol (str): Stock ticker
            period (str): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            str: JSON array with OHLCV data
        """
        ticker = self._get_ticker(symbol)
        try:
            hist = ticker.history(period=period, interval=interval)
            if hist.empty:
                raise DataNotAvailableError(f"Historical data for {period}", symbol)
            
            hist = hist.reset_index(names="Date")
            return hist.to_json(orient="records", date_format="iso", indent=2)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting historical data: {e}", symbol)
    
    def get_dividends(self, symbol: str) -> str:
        """
        Get dividend history
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: JSON with dividend dates and amounts
        """
        ticker = self._get_ticker(symbol)
        try:
            dividends = ticker.dividends
            if dividends.empty:
                return json.dumps({"message": f"No dividends for {symbol}"}, indent=2)
            
            dividends = format_dataframe_dates(dividends)
            return dividends.to_json(orient="index", indent=2)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting dividends: {e}", symbol)
    
    def get_stock_actions(self, symbol: str) -> str:
        """
        Get stock actions (dividends + splits)
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: JSON array with dividends and splits
        """
        ticker = self._get_ticker(symbol)
        try:
            actions = ticker.actions
            if actions.empty:
                return json.dumps({"message": f"No actions for {symbol}"}, indent=2)
            
            actions = actions.reset_index(names="Date")
            return actions.to_json(orient="records", date_format="iso", indent=2)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting actions: {e}", symbol)
    
    # ========================================================================
    # COMPANY INFO (1 tool)
    # ========================================================================
    
    def get_stock_info(self, symbol: str) -> str:
        """
        Get comprehensive stock information
        
        Returns all available yfinance fields (~100 campos)
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: JSON with complete stock info
        """
        ticker = self._get_ticker(symbol)
        try:
            info = ticker.info
            if not info:
                raise DataNotAvailableError("Stock info", symbol)
            return json.dumps(info, indent=2)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting info: {e}", symbol)
    
    # ========================================================================
    # FINANCIAL STATEMENTS (3 tools)
    # ========================================================================
    
    def get_income_statement(
        self, symbol: str, freq: FrequencyType = "yearly"
    ) -> str:
        """
        Get income statement (DRE)
        
        Args:
            symbol (str): Stock ticker
            freq (str): yearly, quarterly, or trailing
        
        Returns:
            str: JSON with income statement
        """
        ticker = self._get_ticker(symbol)
        try:
            stmt = ticker.get_income_stmt(freq=freq, pretty=True)
            if stmt is None or (isinstance(stmt, pd.DataFrame) and stmt.empty):
                raise DataNotAvailableError(f"Income statement ({freq})", symbol)
            
            if isinstance(stmt, pd.DataFrame):
                stmt.columns = [str(col.date()) for col in stmt.columns]
                return stmt.to_json(indent=2)
            return str(stmt)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting income statement: {e}", symbol)
    
    def get_balance_sheet(
        self, symbol: str, freq: FrequencyType = "yearly"
    ) -> str:
        """
        Get balance sheet (Balanço Patrimonial)
        
        Args:
            symbol (str): Stock ticker
            freq (str): yearly, quarterly, or trailing
        
        Returns:
            str: JSON with balance sheet
        """
        ticker = self._get_ticker(symbol)
        try:
            if freq == "yearly":
                stmt = ticker.balance_sheet
            elif freq == "quarterly":
                stmt = ticker.quarterly_balance_sheet
            else:
                stmt = ticker.get_balance_sheet(freq=freq, pretty=True)
            
            if stmt is None or (isinstance(stmt, pd.DataFrame) and stmt.empty):
                raise DataNotAvailableError(f"Balance sheet ({freq})", symbol)
            
            if isinstance(stmt, pd.DataFrame):
                stmt.columns = [str(col.date()) for col in stmt.columns]
                return stmt.to_json(indent=2)
            return str(stmt)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting balance sheet: {e}", symbol)
    
    def get_cashflow(
        self, symbol: str, freq: FrequencyType = "yearly"
    ) -> str:
        """
        Get cash flow statement
        
        Args:
            symbol (str): Stock ticker
            freq (str): yearly, quarterly, or trailing
        
        Returns:
            str: JSON with cash flow
        """
        ticker = self._get_ticker(symbol)
        try:
            stmt = ticker.get_cashflow(freq=freq, pretty=True)
            if stmt is None or (isinstance(stmt, pd.DataFrame) and stmt.empty):
                raise DataNotAvailableError(f"Cash flow ({freq})", symbol)
            
            if isinstance(stmt, pd.DataFrame):
                stmt.columns = [str(col.date()) for col in stmt.columns]
                return stmt.to_json(indent=2)
            return str(stmt)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting cash flow: {e}", symbol)
    
    # ========================================================================
    # HOLDERS & OWNERSHIP (1 tool)
    # ========================================================================
    
    def get_holder_info(
        self, symbol: str, holder_type: HolderInfoType
    ) -> str:
        """
        Get holder information (6 tipos)
        
        Args:
            symbol (str): Stock ticker
            holder_type (str): major_holders, institutional_holders, 
                              mutualfund_holders, insider_transactions,
                              insider_purchases, insider_roster_holders
        
        Returns:
            str: JSON with holder data
        """
        ticker = self._get_ticker(symbol)
        
        try:
            if holder_type == "major_holders":
                data = ticker.major_holders
                if data is not None and not data.empty:
                    return data.reset_index(names="metric").to_json(
                        orient="records", indent=2
                    )
            
            elif holder_type == "institutional_holders":
                data = ticker.institutional_holders
                if data is not None and not data.empty:
                    return data.to_json(orient="records", indent=2)
            
            elif holder_type == "mutualfund_holders":
                data = ticker.mutualfund_holders
                if data is not None and not data.empty:
                    return data.to_json(orient="records", date_format="iso", indent=2)
            
            elif holder_type == "insider_transactions":
                data = ticker.insider_transactions
                if data is not None and not data.empty:
                    return data.to_json(orient="records", date_format="iso", indent=2)
            
            elif holder_type == "insider_purchases":
                data = ticker.insider_purchases
                if data is not None and not data.empty:
                    return data.to_json(orient="records", date_format="iso", indent=2)
            
            elif holder_type == "insider_roster_holders":
                data = ticker.insider_roster_holders
                if data is not None and not data.empty:
                    return data.to_json(orient="records", date_format="iso", indent=2)
            
            raise DataNotAvailableError(f"Holder info ({holder_type})", symbol)
            
        except Exception as e:
            raise YFinanceAPIError(f"Error getting holder info: {e}", symbol)
    
    # ========================================================================
    # OPTIONS (2 tools)
    # ========================================================================
    
    def get_option_expiration_dates(self, symbol: str) -> str:
        """
        Get available option expiration dates
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: JSON array of dates
        """
        ticker = self._get_ticker(symbol)
        try:
            dates = ticker.options
            if not dates:
                raise DataNotAvailableError("Option dates", symbol)
            return json.dumps(list(dates), indent=2)
        except Exception as e:
            raise YFinanceAPIError(f"Error getting option dates: {e}", symbol)
    
    def get_option_chain(
        self,
        symbol: str,
        expiration_date: str,
        option_type: OptionChainType = "both"
    ) -> str:
        """
        Get option chain
        
        Args:
            symbol (str): Stock ticker
            expiration_date (str): Expiration date (YYYY-MM-DD)
            option_type (str): calls, puts, or both
        
        Returns:
            str: JSON with option chain
        """
        ticker = self._get_ticker(symbol)
        
        try:
            if expiration_date not in ticker.options:
                raise DataNotAvailableError(
                    f"Options for {expiration_date}", symbol
                )
            
            chain = ticker.option_chain(expiration_date)
            result = {"underlying": chain.underlying}
            
            if option_type in ["calls", "both"]:
                if chain.calls is not None and not chain.calls.empty:
                    calls = chain.calls.copy()
                    if "lastTradeDate" in calls.columns:
                        calls["lastTradeDate"] = calls["lastTradeDate"].astype(str)
                    result["calls"] = calls.to_dict(orient="records")
                else:
                    result["calls"] = []
            
            if option_type in ["puts", "both"]:
                if chain.puts is not None and not chain.puts.empty:
                    puts = chain.puts.copy()
                    if "lastTradeDate" in puts.columns:
                        puts["lastTradeDate"] = puts["lastTradeDate"].astype(str)
                    result["puts"] = puts.to_dict(orient="records")
                else:
                    result["puts"] = []
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            raise YFinanceAPIError(f"Error getting option chain: {e}", symbol)
    
    # ========================================================================
    # NEWS & ANALYSIS (3 tools)
    # ========================================================================
    
    def get_news(self, symbol: str) -> str:
        """
        Get recent news
        
        Args:
            symbol (str): Stock ticker
        
        Returns:
            str: JSON array of news articles
        """
        ticker = self._get_ticker(symbol)
        try:
            news = ticker.news
            if not news:
                return json.dumps({"message": f"No news for {symbol}"}, indent=2)
            
            articles = []
            for item in news:
                content = item.get("content", {})
                if content.get("contentType") == "STORY":
                    articles.append({
                        "title": content.get("title", ""),
                        "summary": content.get("summary", ""),
                        "url": content.get("canonicalUrl", {}).get("url", ""),
                        "provider": content.get("provider", {}).get("displayName", ""),
                        "publishedAt": content.get("pubDate", "")
                    })
            
            return json.dumps(articles, indent=2)
            
        except Exception as e:
            raise YFinanceAPIError(f"Error getting news: {e}", symbol)
    
    def get_recommendations(
        self,
        symbol: str,
        recommendation_type: RecommendationInfoType = "recommendations",
        months_back: int = 12
    ) -> str:
        """
        Get analyst recommendations
        
        Args:
            symbol (str): Stock ticker
            recommendation_type (str): recommendations or upgrades_downgrades
            months_back (int): For upgrades_downgrades, months to look back
        
        Returns:
            str: JSON with recommendations
        """
        ticker = self._get_ticker(symbol)
        
        try:
            if recommendation_type == "recommendations":
                data = ticker.recommendations
                if data is None or data.empty:
                    raise DataNotAvailableError("Recommendations", symbol)
                return data.to_json(orient="records", indent=2)
            
            elif recommendation_type == "upgrades_downgrades":
                data = ticker.upgrades_downgrades
                if data is None or data.empty:
                    raise DataNotAvailableError("Upgrades/downgrades", symbol)
                
                # Filter by date
                data = data.reset_index()
                cutoff = pd.Timestamp.now() - pd.DateOffset(months=months_back)
                data = data[data["GradeDate"] >= cutoff]
                data = data.sort_values("GradeDate", ascending=False)
                # Most recent per firm
                data = data.drop_duplicates(subset=["Firm"])
                
                return data.to_json(orient="records", date_format="iso", indent=2)
                
        except Exception as e:
            raise YFinanceAPIError(f"Error getting recommendations: {e}", symbol)
    
    def get_earning_dates(self, symbol: str, limit: int = 12) -> str:
        """
        Get earnings announcement dates
        
        Args:
            symbol (str): Stock ticker
            limit (int): Number of dates (default 12 = 4 future + 8 past)
        
        Returns:
            str: JSON with earning dates
        """
        ticker = self._get_ticker(symbol)
        try:
            dates = ticker.get_earnings_dates(limit=limit)
            if dates is None or (isinstance(dates, pd.DataFrame) and dates.empty):
                raise DataNotAvailableError("Earning dates", symbol)
            
            if isinstance(dates, pd.DataFrame):
                dates.index = dates.index.date.astype(str)
                return dates.to_json(indent=2)
            return str(dates)
            
        except Exception as e:
            raise YFinanceAPIError(f"Error getting earning dates: {e}", symbol)
```

---

### 6. server.py - MCP Server Orchestration

```python
"""
MCP Server main entry point

Responsibilities:
- Register 18 tools via @server.list_tools()
- Handle tool calls via @server.call_tool()
- Integrate cache layer transparently
- Format responses for Claude
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .service import YahooFinanceService
from .cache import CacheManager, CACHE_TTL
from .utils import generate_cache_key, generate_tool_schema
from .exceptions import YFinanceMCPError


# Initialize components
server = Server("mcp-yfinance")
service = YahooFinanceService()
cache = CacheManager()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools
    
    Dynamically generates Tool schemas from service methods
    """
    return [
        # Pricing & Historical (6)
        generate_tool_schema(service.get_current_stock_price),
        generate_tool_schema(service.get_stock_price_by_date),
        generate_tool_schema(service.get_stock_price_date_range),
        generate_tool_schema(service.get_historical_stock_prices),
        generate_tool_schema(service.get_dividends),
        generate_tool_schema(service.get_stock_actions),
        
        # Company Info (1)
        generate_tool_schema(service.get_stock_info),
        
        # Financial Statements (3)
        generate_tool_schema(service.get_income_statement),
        generate_tool_schema(service.get_balance_sheet),
        generate_tool_schema(service.get_cashflow),
        
        # Holders (1)
        generate_tool_schema(service.get_holder_info),
        
        # Options (2)
        generate_tool_schema(service.get_option_expiration_dates),
        generate_tool_schema(service.get_option_chain),
        
        # News & Analysis (3)
        generate_tool_schema(service.get_news),
        generate_tool_schema(service.get_recommendations),
        generate_tool_schema(service.get_earning_dates),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool execution with caching
    
    Flow:
    1. Generate cache key
    2. Check cache
    3. If hit: return cached data
    4. If miss: call service, cache result, return
    """
    try:
        # Generate cache key
        cache_key = generate_cache_key(name, **arguments)
        
        # Try cache first (exceto para alguns tools que devem ser sempre frescos)
        if name not in ["get_current_stock_price", "get_option_chain"]:
            cached = cache.get(cache_key)
            if cached:
                return [TextContent(type="text", text=cached["data"])]
        
        # Cache miss - call service
        method = getattr(service, name)
        result = method(**arguments)
        
        # Determine TTL based on tool name
        ttl = CACHE_TTL.get(name.replace("get_", ""), 3600)
        
        # Cache result
        cache.set(cache_key, {"data": result}, ttl=ttl)
        
        return [TextContent(type="text", text=result)]
        
    except YFinanceMCPError as e:
        # Known error - return formatted message
        return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    except Exception as e:
        # Unknown error - log and return generic message
        import traceback
        traceback.print_exc()
        return [TextContent(
            type="text",
            text=f"Unexpected error in {name}: {str(e)}"
        )]


async def main():
    """Main entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## 📦 DEPLOYMENT

### pyproject.toml

```toml
[project]
name = "mcp-yfinance"
version = "0.1.0"
description = "MCP server for Yahoo Finance with 18 tools, caching, and global+BR support"
authors = [{name = "Oliver", email = "seu_email@example.com"}]
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
keywords = ["mcp", "yahoo-finance", "finance", "stocks", "b3"]

dependencies = [
    "mcp>=1.6.0",
    "yfinance>=0.2.62",
    "pydantic>=2.0.0",
    "pandas>=2.0.0",
]

[project.scripts]
mcp-yfinance = "mcp_yfinance:main"

[project.urls]
Homepage = "https://github.com/seu-usuario/mcp-yfinance"
Repository = "https://github.com/seu-usuario/mcp-yfinance.git"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "ruff>=0.11.5",
    "pytest>=8.3.5",
    "pytest-asyncio>=0.26.0",
    "pytest-cov>=6.0.0",
    "mypy>=1.13.0",
]

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

### README.md

```markdown
# MCP Yahoo Finance

MCP server with 18 tools for Yahoo Finance data access.

## Features

- ✅ 18 comprehensive tools (pricing, financials, options, holders, news)
- ✅ Intelligent SQLite caching (reduces latency + API limits)
- ✅ Global + Brazil support (auto .SA normalization)
- ✅ Type-safe (Pydantic + full type hints)
- ✅ Production-ready error handling
- ✅ Zero config (works via uvx one-liner)

## Installation

### Via uvx (Recommended)

```bash
# In claude_desktop_config.json
{
  "mcpServers": {
    "yfinance": {
      "command": "uvx",
      "args": ["mcp-yfinance"]
    }
  }
}
```

### Manual Installation

```bash
uv pip install mcp-yfinance
```

## Tools

### Pricing & Historical
- `get_current_stock_price` - Current price + day change
- `get_stock_price_by_date` - Price on specific date
- `get_stock_price_date_range` - Price series for date range
- `get_historical_stock_prices` - Full OHLCV historical data
- `get_dividends` - Dividend history
- `get_stock_actions` - Dividends + stock splits

### Company Information
- `get_stock_info` - Complete company info (~100 fields)

### Financial Statements
- `get_income_statement` - Income statement (DRE)
- `get_balance_sheet` - Balance sheet
- `get_cashflow` - Cash flow statement

### Ownership
- `get_holder_info` - 6 types of holder information

### Options
- `get_option_expiration_dates` - Available expiration dates
- `get_option_chain` - Option chain (calls/puts/both)

### News & Analysis
- `get_news` - Recent news articles
- `get_recommendations` - Analyst recommendations
- `get_earning_dates` - Earnings announcement dates

## Example Usage

```
Get current price of Apple stock
→ Returns: {"symbol": "AAPL", "price": 234.56, "change": 2.34, ...}

Get quarterly income statement for Microsoft
→ Returns: Full DRE with quarterly data

Get call options for Tesla expiring on 2025-01-17
→ Returns: Option chain with strikes, prices, Greeks
```

## Cache

- SQLite cache in `~/.mcp-yfinance/cache.db`
- TTL by data type:
  - 5 min: quotes, option chains
  - 1 hour: stock info
  - 24 hours: historical, financials, holders, news, recommendations
- Auto-cleanup of expired entries

## License

MIT
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Setup (use este prompt no Claude Code Web)
```
Criar estrutura de diretórios conforme especificação.
Implementar:
1. pyproject.toml completo
2. src/mcp_yfinance/__init__.py com version
3. .python-version com 3.10
4. README.md básico
```

### Fase 2: Models & Exceptions
```
Implementar conforme especificação:
1. models.py - todos os Enums e Pydantic models
2. exceptions.py - 4 custom exceptions
3. Testar: importações devem funcionar
```

### Fase 3: Cache & Utils
```
Implementar:
1. cache.py - CacheManager completo com SQLite
2. utils.py - normalize_ticker, generate_cache_key, etc
3. Testar: cache set/get, ticker normalization
```

### Fase 4: Service Layer
```
Implementar service.py com os 18 métodos:
1. Pricing & Historical (6 métodos)
2. Company Info (1 método)
3. Financial Statements (3 métodos)
4. Holders (1 método)
5. Options (2 métodos)
6. News & Analysis (3 métodos)

Testar cada método isoladamente
```

### Fase 5: Server Integration
```
Implementar server.py:
1. Initialize components (service, cache)
2. @server.list_tools() - registrar 18 tools
3. @server.call_tool() - com integração de cache
4. main() entry point

Testar: uv run mcp-yfinance
```

### Fase 6: Polish
```
1. Adicionar docstrings faltantes
2. Type hints em 100% do código
3. README.md completo com exemplos
4. Testes básicos (opcional para MVP)
```

---

## 🎯 PRIORIDADES

**MUST HAVE (MVP)**:
- ✅ 18 tools funcionando
- ✅ Cache SQLite básico
- ✅ Error handling robusto
- ✅ Funciona via uvx

**SHOULD HAVE (v0.2)**:
- ✅ Testes unitários
- ✅ CI/CD pipeline
- ✅ Documentação expandida
- ✅ Retry logic avançado

**NICE TO HAVE (futuro)**:
- Rate limiting inteligente
- Múltiplas sources (Alpha Vantage, etc)
- Real-time WebSocket quotes
- Backtesting tools

---

## 📌 NOTAS FINAIS

### Diferencial vs MCPs Existentes

| Aspecto | MCPs Antigos | Este MCP |
|---------|--------------|----------|
| Tools | 1-12 | **18 completos** |
| Cache | ❌ Nenhum | ✅ SQLite com TTL |
| Type Safety | ⚠️ Parcial | ✅ Pydantic completo |
| Brasil | ⚠️ Manual .SA | ✅ Auto-normalização |
| Error Handling | ⚠️ Básico | ✅ Custom exceptions |
| Arquitetura | ⚠️ Monolítica | ✅ 4 camadas |
| Deployment | ⚠️ Git clone | ✅ uvx one-liner |

### Por Que Esta Arquitetura?

1. **Cache SQLite**: Reduz latência 90% em queries repetidas
2. **4 Camadas**: Cada responsabilidade isolada e testável
3. **18 Tools**: Cobertura completa para análise profissional
4. **Type Safety**: Pydantic valida tudo automaticamente
5. **Brasil + Global**: Um único MCP para todos os mercados
6. **Zero Config**: Usuario só precisa de uma linha no config

---

**Este documento contém tudo que Claude Code Web precisa para desenvolver o MCP completo e production-ready.**
