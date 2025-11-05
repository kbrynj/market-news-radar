# Changelog

All notable changes to Market News Radar will be documented in this file.

## [Unreleased]

### Added
- **Light/Dark Theme Toggle** - Users can now switch between light and dark modes with persistent localStorage preference
- **Rate Limiting** - Implemented RSS feed etiquette with staggered requests (1s delays) and proper User-Agent headers
- **Ticker Autocomplete** - Smart search with 5,000+ tickers from local dataset (US, Nordic, crypto)
- **Dynamic Ticker Support** - Scraper automatically uses all tickers and company names from database
- **8 RSS Feeds** - Added Bloomberg, E24 (Norwegian), Investing.com, Financial Times, WSJ
- **Scripts Directory** - Organized utility scripts for maintenance and testing
- **Comprehensive Documentation** - Added RATE_LIMITING.md, TICKER_AUTOCOMPLETE.md, UPDATE_SCHEDULE.md

### Changed
- **Refresh Interval** - Increased default from 5 minutes to 10 minutes to respect feed servers
- **Request Handling** - Added User-Agent: "Market News Radar RSS Reader/1.0" with project link
- **Feed Management** - Removed non-working feeds (Yahoo Finance, Reuters, CNBC)
- **Project Structure** - Moved test/utility scripts to `scripts/` directory

### Fixed
- **Rate Limiting Issues** - Staggered requests prevent simultaneous hits to feed servers
- **Company Matching** - Dynamic database mappings now properly integrated with static mappings
- **Theme Persistence** - User theme preference saved to localStorage and restored on reload

### Documentation
- Updated README with rate limiting features
- Created scripts/README.md for utility script documentation
- Added detailed rate limiting explanation in RATE_LIMITING.md
- Documented ticker dataset update schedule in UPDATE_SCHEDULE.md
- Explained autocomplete functionality in TICKER_AUTOCOMPLETE.md

### Technical Improvements
- Reduced request frequency by 50% (96 → 48 requests/hour)
- Implemented proper RSS feed etiquette
- Added themed CSS with light mode support
- Enhanced .gitignore for better project organization

## [1.0.0] - Initial Release

### Features
- RSS feed monitoring with FastAPI backend
- Ticker and keyword tracking
- Smart scoring system
- VADER sentiment analysis
- WebSocket live updates
- Infinite scroll
- Admin token authentication
- Docker containerization
- SQLite with WAL mode
- Async everything (aiohttp, aiosqlite)

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward-compatible manner
- PATCH version for backward-compatible bug fixes
