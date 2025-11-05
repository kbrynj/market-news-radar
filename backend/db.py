"""
Database layer for Market News Radar
- Singleton connection with WAL mode
- Table creation and migrations
- CRUD operations for feeds, tickers, keywords, settings, articles
"""
import aiosqlite
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

# Database path
DB_PATH = os.getenv("DB_PATH", "/data/news.db")

# Singleton connection
_db_connection: Optional[aiosqlite.Connection] = None


def row_to_dict(cursor: aiosqlite.Cursor, row: aiosqlite.Row) -> Dict[str, Any]:
    """Convert a row to a dictionary."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


async def get_db() -> aiosqlite.Connection:
    """Get or create singleton database connection with WAL mode."""
    global _db_connection
    
    if _db_connection is None:
        # Ensure directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        _db_connection = await aiosqlite.connect(DB_PATH)
        _db_connection.row_factory = aiosqlite.Row
        
        # Enable WAL mode for better concurrent access
        await _db_connection.execute("PRAGMA journal_mode=WAL")
        await _db_connection.execute("PRAGMA synchronous=NORMAL")
        await _db_connection.commit()
    
    return _db_connection


async def init_db():
    """Initialize database tables and seed default data."""
    db = await get_db()
    
    # Create feeds table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create tickers table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS tickers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            company_names TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create keywords table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create settings table (single row, id=1)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            refresh_interval INTEGER DEFAULT 600,
            min_score INTEGER DEFAULT 1,
            strong_words TEXT DEFAULT 'breaking,exclusive,surge,crash,boom,plunge',
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create articles table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_id INTEGER NOT NULL,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            published_ts INTEGER NOT NULL,
            published_str TEXT,
            score INTEGER DEFAULT 0,
            sentiment REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (feed_id) REFERENCES feeds(id) ON DELETE CASCADE
        )
    """)
    
    # Create article_tickers junction table
    await db.execute("""
        CREATE TABLE IF NOT EXISTS article_tickers (
            article_id INTEGER NOT NULL,
            ticker_id INTEGER NOT NULL,
            PRIMARY KEY (article_id, ticker_id),
            FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
            FOREIGN KEY (ticker_id) REFERENCES tickers(id) ON DELETE CASCADE
        )
    """)
    
    # Create index for efficient article queries
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_articles_published 
        ON articles(published_ts DESC)
    """)
    
    await db.commit()
    
    # Migration: Add sentiment column if it doesn't exist
    try:
        await db.execute("ALTER TABLE articles ADD COLUMN sentiment REAL DEFAULT 0.0")
        await db.commit()
        print("Migration: Added sentiment column to articles table")
    except aiosqlite.OperationalError:
        # Column already exists, ignore
        pass
    
    # Migration: Add company_names column to tickers if it doesn't exist
    try:
        await db.execute("ALTER TABLE tickers ADD COLUMN company_names TEXT DEFAULT ''")
        await db.commit()
        print("Migration: Added company_names column to tickers table")
    except aiosqlite.OperationalError:
        # Column already exists, ignore
        pass
    
    # Seed default data if tables are empty
    await _seed_defaults(db)


async def _seed_defaults(db: aiosqlite.Connection):
    """Seed default feeds, tickers, keywords, and settings."""
    
    # Check if settings exist
    cursor = await db.execute("SELECT COUNT(*) FROM settings WHERE id = 1")
    settings_count = (await cursor.fetchone())[0]
    
    if settings_count == 0:
        await db.execute("""
            INSERT INTO settings (id, refresh_interval, min_score, strong_words)
            VALUES (1, 600, 1, 'breaking,exclusive,surge,crash,boom,plunge')
        """)
        print("Seeded default settings (10 min refresh interval)")
    
    # Check if feeds exist
    cursor = await db.execute("SELECT COUNT(*) FROM feeds")
    feeds_count = (await cursor.fetchone())[0]
    
    if feeds_count == 0:
        default_feeds = [
            ("https://feeds.finance.yahoo.com/rss/2.0/headline", "Yahoo Finance"),
            ("https://www.cnbc.com/id/100003114/device/rss/rss.html", "CNBC Top News"),
            ("https://www.reuters.com/rssfeed/businessNews", "Reuters Business"),
            ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg Markets"),
        ]
        
        for url, name in default_feeds:
            try:
                await db.execute(
                    "INSERT INTO feeds (url, name) VALUES (?, ?)",
                    (url, name)
                )
            except aiosqlite.IntegrityError:
                # Feed already exists
                pass
        
        print(f"Seeded {len(default_feeds)} default feeds")
    
    # Check if tickers exist
    cursor = await db.execute("SELECT COUNT(*) FROM tickers")
    tickers_count = (await cursor.fetchone())[0]
    
    if tickers_count == 0:
        default_tickers = [
            ("AAPL", "apple,apple inc"),
            ("MSFT", "microsoft,microsoft corporation"),
            ("GOOGL", "google,alphabet,alphabet inc"),
            ("AMZN", "amazon,amazon.com"),
            ("TSLA", "tesla,tesla motors"),
            ("META", "meta,facebook,meta platforms"),
            ("NVDA", "nvidia,nvidia corporation"),
            ("BTC", "bitcoin"),
            ("ETH", "ethereum"),
            ("SPY", "s&p 500,s&p,spy")
        ]
        
        for symbol, company_names in default_tickers:
            try:
                await db.execute(
                    "INSERT INTO tickers (symbol, company_names) VALUES (?, ?)",
                    (symbol, company_names)
                )
            except aiosqlite.IntegrityError:
                pass
        
        print(f"Seeded {len(default_tickers)} default tickers")
    
    # Check if keywords exist
    cursor = await db.execute("SELECT COUNT(*) FROM keywords")
    keywords_count = (await cursor.fetchone())[0]
    
    if keywords_count == 0:
        default_keywords = [
            "earnings", "revenue", "profit", "loss", "merger",
            "acquisition", "IPO", "stock", "market", "trade"
        ]
        
        for word in default_keywords:
            try:
                await db.execute(
                    "INSERT INTO keywords (word) VALUES (?)",
                    (word,)
                )
            except aiosqlite.IntegrityError:
                pass
        
        print(f"Seeded {len(default_keywords)} default keywords")
    
    await db.commit()


# CRUD operations for feeds
async def get_all_feeds() -> List[Dict[str, Any]]:
    """Get all feeds."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM feeds ORDER BY name")
    rows = await cursor.fetchall()
    return [row_to_dict(cursor, row) for row in rows]


