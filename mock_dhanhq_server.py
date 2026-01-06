import asyncio
import random
import json
import websockets
from datetime import datetime

async def mock_price_feed(websocket, path):
    symbols = ["AAPL", "TSLA", "GOOG"]
    prices = {s: random.uniform(90, 110) for s in symbols}
    client = websocket.remote_address
    print(f"📡 New client connected from {client}")

    try:
        while True:
            updates = []
            for s in symbols:
                # Random walk in price
                change = random.uniform(-0.5, 0.5)
                prices[s] = max(1, prices[s] + change)
                update = {"symbol": s, "price": round(prices[s], 2)}
                updates.append(update)

                # Send each update as JSON
                await websocket.send(json.dumps(update))

            # Pretty console log
            timestamp = datetime.now().strftime("%H:%M:%S")
            printable = ", ".join([f"{u['symbol']}: {u['price']}" for u in updates])
            print(f"[{timestamp}] Sent → {printable}")

            await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client {client} disconnected — closing connection cleanly.")
    except Exception as e:
        print(f"⚠️ Unexpected error in connection handler ({client}): {e}")

async def main():
    print("🚀 Mock DhanHQ WebSocket running on ws://localhost:8765")
    async with websockets.serve(mock_price_feed, "localhost", 8765, ping_interval=None):
        await asyncio.Future()  # Keep running forever

if __name__ == "__main__":
    asyncio.run(main())
