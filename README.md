# 📡 Market News Radar

A self-hosted web application for monitoring and analyzing market news from RSS feeds. Built with Python (FastAPI) backend and vanilla JavaScript frontend.

## 🚀 Quick Start

```bash
# Clone the repository and navigate to the project directory
cd StockNews

# Start the application with Docker Compose
docker compose up --build -d

# Open your browser
# http://localhost:8000
```

That's it! The application will:
- Initialize the SQLite database with default feeds, tickers, and keywords
- Start scraping RSS feeds every 5 minutes (configurable)
- Serve the web interface on port 8000

## ✨ Features

### Core Functionality
- **📰 RSS Feed Monitoring** - Add/remove RSS feeds with real-time scraping
- **📈 Ticker Tracking** - Configure stock tickers (AAPL, TSLA, BTC, etc.) to monitor
- **🏢 Company Name Matching** - Smart ticker detection via company names (e.g., "Apple" → AAPL)
- **🔑 Keyword Matching** - Track specific keywords (earnings, IPO, merger, etc.)
- **⚙️ Configurable Settings** - Adjust refresh intervals, scoring thresholds, and strong words
- **🎯 Smart Scoring System** - Automatic relevance scoring based on content analysis
- **😊 Sentiment Analysis** - VADER sentiment analysis for each article (compound score)
- **🏷️ Ticker Badges** - Visual ticker tags on articles with click-to-filter functionality
- **🔄 Auto-Refresh** - Articles automatically refresh every 30 seconds
- **⚡ WebSocket Live Updates** - Real-time notifications when new articles arrive
- **♾️ Infinite Scroll** - Seamless article browsing with pagination
- **🔍 Search & Filter** - Full-text search and minimum score filtering
- **🗑️ Maintenance** - Prune old articles (7+ days)

### Technical Features
- **Async Everything** - aiohttp for RSS fetching, aiosqlite for database, FastAPI async endpoints
- **SQLite WAL Mode** - Improved concurrent access for read-heavy workloads
- **Duplicate Detection** - URL-based deduplication to avoid storing the same article twice
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark Theme** - Easy on the eyes for long monitoring sessions

## 📊 Scoring Formula

Each article receives a relevance score calculated as:

```
score = (2 × matched_tickers) + keyword_hits + strong_word_bonus
```

Where:
- **`matched_tickers`** - Number of configured tickers found in the article (worth 2 points each)
  - Matches ticker symbols directly (e.g., "AAPL", "$TSLA")
  - Matches company names (e.g., "Apple Inc" → AAPL, "Tesla" → TSLA)
  - Uses both static mappings (70+ companies) and dynamic database mappings
- **`keyword_hits`** - Total count of keyword matches (can match multiple times)
- **`strong_word_bonus`** - +1 if any "strong word" is present (e.g., breaking, exclusive, surge, crash)

### Example
An article with:
- 2 tickers (AAPL, TSLA) → 2 × 2 = **4 points**
- "earnings" mentioned 3 times → **3 points**
- Contains "breaking" → **1 point**
- **Total score: 8**

## 😊 Sentiment Analysis

Each article includes a VADER sentiment score (compound value from -1 to +1):
- **Green badge (😊)** - Positive sentiment (> 0.1)
- **Gray badge (😐)** - Neutral sentiment (-0.1 to 0.1)
- **Red badge (😟)** - Negative sentiment (< -0.1)

The sentiment is calculated from the article's title and summary combined.

## 🏢 Company Name Matching

The application uses intelligent company name matching to detect relevant tickers in articles:

### Two-Tier Matching System
1. **Static Mappings** - 70+ pre-configured company names (Apple→AAPL, Tesla→TSLA, etc.)
2. **Dynamic Mappings** - User-configurable company names stored in database

### Adding Company Names to Tickers
When adding a ticker, you can specify comma-separated company name variations:
```
Ticker: NFLX
Company Names: netflix,netflix inc,netflix incorporated
```

Now any article mentioning "Netflix" will automatically show the NFLX ticker badge.

### Examples of Auto-Detection
- "Apple announced..." → **AAPL** badge
- "Tesla CEO Elon Musk..." → **TSLA** badge
- "Microsoft and Google..." → **MSFT** and **GOOGL** badges
- "Bitcoin hit new highs..." → **BTC** badge

Click on any ticker badge to filter articles for that specific ticker.

## 🗂️ Project Structure

```
StockNews/
├── backend/
│   ├── __init__.py
│   ├── app.py          # FastAPI application & endpoints
│   ├── db.py           # Database layer (aiosqlite)
│   └── scraper.py      # RSS scraping & scoring logic
├── frontend/
│   ├── index.html      # UI structure
│   ├── styles.css      # Dark theme styling
│   └── app.js          # Frontend logic & WebSocket
├── requirements.txt            # Python dependencies
├── run_dev.py                 # Local development server script
├── test_company_matching.py   # Test suite for company matching
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Orchestration config
└── README.md                  # This file
```

## 🔌 API Endpoints

