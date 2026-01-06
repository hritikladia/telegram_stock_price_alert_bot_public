from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def start_command(update, context):
    keyboard = [
        [InlineKeyboardButton("🆕 Create Alert", callback_data="create_alert")],
        [InlineKeyboardButton("📋 My Alerts", callback_data="list_alerts")]
    ]

    await update.message.reply_text(
        "👋 Welcome! I’ll help you track market movements.\nChoose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
