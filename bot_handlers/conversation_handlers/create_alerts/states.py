#bot_handlers/create_alert/states.py

# Conversation step identifiers
ASK_SEGMENT, ASK_EXCHANGE, ASK_SYMBOL, ASK_RULE, ASK_PARAM, ASK_WINDOW, ASK_COOLDOWN, CONFIRM = range(8)

# Human-readable rule names
RULES = {
    "ABOVE": "Price moves above the hreshold",
    "BELOW": "Price moves below the threshold",
    "PERCENT_MOVE": "% Moves in a time window"
}
