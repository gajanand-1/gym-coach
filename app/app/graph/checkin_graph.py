"""
Weekly Check-In LangGraph
--------------------------
Nodes:
  1. collect_data       — pull food, weight, workout, sleep summaries from stores
  2. run_analysis       — call WeeklyCheckInAgent
  3. apply_adjustments  — optionally update user's calorie/protein targets in DB
  4. save_checkin       — persist report via CheckInStore

Entry: collect_data → run_analysis → apply_adjustments → save_checkin → END
"""

from datetime import date, timedelta
from langgraph.graph import StateGraph, END
from app.graph.state import CheckInState
from app.agents.weekly_checkin import WeeklyCheckInAgent
from app.models.database import SessionLocal
from app.storage.food_store import FoodStore
from app.storage.weight_store import WeightStore
from app.storage.workout_store import WorkoutStore
from app.storage.sleep_store import SleepStore
from app.storage.checkin_store import CheckInStore
from app.storage.user_store import UserStore


# -----------------------------------------------------------------------
# Nodes
# -----------------------------------------------------------------------

def collect_data(state: CheckInState) -> CheckInState:
    """Pull last 7 days of data from every store."""
    uid = state["user_id"]
    try:
        db = SessionLocal()
        food_store = FoodStore(db)
        weight_store = WeightStore(db)
        workout_store = WorkoutStore(db)
        sleep_store = SleepStore(db)

        # Food summary per day
        food_summary = food_store.get_weekly_summary(uid)

        # Weight logs
        end = date.today()
        start = end - timedelta(days=7)
        weight_entries = weight_store.get_range(uid, start, end)
        weight_log = [
            {"date": e.log_date.isoformat(), "weight_kg": e.weight_kg}
            for e in weight_entries
        ]

        # Workout sessions
        workout_entries = workout_store.get_recent(uid, days=7)
        workout_summary = [
            {
                "date": w.log_date.isoformat(),
                "session_name": w.session_name,
                "total_volume_kg": w.total_volume_kg,
            }
            for w in workout_entries
        ]

        # Sleep logs
        sleep_entries = sleep_store.get_recent(uid, days=7)
        sleep_log = [
            {"date": s.log_date.isoformat(), "hours": s.hours, "quality": s.quality}
            for s in sleep_entries
        ]

        db.close()
        return {
            **state,
            "food_log_summary": food_summary,
            "weight_log": weight_log,
            "workout_log_summary": workout_summary,
            "sleep_log": sleep_log,
            "error": "",
        }
    except Exception as e:
        return {
            **state,
            "food_log_summary": [],
            "weight_log": [],
            "workout_log_summary": [],
            "sleep_log": [],
            "error": str(e),
        }


def run_analysis(state: CheckInState) -> CheckInState:
    """Run the WeeklyCheckInAgent."""
    try:
        agent = WeeklyCheckInAgent()
        report = agent.analyse(
            current_weight_kg=state["current_weight_kg"],
            target_weight_kg=state["target_weight_kg"],
            goal=state["goal"],
            current_calories_target=state["current_calories_target"],
            current_protein_target=state["current_protein_target"],
            energy_level=state["energy_level"],
            hunger_level=state["hunger_level"],
            sleep_quality=state["sleep_quality"],
            recovery_quality=state["recovery_quality"],
            food_log_summary=state["food_log_summary"],
            weight_log=state["weight_log"],
            workout_log_summary=state["workout_log_summary"],
            sleep_log=state["sleep_log"],
        )
        return {**state, "report": report, "error": ""}
    except Exception as e:
        return {**state, "report": {}, "error": str(e)}


def apply_adjustments(state: CheckInState) -> CheckInState:
    """Update user targets if the AI recommends calorie/protein changes."""
    if state.get("error") or not state.get("report"):
        return {**state, "adjustments_applied": False}

    adjustments = state["report"].get("adjustments", {})
    new_calories = adjustments.get("new_daily_calories", 0)
    new_protein = adjustments.get("new_protein_target", 0)

    if new_calories > 0 or new_protein > 0:
        try:
            db = SessionLocal()
            user_store = UserStore(db)
            update_kwargs = {}
            if new_calories > 0:
                update_kwargs["target_calories"] = new_calories
            if new_protein > 0:
                update_kwargs["protein_target_g"] = new_protein
            user_store.update_profile(state["user_id"], **update_kwargs)
            db.close()
            return {**state, "adjustments_applied": True}
        except Exception:
            pass

    return {**state, "adjustments_applied": False}


def save_checkin(state: CheckInState) -> CheckInState:
    """Persist the check-in report to the database."""
    if not state.get("report"):
        return state

    adjustments = state["report"].get("adjustments", {})
    try:
        db = SessionLocal()
        store = CheckInStore(db)
        store.save_checkin(
            user_id=state["user_id"],
            current_weight_kg=state["current_weight_kg"],
            energy_level=state["energy_level"],
            hunger_level=state["hunger_level"],
            sleep_quality=state["sleep_quality"],
            recovery_quality=state["recovery_quality"],
            ai_analysis=state["report"].get("weekly_summary", ""),
            calorie_adjustment=adjustments.get("calorie_change", 0),
            protein_adjustment=adjustments.get("protein_change", 0),
            cardio_recommendation=adjustments.get("cardio_recommendation", ""),
            volume_recommendation=adjustments.get("volume_recommendation", ""),
            report=state["report"],
        )
        db.close()
    except Exception as e:
        return {**state, "error": str(e)}

    return state


# -----------------------------------------------------------------------
# Graph assembly
# -----------------------------------------------------------------------

def build_checkin_graph() -> StateGraph:
    g = StateGraph(CheckInState)

    g.add_node("collect_data", collect_data)
    g.add_node("run_analysis", run_analysis)
    g.add_node("apply_adjustments", apply_adjustments)
    g.add_node("save_checkin", save_checkin)

    g.set_entry_point("collect_data")
    g.add_edge("collect_data", "run_analysis")
    g.add_edge("run_analysis", "apply_adjustments")
    g.add_edge("apply_adjustments", "save_checkin")
    g.add_edge("save_checkin", END)

    return g.compile()


_graph = None


def run_checkin_graph(
    user_id: int,
    current_weight_kg: float,
    target_weight_kg: float,
    goal: str,
    current_calories_target: float,
    current_protein_target: float,
    energy_level: int,
    hunger_level: int,
    sleep_quality: int,
    recovery_quality: int,
) -> CheckInState:
    global _graph
    if _graph is None:
        _graph = build_checkin_graph()

    initial: CheckInState = {
        "user_id": user_id,
        "current_weight_kg": current_weight_kg,
        "target_weight_kg": target_weight_kg,
        "goal": goal,
        "current_calories_target": current_calories_target,
        "current_protein_target": current_protein_target,
        "energy_level": energy_level,
        "hunger_level": hunger_level,
        "sleep_quality": sleep_quality,
        "recovery_quality": recovery_quality,
        "food_log_summary": [],
        "weight_log": [],
        "workout_log_summary": [],
        "sleep_log": [],
        "report": {},
        "adjustments_applied": False,
        "error": "",
    }
    return _graph.invoke(initial)
