# rules/factory.py
from .above_rule import AboveRule
from .below_rule import BelowRule
from .percent_move_rule import PercentMoveRule
RULE_REGISTRY = {
    "ABOVE": AboveRule,
    "BELOW": BelowRule,
    "PERCENT_MOVE": PercentMoveRule,
    # Future: "CROSSES_ABOVE": CrossesAboveRule,
    #          "WITHIN_RANGE": RangeRule,
}

def create_rule_from_watch(watch):
    rule_type = watch["rule"].upper()
    rule_cls = RULE_REGISTRY.get(rule_type)

    if not rule_cls:
        raise ValueError(f"Unknown rule type: {rule_type}")

    if rule_type == "PERCENT_MOVE":
        return rule_cls(
            symbol=watch["symbol"],
            threshold_percent=watch["threshold"],
            window_minutes=watch.get("window_minutes", 10),
            cooldown_minutes=watch.get("cooldown_minutes", 5)
        )
    else:
        return rule_cls(
            symbol=watch["symbol"],
            threshold=watch["threshold"],
            cooldown_minutes=watch.get("cooldown_minutes", 5)
        )