async def add_feed(url: str, name: str) -> int:
    """Add a new feed. Returns feed ID."""
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO feeds (url, name) VALUES (?, ?)",
        (url, name)
    )
    await db.commit()
    return cursor.lastrowid


async def delete_feed(feed_id: int):
    """Delete a feed and its articles."""
    db = await get_db()
    await db.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
    await db.commit()


async def toggle_feed(feed_id: int, active: bool):
    """Toggle feed active status."""
    db = await get_db()
    await db.execute(
        "UPDATE feeds SET active = ? WHERE id = ?",
        (1 if active else 0, feed_id)
    )
    await db.commit()


# CRUD operations for tickers
async def get_all_tickers() -> List[Dict[str, Any]]:
    """Get all tickers."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM tickers ORDER BY symbol")
    rows = await cursor.fetchall()
    return [row_to_dict(cursor, row) for row in rows]


async def add_ticker(symbol: str, company_names: str = "") -> int:
    """Add a new ticker with optional company name aliases. Returns ticker ID."""
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO tickers (symbol, company_names) VALUES (?, ?)",
        (symbol.upper(), company_names.lower())
    )
    await db.commit()
    return cursor.lastrowid


async def update_ticker_company_names(ticker_id: int, company_names: str):
    """Update company names for a ticker."""
    db = await get_db()
    await db.execute(
        "UPDATE tickers SET company_names = ? WHERE id = ?",
        (company_names.lower(), ticker_id)
    )
    await db.commit()


async def delete_ticker(ticker_id: int):
    """Delete a ticker."""
    db = await get_db()
    await db.execute("DELETE FROM tickers WHERE id = ?", (ticker_id,))
    await db.commit()


# CRUD operations for keywords
async def get_all_keywords() -> List[Dict[str, Any]]:
    """Get all keywords."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM keywords ORDER BY word")
    rows = await cursor.fetchall()
    return [row_to_dict(cursor, row) for row in rows]


