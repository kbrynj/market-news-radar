import asyncio
import aiosqlite
import aiohttp

async def test_and_add_feed(url, name):
    """Test a feed and add it if it works"""
    print(f"\n🔍 Testing: {name}")
    print(f"   URL: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10), headers=headers) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    if '<rss' in content.lower() or '<feed' in content.lower() or '<?xml' in content.lower():
                        print(f"   ✅ Working! (Status: {resp.status}, Size: {len(content)} bytes)")
                        return True
                    else:
                        print(f"   ⚠️  Status {resp.status} but content doesn't look like RSS")
                        return False
                else:
                    print(f"   ❌ Failed: HTTP {resp.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def main():
    print("\n📰 Testing Additional RSS Feeds")
    print("=" * 80)
    
    # Feeds to test
    feeds_to_test = [
        ("https://e24.no/rss", "E24 (Norwegian Business News)"),
        ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg Markets"),
        ("https://www.investing.com/rss/news.rss", "Investing.com"),
        ("https://www.ft.com/rss/home", "Financial Times"),
        ("https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "Wall Street Journal Markets"),
    ]
    
    working_feeds = []
    for url, name in feeds_to_test:
        if await test_and_add_feed(url, name):
            working_feeds.append((url, name))
    
    # Add working feeds to database
    if working_feeds:
        print("\n\n➕ Adding Working Feeds to Database")
        print("=" * 80)
        
        async with aiosqlite.connect('data/news.db') as db:
            for url, name in working_feeds:
                # Check if already exists
                async with db.execute("SELECT id FROM feeds WHERE url = ?", (url,)) as cursor:
                    existing = await cursor.fetchone()
                
                if existing:
                    print(f"⏭️  {name} already exists")
                else:
                    await db.execute(
                        "INSERT INTO feeds (url, name, active) VALUES (?, ?, 1)",
                        (url, name)
                    )
                    print(f"✅ Added: {name}")
            
            await db.commit()
            
            # Show all feeds
            print("\n\n📡 All RSS Feeds in Database:")
            print("-" * 80)
            async with db.execute("SELECT id, name, url, active FROM feeds ORDER BY id") as cursor:
                feeds = await cursor.fetchall()
                for feed in feeds:
                    status = "✅" if feed[3] else "❌"
                    print(f"{status} ID:{feed[0]:2d} - {feed[1]}")
                    print(f"         {feed[2]}")
            
            print(f"\n📊 Total active feeds: {len([f for f in feeds if f[3]])}")

if __name__ == '__main__':
    asyncio.run(main())
