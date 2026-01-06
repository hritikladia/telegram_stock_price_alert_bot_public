from datetime import datetime, timedelta
from .base_rule import AlertRule

class PercentMoveRule(AlertRule):
    """
    Fires when the price changes by more than X% within a given time window.
    Example: alert if BTC changes ±3% within 10 minutes.
    """

    def __init__(self, symbol: str, threshold_percent: float, window_minutes: int = 10, cooldown_minutes: int = 5):
        super().__init__(symbol, threshold_percent, cooldown_minutes)
        self.window_minutes = window_minutes
        self.history = []  # in-memory cache of (timestamp, price) tuples

    def _update_history(self, price: float):
        """Keep only recent data within the window."""
        now = datetime.utcnow()
        self.history.append((now, price))
        cutoff = now - timedelta(minutes=self.window_minutes)
        self.history = [(t, p) for (t, p) in self.history if t >= cutoff]

    def condition_met(self, price: float) -> bool:
        """Return True if price moved more than threshold % in window."""
        self._update_history(price)

        if not self.history:
            return False

        oldest_time, oldest_price = self.history[0]
        if oldest_price == 0:
            return False

        pct_move = ((price - oldest_price) / oldest_price) * 100
        return abs(pct_move) >= self.threshold  # trigger on ±X% change

    def describe(self, price: float = None) -> str:
        direction = "UP" if price >= self.history[0][1] else "DOWN"
        return (
            f"{self.symbol} moved {direction} by more than {self.threshold:.2f}% "
            f"in the last {self.window_minutes} minutes "
            f"(current: {price})"
        )
