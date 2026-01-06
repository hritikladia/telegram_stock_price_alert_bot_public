from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Watch:
    id: int
    user_id: int
    symbol: str              # user-friendly (e.g., "RELIANCE")
    rule: str
    threshold: float
    exchange: str = "NSE"    # "NSE" | "BSE"
    security_id: int | None = None
    segment: str = "EQUITY"  # "EQUITY" | "INDEX" | "FNO"
    instrument_token: str | None = None
    window_minutes: int | None = None
    cooldown_minutes: int = 5
    last_triggered_at: Optional[datetime] = None
    last_triggered_state: bool = False  # optional new field for rule-specific cooldown
