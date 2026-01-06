from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters
)
from .state_functions import action_callback, process_action, cancel_action
from .states import ASK_ID

manage_alert_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(action_callback, pattern=r"^action:")],
    states={
        ASK_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_action)],
    },
    fallbacks=[CommandHandler("cancel", cancel_action)],
)