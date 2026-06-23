"""
Coach Chat Node
---------------
Handles general conversation using full user context already in state.
"""

from app.graph.gym_state import GymCoachState
from app.agents.coach_chat import CoachChatAgent
from app.models.database import SessionLocal
from app.storage.chat_store import ChatStore


def coach_chat_node(state: GymCoachState) -> GymCoachState:
    uid        = state["user_id"]
    session_id = state.get("session_id", "default")

    try:
        agent    = CoachChatAgent()
        response = agent.chat(
            user_message        = state["user_input"],
            chat_history        = state.get("chat_history", []),
            user_profile        = state.get("user_profile", {}),
            today_food_totals   = state.get("today_food", {}),
            today_water         = state.get("today_water", {}),
            recent_weight       = state.get("recent_weight", []),
            active_diet_plan    = state.get("active_diet_plan"),
            active_workout_plan = state.get("active_workout_plan"),
            recent_workouts     = state.get("recent_workouts", []),
            sleep_avg           = state.get("sleep_avg", 0.0),
        )

        # Persist messages
        db    = SessionLocal()
        store = ChatStore(db)
        store.add_message(uid, "user",      state["user_input"], session_id)
        store.add_message(uid, "assistant", response,            session_id)
        db.close()

        return {**state, "chat_result": response,
                "chat_history": state.get("chat_history", []) +
                    [{"role": "user",      "content": state["user_input"]},
                     {"role": "assistant", "content": response}],
                "error": ""}

    except Exception as e:
        return {**state, "chat_result": "", "error": f"coach_chat: {e}"}
