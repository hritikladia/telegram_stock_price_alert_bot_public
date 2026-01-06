import asyncio
from supabase import create_client
from realtime import AsyncRealtimeClient



class WatchlistManager:
    def __init__(self, supabase_url: str, supabase_key: str, table: str = "watches"):
        self.supabase = create_client(supabase_url, supabase_key)
        # convert to wss websocket URL
        domain = supabase_url.replace("https://", "")
        self.ws_url = f"wss://{domain}/realtime/v1/websocket"
        self.key = supabase_key
        self.table = table

        self.WATCHLIST = {}
        self.on_change = asyncio.Event()

        self.realtime = None
        self.channel = None

    def load_all(self):
        resp = self.supabase.table(self.table).select("*").execute()
        self.WATCHLIST = {}
        for w in resp.data:
            sec_id = str(w["security_id"])
            self.WATCHLIST.setdefault(sec_id, []).append(w)
        print("[Watchlist] Loaded", len(resp.data), "watches")

    async def start_realtime(self):
        """Keeps the realtime listener connected forever."""
        while True:
            try:
                print("[Watchlist] Connecting to Supabase Realtime...")
                self.realtime = AsyncRealtimeClient(self.ws_url, self.key)
                await self.realtime.connect()

                topic = f"realtime:public:{self.table}"
                self.channel = self.realtime.channel(topic)

                self.channel.on_postgres_changes(
                    event="*",
                    schema="public",
                    table=self.table,
                    callback=self._handle_event
                )
                await self.channel.subscribe()
                print("[Watchlist] Realtime listener started for table:", self.table)

                # this blocks until connection breaks
                await self.realtime.listen()

            except Exception as e:
                print("[Watchlist] ⚠️ Realtime connection error:", e)

            # if we reach here, connection is closed
            print("[Watchlist] 🔁 Attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)


    def _handle_event(self, payload):
        print('[Watchlist] recieved:', payload)
        # print(f"[Watchlist] Event received: {payload.get('eventType')}")
        try:
            # Supabase AsyncRealtimeClient format:
            data = payload.get("data", {})
            event = data.get("type")  # e.g. "INSERT", "UPDATE", "DELETE"
            record = data.get("record", {}) or {}
            old_record = data.get("old_record", {}) or {}

            print(f"[Watchlist] Event received: {event}")
            print('[Watchlist] old record', old_record)
            print('[Watchlist] new record', record)
            if event == "INSERT" and record:
                sec_id = str(record.get("security_id"))
                if sec_id:
                    self.WATCHLIST.setdefault(sec_id, []).append(record)
                    print(f"➕ Insert {sec_id}")
                    print('[Watchlist] updated', self.get_all_security_ids())


            elif event == "UPDATE" and record:
                sec_id = str(record.get("security_id"))
                if sec_id in self.WATCHLIST:
                    for i, w in enumerate(self.WATCHLIST[sec_id]):
                        if w["id"] == old_record.get("id"):
                            self.WATCHLIST[sec_id][i] = record
                            print(f"✏️ Update {sec_id}")
                            print('[Watchlist] updated', self.get_all_security_ids())
                            break

            elif event == "DELETE" and old_record:
                deleted_id = old_record.get("id")

                # find which sec_id this id belongs to
                sec_id = None
                for s, watches in self.WATCHLIST.items():
                    for w in watches:
                        if w["id"] == deleted_id:
                            sec_id = s
                            break
                    if sec_id:
                        break

                if sec_id:
                    self.WATCHLIST[sec_id] = [
                        w for w in self.WATCHLIST[sec_id] if w["id"] != deleted_id
                    ]
                    if not self.WATCHLIST[sec_id]:
                        del self.WATCHLIST[sec_id]
                    print(f"🗑 Delete watch id {deleted_id} under {sec_id}")
                else:
                    print(f"⚠️ Could not find sec_id for deleted id={deleted_id}")

                print("[Watchlist] Current IDs:", list(self.WATCHLIST.keys()))

                print('[Watchlist] updated', self.get_all_security_ids())

            print("[Watchlist] Current IDs:", list(self.WATCHLIST.keys()))
            self.on_change.set()

        except Exception as e:
            print("[Watchlist] ERROR in event handler:", e)
            import traceback; traceback.print_exc()

    def get_all_security_ids(self):
        return set(self.WATCHLIST.keys())

    def get_watches_for(self, sec_id):
        return self.WATCHLIST.get(str(sec_id), [])

    def has(self, sec_id):
        return str(sec_id) in self.WATCHLIST
