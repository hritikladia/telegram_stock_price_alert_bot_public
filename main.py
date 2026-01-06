import os
import asyncio
from core.watchlist_manager import WatchlistManager
from core.feeds.feed_manager import FeedManager
from engine.alert_engine import alert_engine
from dotenv import load_dotenv
load_dotenv() 

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")


async def main():
    watch_mgr = WatchlistManager(SUPABASE_URL, SUPABASE_KEY)
    watch_mgr.load_all()
    await watch_mgr.start_realtime()
    print(watch_mgr.get_all_security_ids())
    feed_mgr = FeedManager(DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN, [], watch_mgr)
    feed_mgr.start()

    await alert_engine(feed_mgr.price_queue, watch_mgr)

if __name__ == "__main__":
    asyncio.run(main())
