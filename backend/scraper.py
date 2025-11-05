"""
RSS Scraper for Market News Radar
- Async fetching with aiohttp
- Scoring based on tickers, keywords, strong words
- VADER sentiment analysis
- Duplicate detection
"""
import aiohttp
import feedparser
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from email.utils import parsedate_to_datetime
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from . import db


# Sentiment analyzer instance
sentiment_analyzer = SentimentIntensityAnalyzer()


# Company name to ticker mapping
# Maps common company names/variations to their ticker symbols
COMPANY_TO_TICKER = {
    # Tech Giants
    'apple': 'AAPL',
    'microsoft': 'MSFT',
    'alphabet': 'GOOGL',
    'google': 'GOOGL',
    'amazon': 'AMZN',
    'meta': 'META',
    'facebook': 'META',
    'tesla': 'TSLA',
    'nvidia': 'NVDA',
    'netflix': 'NFLX',
    'adobe': 'ADBE',
    'salesforce': 'CRM',
    'oracle': 'ORCL',
    'intel': 'INTC',
    'amd': 'AMD',
    'ibm': 'IBM',
    'cisco': 'CSCO',
    'qualcomm': 'QCOM',
    
    # Finance
    'jpmorgan': 'JPM',
    'jp morgan': 'JPM',
    'bank of america': 'BAC',
    'wells fargo': 'WFC',
    'goldman sachs': 'GS',
    'morgan stanley': 'MS',
    'citigroup': 'C',
    'visa': 'V',
    'mastercard': 'MA',
    'paypal': 'PYPL',
    'square': 'SQ',
    'american express': 'AXP',
    
    # Retail & Consumer
    'walmart': 'WMT',
    'target': 'TGT',
    'costco': 'COST',
    'home depot': 'HD',
    'nike': 'NKE',
    'starbucks': 'SBUX',
    'mcdonalds': 'MCD',
    "mcdonald's": 'MCD',
    'coca cola': 'KO',
    'coca-cola': 'KO',
    'pepsi': 'PEP',
    'procter & gamble': 'PG',
    'disney': 'DIS',
    
    # Automotive
    'general motors': 'GM',
    'ford': 'F',
    'gm': 'GM',
    
    # Pharma & Healthcare
    'pfizer': 'PFE',
    'moderna': 'MRNA',
    'johnson & johnson': 'JNJ',
    'abbvie': 'ABBV',
    'merck': 'MRK',
    'eli lilly': 'LLY',
    'bristol myers': 'BMY',
    'unitedhealth': 'UNH',
    
    # Energy
    'exxon': 'XOM',
    'chevron': 'CVX',
    'conocophillips': 'COP',
    'schlumberger': 'SLB',
    
    # Crypto (as company references)
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'coinbase': 'COIN',
    'microstrategy': 'MSTR',
    
    # Aerospace & Defense
    'boeing': 'BA',
    'lockheed martin': 'LMT',
    'raytheon': 'RTX',
    
    # Other Major Companies
    'berkshire hathaway': 'BRK.B',
    'at&t': 'T',
    'verizon': 'VZ',
    'comcast': 'CMCSA',
    'lowes': 'LOW',
    "lowe's": 'LOW',
}


def clean_html(text: str) -> str:
    """Remove HTML tags and clean text."""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def parse_published_date(date_str: Optional[str]) -> Tuple[int, str]:
    """
    Parse published date to unix timestamp and formatted string.
    Falls back to current time if parsing fails.
    """
    if not date_str:
        now = datetime.now()
        return int(now.timestamp()), now.strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Try parsing with email.utils (handles RSS date formats)
        dt = parsedate_to_datetime(date_str)
        return int(dt.timestamp()), dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # Fallback to current time
        now = datetime.now()
        return int(now.timestamp()), now.strftime("%Y-%m-%d %H:%M:%S")


