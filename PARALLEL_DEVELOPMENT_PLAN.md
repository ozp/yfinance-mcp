# Parallel Development Plan - MCP Yahoo Finance

## Overview

This document provides specific instructions for 5 parallel Claude Code sessions to develop the MCP Yahoo Finance server efficiently.

**Important Notes:**
- All code must be in English (comments, docstrings, variable names)
- Ticker normalization must be configurable for any country (not just Brazil)
- Each session works independently on different components
- Final integration will be done after all sessions complete

---

## Session 1: Foundation & Type System

**Branch:** `claude/foundation-types-{session-id}`

### Responsibilities
1. Create project directory structure
2. Implement `models.py` (Enums + Pydantic models)
3. Implement `exceptions.py` (Custom exception hierarchy)

### Tasks

#### 1.1 Create Directory Structure
```bash
mkdir -p src/mcp_yfinance
mkdir -p tests
touch src/mcp_yfinance/__init__.py
touch src/mcp_yfinance/py.typed
```

#### 1.2 Implement `src/mcp_yfinance/models.py`
**Requirements:**
- All Enums (Period, Interval, Frequency, HolderType, OptionType, RecommendationType)
- Type aliases for Literal types
- Pydantic models: Quote, Dividend, StockAction, HistoricalDataPoint, OptionContract, NewsArticle, Recommendation
- Complete type hints
- Google-style docstrings in English

**Key considerations:**
- Use `str, Enum` for all Enums to ensure JSON serialization
- Add `Config` class to Pydantic models with proper JSON encoders
- Include field validation where appropriate

#### 1.3 Implement `src/mcp_yfinance/exceptions.py`
**Requirements:**
- Base exception: `YFinanceMCPError`
- Specific exceptions:
  - `TickerNotFoundError` (with ticker attribute)
  - `YFinanceAPIError` (with optional ticker)
  - `InvalidParameterError` (with param, value, valid_values)
  - `DataNotAvailableError` (with data_type, ticker)

**Deliverables:**
- `src/mcp_yfinance/models.py` (~200 lines)
- `src/mcp_yfinance/exceptions.py` (~50 lines)
- Test imports work correctly

---

## Session 2: Cache & Utilities

**Branch:** `claude/cache-utils-{session-id}`

### Responsibilities
1. Implement `cache.py` (SQLite cache manager with TTL)
2. Implement `utils.py` with **configurable localization**

### Tasks

#### 2.1 Implement `src/mcp_yfinance/cache.py`
**Requirements:**
- `CacheManager` class with SQLite backend
- Thread-safe operations using `threading.Lock`
- Methods: `get()`, `set()`, `delete()`, `clear_expired()`, `clear_all()`, `get_stats()`
- Database schema with index on `expires_at`
- Default path: `~/.mcp-yfinance/cache.db`
- `CACHE_TTL` dictionary with TTL configurations

**Key features:**
- Auto-cleanup of expired entries on get
- JSON serialization of cached values
- Timestamp-based expiration

#### 2.2 Implement `src/mcp_yfinance/utils.py` - **IMPORTANT: Configurable Localization**
**Requirements:**
- `normalize_ticker(ticker: str, market: str = "US")` - support for **any market**
  - US: No suffix
  - BR: .SA suffix
  - UK: .L suffix
  - DE: .DE suffix
  - FR: .PA suffix
  - JP: .T suffix
  - IN: .NS or .BO suffix
  - HK: .HK suffix
  - AU: .AX suffix
  - CA: .TO suffix
  - Add extensibility for future markets
- `format_dataframe_dates(df: pd.DataFrame)` - Convert datetime index to ISO strings
- `generate_cache_key(tool_name: str, **kwargs)` - Consistent cache keys
- `parse_docstring(docstring: str)` - Extract parameter descriptions
- `generate_tool_schema(func: Callable)` - Auto-generate MCP Tool schema from function

