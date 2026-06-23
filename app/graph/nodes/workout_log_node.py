"""
Workout Log Node
----------------
Logs a completed workout session extracted from user input.
If no structured exercises are present, falls back to raw text storage.
"""

from app.graph.gym_state import GymCoachState
from app.models.database import SessionLocal
from app.storage.workout_store import WorkoutStore


def workout_log_node(state: GymCoachState) -> GymCoachState:
    uid         = state["user_id"]
    intent_data = state.get("intent_data", {})
    profile     = state.get("user_profile", {})

    session_name     = intent_data.get("session_name", "Workout")
    exercises        = intent_data.get("exercises", [])
    duration_minutes = int(intent_data.get("duration_minutes", 0))
    split_type       = intent_data.get("split_type", profile.get("workout_split", ""))

    # If no exercises extracted, store raw input as notes
    if not exercises:
        exercises = [{
            "exercise":  state["user_input"],
            "weight_kg": 0,
            "sets":      [],
            "rpe":       0,
        }]

    # Ensure each exercise has required keys
    cleaned = []
    for ex in exercises:
        cleaned.append({
            "exercise":  ex.get("exercise", ex.get("name", "Unknown")),
            "weight_kg": float(ex.get("weight_kg", 0)),
            "sets":      ex.get("sets", []),
            "rpe":       float(ex.get("rpe", 0)),
        })

    try:
        db  = SessionLocal()
        wl  = WorkoutStore(db).log_session(
            user_id          = uid,
            session_name     = session_name,
            split_type       = split_type,
            exercises        = cleaned,
            duration_minutes = duration_minutes,
            notes            = state["user_input"],
        )
        db.close()

        return {**state,
                "workout_log_result": {
                    "session_id":     wl.id,
                    "session_name":   wl.session_name,
                    "total_volume_kg": wl.total_volume_kg,
                    "exercises_count": len(cleaned),
                    "log_date":       wl.log_date.isoformat(),
                },
                "error": ""}

    except Exception as e:
        return {**state, "workout_log_result": {}, "error": f"workout_log: {e}"}
