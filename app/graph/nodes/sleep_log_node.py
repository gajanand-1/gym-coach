"""
Sleep Log Node
--------------
Logs sleep hours and quality for today.
"""

import re
from app.graph.gym_state import GymCoachState
from app.models.database import SessionLocal
from app.storage.sleep_store import SleepStore


def sleep_log_node(state: GymCoachState) -> GymCoachState:
    uid         = state["user_id"]
    intent_data = state.get("intent_data", {})

    hours   = float(intent_data.get("sleep_hours", 0))
    quality = intent_data.get("sleep_quality", "good")

    if not hours:
        m = re.search(r"(\d+\.?\d*)\s*h(?:ours?)?", state["user_input"], re.I)
        if m:
            hours = float(m.group(1))

    if not hours:
        return {**state,
                "sleep_result": {"error": "No sleep duration found. Try: 'Slept 7.5 hours'"},
                "error": "No sleep hours found"}

    try:
        db    = SessionLocal()
        store = SleepStore(db)
        entry = store.log_sleep(uid, hours, quality)
        avg   = store.get_average_hours(uid, days=7)
        db.close()

        result = {
            "hours":       hours,
            "quality":     quality,
            "avg_7d":      avg,
            "log_date":    entry.log_date.isoformat(),
        }
        return {**state, "sleep_result": result,
                "sleep_avg": avg, "error": ""}

    except Exception as e:
        return {**state, "sleep_result": {}, "error": f"sleep_log: {e}"}
