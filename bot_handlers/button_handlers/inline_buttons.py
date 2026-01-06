#bot_handlers/inline_buttons.py
from telegram import Update
from telegram.ext import ContextTypes
from bot_handlers.command_handlers.list_command import list_command
from bot_handlers.command_handlers.watch_db_control_commands import handle_control_command
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks like 'list_alerts', 'pause_alert', etc."""
    query = update.callback_query
    await query.answer()

    data = query.data

    print(f"[DEBUG] callback_data received: {query.data}")

    if data == "list_alerts":
        await list_command(update, context)

    elif data == "test_alert":
        await query.message.reply_text("🚨 This is a sample test alert!")

    else:
        await query.message.reply_text("⚙️ Unknown action.")

