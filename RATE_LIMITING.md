# Rate Limiting & RSS Feed Etiquette

## Changes Made

### 1. User-Agent Headers ✅
The scraper now identifies itself properly to RSS feed servers:
```
User-Agent: Market News Radar RSS Reader/1.0 (RSS Feed Aggregator; +https://github.com/kbrynj/market-news-radar)
```

This follows RSS best practices by:
- Identifying as a legitimate RSS reader
- Including a link to the project for server admins
- Using proper Accept headers for RSS/XML content

### 2. Request Delays ✅
Feeds are now fetched with staggered delays:
- **First feed**: No delay
- **Subsequent feeds**: 1s, 2s, 3s, etc.

With 8 feeds, the entire scrape cycle spreads requests over 7 seconds instead of hitting all servers simultaneously.

### 3. Increased Refresh Interval ✅
- **Before**: 300 seconds (5 minutes)
- **After**: 600 seconds (10 minutes)

This reduces the total number of requests per hour by 50%.

## Request Frequency Calculation

**Before rate limiting:**
- 8 feeds × 12 scrapes/hour = 96 requests/hour

**After rate limiting:**
- 8 feeds × 6 scrapes/hour = 48 requests/hour (50% reduction)

## Benefits

1. **Avoids Rate Limiting**: Spreads out requests to avoid triggering anti-bot measures
2. **Respectful**: Follows RSS feed etiquette and reduces server load
3. **Sustainable**: Prevents feeds from blocking your IP address
4. **Reliable**: More stable operation over long periods

## Current Active Feeds

1. CoinDesk
2. MarketWatch Top Stories
3. Seeking Alpha
4. E24 (Norwegian Business News)
5. Bloomberg Markets
6. Investing.com
7. Financial Times
8. Wall Street Journal Markets

## Manual Refresh

You can still manually trigger a refresh from the UI when needed. The rate limiting only affects automatic background scraping.

## Adjusting Settings

To change the refresh interval:
1. Go to Settings panel in the UI
2. Adjust "Refresh Interval" (in seconds)
3. Save settings

**Recommended intervals:**
- **Testing/Development**: 600-900 seconds (10-15 minutes)
- **Production**: 900-1800 seconds (15-30 minutes)
- **Conservative**: 3600 seconds (1 hour)
