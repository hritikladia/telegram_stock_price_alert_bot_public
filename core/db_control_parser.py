#core/db_control_parser.py
import re
from typing import Tuple, Optional, Dict

VALID_COMMANDS = {"pause", "resume", "delete", "edit", "snooze"}

def parse_control_command(text: str) -> Optional[Dict]:
    """
    Parse a user control command like:
      /pause 12
      /resume 5
      /delete 3
      /edit 7 threshold 200
      /edit 10 window_minutes 15
      /snooze 4 60

    Returns a dict:
      {
        "command": "pause",
        "watch_id": 12,
        "args": {"field": "threshold", "value": 200}
      }

    Returns None if the command is invalid.
    """
    text = text.strip()
    if not text.startswith("/"):
        return None

    parts = text[1:].split()
    if not parts:
        return None

    command = parts[0].lower()
    if command not in VALID_COMMANDS:
        return None

    try:
        watch_id = int(parts[1])
    except (IndexError, ValueError):
        return None

    # Handle /edit and /snooze which take extra arguments
    args = {}
    if command == "edit":
        if len(parts) < 4:
            return None
        field, value = parts[2], parts[3]
        args = {"field": field, "value": value}
        
    return {"command": command, "watch_id": watch_id, "args": args}
