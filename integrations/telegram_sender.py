import os
import aiohttp
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


async def send_alert(watch, current_price, description: str):
    """
    Sends a Telegram alert to the user with a rule-provided description.
    This function is intentionally rule-agnostic — it just handles messaging.
    """

    user_id = watch["user_id"]
    symbol = watch["symbol"]

    text = (
        f"🚨 *{symbol}*\n"
        f"{description}\n\n"
        f"💰 Current price: *{current_price}*\n"
        f"⏱ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

    payload = {
        "chat_id": user_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(TELEGRAM_API_URL, json=payload) as response:
            if response.status != 200:
                body = await response.text()
                print(f"[!] Failed to send alert to user {user_id}: {body}")
            else:
                print(f"[✓] Alert sent to {user_id} for {symbol}")
