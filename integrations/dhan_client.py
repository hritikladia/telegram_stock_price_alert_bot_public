import asyncio
import websockets
import json

async def dhan_price_stream(queue):
    uri = "ws://localhost:8765"

    while True:
        try:
            async with websockets.connect(uri, ping_interval=30, ping_timeout=30) as websocket:
                print("✅ Connected to mock DhanHQ WebSocket")

                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await queue.put(data)
                    except json.JSONDecodeError:
                        print(f"⚠️ Invalid JSON: {message}")

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"⚠️ Connection closed (code {e.code}): {e}. Retrying in 3s...")
            await asyncio.sleep(3)
        except ConnectionRefusedError:
            print("🚫 Connection refused — is the mock server running? Retrying in 3s...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"⚠️ Unexpected error in dhan_price_stream: {e}")
            await asyncio.sleep(3)

