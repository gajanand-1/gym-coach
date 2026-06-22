"""
Coach Chat LangGraph
---------------------
Nodes:
  1. load_context     — pull all user data from stores into state
  2. run_chat         — call CoachChatAgent with full context
  3. save_message     — persist user + assistant messages to ChatStore

Entry: load_context → run_chat → save_message → END
"""

from datetime import date
from langgraph.graph import StateGraph, END
from app.graph.state import CoachChatState
from app.agents.coach_chat import CoachChatAgent
from app.models.database import SessionLocal
from app.storage.chat_store import ChatStore
from app.storage.food_store import FoodStore
from app.storage.water_store import WaterStore
from app.storage.weight_store import WeightStore
from app.storage.sleep_store import SleepStore
from app.storage.workout_store import WorkoutStore
from app.storage.diet_store import DietStore
from app.storage.workout_plan_store import WorkoutPlanStore
from app.storage.user_store import UserStore


# -----------------------------------------------------------------------
# Nodes
# -----------------------------------------------------------------------

def load_context(state: CoachChatState) -> CoachChatState:
    """Hydrate state with all relevant user data from the database."""
    uid = state["user_id"]
    session_id = state.get("session_id", "default")

    try:
        db = SessionLocal()

        # User profile
        user_store = UserStore(db)
        user = user_store.get_by_id(uid)
        user_profile = {}
        if user:
            user_profile = {
                "name": user.name,
                "age": user.age,
                "gender": user.gender,
                "weight_kg": user.weight_kg,
                "target_weight_kg": user.target_weight_kg,
                "goal": user.goal,
                "target_calories": user.target_calories,
                "protein_target_g": user.protein_target_g,
                "workout_split": user.workout_split,
                "gym_experience": user.gym_experience,
            }

        # Today's food totals
        food_store = FoodStore(db)
        today_totals = food_store.get_daily_totals(uid, date.today())

        # Water intake
        water_store = WaterStore(db)
        water_entry = water_store.get_today(uid, user.water_target_liters if user else 3.5)
        today_water = {
            "consumed_liters": water_entry.consumed_liters,
            "target_liters": water_entry.target_liters,
        }

        # Recent weight (7 entries)
        weight_store = WeightStore(db)
        recent_weight = weight_store.get_trend_data(uid, days=7)

        # Sleep average
        sleep_store = SleepStore(db)
        sleep_avg = sleep_store.get_average_hours(uid, days=7)

        # Active plans
        diet_store = DietStore(db)
        active_diet = diet_store.get_active(uid)
        active_diet_plan = {"id": active_diet.id, "week_start": active_diet.week_start} if active_diet else None

        wp_store = WorkoutPlanStore(db)
        active_wp = wp_store.get_active(uid)
        active_workout_plan = {
            "split_type": active_wp.split_type,
            "plan_name": active_wp.plan_name,
        } if active_wp else None

        # Recent workouts (last 3)
        workout_store = WorkoutStore(db)
        recent_raw = workout_store.get_recent(uid, days=14)[:3]
        recent_workouts = [
            {
                "session_name": w.session_name,
                "log_date": w.log_date.isoformat(),
                "total_volume_kg": w.total_volume_kg,
            }
            for w in recent_raw
        ]

        # Chat history
        chat_store = ChatStore(db)
        chat_history = chat_store.get_as_langchain_messages(uid, session_id, limit=20)

        db.close()

        return {
            **state,
            "user_profile": user_profile,
            "today_food_totals": today_totals,
            "today_water": today_water,
            "recent_weight": recent_weight,
            "sleep_avg": sleep_avg,
            "active_diet_plan": active_diet_plan,
            "active_workout_plan": active_workout_plan,
            "recent_workouts": recent_workouts,
            "chat_history": chat_history,
            "error": "",
        }
    except Exception as e:
        return {**state, "error": str(e)}


def run_chat(state: CoachChatState) -> CoachChatState:
    """Call the CoachChatAgent with full context."""
    if state.get("error"):
        return {**state, "response": f"Sorry, I encountered an error loading your data: {state['error']}"}

    try:
        agent = CoachChatAgent()
        response = agent.chat(
            user_message=state["user_message"],
            chat_history=state.get("chat_history", []),
            user_profile=state.get("user_profile", {}),
            today_food_totals=state.get("today_food_totals", {}),
            today_water=state.get("today_water", {}),
            recent_weight=state.get("recent_weight", []),
            active_diet_plan=state.get("active_diet_plan"),
            active_workout_plan=state.get("active_workout_plan"),
            recent_workouts=state.get("recent_workouts", []),
            sleep_avg=state.get("sleep_avg", 0.0),
        )
        return {**state, "response": response, "error": ""}
    except Exception as e:
        return {**state, "response": "I'm having trouble connecting right now. Please try again.", "error": str(e)}


def save_message(state: CoachChatState) -> CoachChatState:
    """Persist user message and assistant response to ChatStore."""
    try:
        db = SessionLocal()
        store = ChatStore(db)
        session_id = state.get("session_id", "default")
        store.add_message(state["user_id"], "user", state["user_message"], session_id)
        if state.get("response"):
            store.add_message(state["user_id"], "assistant", state["response"], session_id)
        db.close()
    except Exception:
        pass  # Don't fail the whole graph on save error
    return state


# -----------------------------------------------------------------------
# Graph assembly
# -----------------------------------------------------------------------

def build_coach_chat_graph() -> StateGraph:
    g = StateGraph(CoachChatState)

    g.add_node("load_context", load_context)
    g.add_node("run_chat", run_chat)
    g.add_node("save_message", save_message)

    g.set_entry_point("load_context")
    g.add_edge("load_context", "run_chat")
    g.add_edge("run_chat", "save_message")
    g.add_edge("save_message", END)

    return g.compile()


_graph = None


def run_coach_chat_graph(
    user_id: int,
    user_message: str,
    session_id: str = "default",
) -> CoachChatState:
    global _graph
    if _graph is None:
        _graph = build_coach_chat_graph()

    initial: CoachChatState = {
        "user_id": user_id,
        "user_message": user_message,
        "session_id": session_id,
        "chat_history": [],
        "user_profile": {},
        "today_food_totals": {},
        "today_water": {},
        "recent_weight": [],
        "active_diet_plan": None,
        "active_workout_plan": None,
        "recent_workouts": [],
        "sleep_avg": 0.0,
        "response": "",
        "error": "",
    }
    return _graph.invoke(initial)