**Localization configuration:**
Create a `MARKET_SUFFIXES` dictionary:
```python
MARKET_SUFFIXES = {
    "US": "",
    "BR": ".SA",
    "UK": ".L",
    "DE": ".DE",
    "FR": ".PA",
    "JP": ".T",
    "IN_NSE": ".NS",  # National Stock Exchange
    "IN_BSE": ".BO",  # Bombay Stock Exchange
    "HK": ".HK",
    "AU": ".AX",
    "CA": ".TO",
    # Add more markets as needed
}
```

**Deliverables:**
- `src/mcp_yfinance/cache.py` (~150 lines)
- `src/mcp_yfinance/utils.py` (~120 lines) with market configuration
- Test cache operations and ticker normalization for multiple markets

---

## Session 3: Service Layer - Part 1 (Pricing, Info, Financials)

**Branch:** `claude/service-part1-{session-id}`

### Responsibilities
Implement first 10 methods of `YahooFinanceService` class

### Tasks

#### 3.1 Create `src/mcp_yfinance/service.py` structure
**Requirements:**
- Import dependencies (yfinance, pandas, models, exceptions, utils)
- `YahooFinanceService` class with `__init__` accepting:
  - `session: Session | None = None`
  - `verify: bool = True`
  - `default_market: str = "US"` (configurable market)
- Helper method `_get_ticker(symbol: str)` with validation

#### 3.2 Implement Methods (Category 1-3)

**Pricing & Historical (6 methods):**
1. `get_current_stock_price(symbol: str) -> str`
2. `get_stock_price_by_date(symbol: str, date: str) -> str`
3. `get_stock_price_date_range(symbol: str, start_date: str, end_date: str) -> str`
4. `get_historical_stock_prices(symbol: str, period: PeriodType = "1mo", interval: IntervalType = "1d") -> str`
5. `get_dividends(symbol: str) -> str`
6. `get_stock_actions(symbol: str) -> str`

**Company Info (1 method):**
7. `get_stock_info(symbol: str) -> str`

**Financial Statements (3 methods):**
8. `get_income_statement(symbol: str, freq: FrequencyType = "yearly") -> str`
9. `get_balance_sheet(symbol: str, freq: FrequencyType = "yearly") -> str`
10. `get_cashflow(symbol: str, freq: FrequencyType = "yearly") -> str`

**Key requirements:**
- All methods return JSON strings (use `json.dumps(indent=2)`)
- Proper error handling with custom exceptions
- Use `normalize_ticker` from utils with `default_market`
- Google-style docstrings
- Type hints on all parameters and returns

**Deliverables:**
- Partial `src/mcp_yfinance/service.py` (~400 lines)
- Test methods independently with real tickers

---

## Session 4: Service Layer - Part 2 (Holders, Options, News)

**Branch:** `claude/service-part2-{session-id}`

### Responsibilities
Implement remaining 8 methods of `YahooFinanceService` class

### Tasks

#### 4.1 Implement Methods (Category 4-6)

**Holders & Ownership (1 method with 6 subtypes):**
11. `get_holder_info(symbol: str, holder_type: HolderInfoType) -> str`
    - Support: major_holders, institutional_holders, mutualfund_holders, insider_transactions, insider_purchases, insider_roster_holders

**Options (2 methods):**
12. `get_option_expiration_dates(symbol: str) -> str`
13. `get_option_chain(symbol: str, expiration_date: str, option_type: OptionChainType = "both") -> str`

**News & Analysis (3 methods):**
14. `get_news(symbol: str) -> str`
15. `get_recommendations(symbol: str, recommendation_type: RecommendationInfoType = "recommendations", months_back: int = 12) -> str`
16. `get_earning_dates(symbol: str, limit: int = 12) -> str`

**Additional methods:**
17. `get_stock_splits(symbol: str) -> str` (bonus tool)
18. `get_analyst_price_targets(symbol: str) -> str` (bonus tool)

