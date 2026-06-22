"""
Workout Plan LangGraph
----------------------
Nodes:
  1. generate_plan   — call WorkoutPlannerAgent
  2. validate_plan   — ensure all 7 days present with proper structure
  3. save_plan       — persist via WorkoutPlanStore

Entry: generate_plan → validate_plan → save_plan → END
"""

from langgraph.graph import StateGraph, END
from app.graph.state import WorkoutPlanState
from app.agents.workout_planner import WorkoutPlannerAgent
from app.models.database import SessionLocal
from app.storage.workout_plan_store import WorkoutPlanStore

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# -----------------------------------------------------------------------
# Nodes
# -----------------------------------------------------------------------

def generate_plan(state: WorkoutPlanState) -> WorkoutPlanState:
    try:
        agent = WorkoutPlannerAgent()
        plan = agent.generate_plan(
            split_type=state["split_type"],
            experience=state["experience"],
            goal=state["goal"],
            current_weight_kg=state["current_weight_kg"],
            age=state["age"],
            gender=state["gender"],
        )
        return {**state, "plan_data": plan, "error": ""}
    except Exception as e:
        return {**state, "plan_data": {}, "error": str(e)}


def validate_plan(state: WorkoutPlanState) -> WorkoutPlanState:
    if state.get("error"):
        return state

    plan = state.get("plan_data", {})

    for day in DAYS:
        if day not in plan:
            plan[day] = {"session": "Rest", "exercises": []}

        # Ensure each exercise has required fields
        exercises = plan[day].get("exercises", [])
        sanitized = []
        for ex in exercises:
            sanitized.append({
                "name": ex.get("name", "Unknown Exercise"),
                "sets": int(ex.get("sets", 3)),
                "reps": str(ex.get("reps", "10")),
                "rest_seconds": int(ex.get("rest_seconds", ex.get("rest_sec", 90))),
                "notes": ex.get("notes", ""),
            })
        plan[day]["exercises"] = sanitized

    return {**state, "plan_data": plan}


def save_plan(state: WorkoutPlanState) -> WorkoutPlanState:
    if state.get("error") or not state.get("plan_data"):
        return state
    try:
        db = SessionLocal()
        store = WorkoutPlanStore(db)
        store.save_plan(
            user_id=state["user_id"],
            plan_data=state["plan_data"],
            split_type=state["split_type"],
        )
        db.close()
        return {**state, "plan_saved": True}
    except Exception as e:
        return {**state, "plan_saved": False, "error": str(e)}


# -----------------------------------------------------------------------
# Graph assembly
# -----------------------------------------------------------------------

def build_workout_plan_graph() -> StateGraph:
    g = StateGraph(WorkoutPlanState)

    g.add_node("generate_plan", generate_plan)
    g.add_node("validate_plan", validate_plan)
    g.add_node("save_plan", save_plan)

    g.set_entry_point("generate_plan")
    g.add_edge("generate_plan", "validate_plan")
    g.add_edge("validate_plan", "save_plan")
    g.add_edge("save_plan", END)

    return g.compile()


_graph = None


def run_workout_plan_graph(
    user_id: int,
    split_type: str = "push_pull_legs",
    experience: str = "beginner",
    goal: str = "fat_loss",
    current_weight_kg: float = 80,
    age: int = 22,
    gender: str = "male",
) -> WorkoutPlanState:
    global _graph
    if _graph is None:
        _graph = build_workout_plan_graph()

    initial: WorkoutPlanState = {
        "user_id": user_id,
        "split_type": split_type,
        "experience": experience,
        "goal": goal,
        "current_weight_kg": current_weight_kg,
        "age": age,
        "gender": gender,
        "plan_data": {},
        "plan_saved": False,
        "error": "",
    }
    return _graph.invoke(initial)
