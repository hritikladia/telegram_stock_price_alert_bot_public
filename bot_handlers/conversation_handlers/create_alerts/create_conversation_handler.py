# handlers/create_alert/conversation.py

from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    CommandHandler,
    filters
)
from .states import ASK_SYMBOL, ASK_EXCHANGE, ASK_SEGMENT, ASK_RULE, ASK_PARAM, ASK_WINDOW, ASK_COOLDOWN, CONFIRM
from .state_functions import (
    start_create_alert,
    ask_exchange,
    ask_symbol,
    ask_rule,
    ask_param,
    ask_window,
    ask_cooldown,
    confirm,
    save_alert,
    cancel
)
from .state_functions import handle_symbol_input

create_alert_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_create_alert, pattern="^create_alert$")],
    states={
        ASK_SEGMENT: [CallbackQueryHandler(ask_exchange, pattern="^seg:")],
        ASK_EXCHANGE: [CallbackQueryHandler(ask_symbol, pattern="^ex:")],
        ASK_SYMBOL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_input),
            CallbackQueryHandler(ask_rule, pattern="^symbol:")
        ],
        ASK_RULE: [CallbackQueryHandler(ask_param, pattern="^rule:")],
        ASK_PARAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_window)],
        ASK_WINDOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_cooldown)],
        ASK_COOLDOWN: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        CONFIRM: [CallbackQueryHandler(save_alert, pattern="^(confirm_create|cancel_create)$")],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=False
)