**Key requirements:**
- Same standards as Part 1
- Handle empty DataFrames gracefully
- Date formatting for all timestamps
- Proper error messages for unsupported holder types

**Deliverables:**
- Remaining methods for `src/mcp_yfinance/service.py` (~350 lines)
- Test with various tickers including options-enabled stocks

---

## Session 5: Server Integration & Deployment

**Branch:** `claude/server-deployment-{session-id}`

### Responsibilities
1. Implement `server.py` (MCP protocol orchestration)
2. Create deployment files (`pyproject.toml`, `__init__.py`, `__main__.py`)
3. Write comprehensive English README.md
4. Add configuration file for market selection

### Tasks

#### 5.1 Implement `src/mcp_yfinance/server.py`
**Requirements:**
- Initialize components: `Server("mcp-yfinance")`, `YahooFinanceService()`, `CacheManager()`
- `@server.list_tools()` - Register all 18 tools using `generate_tool_schema()`
- `@server.call_tool()` - Handle tool execution with caching layer
- `async def main()` - Entry point with stdio_server
- Error handling with try/except for custom exceptions

**Caching strategy:**
- Skip cache for: `get_current_stock_price`, `get_option_chain`
- Use cache for all others with appropriate TTL

#### 5.2 Create `pyproject.toml`
**Requirements:**
- Project metadata (name, version, description, authors)
- Python ≥3.10
- Dependencies: mcp>=1.6.0, yfinance>=0.2.62, pydantic>=2.0.0, pandas>=2.0.0
- Dev dependencies: ruff, pytest, pytest-asyncio, mypy
- Scripts: `mcp-yfinance = "mcp_yfinance:main"`
- Build system: hatchling
- Ruff and mypy configuration

#### 5.3 Create Package Files
**`src/mcp_yfinance/__init__.py`:**
```python
"""MCP Yahoo Finance Server"""

__version__ = "0.1.0"

from .server import main

__all__ = ["main"]
```

**`src/mcp_yfinance/__main__.py`:**
```python
"""CLI entry point"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())
```

#### 5.4 Create Configuration File
**`src/mcp_yfinance/config.py`:**
```python
"""Configuration for MCP Yahoo Finance"""

import os
from typing import Literal

# Default market for ticker normalization
DEFAULT_MARKET: str = os.getenv("YFINANCE_DEFAULT_MARKET", "US")

# Supported markets
SUPPORTED_MARKETS = [
    "US", "BR", "UK", "DE", "FR", "JP",
    "IN_NSE", "IN_BSE", "HK", "AU", "CA"
]
```

#### 5.5 Create English README.md
**Structure:**
- Project overview
- Features (18 tools, caching, multi-market support, type safety)
- Installation (via uvx, manual)
- Configuration (market selection via env var)
- Tool documentation (organized by category)
- Example usage with Claude Desktop
- Cache information
- Development setup
- Contributing guidelines
- License (MIT)

**Deliverables:**
- `src/mcp_yfinance/server.py` (~180 lines)
- `pyproject.toml` (complete)
- `src/mcp_yfinance/__init__.py`
- `src/mcp_yfinance/__main__.py`
- `src/mcp_yfinance/config.py`
- `README.md` (comprehensive English documentation)
- `.python-version` (3.10)

---

## Integration Phase (After All Sessions Complete)

**Coordinator Session Tasks:**
1. Merge all branches into main development branch
2. Resolve any conflicts
3. Run integration tests
4. Verify all 18 tools work correctly
5. Test with different markets (US, BR, UK, JP)
6. Create comprehensive test suite
7. Add CI/CD configuration (GitHub Actions)
8. Create pull request to main branch

---

## Session Start Commands

### For Each Session:

```bash
# Verify branch
git status

# Create necessary directories (if not exist)
mkdir -p src/mcp_yfinance
mkdir -p tests

# After implementation, commit your work
git add .
git commit -m "Implement [component-name]: [description]"

# Push to your branch
git push -u origin claude/[component-name]-{session-id}
```

