"""
Supplement Node
---------------
Marks a supplement as taken / not taken for today.
"""

import re
from app.graph.gym_state import GymCoachState
from app.models.database import SessionLocal
from app.storage.supplement_store import SupplementStore

SUPPLEMENT_ALIASES = {
    "whey":        "Whey Protein",
    "protein":     "Whey Protein",
    "creatine":    "Creatine",
    "fish oil":    "Fish Oil",
    "omega":       "Fish Oil",
    "multivitamin":"Multivitamin",
    "multi":       "Multivitamin",
}


def supplement_node(state: GymCoachState) -> GymCoachState:
    uid   = state["user_id"]
    msg   = state["user_input"].lower()

    # Detect taken / not taken
    taken = "not" not in msg and "skip" not in msg and "miss" not in msg

    # Match supplement name
    matched = None
    for alias, name in SUPPLEMENT_ALIASES.items():
        if alias in msg:
            matched = name
            break

    try:
        db    = SessionLocal()
        store = SupplementStore(db)
        entry = store.get_today(uid)

        if matched:
            store.update_supplement(uid, matched, taken)
            entry = store.get_today(uid)

        db.close()
        taken_count = sum(1 for s in entry.supplements if s.get("taken"))
        total_count = len(entry.supplements)

        result = {
            "supplements":   entry.supplements,
            "updated":       matched,
            "taken":         taken,
            "taken_count":   taken_count,
            "total_count":   total_count,
            "adherence_pct": round(taken_count / total_count * 100) if total_count else 0,
        }
        return {**state, "supplement_result": result, "error": ""}

    except Exception as e:
        return {**state, "supplement_result": {}, "error": f"supplement: {e}"}
