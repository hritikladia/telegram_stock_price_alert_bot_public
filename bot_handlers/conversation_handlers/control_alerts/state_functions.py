from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from .helper import perform_alert_action
from .states import ASK_ID

async def action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered when an action button is pressed (pause/resume/edit/delete)."""
    query = update.callback_query
    await query.answer()

    action = query.data.split(":")[1]  # e.g. "pause"
    context.user_data["action"] = action

    await query.message.reply_text(f"Please send the *ID* of the alert you want to {action}.", parse_mode="Markdown")
    return ASK_ID


async def process_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive the alert ID and perform the corresponding action."""
    user_id = update.message.from_user.id
    watch_id = update.message.text.strip()
    action = context.user_data.get("action")

    # Example: call your database or service layer
    success = perform_alert_action(user_id, watch_id, action)

    if success:
        await update.message.reply_text(f"✅ Successfully {action}d alert ID: {watch_id}.")
    else:
        await update.message.reply_text(f"⚠️ Could not {action} alert `{watch_id}`. Please check the ID.")
    
    return ConversationHandler.END


async def cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Action cancelled.")
    return ConversationHandler.END