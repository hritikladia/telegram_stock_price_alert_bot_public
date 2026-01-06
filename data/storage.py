from datetime import datetime
from .supabase_client import supabase
from core.models import Watch

def add_watch(watch: Watch):
    """Insert a new watch into the database."""
    data = {
        "user_id": watch.user_id,
        "symbol": watch.symbol,
        "rule": watch.rule,
        "threshold": watch.threshold,
        "exchange": watch.exchange,
        "segment": watch.segment,
        'security_id': watch.security_id,
        "instrument_token": watch.instrument_token,
        "cooldown_minutes": getattr(watch, "cooldown_minutes", 5),
        "window_minutes": getattr(watch, "window_minutes", None),
        "last_triggered_at": watch.last_triggered_at,
        "last_triggered_state": watch.last_triggered_state,
    }

    result = supabase.table("watches").insert(data).execute()
    return result.data[0] if result.data else None


def list_user_watches(user_id: int):
    """Return all watches for a specific Telegram user."""
    result = supabase.table("watches").select("*").eq("user_id", user_id).execute()
    return result.data


def update_last_triggered(watch_id, active_state):
    """Update last triggered time and current active state in the database."""
    payload = {
        "last_triggered_at": datetime.utcnow().isoformat(timespec='microseconds'),
        "last_triggered_state": bool(active_state)
    }

    supabase.table("watches").update(payload).eq("id", watch_id).execute()


def list_all_watches():
    """Return all watches for all users."""
    result = supabase.table("watches").select("*").execute()
    return result.data