---

## Testing Guidelines

### Each session should test their components:

**Session 1 (Models):**
```python
# Test imports
from mcp_yfinance.models import Period, Quote, OptionType
from mcp_yfinance.exceptions import TickerNotFoundError

# Test model creation
quote = Quote(symbol="AAPL", price=234.56)
print(quote.model_dump_json())
```

**Session 2 (Cache/Utils):**
```python
# Test cache
cache = CacheManager()
cache.set("test_key", {"data": "test"}, ttl=60)
assert cache.get("test_key") == {"data": "test"}

# Test ticker normalization
from mcp_yfinance.utils import normalize_ticker
assert normalize_ticker("PETR4", "BR") == "PETR4.SA"
assert normalize_ticker("AAPL", "US") == "AAPL"
assert normalize_ticker("RELIANCE", "IN_NSE") == "RELIANCE.NS"
```

**Session 3 & 4 (Service):**
```python
# Test service methods
service = YahooFinanceService(default_market="US")
result = service.get_current_stock_price("AAPL")
print(result)

# Test BR market
service_br = YahooFinanceService(default_market="BR")
result = service_br.get_current_stock_price("PETR4")  # Auto .SA
print(result)
```

**Session 5 (Server):**
```bash
# Test server startup
uv run python -m mcp_yfinance

# Test with MCP inspector
npx @modelcontextprotocol/inspector uv run mcp-yfinance
```

---

## Key Changes from Original Spec

### 1. **Configurable Localization**
- Changed from Brazil-only to multi-market support
- Added `MARKET_SUFFIXES` dictionary
- Added `default_market` parameter to service
- Environment variable `YFINANCE_DEFAULT_MARKET`

### 2. **English-Only Code**
- All comments, docstrings, and documentation in English
- Portuguese only in this planning document

### 3. **Modular Architecture**
- Clear separation allows parallel development
- Each session can work independently
- Integration phase combines all work

---

## Timeline Estimate

- **Each Session:** 30-45 minutes
- **Integration:** 20-30 minutes
- **Total (with parallelization):** ~1 hour
- **Total (sequential):** ~3-4 hours

**Savings: 60-70% time reduction with parallel development**

---

## Success Criteria

- [ ] All 18 tools implemented and functional
- [ ] Multi-market support working (test US, BR, UK, JP)
- [ ] Cache working with appropriate TTLs
- [ ] Type safety verified (mypy passes)
- [ ] Server starts successfully via uvx
- [ ] All code in English
- [ ] Comprehensive README in English
- [ ] All tests passing
- [ ] PR created to main branch

---

## Quick Start for Each Session

Copy and paste the appropriate section header into your Claude Code session:

### Session 1:
```
I'm Session 1: Foundation & Type System
Implement models.py and exceptions.py according to PARALLEL_DEVELOPMENT_PLAN.md
Focus on complete type system with Enums and Pydantic models
All code in English
```

### Session 2:
```
I'm Session 2: Cache & Utilities
Implement cache.py and utils.py with CONFIGURABLE multi-market support
Create MARKET_SUFFIXES for US, BR, UK, DE, FR, JP, IN, HK, AU, CA
All code in English
```

### Session 3:
```
I'm Session 3: Service Layer Part 1
Implement YahooFinanceService methods 1-10
Pricing (6 methods) + Company Info (1) + Financials (3)
Use configurable market normalization
All code in English
```

### Session 4:
```
I'm Session 4: Service Layer Part 2
Implement YahooFinanceService methods 11-18
Holders (1) + Options (2) + News & Analysis (3) + Bonus (2)
All code in English
```

### Session 5:
```
I'm Session 5: Server Integration & Deployment
Implement server.py, pyproject.toml, package files
Create comprehensive English README.md
Add market configuration system
All code in English
```

---

**Good luck! Remember: All code must be in English, and ticker normalization must support any market!**