async def fetch_feed(session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
    """Fetch and parse RSS feed with timeout."""
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                content = await response.text()
                feed = feedparser.parse(content)
                return feed
            else:
                print(f"Failed to fetch {url}: HTTP {response.status}")
                return None
    except asyncio.TimeoutError:
        print(f"Timeout fetching {url}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def calculate_score(
    text: str,
    tickers: List[str],
    keywords: List[str],
    strong_words: List[str]
) -> Tuple[int, List[str]]:
    """
    Calculate article score based on matched tickers, keywords, and strong words.
    Also matches company names to tickers for better detection.
    
    Score formula:
    score = 2 * len(matched_tickers) + keyword_hits + (1 if strong_word_present else 0)
    
    Returns: (score, matched_tickers)
    """
    text_lower = text.lower()
    text_upper = text.upper()
    
    # Find matched tickers (case-insensitive, word boundaries)
    matched_tickers = set()  # Use set to avoid duplicates
    
    # Method 1: Direct ticker symbol matching
    for ticker in tickers:
        # Check for ticker as whole word (with common delimiters)
        ticker_patterns = [
            f" {ticker} ",
            f" {ticker},",
            f" {ticker}.",
            f"({ticker})",
            f"${ticker}",
        ]
        if any(pattern.upper() in text_upper or pattern.upper() in f" {text_upper} " 
               for pattern in ticker_patterns):
            matched_tickers.add(ticker)
    
    # Method 2: Company name matching
    for company_name, ticker_symbol in COMPANY_TO_TICKER.items():
        # Only check if this ticker is in our configured list
        if ticker_symbol in tickers:
            # Check if company name appears in text
            if company_name in text_lower:
                matched_tickers.add(ticker_symbol)
    
    # Count keyword hits (can match multiple times)
    keyword_hits = 0
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Count occurrences of keyword
        keyword_hits += text_lower.count(keyword_lower)
    
    # Check for strong words (binary: present or not)
    strong_word_present = any(
        strong_word.lower() in text_lower 
        for strong_word in strong_words
    )
    
    # Calculate score
    score = (2 * len(matched_tickers)) + keyword_hits + (1 if strong_word_present else 0)
    
    return score, list(matched_tickers)


def calculate_sentiment(text: str) -> float:
    """Calculate sentiment using VADER. Returns compound score [-1, 1]."""
    if not text:
        return 0.0
    
    scores = sentiment_analyzer.polarity_scores(text)
    return scores['compound']


async def process_feed_entries(
    feed_data: Dict,
    feed_id: int,
    feed_name: str,
    tickers: List[str],
    keywords: List[str],
    strong_words: List[str],
    ticker_map: Dict[str, int]
) -> List[Dict]:
    """Process entries from a feed and return article data."""
    articles = []
    
    if not feed_data or not hasattr(feed_data, 'entries'):
        return articles
    
    for entry in feed_data.entries:
        try:
            # Extract basic fields
            url = entry.get('link', '')
            title = entry.get('title', 'No title')
            
            # Get summary (try multiple fields)
            summary = (
                entry.get('summary', '') or 
                entry.get('description', '') or 
                entry.get('content', [{}])[0].get('value', '')
            )
            
            # Clean HTML from title and summary
            title_clean = clean_html(title)
            summary_clean = clean_html(summary)
            
            # Skip if no URL or title
            if not url or not title_clean:
                continue
            
            # Check if article already exists
            if await db.article_exists(url):
                continue
            
            # Parse published date
            published_date = entry.get('published', entry.get('updated', ''))
            published_ts, published_str = parse_published_date(published_date)
            
            # Combine title and summary for scoring and sentiment
            full_text = f"{title_clean} {summary_clean}"
            
            # Calculate score and find matched tickers
            score, matched_ticker_symbols = calculate_score(
                full_text, tickers, keywords, strong_words
            )
            
            # Get ticker IDs for matched tickers
            matched_ticker_ids = [
                ticker_map[symbol] 
                for symbol in matched_ticker_symbols 
                if symbol in ticker_map
            ]
            
            # Calculate sentiment
            sentiment = calculate_sentiment(full_text)
            
            # Store article data
            articles.append({
                'feed_id': feed_id,
                'url': url,
                'title': title_clean,
                'summary': summary_clean[:500],  # Limit summary length
                'published_ts': published_ts,
                'published_str': published_str,
                'score': score,
                'sentiment': sentiment,
                'ticker_ids': matched_ticker_ids
            })
            
        except Exception as e:
            print(f"Error processing entry from {feed_name}: {e}")
            continue
    
    return articles


async def run_cycle() -> int:
    """
    Run one scraping cycle:
    1. Load configuration from DB
    2. Fetch all active feeds concurrently
    3. Process entries, calculate scores and sentiment
    4. Insert new articles
    
    Returns: Number of articles inserted
    """
    print(f"Starting scrape cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration from database
    feeds = await db.get_all_feeds()
    active_feeds = [f for f in feeds if f['active'] == 1]
    
    if not active_feeds:
        print("No active feeds configured")
        return 0
    
    tickers_data = await db.get_all_tickers()
    tickers = [t['symbol'] for t in tickers_data]
    ticker_map = {t['symbol']: t['id'] for t in tickers_data}
    
    keywords_data = await db.get_all_keywords()
    keywords = [k['word'] for k in keywords_data]
    
    settings = await db.get_settings()
    strong_words_str = settings.get('strong_words', '')
    strong_words = [w.strip() for w in strong_words_str.split(',') if w.strip()]
    
    print(f"Configuration: {len(active_feeds)} feeds, {len(tickers)} tickers, "
          f"{len(keywords)} keywords, {len(strong_words)} strong words")
    
    # Fetch all feeds concurrently
    all_articles = []
    
    async with aiohttp.ClientSession() as session:
        # Create fetch tasks for all active feeds
        fetch_tasks = [
            fetch_feed(session, feed['url'])
            for feed in active_feeds
        ]
        
        # Wait for all fetches to complete
        feed_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
        
        # Process each feed's entries
        process_tasks = []
        for i, feed_data in enumerate(feed_results):
            if isinstance(feed_data, Exception):
                print(f"Exception fetching feed {active_feeds[i]['name']}: {feed_data}")
                continue
            
            if feed_data:
                task = process_feed_entries(
                    feed_data,
                    active_feeds[i]['id'],
                    active_feeds[i]['name'],
                    tickers,
                    keywords,
                    strong_words,
                    ticker_map
                )
                process_tasks.append(task)
        
        # Wait for all processing to complete
        if process_tasks:
            processed_results = await asyncio.gather(*process_tasks)
            for articles in processed_results:
                all_articles.extend(articles)
    
    # Insert new articles into database
    inserted_count = 0
    for article in all_articles:
        try:
            await db.insert_article(
                feed_id=article['feed_id'],
                url=article['url'],
                title=article['title'],
                summary=article['summary'],
                published_ts=article['published_ts'],
                published_str=article['published_str'],
                score=article['score'],
                sentiment=article['sentiment'],
                ticker_ids=article['ticker_ids']
            )
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting article '{article['title']}': {e}")
    
    print(f"Scrape cycle complete: {inserted_count} new articles inserted")
    return inserted_count


async def scraper_loop(interval_seconds: int = 300):
    """
    Continuous scraper loop that runs at specified intervals.
    Interval is refreshed from DB settings on each cycle.
    """
    while True:
        try:
            # Run scrape cycle
            inserted = await run_cycle()
            
            # Get current interval from settings
            settings = await db.get_settings()
            interval = settings.get('refresh_interval', interval_seconds)
            
            print(f"Next scrape in {interval} seconds")
            await asyncio.sleep(interval)
            
        except Exception as e:
            print(f"Error in scraper loop: {e}")
            # Wait a bit before retrying on error
            await asyncio.sleep(60)
