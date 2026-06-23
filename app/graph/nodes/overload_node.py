"""
Progressive Overload Node
-------------------------
Fetches last 2 weeks of workout history and runs the ProgressiveOverloadAgent.
"""

from app.graph.gym_state import GymCoachState
from app.agents.progressive_overload import ProgressiveOverloadAgent
from app.models.database import SessionLocal
from app.storage.workout_store import WorkoutStore


def overload_node(state: GymCoachState) -> GymCoachState:
    uid = state["user_id"]
    try:
        db      = SessionLocal()
        history = WorkoutStore(db).get_all_exercises_last_two_weeks(uid)
        db.close()

        agent  = ProgressiveOverloadAgent()
        result = agent.analyse(history)

        return {**state, "overload_result": result, "error": ""}

    except Exception as e:
        return {**state, "overload_result": {}, "error": f"overload: {e}"}
