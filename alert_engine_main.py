import asyncio
from integrations.dhan_client import dhan_price_stream
from engine.alert_engine import alert_engine

async def run_alert_engine():
    price_queue = asyncio.Queue()

    await asyncio.gather(
        dhan_price_stream(price_queue),
        alert_engine(price_queue)
    )

if __name__ == "__main__":
    asyncio.run(run_alert_engine())
