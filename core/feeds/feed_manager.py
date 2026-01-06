import asyncio
import threading
import time
from dhanhq import DhanContext, MarketFeed

class FeedManager:
    """
    FeedManager that subscribes dynamically to symbols
    based on WatchlistManager updates.
    """

    def __init__(self, client_id, access_token, instruments, watchlist_mgr):
        self.client_id = client_id
        self.access_token = access_token
        self.instruments = instruments  # initial instrument universe (NSE EQ, IDX)
        self.watchlist_mgr = watchlist_mgr

        self.price_queue = asyncio.Queue()
        self._thread = None
        self._feed = None
        self._stopped = False
        self._main_loop = None

        # Track live subscriptions
        self.subscribed_ids = set()
        self.last_tick_time = time.time()
    # ────────────────────────────────
    #  Public lifecycle methods
    # ────────────────────────────────

    def start(self):
        print("[FeedManager] Starting…")
        self._main_loop = asyncio.get_running_loop()

        # Start websocket feed in background thread
        self._thread = threading.Thread(target=self._thread_run, daemon=True)
        self._thread.start()

        # Immediately sync with current watchlist once
        self._main_loop.create_task(self._initial_sync())
        # Start heartbeat monitor (in main loop)
        self._main_loop.create_task(self._heartbeat())
        # Start async watchlist monitor for future changes
        self._main_loop.create_task(self._monitor_watchlist_changes())

        print("[FeedManager] Started.")


    def stop(self):
        print("[FeedManager] Stopping…")
        self._stopped = True
        if self._feed:
            self._feed.disconnect()
        print("[FeedManager] Stopped.")

    
    # ────────────────────────────────
    #  Thread: websocket loop
    # ────────────────────────────────

    def _thread_run(self):
        # Dhan requires a local event loop for its websocket
        thread_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(thread_loop)

        ctx = DhanContext(self.client_id, self.access_token)
        # Start empty: we'll dynamically subscribe later
        self._feed = MarketFeed(ctx, [], version="v2")

        print("[FeedManager] Feed thread connected (dynamic mode).")
        retry_delay = 5
        while not self._stopped:
            try:
                self._feed.run_forever()
                msg = self._feed.get_data()
                if not msg:
                    continue

                sec_id = str(msg.get("security_id"))
                ltp = msg.get("LTP")
                ltt = msg.get("LTT")
                # print('[FeedManager] Raw', msg)
                # Forward only if still watched
                if not self.watchlist_mgr.has(sec_id):
                    continue

                if sec_id and ltp is not None:
                    update = {"security_id": sec_id, "price": float(ltp), "LTT": ltt}
                    print('[FeedManager] Mapped Tick', update)
                    self._main_loop.call_soon_threadsafe(
                        self.price_queue.put_nowait, update
                    )
                retry_delay = 5
            except Exception as e:
                print(f"[FeedManager] Feed thread error: {e}. Retrying in {retry_delay}s")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay*2, 60) # exponential back off

        print("[FeedManager] Feed thread exiting.")
    
    def _restart_feed(self):
        print("[FeedManager] Restarting feed thread...")
        try:
            self._stopped = True
            if self._feed:
                self._feed.disconnect()

            if self._thread and self._thread.is_alive():
                print("[FeedManager] Waiting for old feed thread to stop…")
                self._thread.join(timeout=5)
        except Exception as e:
            print("[FeedManager] Error while stopping old thread:", e)

        # reset state and start again
        self._stopped = False
        self._thread = threading.Thread(target=self._thread_run, daemon=True)
        self._thread.start()

    async def _heartbeat(self):
        while not self._stopped:
            await asyncio.sleep(30)
            delta = time.time() - self.last_tick_time
            if delta > 60:
                print(f"⚠️ [FeedManager] No tick for {int(delta)}s — reconnecting...")
                self._restart_feed()
            else:
                print(f"✅ [FeedManager] Alive ({len(self.subscribed_ids)} subs, last tick {int(delta)}s ago)")

    # ────────────────────────────────
    #  Subscription sync logic
    # ────────────────────────────────
    async def _initial_sync(self):
        """Sync current watchlist immediately on startup."""
        await asyncio.sleep(1)  # small delay to let thread connect
        desired_ids = self.watchlist_mgr.get_all_security_ids()
        for sec_id in desired_ids:
            self._subscribe_id(sec_id)
        self.subscribed_ids = desired_ids.copy()
        print(f"[FeedManager] Initial sync complete. Subscribed {len(desired_ids)} instruments.")

    async def _monitor_watchlist_changes(self):
        """Monitors watchlist for updates and syncs subscriptions."""
        print("[FeedManager] Watching for watchlist updates…")
        while not self._stopped:
            await self.watchlist_mgr.on_change.wait()
            self.watchlist_mgr.on_change.clear()
            await asyncio.sleep(0.5)  # debounce multiple DB events

            desired_ids = self.watchlist_mgr.get_all_security_ids()
            to_sub = desired_ids - self.subscribed_ids
            to_unsub = self.subscribed_ids - desired_ids

            for sec_id in to_sub:
                self._subscribe_id(sec_id)
            for sec_id in to_unsub:
                self._unsubscribe_id(sec_id)

            self.subscribed_ids = desired_ids.copy()
            print(f"[FeedManager] Sync complete. Active subs: {len(self.subscribed_ids)}")
            print(f'[FeedManager]', self.watchlist_mgr.get_all_security_ids())

    def _subscribe_id(self, sec_id):
        """Send subscription to Dhan feed if connected."""
        if not self._feed:
            return
        self._feed.subscribe_symbols([(MarketFeed.NSE, sec_id, MarketFeed.Ticker)])
        print(f"✅ Subscribed {sec_id}")

    def _unsubscribe_id(self, sec_id):
        """Send unsubscription to Dhan feed."""
        if not self._feed:
            return
        self._feed.unsubscribe_symbols([(MarketFeed.NSE, sec_id, MarketFeed.Ticker)])
        print(f"❌ Unsubscribed {sec_id}")
