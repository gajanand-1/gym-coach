"""
Grocery Node
------------
Fetches the active grocery plan from DB and returns it.
"""

from app.graph.gym_state import GymCoachState
from app.models.database import SessionLocal
from app.storage.grocery_store import GroceryStore


def grocery_node(state: GymCoachState) -> GymCoachState:
    uid = state["user_id"]
    try:
        db   = SessionLocal()
        plan = GroceryStore(db).get_active(uid)
        db.close()

        if not plan:
            return {**state,
                    "grocery_result": {"items": [], "message":
                        "No grocery list yet. Generate a Diet Plan first."},
                    "error": ""}

        return {**state,
                "grocery_result": {
                    "items":      plan.items,
                    "week_start": plan.week_start,
                    "plan_id":    plan.id,
                },
                "error": ""}

    except Exception as e:
        return {**state, "grocery_result": {}, "error": f"grocery: {e}"}
