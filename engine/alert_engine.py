# import asyncio
# from data.storage import list_all_watches, update_last_triggered
# from rules.factory import create_rule_from_watch
# from integrations.telegram_sender import send_alert
# from datetime import datetime

# async def alert_engine(price_stream):
#     print("⚡ Alert engine started and waiting for updates...")
#     while True:
#         print("Waiting for update from queue…")

#         update = await price_stream.get()
#         security_id, price, time = update["security_id"], update["price"], update['LTT']
#         # print(update)
#         print(f"[QUEUE GET] security_id={security_id}, price={price}, time = {time}")
        
#         watches = list_all_watches()
#         for w in watches:
#             if w["security_id"] != security_id:
#                 continue

#             try:
#                 rule = create_rule_from_watch(w)
#                 if rule.should_trigger(price, w):
#                     await send_alert(w, price, rule.describe(price))
#                     update_last_triggered(w["id"], True)
#                 elif not rule.condition_met(price):
#                     # Reset only when condition becomes false again
#                     update_last_triggered(w["id"], False)

#             except Exception as e:
#                 print(f"Error evaluating rule {w}: {e}")

import asyncio
from rules.factory import create_rule_from_watch
from integrations.telegram_sender import send_alert
from data.storage import update_last_triggered

async def alert_engine(price_stream, wl_manager):
    print("⚡ Alert engine started and waiting for updates...")
    while True:
        print("Waiting for update from queue…")
        update = await price_stream.get()
        security_id = update.get("security_id")
        price = update.get("price")
        time = update.get("LTT")
        # print(f"[QUEUE GET] security_id={security_id}, price={price}, time = {time}")
        # Optionally time or additional data

        # Instead of querying DB, fetch watches from in-memory watchlist
        watches = wl_manager.get_watches_for(security_id)
        if not watches:
            continue  # no watch for this security_id

        for w in watches:
            try:
                rule = create_rule_from_watch(w)
                if rule.should_trigger(price, w):
                    await send_alert(w, price, rule.describe(price))
                    update_last_triggered(w["id"], True)
                elif not rule.condition_met(price):
                    # Reset only when condition becomes false again
                    update_last_triggered(w["id"], False)

            except Exception as e:
                print(f"Error evaluating rule {w}: {e}")


# import asyncio
# import time
# from rules.factory import create_rule_from_watch
# from integrations.telegram_sender import send_alert
# from data.storage import update_last_triggered

# async def alert_engine(price_stream, wl_manager):
#     print("⚡ [AlertEngine] Started and waiting for updates...")
#     tick_count = 0
#     last_log = time.time()

#     while True:
#         try:
#             update = await asyncio.wait_for(price_stream.get(), timeout=30)
#             security_id = update.get("security_id")
#             price = update.get("price")
#             tick_time = update.get("LTT")

#             watches = wl_manager.get_watches_for(security_id)
#             if not watches:
#                 continue

#             for w in watches:
#                 try:
#                     rule = create_rule_from_watch(w)
#                     if rule.should_trigger(price, w):
#                         await send_alert(w, price, rule.describe(price))
#                         update_last_triggered(w["id"], True)
#                     elif not rule.condition_met(price):
#                         update_last_triggered(w["id"], False)
#                 except Exception as e:
#                     print(f"[AlertEngine] Error evaluating rule {w}: {e}")

#             tick_count += 1
#             if tick_count % 100 == 0 or time.time() - last_log > 60:
#                 print(f"💡 [AlertEngine] Processed {tick_count} ticks. Queue size: {price_stream.qsize()}")
#                 last_log = time.time()

#         except asyncio.TimeoutError:
#             print("⚠️ [AlertEngine] No new prices in 30s — alive and waiting.")
#         except Exception as e:
#             print(f"[AlertEngine] Fatal loop error: {e}")
#             import traceback; traceback.print_exc()
#             await asyncio.sleep(2)
