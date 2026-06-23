"""
Water Log Node
--------------
Adds water intake to today's total and returns updated gauge data.
"""

import re
from app.graph.gym_state import GymCoachState
from app.models.database import SessionLocal
from app.storage.water_store import WaterStore


def water_log_node(state: GymCoachState) -> GymCoachState:
    uid         = state["user_id"]
    profile     = state.get("user_profile", {})
    intent_data = state.get("intent_data", {})
    target      = profile.get("water_target_liters", 3.5)

    liters = float(intent_data.get("water_liters", 0))
    if not liters:
        # Parse from input: "500ml", "2 litres", "1.5L"
        ml_m = re.search(r"(\d+\.?\d*)\s*ml", state["user_input"], re.I)
        l_m  = re.search(r"(\d+\.?\d*)\s*l(?:itr?e?s?)?", state["user_input"], re.I)
        if ml_m:
            liters = float(ml_m.group(1)) / 1000
        elif l_m:
            liters = float(l_m.group(1))
        else:
            liters = 0.25   # default glass

    try:
        db    = SessionLocal()
        entry = WaterStore(db).add_water(uid, liters, target)
        db.close()

        remaining = max(0, target - entry.consumed_liters)
        pct       = round(entry.consumed_liters / target * 100, 1) if target else 0
        result    = {
            "added_liters":    round(liters, 2),
            "consumed_liters": entry.consumed_liters,
            "target_liters":   target,
            "remaining_liters": remaining,
            "pct":             pct,
        }
        return {**state, "water_result": result,
                "today_water": {"consumed_liters": entry.consumed_liters,
                                "target_liters": target},
                "error": ""}

    except Exception as e:
        return {**state, "water_result": {}, "error": f"water_log: {e}"}
