"""
access_anomaly.py — Access-anomaly detection on REAL system activity.
Unlike the earlier demo version, this reads genuine rows from access_log
(populated automatically by backend/main.py every time someone logs in
or performs an action) instead of simulated data. Flags: off-hours
activity, and abnormally high edit-frequency bursts in a short window.
"""
import pandas as pd
from sqlalchemy import text
from backend.database import engine

NORMAL_HOURS = (7, 21)          # 7 AM – 9 PM treated as normal business hours
BURST_WINDOW_MINUTES = 10
BURST_THRESHOLD = 8              # more than 8 actions in 10 minutes = burst


def detect_access_anomalies():
    df = pd.read_sql(text("SELECT * FROM access_log ORDER BY timestamp"), engine)
    if df.empty:
        return []

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour

    flags = []
    # off-hours check
    for _, row in df[(df["hour"] < NORMAL_HOURS[0]) | (df["hour"] >= NORMAL_HOURS[1])].iterrows():
        flags.append({
            "timestamp": row["timestamp"].strftime("%Y-%m-%d %H:%M"),
            "username": row["username"], "warehouse_id": row["warehouse_id"] or "-",
            "risk_level": "medium",
            "reasons": f"off-hours activity at {row['timestamp'].strftime('%H:%M')} "
                       f"(normal window {NORMAL_HOURS[0]}:00-{NORMAL_HOURS[1]}:00)",
        })

    # burst check: >BURST_THRESHOLD actions by same user within BURST_WINDOW_MINUTES
    for user, udf in df.groupby("username"):
        udf = udf.sort_values("timestamp").set_index("timestamp")
        counts = udf["action"].rolling(f"{BURST_WINDOW_MINUTES}min").count()
        over = counts > BURST_THRESHOLD
        # only flag the START of each burst run, not every point while it's sustained
        burst_starts = over & ~over.shift(1, fill_value=False)
        for ts, cnt in counts[burst_starts].items():
            flags.append({
                "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
                "username": user, "warehouse_id": "-",
                "risk_level": "high",
                "reasons": f"abnormal activity burst: {int(cnt)} actions within {BURST_WINDOW_MINUTES} minutes",
            })

    flags.sort(key=lambda f: f["timestamp"], reverse=True)
    return flags
