from abc import ABC, abstractmethod
from rules.cooldown import CooldownManager

class AlertRule(ABC):
    """
    Abstract base class for all alert rules.
    Handles cooldown logic, state change tracking, and description interface.
    """

    def __init__(self, symbol: str, threshold: float, cooldown_minutes: int = 5):
        self.symbol = symbol
        self.threshold = threshold
        self.cooldown = CooldownManager(cooldown_minutes)

    # --- Rule-specific condition ---
    @abstractmethod
    def condition_met(self, price: float) -> bool:
        """Return True if the rule’s condition is satisfied (e.g., price > threshold)."""
        pass

    # --- Unified trigger logic ---
    def should_trigger(self, price: float, watch: dict) -> bool:
        """
        Determine whether an alert should be triggered.
        Combines condition, cooldown, and state tracking.
        """
        
        # Skip trigger if disabled
        if not watch.get("enabled", True):
            return False
        
        condition = self.condition_met(price)
        prev_state = watch.get("last_triggered_state", False)
        last_time = watch.get("last_triggered_at")

        # Case 1: Condition no longer met → reset state (so future alerts can re-fire)
        if not condition and prev_state:
            return False

        # Case 2: Condition met but cooldown still active → suppress duplicate alert
        if condition and not self.cooldown.is_cooldown_over(last_time):
            return False

        # Case 3: Condition met, cooldown expired, and was previously inactive → fire alert
        if condition and not prev_state:
            return True

        # Case 4: Condition true but was already active (no reset yet) → skip
        return False

    # --- Description interface ---
    @abstractmethod
    def describe(self, price: float = None) -> str:
        """
        Return a human-readable description of what just happened.
        Example: "BTC rose ABOVE 45000 (current 45120)"
        """
        pass
