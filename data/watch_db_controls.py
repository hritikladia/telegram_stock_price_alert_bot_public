#core/alert_controls.py

from .supabase_client import supabase
# from datetime import datetime, timedelta

def pause_watch(watch_id, user_id):
    supabase.table("watches").update({"enabled": False}) \
        .eq("id", watch_id).eq("user_id", user_id).execute()

def resume_watch(watch_id, user_id):
    supabase.table("watches").update({
        "enabled": True,
        "last_triggered_state": False,
        "last_triggered_at": None  # reset to avoid instant re-fire
    }).eq("id", watch_id).eq("user_id", user_id).execute()

def delete_watch(watch_id, user_id):
    supabase.table("watches").delete().eq("id", watch_id).eq("user_id", user_id).execute()
    # or soft delete: update deleted_at=now()

def edit_watch(watch_id, user_id, field, value):
    allowed = {"threshold", "window_minutes", "cooldown_minutes", "rule"}  # extend later
    if field not in allowed:
        raise ValueError(f"Editable fields: {', '.join(sorted(allowed))}")
    # Cast numeric fields
    if field in {"threshold"}: value = float(value)
    if field in {"window_minutes", "cooldown_minutes"}: value = int(value)
    supabase.table("watches").update({field: value, "last_triggered_state": False}) \
        .eq("id", watch_id).eq("user_id", user_id).execute()