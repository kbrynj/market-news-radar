# Project Organization - November 2025

## What Changed

### File Structure
```
StockNews/
├── backend/                 # FastAPI application
├── frontend/                # Vanilla JS/CSS UI
├── scripts/                 # NEW: Utility & test scripts
│   ├── README.md           # Script documentation
│   ├── generate_tickers_dataset.py
│   ├── check_*.py          # Database checks
│   ├── test_*.py           # Testing scripts
│   ├── add_feeds.py
│   ├── fix_feeds.py
│   └── ...
├── data/                    # Database storage
├── CHANGELOG.md            # NEW: Version history
├── RATE_LIMITING.md        # NEW: RSS etiquette docs
├── TICKER_AUTOCOMPLETE.md
├── UPDATE_SCHEDULE.md
└── README.md               # Updated with new features
```

### Scripts Directory
All utility and test scripts moved to `scripts/` for better organization:
- **Maintenance**: `generate_tickers_dataset.py`
- **Database Tools**: `check_feeds.py`, `check_feed_articles.py`, `quick_check.py`
- **Feed Testing**: `test_yahoo_rss.py`, `add_feeds.py`, `fix_feeds.py`
- **Validation**: `validate_setup.py`, `test_dynamic_tickers.py`

### Updated .gitignore
Added patterns to exclude test/temporary files:
```gitignore
# Development/test scripts (use scripts/ for utilities)
test_*.py
check_*.py
fix_*.py
quick_*.py

# Project-specific
market_news.db
```

### Documentation Improvements

**New Files:**
- `CHANGELOG.md` - Version history and release notes
- `RATE_LIMITING.md` - RSS feed etiquette explained
- `scripts/README.md` - Utility script documentation

**Updated Files:**
- `README.md` - Added rate limiting, scripts section, updated features
- `.gitignore` - Better organization

### Code Improvements

**backend/scraper.py:**
- Added User-Agent header: "Market News Radar RSS Reader/1.0"
- Implemented staggered request delays (0s, 1s, 2s, 3s...)
- Better error handling and logging

**backend/db.py:**
- Increased default refresh interval from 300s to 600s (10 minutes)
- Better documentation

**frontend/**
- Light/dark theme toggle with localStorage persistence
- CSS custom properties for theming
- Theme toggle button with emoji icons (🌙/☀️)

## Benefits

1. **Better Organization** - Scripts in dedicated directory
2. **Cleaner Root** - No test files cluttering the project root
3. **Better Documentation** - Clear README for scripts, changelog for tracking changes
4. **Rate Limiting** - 50% fewer requests, respects RSS servers
5. **Theme Support** - User choice between light/dark modes
6. **Sustainability** - Won't get IP blocked from feed providers

## For Developers

### Running Scripts
All scripts should be run from the project root:
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run a script
python scripts/check_feeds.py
```

### Adding New Scripts
1. Place in `scripts/` directory
2. Document in `scripts/README.md`
3. Use descriptive prefixes: `check_`, `test_`, `update_`, `fix_`

### Git Workflow
Test scripts are now gitignored, but keep utilities like `generate_tickers_dataset.py` in version control.

## Summary Statistics

- **Scripts Moved**: 12 files → `scripts/` directory
- **Documentation Added**: 3 new markdown files (CHANGELOG, RATE_LIMITING, scripts/README)
- **Request Reduction**: 50% fewer requests per hour (96 → 48)
- **New Features**: Light theme, rate limiting, better organization
- **RSS Feeds**: 8 active feeds (removed 3 broken, added 5 new)
