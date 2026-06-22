"""
Workout Service
---------------
Handles workout logging, plan generation, and progressive overload.
"""

from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.graph.workout_plan_graph import run_workout_plan_graph
from app.graph.progressive_overload_graph import run_progressive_overload_graph
from app.storage.workout_store import WorkoutStore
from app.storage.workout_plan_store import WorkoutPlanStore


class WorkoutService:

    def __init__(self, db: Session):
        self.db = db
        self.workout_store = WorkoutStore(db)
        self.plan_store = WorkoutPlanStore(db)

    # ------------------------------------------------------------------ #
    # Plan generation
    # ------------------------------------------------------------------ #

    def generate_plan(
        self,
        user_id: int,
        split_type: str,
        experience: str,
        goal: str,
        weight_kg: float,
        age: int,
        gender: str,
    ) -> dict:
        """Generate and save a new workout plan via LangGraph."""
        result = run_workout_plan_graph(
            user_id=user_id,
            split_type=split_type,
            experience=experience,
            goal=goal,
            current_weight_kg=weight_kg,
            age=age,
            gender=gender,
        )
        return result

    def get_active_plan(self, user_id: int) -> Optional[dict]:
        plan = self.plan_store.get_active(user_id)
        if not plan:
            return None
        return {
            "id": plan.id,
            "split_type": plan.split_type,
            "plan_name": plan.plan_name,
            "plan_data": plan.plan_data,
            "created_at": plan.created_at.isoformat(),
        }

    def get_today_session(self, user_id: int) -> Optional[dict]:
        """Return today's planned session from the active plan."""
        plan = self.plan_store.get_active(user_id)
        if not plan or not plan.plan_data:
            return None
        day_name = date.today().strftime("%A")
        return plan.plan_data.get(day_name)

    # ------------------------------------------------------------------ #
    # Workout logging
    # ------------------------------------------------------------------ #

    def log_session(
        self,
        user_id: int,
        session_name: str,
        split_type: str,
        exercises: List[Dict[str, Any]],
        notes: str = "",
        duration_minutes: int = 0,
    ) -> dict:
        """
        Log a completed workout session.

        exercises format:
        [{"exercise": "bench_press", "weight_kg": 60, "sets": [10,10,8,7], "rpe": 8}]
        """
        wl = self.workout_store.log_session(
            user_id=user_id,
            session_name=session_name,
            split_type=split_type,
            exercises=exercises,
            notes=notes,
            duration_minutes=duration_minutes,
        )
        return {
            "id": wl.id,
            "session_name": wl.session_name,
            "total_volume_kg": wl.total_volume_kg,
            "log_date": wl.log_date.isoformat(),
        }

    def get_recent_sessions(self, user_id: int, days: int = 14) -> list:
        sessions = self.workout_store.get_recent(user_id, days)
        return [
            {
                "id": w.id,
                "date": w.log_date.isoformat(),
                "session_name": w.session_name,
                "split_type": w.split_type,
                "exercises": w.exercises,
                "volume_kg": w.total_volume_kg,
                "duration_min": w.duration_minutes,
                "notes": w.notes,
            }
            for w in sessions
        ]

    def delete_session(self, session_id: int, user_id: int) -> bool:
        return self.workout_store.delete_session(session_id, user_id)

    # ------------------------------------------------------------------ #
    # Progressive overload
    # ------------------------------------------------------------------ #

    def get_progressive_overload_recommendations(self, user_id: int) -> dict:
        """Run the progressive overload LangGraph and return recommendations."""
        result = run_progressive_overload_graph(user_id)
        return result.get("recommendations", {})

    def get_exercise_history(self, user_id: int, exercise_name: str) -> list:
        sets = self.workout_store.get_exercise_history(user_id, exercise_name)
        return [
            {
                "date": s.log_date.isoformat(),
                "set": s.set_number,
                "weight_kg": s.weight_kg,
                "reps": s.reps,
            }
            for s in sets
        ]