### Feeds
- `GET /api/feeds` - List all RSS feeds
- `POST /api/feeds` - Add new feed (body: `{url, name}`)
- `DELETE /api/feeds/{id}` - Delete feed

### Tickers
- `GET /api/tickers` - List all tickers
- `POST /api/tickers` - Add ticker (body: `{symbol, company_names}`)
- `PUT /api/tickers/{id}` - Update ticker company names (body: `{company_names}`)
- `DELETE /api/tickers/{id}` - Delete ticker

### Keywords
- `GET /api/keywords` - List all keywords
- `POST /api/keywords` - Add keyword (body: `{word}`)
- `DELETE /api/keywords/{id}` - Delete keyword

### Settings
- `GET /api/settings` - Get current settings
- `PUT /api/settings` - Update settings (body: `{refresh_interval, min_score, strong_words}`)

### Articles
- `GET /api/articles?q=&min_score=&limit=&offset=` - Get articles with filters
- `POST /api/refresh` - Trigger immediate scrape
- `DELETE /api/articles?days=7` - Prune old articles

### WebSocket
- `WS /ws` - Live updates (broadcasts `{type: "refresh", inserted: N}` on new articles)

## 💾 Data Persistence

All data is stored in SQLite with WAL (Write-Ahead Logging) mode for better concurrent access:
- **Location**: `/data/news.db` (inside container)
- **Volume**: `news-data` (Docker named volume)
- **Tables**: feeds, tickers, keywords, settings, articles, article_tickers

To backup your data:
```bash
docker compose exec news sqlite3 /data/news.db ".backup /data/backup.db"
docker cp market-news-radar:/data/backup.db ./backup.db
```

To access the database directly:
```bash
docker compose exec news sqlite3 /data/news.db
```

## ⚙️ Configuration

### Default Settings
- **Refresh Interval**: 300 seconds (5 minutes)
- **Min Score to Show**: 1
- **Strong Words**: breaking, exclusive, surge, crash, boom, plunge

### Default Feeds
- CoinDesk (Crypto news)
- MarketWatch Top Stories
- Seeking Alpha
- Yahoo Finance News

### Default Tickers (with Company Name Mappings)
- **AAPL** - apple, apple inc
- **MSFT** - microsoft, microsoft corp
- **GOOGL** - google, alphabet, alphabet inc
- **AMZN** - amazon, amazon.com
- **TSLA** - tesla, tesla inc
- **META** - meta, facebook, meta platforms
- **NVDA** - nvidia, nvidia corp
- **BTC** - bitcoin, btc
- **ETH** - ethereum, eth
- **SPY** - s&p 500, s&p, spdr

### Default Keywords
earnings, revenue, profit, loss, merger, acquisition, IPO, stock, market, trade

All defaults can be modified through the UI after startup.

## 🛠️ Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server with hot reload
python run_dev.py
```

The development server uses `./data/news.db` for local testing and includes hot reload on file changes.

### Testing Company Name Matching

```bash
# Run the test suite
python test_company_matching.py
```

This script verifies that company name matching works correctly with 8+ test cases covering various scenarios.

### With Docker (rebuild after changes)

```bash
docker compose up --build
```

## 📝 Notes & Best Practices

### RSS Feed Etiquette
- **Respect Terms of Service**: Only add RSS feeds that you have permission to access
- **Rate Limiting**: The default 5-minute refresh interval is conservative; adjust based on feed provider guidelines
- **User Agent**: The scraper uses aiohttp's default user agent; consider customizing if needed
- **Caching**: Articles are deduplicated by URL to avoid unnecessary storage

### Performance
- **SQLite WAL Mode**: Enables concurrent reads while writing
- **Async Operations**: All I/O is non-blocking (HTTP, database)
- **Pagination**: Frontend uses infinite scroll with 50 articles per page
- **Indexing**: Articles are indexed by `published_ts DESC` for fast queries

### Privacy & Security
- **No Authentication**: This is a single-user application; add auth if exposing publicly
- **No External APIs**: Uses only RSS feeds (no paid services)
- **Local Data**: All data stays on your server

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs -f news

# Verify port 8000 is available
netstat -an | grep 8000
```

### No articles appearing
- Check if feeds are active (toggle in UI)
- Verify RSS feed URLs are accessible
- Check scraper logs: `docker compose logs -f news`
- Trigger manual refresh via "Refresh Now" button

### Database locked errors
- WAL mode should prevent this, but if it occurs, restart the container
- Check disk space: `docker compose exec news df -h`

### WebSocket not connecting
- Ensure browser supports WebSocket
- Check for proxy/firewall blocking WS connections
- Verify in browser console (F12)

## 📄 License

This project is open source. Use responsibly and respect RSS feed providers' terms of service.

## 🙏 Acknowledgments

- **FastAPI** - Modern async web framework
- **aiohttp** - Async HTTP client
- **feedparser** - RSS/Atom feed parsing
- **VADER Sentiment** - Social media sentiment analysis
- **BeautifulSoup** - HTML parsing and cleaning

---

**Happy monitoring! 📈**
