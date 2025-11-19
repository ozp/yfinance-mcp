# Quick Session Start Guide

Use these prompts to start each parallel Claude Code session. Copy exactly as shown.

---

## 📋 Session 1: Foundation & Type System

**Branch:** Create `claude/foundation-types-{session-id}`

**Prompt to use:**
```
I need to implement the Foundation & Type System for the MCP Yahoo Finance project.

Please read PARALLEL_DEVELOPMENT_PLAN.md and implement Session 1:
- Create directory structure
- Implement src/mcp_yfinance/models.py (all Enums and Pydantic models)
- Implement src/mcp_yfinance/exceptions.py (4 custom exceptions)

Requirements:
- All code in English
- Complete type hints
- Google-style docstrings
- Follow the specification exactly

After completion, commit and push to the branch.
```

**Estimated time:** 30-40 minutes

---

## 🗄️ Session 2: Cache & Utilities

**Branch:** Create `claude/cache-utils-{session-id}`

**Prompt to use:**
```
I need to implement Cache & Utilities for the MCP Yahoo Finance project.

Please read PARALLEL_DEVELOPMENT_PLAN.md and implement Session 2:
- Implement src/mcp_yfinance/cache.py (SQLite cache with TTL)
- Implement src/mcp_yfinance/utils.py with CONFIGURABLE multi-market support

CRITICAL: The ticker normalization must support ANY country, not just Brazil.
Create MARKET_SUFFIXES dictionary for: US, BR, UK, DE, FR, JP, IN, HK, AU, CA

Requirements:
- All code in English
- Thread-safe cache operations
- Extensible market configuration
- Complete docstrings

After completion, commit and push to the branch.
```

**Estimated time:** 30-40 minutes

---

## 📊 Session 3: Service Layer Part 1

**Branch:** Create `claude/service-part1-{session-id}`

**Prompt to use:**
```
I need to implement Service Layer Part 1 for the MCP Yahoo Finance project.

Please read PARALLEL_DEVELOPMENT_PLAN.md and implement Session 3:
- Create YahooFinanceService class structure
- Implement methods 1-10:
  * Pricing & Historical (6 methods)
  * Company Info (1 method)
  * Financial Statements (3 methods)

Requirements:
- All code in English
- Use configurable market normalization
- All methods return JSON strings
- Proper error handling with custom exceptions
- Google-style docstrings

After completion, commit and push to the branch.
```

**Estimated time:** 35-45 minutes

---

## 📈 Session 4: Service Layer Part 2

**Branch:** Create `claude/service-part2-{session-id}`

**Prompt to use:**
```
I need to implement Service Layer Part 2 for the MCP Yahoo Finance project.

Please read PARALLEL_DEVELOPMENT_PLAN.md and implement Session 4:
- Implement remaining YahooFinanceService methods 11-18:
  * Holders & Ownership (1 method, 6 subtypes)
  * Options (2 methods)
  * News & Analysis (3 methods)
  * Bonus tools (2 methods)

Requirements:
- All code in English
- Same standards as Part 1
- Handle empty DataFrames gracefully
- Date formatting for timestamps
- Complete error handling

After completion, commit and push to the branch.
```

**Estimated time:** 35-45 minutes

---

## 🚀 Session 5: Server & Deployment

**Branch:** Create `claude/server-deployment-{session-id}`

**Prompt to use:**
```
I need to implement Server Integration & Deployment for the MCP Yahoo Finance project.

Please read PARALLEL_DEVELOPMENT_PLAN.md and implement Session 5:
- Implement src/mcp_yfinance/server.py (MCP orchestration)
- Create pyproject.toml (complete package config)
- Create package files (__init__.py, __main__.py, config.py)
- Write comprehensive English README.md
- Add market configuration system

Requirements:
- All code in English
- Cache integration in server
- Environment variable for market selection
- Professional README with examples
- uvx deployment support

After completion, commit and push to the branch.
```

**Estimated time:** 40-50 minutes

---

## 🔄 Integration Session (After all 5 complete)

**Prompt to use:**
```
I need to integrate all parallel development sessions for MCP Yahoo Finance.

All 5 sessions have completed their work on separate branches.
Please:
1. List all branches starting with 'claude/'
2. Merge them into a single integration branch
3. Resolve any conflicts
4. Test all 18 tools
5. Verify multi-market support (US, BR, UK, JP)
6. Run type checking
7. Create PR to main branch

Focus on ensuring everything works together correctly.
```

**Estimated time:** 20-30 minutes

---

## 📝 How to Use This Guide

### Starting a New Session:

1. **Open new Claude Code session**
2. **Navigate to project:**
   ```bash
   cd /path/to/yfinance-mcp
   ```
3. **Copy the prompt** for your session number
4. **Paste into Claude Code**
5. **Let Claude work autonomously**

### All Sessions Can Run in Parallel!

You can have 5 browser tabs open, each running a different session simultaneously. This reduces total time from 3-4 hours to about 1 hour.

---

## ⚠️ Important Reminders

### For ALL Sessions:
- ✅ All code must be in English
- ✅ Complete type hints on everything
- ✅ Google-style docstrings
- ✅ Follow PARALLEL_DEVELOPMENT_PLAN.md exactly
- ✅ Commit and push when done

### Session-Specific Notes:

**Session 2 (Cache & Utils):**
- 🌍 CRITICAL: Multi-market support, not just Brazil!
- 🌍 Add MARKET_SUFFIXES for 10+ markets
- 🌍 Make it extensible for future markets

**Sessions 3 & 4 (Service):**
- 🔧 Use `default_market` parameter
- 🔧 Return JSON strings (not objects)
- 🔧 Handle empty data gracefully

**Session 5 (Server):**
- 📦 Complete deployment configuration
- 📦 Professional English README
- 📦 Environment variable for market selection

---

## 🎯 Success Criteria

After integration, verify:
- [ ] All 18 tools work correctly
- [ ] Ticker "AAPL" works (US market)
- [ ] Ticker "PETR4" auto-adds .SA (BR market)
- [ ] Ticker "RELIANCE" with IN_NSE market adds .NS
- [ ] Cache stores and retrieves data
- [ ] Server starts via `uvx mcp-yfinance`
- [ ] All code is in English
- [ ] Type checking passes
- [ ] README is comprehensive and in English

---

## 💡 Pro Tips

1. **Start all 5 sessions at once** for maximum parallelization
2. **Session 5 can start while others are working** since it has minimal dependencies
3. **Use the same project directory** for all sessions
4. **Each session commits to its own branch** - no conflicts!
5. **Integration session merges everything** at the end

---

## 📊 Time Savings

| Approach | Time Required |
|----------|---------------|
| Sequential (1 session) | 3-4 hours |
| Parallel (5 sessions) | 1-1.5 hours |
| **Savings** | **60-70%** |

---

**Ready to start? Pick a session and go! 🚀**
