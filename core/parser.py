from .models import Watch
from rules.factory import RULE_REGISTRY  # dynamically loads all registered rules

def parse_watch_command(user_id: int, text: str, next_id: int) -> Watch:
    """
    Parse Telegram command of the form:
        /watch SYMBOL RULE PRICE [EXTRA_ARGS...]

    Examples:
        /watch AAPL above 100
        /watch TSLA below 200
        /watch BTC percent_move 3 10
    """

    parts = text.strip().split()

    if len(parts) < 4:
        raise ValueError("Invalid format. Use: /watch SYMBOL RULE PRICE [extra args]")

    cmd, symbol, rule_name, *args = parts

    if cmd.lower() != "/watch":
        raise ValueError("Command must start with /watch")

    rule_name = rule_name.upper()
    allowed_rules = tuple(RULE_REGISTRY.keys())

    if rule_name not in allowed_rules:
        raise ValueError(f"Unknown rule '{rule_name}'. Allowed: {', '.join(allowed_rules)}")

    # --- Parse numeric arguments ---
    try:
        numeric_args = list(map(float, args))
    except ValueError:
        raise ValueError("Threshold and other parameters must be numeric")

    if len(numeric_args) == 0:
        raise ValueError("Missing threshold argument")

    # --- Rule-specific argument mapping ---
    extra = {}

    if rule_name in ("ABOVE", "BELOW"):
        threshold = numeric_args[0]

    elif rule_name == "PERCENT_MOVE":
        # Format: /watch BTC percent_move 3 10
        # → move >=3% within 10 minutes
        if len(numeric_args) < 2:
            raise ValueError("Usage: /watch SYMBOL percent_move PERCENT WINDOW_MINUTES")
        threshold = numeric_args[0]
        extra["window_minutes"] = int(numeric_args[1])

    else:
        threshold = numeric_args[0]  # fallback for unknown rule types

    # --- Construct the Watch dataclass ---
    return Watch(
        id=next_id,
        user_id=user_id,
        symbol=symbol.upper(),
        rule=rule_name,
        threshold=threshold,
        last_triggered_at=None,
        last_triggered_state=False,
        **extra  # dynamically add optional fields like window_minutes
    )


