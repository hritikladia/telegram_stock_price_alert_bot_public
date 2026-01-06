from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.helpers import escape_markdown
from data.storage import list_user_watches

from html import escape

def safe_html(text: str) -> str:
    return escape(str(text)) if text is not None else ""

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        send_func = query.message.reply_text
    else:
        user_id = update.message.from_user.id
        send_func = update.message.reply_text

    watches = list_user_watches(user_id)

    if not watches:
        await send_func("📭 You don’t have any active alerts yet.")
        return

    msg_lines = []
    for w in watches:
        watch_id = safe_html(w.get("id", "?"))
        symbol = safe_html(w.get("symbol", "N/A"))
        rule = safe_html(w.get("rule", "UNKNOWN"))
        threshold = safe_html(w.get("threshold", "—"))
        enabled = "✅" if w.get("enabled", True) else "⏸️"
        cooldown = w.get("cooldown_minutes")
        last = w.get("last_triggered_at")
        window_minutes = w.get("window_minutes")

        line = f"{enabled} <b>ID:</b> <code>{watch_id}</code> | <b>{symbol}</b> {rule} {threshold}"
        if window_minutes:
            line += f" | ⏳ {safe_html(window_minutes)}m window"
        if cooldown:
            line += f" | ⏱ {safe_html(cooldown)}m cooldown"
        if last:
            line += f" | Last: {safe_html(last.split('T')[0])}"

        msg_lines.append(line)

    msg = "\n".join(msg_lines)
    header = "📋 <b>Your Watches:</b>"

    keyboard = [
        [
            InlineKeyboardButton("⏸ Pause", callback_data="action:pause"),
            InlineKeyboardButton("▶ Resume", callback_data="action:resume"),
        ],
        [
            # InlineKeyboardButton("✏ Edit", callback_data="action:edit"),
            InlineKeyboardButton("🗑 Delete", callback_data="action:delete"),
            InlineKeyboardButton("🆕 Add More Alerts", callback_data="create_alert")
        ]
    ]

    await send_func(
        f"{header}\n\n{msg}\n\n<i>Select an action below</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
