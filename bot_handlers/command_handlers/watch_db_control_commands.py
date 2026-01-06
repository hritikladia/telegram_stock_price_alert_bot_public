from telegram import Update
from telegram.ext import ContextTypes
from data.watch_db_controls import pause_watch, resume_watch, delete_watch, edit_watch
from core.db_control_parser import parse_control_command

async def handle_control_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generic handler for all alert control commands (/pause, /resume, /delete, /edit)."""
    message = update.message
    user_id = message.from_user.id
    text = message.text.strip()

    parsed = parse_control_command(text)
    if not parsed:
        await message.reply_text("⚠️ Invalid command format. Try /list to see your watches.")
        return

    command = parsed["command"]
    watch_id = parsed["watch_id"]
    args = parsed.get("args", {})

    try:
        if command == "pause":
            pause_watch(watch_id, user_id)
            await message.reply_text(f"⏸️ Watch {watch_id} has been paused.")
        elif command == "resume":
            resume_watch(watch_id, user_id)
            await message.reply_text(f"▶️ Watch {watch_id} has been resumed.")
        elif command == "delete":
            delete_watch(watch_id, user_id)
            await message.reply_text(f"🗑️ Watch {watch_id} has been deleted.")
        elif command == "edit":
            field, value = args.get("field"), args.get("value")
            edit_watch(watch_id, user_id, field, value)
            await message.reply_text(f"🛠️ Watch {watch_id} updated: {field} → {value}")
        elif command == "snooze":
            await message.reply_text("⏰ Snooze feature not implemented yet.")
        else:
            await message.reply_text("⚠️ Unknown command.")
    except PermissionError as e:
        await message.reply_text(str(e))
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
