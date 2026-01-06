from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from core.models import Watch
from data.storage import add_watch
from .states import (
    ASK_SEGMENT, ASK_EXCHANGE, ASK_SYMBOL, ASK_RULE, ASK_PARAM,
    ASK_WINDOW, ASK_COOLDOWN, CONFIRM, RULES
)
from rules.factory import RULE_REGISTRY
from data.instrument_map import search_symbols, get_security_details

# -------------------------------------
# Step 1: Start alert creation
# -------------------------------------
async def start_create_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    keyboard = [
        [
            InlineKeyboardButton("📈 Equity", callback_data="seg:E"),
            InlineKeyboardButton("📊 Indices", callback_data="seg:I"),
            InlineKeyboardButton("⚙️ F&O", callback_data="seg:FNO"),
        ]
    ]

    await update.callback_query.message.reply_text(
        "💡 Let's create your alert!\n\nSelect a *segment*:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ASK_SEGMENT


# -------------------------------------
# Step 2: Ask exchange (after segment)
# -------------------------------------
async def ask_exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    segment = query.data.split(":")[1]
    context.user_data["segment"] = segment

    keyboard = [
        [
            InlineKeyboardButton("NSE", callback_data="ex:NSE"),
            InlineKeyboardButton("BSE", callback_data="ex:BSE"),
        ]
    ]

    await query.edit_message_text(
        f"Segment set to *{segment}*.\n\nChoose exchange:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ASK_EXCHANGE


# -------------------------------------
# Step 3: Ask symbol input
# -------------------------------------
async def ask_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    exchange = query.data.split(":")[1]
    context.user_data["exchange"] = exchange

    await query.edit_message_text(
        f"Exchange set to *{exchange}*.\n\nEnter the *symbol or name* of the instrument:",
        parse_mode="Markdown"
    )
    return ASK_SYMBOL


# -------------------------------------
# Step 4: Ask rule type
# -------------------------------------
async def ask_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, symbol, exchange, seg = query.data.split(":")
    context.user_data.update({
        "symbol": symbol,
        "exchange": exchange,
        "segment": seg
    })

    # Enrich with security_id
    sec = get_security_details(symbol, segment_filter=seg, exchange_filter=exchange)
    print(sec)
    if sec:
        security_id, exch_seg, seg_code = sec
        context.user_data["security_id"] = security_id
        context.user_data["exchange_segment"] = exch_seg
    else:
        context.user_data["security_id"] = None

    keyboard = [
        [InlineKeyboardButton("📈 Alert when price moves ABOVE a level", callback_data="rule:ABOVE")],
        [InlineKeyboardButton("📉 Alert when price moves BELOW a level", callback_data="rule:BELOW")],
        [InlineKeyboardButton("📊 Alert when price moves by a percentage", callback_data="rule:PERCENT_MOVE")],
    ]


    await query.edit_message_text(
        f"✅ *{symbol}* selected.\n\nChoose alert rule:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ASK_RULE


# -------------------------------------
# Step 5: Ask parameter
# -------------------------------------
async def ask_param(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    rule_type = query.data.split(":")[1]
    context.user_data["rule_type"] = rule_type

    if rule_type == ("ABOVE" or "BELOW") :
        text = "Enter the *threshold price level* to watch (e.g., 200.5):"
    else:
        text = "Enter the *% change* threshold (e.g., 5 for ±5%):"

    await query.edit_message_text(text, parse_mode="Markdown")
    return ASK_PARAM


# -------------------------------------
# Step 6: Ask window / cooldown
# -------------------------------------
async def ask_window(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["param"] = update.message.text.strip()

    if context.user_data["rule_type"] == "percent":
        await update.message.reply_text(
            "⏱️ Over how many minutes should this % move be checked? (default = 60):",
            parse_mode="Markdown"
        )
        return ASK_WINDOW

    await update.message.reply_text(
        "Set *cooldown* between alerts in minutes (default = 5):",
        parse_mode="Markdown"
    )
    return ASK_COOLDOWN


async def ask_cooldown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["rule_type"] == "percent" and "window_minutes" not in context.user_data:
        text = update.message.text.strip()
        window = int(text) if text.isdigit() else 60
        context.user_data["window_minutes"] = window

        await update.message.reply_text(
            "Set *cooldown* between alerts in minutes (default = 5):",
            parse_mode="Markdown"
        )
        return ASK_COOLDOWN

    cooldown_text = update.message.text.strip()
    cooldown = int(cooldown_text) if cooldown_text.isdigit() else 5
    context.user_data["cooldown"] = cooldown
    return await confirm(update, context)


# -------------------------------------
# Step 7: Confirm and save
# -------------------------------------
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cooldown_text = update.message.text.strip()
    cooldown = int(cooldown_text) if cooldown_text.isdigit() else 5
    context.user_data["cooldown"] = cooldown

    summary = (
        f"✅ *Confirm your alert:*\n\n"
        f"Symbol: `{context.user_data['symbol']}` ({context.user_data['exchange']})\n"
        f"Segment: `{context.user_data['segment']}`\n"
        f"Rule: {RULES[context.user_data['rule_type']]}\n"
        f"Threshold: `{context.user_data['param']}`\n"
        f"Cooldown: `{cooldown} min`\n\n"
        "Create this alert?"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Create", callback_data="confirm_create"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_create")
        ] 
    ]

    await update.message.reply_text(summary, parse_mode="Markdown",
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    return CONFIRM


async def save_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_create":
        rule_type = context.user_data["rule_type"]
        window = context.user_data.get("window_minutes", 60 if rule_type == "percent" else None)

        watch = Watch(
            id=None,
            user_id=query.from_user.id,
            symbol=context.user_data["symbol"].upper(),
            rule=rule_type,
            threshold=float(context.user_data["param"]),
            cooldown_minutes=int(context.user_data["cooldown"]),
            window_minutes=window,
            exchange=context.user_data.get("exchange"),
            segment=context.user_data.get("segment"),
            security_id=context.user_data.get("security_id"),
            last_triggered_at=None,
            last_triggered_state=False,
        )

        add_watch(watch)

        keyboard = [
            [InlineKeyboardButton("🔥 Test Alert", callback_data="test_alert")],
            [InlineKeyboardButton("📋 My Alerts", callback_data="list_alerts")],
            [InlineKeyboardButton("🪄 Create More Alerts", callback_data="create_alert")]
        ]

        await query.edit_message_text(
            f"🎯 Alert created successfully for *{watch.symbol}*!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.edit_message_text("🚫 Alert creation cancelled.")

    context.user_data.clear()
    return ConversationHandler.END


# -------------------------------------
# Fallback cancel
# -------------------------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Alert creation cancelled.")
    return ConversationHandler.END

# -------------------------------------
# show buttons for fethced search results
# -------------------------------------
async def handle_symbol_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user text input for symbol search.
    Uses previously selected segment and exchange to filter suggestions.
    """
    query = update.message.text.strip().upper()
    segment = context.user_data.get("segment")
    exchange = context.user_data.get("exchange")

    results = search_symbols(
        query,
        segment_filter=segment,
        exchange_filter=exchange,
        limit=5
    )

    if not results:
        await update.message.reply_text("No matches found. Please try a different prefix.")
        return ASK_SYMBOL

    # Build inline keyboard of suggestions
    keyboard = []
    for sym, exch, seg in results:
        keyboard.append([InlineKeyboardButton(f"{sym} ({exch})", callback_data=f"symbol:{sym}:{exch}:{seg}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select the correct symbol:", reply_markup=reply_markup)
    return ASK_SYMBOL

