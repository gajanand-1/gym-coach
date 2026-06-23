"""
Mess Menu Node
--------------
Parses and saves a hostel mess menu from text supplied in user_input.
"""

from app.graph.gym_state import GymCoachState
from app.agents.mess_parser import MessParserAgent
from app.models.database import SessionLocal
from app.storage.mess_store import MessStore


def mess_menu_node(state: GymCoachState) -> GymCoachState:
    uid       = state["user_id"]
    raw_input = state.get("intent_data", {}).get("menu_text") or state["user_input"]

    try:
        agent   = MessParserAgent()
        parsed  = agent.parse_menu(raw_input)

        db    = SessionLocal()
        saved = MessStore(db).save_menu(uid, parsed,
                                        raw_input=raw_input,
                                        source_type="text")
        today = MessStore(db).get_today_meals(uid)
        db.close()

        return {**state,
                "mess_result":    {"menu": parsed, "menu_id": saved.id},
                "mess_menu_today": today,
                "error": ""}

    except Exception as e:
        return {**state, "mess_result": {}, "error": f"mess_menu: {e}"}
