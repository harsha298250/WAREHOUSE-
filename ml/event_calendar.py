"""
event_calendar.py — NOVELTY: Event-aware demand adjustment
==============================================================
Most student forecasting projects only look at historical stock-out
numbers. In reality, retail/warehouse demand is heavily driven by known
calendar events (festivals, paydays, weather-linked buying patterns).

This module maintains a lightweight event calendar and exposes a
multiplier that the forecast engine (or dashboard) can apply on top of
the base statistical forecast for any given date — with a reason string,
so the adjustment is explainable rather than a silent fudge factor.

Events are generated DYNAMICALLY relative to today's date so the
calendar is never empty regardless of when the application is run.
"""
from datetime import date, timedelta


def _build_dynamic_calendar():
    """Build an event calendar with entries relative to today."""
    today = date.today()
    calendar = {}

    # --- Monthly paydays (1st and 15th of each month for 3 months ahead) ---
    for month_offset in range(0, 3):
        d = today.replace(day=1)
        # Move forward by month_offset months
        month = d.month + month_offset
        year = d.year
        while month > 12:
            month -= 12
            year += 1
        try:
            payday_1 = date(year, month, 1)
            if payday_1 >= today:
                calendar[payday_1.strftime("%Y-%m-%d")] = (1.35, "Month-start payday — demand surge expected")
        except ValueError:
            pass
        try:
            payday_15 = date(year, month, 15)
            if payday_15 >= today:
                calendar[payday_15.strftime("%Y-%m-%d")] = (1.20, "Mid-month salary cycle — moderate demand uptick")
        except ValueError:
            pass

    # --- Indian festivals & seasonal events (relative to today) ---
    festival_offsets = [
        (3,  1.8, "Upcoming regional festival — high warehouse throughput expected"),
        (5,  1.5, "Pre-festival stocking window — suppliers push inventory"),
        (7,  1.6, "Weekend sale event — e-commerce order spike"),
        (10, 1.4, "Bulk corporate procurement cycle"),
        (14, 1.9, "Major festival week — peak demand across all categories"),
        (15, 1.85, "Festival continuation — sustained high demand"),
        (16, 1.7, "Post-festival returns & exchange window"),
        (21, 1.3, "End-of-month clearance & restocking"),
        (25, 1.5, "Flash sale preparation — pre-positioning inventory"),
        (30, 1.6, "Quarterly review — inventory audit & rebalancing"),
        (35, 1.4, "New season catalogue launch — fresh SKU intake"),
        (42, 1.7, "Independence Day / Republic Day sale window"),
        (50, 1.5, "Back-to-school / college season demand"),
        (60, 1.8, "Diwali / Dussehra festival mega-sale window"),
    ]
    for offset, mult, reason in festival_offsets:
        d = today + timedelta(days=offset)
        key = d.strftime("%Y-%m-%d")
        if key not in calendar:  # Don't override paydays
            calendar[key] = (mult, reason)

    # --- Weather-driven demand (seasonal) ---
    month_now = today.month
    if month_now in (6, 7, 8):  # Monsoon
        for offset in (2, 8, 18):
            d = today + timedelta(days=offset)
            key = d.strftime("%Y-%m-%d")
            if key not in calendar:
                calendar[key] = (1.3, "Monsoon season — rain gear & essentials demand spike")
    elif month_now in (11, 12, 1):  # Winter
        for offset in (4, 12, 22):
            d = today + timedelta(days=offset)
            key = d.strftime("%Y-%m-%d")
            if key not in calendar:
                calendar[key] = (1.4, "Winter season — heating & warm clothing demand")
    elif month_now in (3, 4, 5):  # Summer
        for offset in (6, 16, 28):
            d = today + timedelta(days=offset)
            key = d.strftime("%Y-%m-%d")
            if key not in calendar:
                calendar[key] = (1.35, "Summer heat wave — cooling appliances & beverages surge")

    return calendar


# Build once on module load; refreshes each time the server restarts
EVENT_CALENDAR = _build_dynamic_calendar()

CATEGORY_SENSITIVITY = {
    "Electronics": 1.3, "Groceries": 1.0, "Apparel": 1.2,
    "Pharma": 0.7, "Home & Kitchen": 1.1, "Hardware": 1.15,
}


def get_event_adjustment(target_date, category: str = "Groceries"):
    """Return (multiplier, reason) for a given date and category."""
    key = target_date.strftime("%Y-%m-%d") if hasattr(target_date, "strftime") else str(target_date)
    base_mult, reason = EVENT_CALENDAR.get(key, (1.0, "No calendar event"))
    if base_mult == 1.0:
        return 1.0, reason
    sensitivity = CATEGORY_SENSITIVITY.get(category, 1.0)
    adjusted = 1.0 + (base_mult - 1.0) * sensitivity
    return round(adjusted, 2), f"{reason} (category sensitivity x{sensitivity})"


def upcoming_events(from_date, horizon_days: int = 60):
    events = []
    for h in range(horizon_days):
        d = from_date + timedelta(days=h)
        key = d.strftime("%Y-%m-%d")
        if key in EVENT_CALENDAR:
            mult, reason = EVENT_CALENDAR[key]
            events.append({"date": key, "multiplier": mult, "reason": reason})
    return events


if __name__ == "__main__":
    print(f"Events from today ({date.today()}):")
    for ev in upcoming_events(date.today(), 60):
        print(f"  {ev['date']}  x{ev['multiplier']}  {ev['reason']}")

