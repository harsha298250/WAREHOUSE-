"""
alert_notifier.py — Mobile-first alert generation, MySQL-backed.
Formats reorder/shrinkage events as SMS/WhatsApp-style payloads — the
exact structure you'd hand to Twilio/WhatsApp Business API in production.
"""
import pandas as pd
from sqlalchemy import text
from backend.database import engine
from ml.forecast import forecast_item


def generate_reorder_alert_message(warehouse_id: str, item_id: str):
    r = forecast_item(warehouse_id, item_id)
    if not r or not r["needs_reorder"]:
        return None
    return {
        "channel": "whatsapp", "to_role": "warehouse_manager", "priority": "high",
        "message": (
            f"⚠️ REORDER ALERT — {warehouse_id}\n"
            f"{r['item_name']} ({item_id}): {r['current_stock']} units left "
            f"(reorder point {r['reorder_point']}).\n"
            f"Reason: {r['explanation']}\n"
            f"Reply CONFIRM to raise a purchase order."
        ),
    }


def generate_daily_digest(warehouse_id: str):
    items = pd.read_sql(text("SELECT DISTINCT item_id FROM stock_movements WHERE warehouse_id=:wh"),
                         engine, params={"wh": warehouse_id})
    reorder_msgs = []
    for iid in items["item_id"]:
        m = generate_reorder_alert_message(warehouse_id, iid)
        if m:
            reorder_msgs.append(m)
    if reorder_msgs:
        body = f"📋 Daily digest — {warehouse_id}\n{len(reorder_msgs)} item(s) need reorder today.\n" + \
               "\n".join(f"- {m['message'].splitlines()[1]}" for m in reorder_msgs[:5])
    else:
        body = f"📋 Daily digest — {warehouse_id}\nAll stock levels healthy today."
    return {"channel": "whatsapp_digest", "to_role": "warehouse_manager", "message": body}