async def add_keyword(word: str) -> int:
    """Add a new keyword. Returns keyword ID."""
    db = await get_db()
    cursor = await db.execute(
        "INSERT INTO keywords (word) VALUES (?)",
        (word.lower(),)
    )
    await db.commit()
    return cursor.lastrowid


async def delete_keyword(keyword_id: int):
    """Delete a keyword."""
    db = await get_db()
    await db.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))
    await db.commit()


# Settings operations
async def get_settings() -> Dict[str, Any]:
    """Get current settings."""
    db = await get_db()
    cursor = await db.execute("SELECT * FROM settings WHERE id = 1")
    row = await cursor.fetchone()
    return row_to_dict(cursor, row) if row else {}


async def update_settings(
    refresh_interval: Optional[int] = None,
    min_score: Optional[int] = None,
    strong_words: Optional[str] = None
):
    """Update settings."""
    db = await get_db()
    
    updates = []
    params = []
    
    if refresh_interval is not None:
        updates.append("refresh_interval = ?")
        params.append(refresh_interval)
    
    if min_score is not None:
        updates.append("min_score = ?")
        params.append(min_score)
    
    if strong_words is not None:
        updates.append("strong_words = ?")
        params.append(strong_words)
    
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE settings SET {', '.join(updates)} WHERE id = 1"
        await db.execute(query, params)
        await db.commit()


# Article operations
async def article_exists(url: str) -> bool:
    """Check if article URL already exists."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT COUNT(*) FROM articles WHERE url = ?",
        (url,)
    )
    count = (await cursor.fetchone())[0]
    return count > 0


async def insert_article(
    feed_id: int,
    url: str,
    title: str,
    summary: str,
    published_ts: int,
    published_str: str,
    score: int,
    sentiment: float,
    ticker_ids: List[int]
) -> int:
    """Insert a new article with associated tickers. Returns article ID."""
    db = await get_db()
    
    cursor = await db.execute("""
        INSERT INTO articles 
        (feed_id, url, title, summary, published_ts, published_str, score, sentiment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (feed_id, url, title, summary, published_ts, published_str, score, sentiment))
    
    article_id = cursor.lastrowid
    
    # Insert ticker associations
    for ticker_id in ticker_ids:
        await db.execute(
            "INSERT INTO article_tickers (article_id, ticker_id) VALUES (?, ?)",
            (article_id, ticker_id)
        )
    
    await db.commit()
    return article_id


async def get_articles(
    limit: int = 50,
    offset: int = 0,
    min_score: Optional[int] = None,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get articles with optional filtering and pagination."""
    db = await get_db()
    
    query = """
        SELECT 
            a.*,
            f.name as feed_name,
            GROUP_CONCAT(t.symbol, ',') as tickers
        FROM articles a
        JOIN feeds f ON a.feed_id = f.id
        LEFT JOIN article_tickers at ON a.id = at.article_id
        LEFT JOIN tickers t ON at.ticker_id = t.id
    """
    
    conditions = []
    params = []
    
    if min_score is not None:
        conditions.append("a.score >= ?")
        params.append(min_score)
    
    if search:
        conditions.append("(a.title LIKE ? OR a.summary LIKE ?)")
        search_term = f"%{search}%"
        params.extend([search_term, search_term])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += """
        GROUP BY a.id
        ORDER BY a.published_ts DESC
        LIMIT ? OFFSET ?
    """
    
    params.extend([limit, offset])
    
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    return [row_to_dict(cursor, row) for row in rows]


async def get_articles_count(
    min_score: Optional[int] = None,
    search: Optional[str] = None
) -> int:
    """Get total count of articles matching filters."""
    db = await get_db()
    
    query = "SELECT COUNT(*) FROM articles a"
    
    conditions = []
    params = []
    
    if min_score is not None:
        conditions.append("a.score >= ?")
        params.append(min_score)
    
    if search:
        conditions.append("(a.title LIKE ? OR a.summary LIKE ?)")
        search_term = f"%{search}%"
        params.extend([search_term, search_term])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    cursor = await db.execute(query, params)
    count = (await cursor.fetchone())[0]
    return count


async def close_db():
    """Close database connection."""
    global _db_connection
    if _db_connection:
        await _db_connection.close()
        _db_connection = None
