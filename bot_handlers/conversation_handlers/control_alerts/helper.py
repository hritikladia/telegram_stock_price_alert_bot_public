from data.watch_db_controls import pause_watch, resume_watch, delete_watch

def perform_alert_action(user_id, watch_id, action):
    """Route a user action to the correct database operation."""
    try:
        if action == "pause":
            pause_watch(watch_id, user_id)
        elif action == "resume":
            resume_watch(watch_id, user_id)
        elif action == "delete":
            delete_watch(watch_id, user_id)
        elif action == "edit":
            # For edit, you can later extend this to ask for field and value
            # For now, just acknowledge the command
            return False  # conversation not yet implemented
        else:
            return False
        return True
    except Exception as e:
        print(f"[perform_alert_action] Error during {action}: {e}")
        return False
