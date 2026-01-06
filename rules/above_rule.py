from .base_rule import AlertRule

class AboveRule(AlertRule):
    def condition_met(self, price: float) -> bool:
        return price > self.threshold

    def describe(self, price: float = None) -> str:
        if price:
            return f"{self.symbol} rose ABOVE {self.threshold} (current {price})"
        return f"Triggers when {self.symbol} goes ABOVE {self.threshold}"
