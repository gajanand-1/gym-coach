"""
Weight Log Node
---------------
Logs body weight and returns updated trend data.
"""

from datetime import date
from app.graph.gym_state import GymCoachState
from app.models.database import SessionLocal
from app.storage.weight_store import WeightStore
from app.storage.user_store   import UserStore


def weight_log_node(state: GymCoachState) -> GymCoachState:
    uid         = state["user_id"]
    intent_data = state.get("intent_data", {})
    weight_kg   = float(intent_data.get("weight_kg", 0))

    if not weight_kg:
        # Try to parse from raw input (e.g. "82.5 kg")
        import re
        m = re.search(r"(\d+\.?\d*)\s*kg?", state["user_input"], re.I)
        if m:
            weight_kg = float(m.group(1))

    if not weight_kg:
        return {**state,
                "weight_result": {"error": "Could not find a weight value. Try: 'Log weight 82 kg'"},
                "error": "No weight value found"}

    try:
        db    = SessionLocal()
        entry = WeightStore(db).log_weight(uid, weight_kg)
        # Update user's current weight
        UserStore(db).update_profile(uid, weight_kg=weight_kg)
        trend = WeightStore(db).get_trend_data(uid, days=30)
        rate  = WeightStore(db).calculate_rate_of_change(uid, days=14)
        db.close()

        result = {
            "weight_kg":       weight_kg,
            "log_date":        entry.log_date.isoformat(),
            "trend_30d":       trend,
            "rate_per_week":   rate,
        }
        return {**state, "weight_result": result,
                "recent_weight": trend[-7:] if len(trend) >= 7 else trend,
                "error": ""}

    except Exception as e:
        return {**state, "weight_result": {}, "error": f"weight_log: {e}"}
