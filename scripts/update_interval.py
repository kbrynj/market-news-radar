import asyncio
import aiosqlite

async def update_refresh_interval():
    """Update refresh interval to 10 minutes (600 seconds)"""
    async with aiosqlite.connect('data/news.db') as db:
        # Get current setting
        async with db.execute("SELECT refresh_interval FROM settings WHERE id = 1") as cursor:
            row = await cursor.fetchone()
            if row:
                current = row[0]
                print(f"Current refresh interval: {current} seconds ({current//60} minutes)")
        
        # Update to 10 minutes
        await db.execute("UPDATE settings SET refresh_interval = 600 WHERE id = 1")
        await db.commit()
        
        print(f"✅ Updated refresh interval to: 600 seconds (10 minutes)")
        print("\nThis helps avoid rate limiting by:")
        print("  • Reducing request frequency from every 5 min to every 10 min")
        print("  • Combined with 1-second delays between feeds")
        print("  • Using proper User-Agent headers")
        print("\n⚠️  You'll need to restart the server for this to take effect")

if __name__ == '__main__':
    asyncio.run(update_refresh_interval())
