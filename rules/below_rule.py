from .base_rule import AlertRule

class BelowRule(AlertRule):
    def condition_met(self, price: float) -> bool:
        return price < self.threshold

    def describe(self, price: float = None) -> str:
        if price:
            return f"{self.symbol} fell BELOW {self.threshold} (current {price})"
        return f"Triggers when {self.symbol} goes BELOW {self.threshold}"
