"""
Workout Plan Node
-----------------
Generates a weekly workout programme based on user's split preference.
"""

from app.graph.gym_state import GymCoachState
from app.agents.workout_planner import WorkoutPlannerAgent
from app.models.database import SessionLocal
from app.storage.workout_plan_store import WorkoutPlanStore

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


def workout_plan_node(state: GymCoachState) -> GymCoachState:
    uid     = state["user_id"]
    profile = state.get("user_profile", {})

    try:
        agent = WorkoutPlannerAgent()
        plan  = agent.generate_plan(
            split_type        = profile.get("workout_split", "push_pull_legs"),
            experience        = profile.get("gym_experience", "beginner"),
            goal              = profile.get("goal", "fat_loss"),
            current_weight_kg = profile.get("weight_kg", 75),
            age               = profile.get("age", 22),
            gender            = profile.get("gender", "male"),
        )

        # Ensure all 7 days + sanitise exercise fields
        for day in DAYS:
            if day not in plan:
                plan[day] = {"session": "Rest", "exercises": []}
            exercises = []
            for ex in plan[day].get("exercises", []):
                exercises.append({
                    "name":        ex.get("name", "Unknown"),
                    "sets":        int(ex.get("sets", 3)),
                    "reps":        str(ex.get("reps", "10")),
                    "rest_seconds": int(ex.get("rest_seconds",
                                    ex.get("rest_sec", 90))),
                    "notes":       ex.get("notes", ""),
                })
            plan[day]["exercises"] = exercises

        db    = SessionLocal()
        saved = WorkoutPlanStore(db).save_plan(
            user_id    = uid,
            plan_data  = plan,
            split_type = profile.get("workout_split", "push_pull_legs"),
        )
        db.close()

        return {**state,
                "workout_plan_result": {"plan": plan, "plan_id": saved.id,
                                        "split_type": saved.split_type},
                "active_workout_plan": {"id": saved.id, "plan_data": plan,
                                        "split_type": saved.split_type},
                "error": ""}

    except Exception as e:
        return {**state, "workout_plan_result": {}, "error": f"workout_plan: {e}"}
