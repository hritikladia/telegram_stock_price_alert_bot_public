from datetime import datetime, timedelta

class CooldownManager:
    def __init__(self, cooldown_minutes: int = 5):
        self.cooldown = timedelta(minutes=cooldown_minutes)

    def is_cooldown_over(self, last_triggered_time: str | None) -> bool:
        if not last_triggered_time:
            return True
        
        last_time = datetime.fromisoformat(last_triggered_time)
        return datetime.utcnow() - last_time > self.cooldown
