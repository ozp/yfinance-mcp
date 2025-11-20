# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-11-20

### Fixed
- Fixed lxml dependency specification to ensure proper installation from PyPI
- Updated hatchling requirement to >=1.26.3 to fix PyPI upload metadata issue
- Fixed CLI entry point to properly handle async main function

### Changed
- Improved package metadata for better PyPI compatibility

## [0.1.0] - 2025-11-20

### Added
- Initial release with 18 comprehensive Yahoo Finance tools
- Intelligent SQLite caching with TTL-based management
- Multi-market support (US, BR, UK, DE, FR, JP, IN, HK, AU, CA)
- Full type safety with Pydantic models
- Production-ready error handling
- Zero-configuration deployment via uvx
- Async/await support for concurrent operations

### Tools Included
- 6 pricing and historical data tools
- 1 company information tool
- 3 financial statement tools
- 1 holders and ownership tool
- 2 options tools
- 5 news and analysis tools

[0.1.1]: https://github.com/ozp/yfinance-mcp/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ozp/yfinance-mcp/releases/tag/v0.1.0
