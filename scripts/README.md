# Scripts Directory

Utility scripts for development, testing, and maintenance of Market News Radar.

## Maintenance Scripts

### `generate_tickers_dataset.py`
Generates the local ticker dataset (`frontend/tickers_dataset.json`) from multiple sources:
- SEC CIK list (US stocks)
- CoinGecko API (cryptocurrencies)
- Manual Scandinavian stocks list

**Usage:**
```bash
python generate_tickers_dataset.py
```

**When to run:** See [UPDATE_SCHEDULE.md](../UPDATE_SCHEDULE.md) for recommended update frequency.

## Testing & Validation Scripts

### `validate_setup.py`
Validates that all required files and dependencies are present for the application to run.

**Usage:**
```bash
python scripts/validate_setup.py
```

### `test_dynamic_tickers.py`
Tests that the scraper correctly uses dynamically added tickers from the database.

**Usage:**
```bash
python scripts/test_dynamic_tickers.py
```

### `test_company_matching.py`
Tests company name to ticker matching logic.

**Usage:**
```bash
python scripts/test_company_matching.py
```

## Database Management Scripts

### `check_feeds.py`
Displays all RSS feeds in the database with their status.

**Usage:**
```bash
python scripts/check_feeds.py
```

### `check_feed_articles.py`
Shows article counts per feed and identifies feeds that aren't being scraped successfully.

**Usage:**
```bash
python scripts/check_feed_articles.py
```

### `quick_check.py`
Quick database query to show feed article counts (no async, fast).

**Usage:**
```bash
python scripts/quick_check.py
```

### `update_interval.py`
Updates the scraper refresh interval in the database.

**Usage:**
```bash
python scripts/update_interval.py
```

## Feed Testing Scripts

### `test_yahoo_rss.py`
Tests various Yahoo Finance RSS feed URLs to find working ones.

**Usage:**
```bash
python scripts/test_yahoo_rss.py
```

### `add_feeds.py`
Tests and adds multiple RSS feeds to the database.

**Usage:**
```bash
python scripts/add_feeds.py
```

### `fix_feeds.py`
Removes non-working feeds and adds working alternatives.

**Usage:**
```bash
python scripts/fix_feeds.py
```

## Ticker Validation Scripts

### `check_stocks.py`
Validates US stock tickers from the dataset.

**Usage:**
```bash
python scripts/check_stocks.py
```

### `check_nordic.py`
Validates Scandinavian stock tickers from the dataset.

**Usage:**
```bash
python scripts/check_nordic.py
```

## Notes

- All scripts should be run from the project root directory
- Most scripts require the virtual environment to be activated
- Database scripts connect to `data/news.db` by default
- Test scripts are excluded from git via `.gitignore`

## Adding New Scripts

When creating utility scripts:
1. Place them in the `scripts/` directory
2. Add documentation to this README
3. Use descriptive names (e.g., `check_*`, `test_*`, `update_*`)
4. Include usage examples and descriptions
