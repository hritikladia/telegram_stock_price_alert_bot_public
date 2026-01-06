import os
from dotenv import load_dotenv
load_dotenv()
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot_handlers.command_handlers.start_command import start_command
from bot_handlers.command_handlers.watch_commands import watch_command
from bot_handlers.command_handlers.list_command import list_command
from bot_handlers.conversation_handlers.create_alerts.create_conversation_handler import create_alert_conv
from bot_handlers.conversation_handlers.control_alerts.control_alerts_handler import manage_alert_conv
from bot_handlers.command_handlers.watch_db_control_commands import handle_control_command
from bot_handlers.button_handlers.inline_buttons import button_handler


async def start(update, context):
    await update.message.reply_text("Welcome! Use /watch SYMBOL above|below PRICE to set an alert.")

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("watch", watch_command))
    app.add_handler(CommandHandler("list", list_command))
    app.add_handler(CommandHandler(["pause", "resume", "delete", "edit", "snooze"], handle_control_command))
    
    app.add_handler(create_alert_conv)
    app.add_handler(manage_alert_conv)
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Telegram bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
