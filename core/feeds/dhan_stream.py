import time
import asyncio
import threading
from typing import Dict, Tuple, List
from dhanhq import DhanContext, MarketFeed
from data.storage import list_all_watches


def dhan_feed_thread(dhan_ctx, instruments, routing_map, price_queue, main_loop):
    """
    Runs in a background thread.
    """
    import asyncio

    # Ensure this thread has an event loop (Dhan's MarketFeed expects it)
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    feed = MarketFeed(dhan_ctx, instruments, version="v2")
    print("Connecting to Dhan MarketFeed (thread)…")

    while True:
        try:
            feed.run_forever()

            msg = feed.get_data()
            if not msg:
                continue

            # DEBUG: see raw message
            # print("[Dhan raw]", msg)


            sec_id = str(msg.get("security_id"))
            ltp = msg.get("LTP") 
            ltt = msg.get('LTT')

            # print(sec_id, ltp)
            if sec_id in routing_map and ltp is not None:
                exch, symbol = routing_map[sec_id]
                update = {"symbol": symbol, "security_id": sec_id, "price": float(ltp), "LTT": ltt }
 

                print("[Dhan mapped tick]", update)  # DEBUG

                main_loop.call_soon_threadsafe(
                    price_queue.put_nowait, update
                )
        
        except Exception as e:
            print(f"[Dhan Feed Thread] error: {e}. Retrying…")
            time.sleep(10)
            continue


async def dhan_price_stream(client_id: str, access_token: str, price_queue: asyncio.Queue):
    """
    Async wrapper: prepares watch list, routing map, then starts 
    a dedicated Dhan websocket thread.
    """
    watches = list_all_watches()

    routing_map: Dict[str, Tuple[str, str]] = {}
    for w in watches:
        sec_id = str(w["security_id"])
        exch = w["exchange"]
        symbol = w["symbol"]
        routing_map[sec_id] = (exch, symbol)

    print(f"Found {len(routing_map)} instruments to subscribe.")
    print(routing_map)
    
    instruments = []
    for sec_id, (exch, _sym) in routing_map.items():
        instruments.append((MarketFeed.NSE, sec_id, MarketFeed.Ticker))

    # Create Dhan client
    dhan_ctx = DhanContext(client_id, access_token)

    main_loop = asyncio.get_running_loop()


    # --- START THREAD ---
    t = threading.Thread(
        target=dhan_feed_thread,
        args=(dhan_ctx, instruments, routing_map, price_queue, main_loop),
        daemon=True
    )
    t.start()

    print("Dhan feed thread started.")

    # Keep task alive forever
    while True:
        await asyncio.sleep(3600)
