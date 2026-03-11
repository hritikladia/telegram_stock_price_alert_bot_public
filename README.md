Telegram Stock Price Alert Bot
A real-time Telegram bot for automated stock price alerts.

The bot monitors live market prices and triggers instant Telegram notifications when user-defined conditions are met.

It uses an event-driven rule engine that evaluates price ticks against alert conditions such as:

ABOVE price
BELOW price
PERCENT_MOVE
Designed for low-latency alerts, modular extensibility, and persistent watchlists.

Features
Real-time market monitoring
Automatic Telegram alerts when conditions trigger
Multiple rule types (ABOVE / BELOW / PERCENT_MOVE)
Cooldown protection to avoid duplicate alerts
Persistent watchlists stored in Supabase
Async event-driven architecture for fast evaluation
Modular Telegram command handlers
Example Usage
Users interact with the bot directly from Telegram.

Add alert
/watch RELIANCE ABOVE 2500
Add percentage move alert
/watch TCS PERCENT_MOVE 3
View active alerts
/list
Remove alert
/remove RELIANCE
Example Alert
🚨 Price Alert Triggered

Symbol: RELIANCE
Condition: ABOVE 2500
Current Price: 2504.10
Alerts are sent instantly when the rule engine detects a match.

System Architecture
The bot follows an event-driven pipeline where market data flows through rule evaluation before generating alerts.

                ┌─────────────────────┐
                │   Telegram Users    │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │   Telegram Bot API  │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │  Command Handlers   │
                │  (watch/list/etc)   │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │  Watchlist Manager  │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │    Supabase DB      │
                │  Alerts + Users     │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │   Market Feed       │
                │   (Dhan API)        │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │    Alert Engine     │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │     Rule Engine     │
                │ ABOVE / BELOW / %   │
                └─────────┬───────────┘
                          │
                          ▼
                ┌─────────────────────┐
                │  Telegram Sender    │
                └─────────────────────┘
Flow Summary
User creates alerts via Telegram
Alerts are stored in Supabase
Market data streams from the broker API
Alert engine evaluates incoming ticks
Rule engine checks conditions
Telegram notification is sent
Project Structure
bot.py
main.py

bot_handlers/
  command_handlers/
  conversation_handlers/
  button_handlers/

core/
  parser.py
  watchlist_manager.py
  models.py

engine/
  alert_engine.py

rules/
  above_rule.py
  below_rule.py
  percent_move_rule.py
  cooldown.py
  factory.py

integrations/
  dhan_client.py
  telegram_sender.py

data/
  supabase_client.py
  storage.py
Technology Stack
Component	Technology
Backend	Python
Messaging	Telegram Bot API
Async Processing	AsyncIO
Database	Supabase
Market Data	Dhan Broker API
Design Principles
Event-Driven Processing
Market price ticks trigger the evaluation pipeline immediately.

This minimizes latency between price change → alert delivery.

Modular Rule Engine
Alert logic is implemented as independent rule classes.

Current rules:

ABOVE
BELOW
PERCENT_MOVE
New rules can be added without modifying the core engine.

Cooldown Protection
Prevents alert spam by enforcing a cooldown period before the same alert can trigger again.

Persistent Watchlists
User alerts are stored in Supabase so the system:

survives bot restarts
supports multi-user alert management
maintains historical state
Modular Telegram Handlers
Telegram commands are separated into independent handler modules.

This makes it easier to:

add new commands
maintain conversations
extend bot capabilities
Running Locally
1. Install dependencies
pip install -r requirements.txt
2. Configure environment variables
TELEGRAM_BOT_TOKEN=
SUPABASE_URL=
SUPABASE_KEY=
3. Run the bot
python main.py
Possible Extensions
This architecture can easily be extended for:

Crypto price alerts
Forex monitoring
Arbitrage detection
Portfolio risk alerts
News-triggered trading signals
Author
Hritik Ladia

GitHub https://github.com/hritikladia

