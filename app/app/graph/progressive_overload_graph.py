"""
Progressive Overload LangGraph
-------------------------------
Nodes:
  1. fetch_history     — load last 2 weeks of workout sets from WorkoutStore
  2. analyse           — call ProgressiveOverloadAgent
  3. format_output     — clean and structure recommendations

Entry: fetch_history → analyse → format_output → END
"""

from langgraph.graph import StateGraph, END
from app.graph.state import ProgressiveOverloadState
from app.agents.progressive_overload import ProgressiveOverloadAgent
from app.models.database import SessionLocal
from app.storage.workout_store import WorkoutStore


# -----------------------------------------------------------------------
# Nodes
# -----------------------------------------------------------------------

def fetch_history(state: ProgressiveOverloadState) -> ProgressiveOverloadState:
    """Load last 2 weeks of exercise history grouped by exercise name."""
    try:
        db = SessionLocal()
        store = WorkoutStore(db)
        history = store.get_all_exercises_last_two_weeks(state["user_id"])
        db.close()
        return {**state, "exercise_history": history, "error": ""}
    except Exception as e:
        return {**state, "exercise_history": {}, "error": str(e)}


def analyse(state: ProgressiveOverloadState) -> ProgressiveOverloadState:
    """Run the ProgressiveOverloadAgent on the fetched history."""
    if state.get("error"):
        return state
    try:
        agent = ProgressiveOverloadAgent()
        result = agent.analyse(state["exercise_history"])
        return {**state, "recommendations": result}
    except Exception as e:
        return {**state, "recommendations": {}, "error": str(e)}


def format_output(state: ProgressiveOverloadState) -> ProgressiveOverloadState:
    """Ensure recommendations list is well-formed."""
    recs = state.get("recommendations", {})

    if not isinstance(recs, dict):
        recs = {}

    # Ensure required keys
    recs.setdefault("recommendations", [])
    recs.setdefault("overall_assessment", "No data available.")
    recs.setdefault("weekly_volume_change", "0%")
    recs.setdefault("deload_needed", False)
    recs.setdefault("deload_reason", "")

    # Sanitise each recommendation
    sanitized = []
    for r in recs["recommendations"]:
        sanitized.append({
            "exercise": r.get("exercise", "Unknown"),
            "current_weight_kg": r.get("current_weight_kg", 0),
            "current_reps": r.get("current_reps", ""),
            "status": r.get("status", "maintain"),
            "next_weight_kg": r.get("next_weight_kg", 0),
            "next_reps_target": r.get("next_reps_target", ""),
            "reasoning": r.get("reasoning", ""),
        })
    recs["recommendations"] = sanitized

    return {**state, "recommendations": recs}


# -----------------------------------------------------------------------
# Graph assembly
# -----------------------------------------------------------------------

def build_progressive_overload_graph() -> StateGraph:
    g = StateGraph(ProgressiveOverloadState)

    g.add_node("fetch_history", fetch_history)
    g.add_node("analyse", analyse)
    g.add_node("format_output", format_output)

    g.set_entry_point("fetch_history")
    g.add_edge("fetch_history", "analyse")
    g.add_edge("analyse", "format_output")
    g.add_edge("format_output", END)

    return g.compile()


_graph = None


def run_progressive_overload_graph(user_id: int) -> ProgressiveOverloadState:
    global _graph
    if _graph is None:
        _graph = build_progressive_overload_graph()

    initial: ProgressiveOverloadState = {
        "user_id": user_id,
        "exercise_history": {},
        "recommendations": {},
        "error": "",
    }
    return _graph.invoke(initial)
