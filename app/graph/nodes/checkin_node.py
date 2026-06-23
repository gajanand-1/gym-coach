"""
Weekly Check-In Node
--------------------
Runs the full weekly analysis using context already loaded into state.
Applies calorie/protein adjustments to the user profile.
"""

from app.graph.gym_state import GymCoachState
from app.agents.weekly_checkin import WeeklyCheckInAgent
from app.models.database import SessionLocal
from app.storage.checkin_store import CheckInStore
from app.storage.food_store    import FoodStore
from app.storage.weight_store  import WeightStore
from app.storage.workout_store import WorkoutStore
from app.storage.sleep_store   import SleepStore
from app.storage.user_store    import UserStore
from datetime import date, timedelta


def checkin_node(state: GymCoachState) -> GymCoachState:
    uid     = state["user_id"]
    profile = state.get("user_profile", {})

    try:
        db = SessionLocal()

        # Gather week's data
        food_summary    = FoodStore(db).get_weekly_summary(uid)
        end = date.today(); start = end - timedelta(days=7)
        weight_entries  = WeightStore(db).get_range(uid, start, end)
        weight_log      = [{"date": e.log_date.isoformat(), "weight_kg": e.weight_kg}
                           for e in weight_entries]
        workout_entries = WorkoutStore(db).get_recent(uid, days=7)
        workout_summary = [{"date": w.log_date.isoformat(),
                            "session_name": w.session_name,
                            "total_volume_kg": w.total_volume_kg}
                           for w in workout_entries]
        sleep_entries   = SleepStore(db).get_recent(uid, days=7)
        sleep_log       = [{"date": s.log_date.isoformat(),
                            "hours": s.hours, "quality": s.quality}
                           for s in sleep_entries]

        # Subjective scores from intent_data or defaults
        idata           = state.get("intent_data", {})
        current_weight  = float(idata.get("current_weight_kg",
                          profile.get("weight_kg", 80)))

        agent  = WeeklyCheckInAgent()
        report = agent.analyse(
            current_weight_kg       = current_weight,
            target_weight_kg        = profile.get("target_weight_kg", 75),
            goal                    = profile.get("goal", "fat_loss"),
            current_calories_target = profile.get("target_calories", 2000),
            current_protein_target  = profile.get("protein_target_g", 150),
            energy_level            = int(idata.get("energy_level",  6)),
            hunger_level            = int(idata.get("hunger_level",  5)),
            sleep_quality           = int(idata.get("sleep_quality", 6)),
            recovery_quality        = int(idata.get("recovery_quality", 6)),
            food_log_summary        = food_summary,
            weight_log              = weight_log,
            workout_log_summary     = workout_summary,
            sleep_log               = sleep_log,
        )

        # Save check-in
        adj = report.get("adjustments", {})
        CheckInStore(db).save_checkin(
            user_id              = uid,
            current_weight_kg    = current_weight,
            energy_level         = int(idata.get("energy_level",  6)),
            hunger_level         = int(idata.get("hunger_level",  5)),
            sleep_quality        = int(idata.get("sleep_quality", 6)),
            recovery_quality     = int(idata.get("recovery_quality", 6)),
            ai_analysis          = report.get("weekly_summary", ""),
            calorie_adjustment   = adj.get("calorie_change", 0),
            protein_adjustment   = adj.get("protein_change", 0),
            cardio_recommendation= adj.get("cardio_recommendation", ""),
            volume_recommendation= adj.get("volume_recommendation", ""),
            report               = report,
        )

        # Apply adjustments
        new_cal = adj.get("new_daily_calories", 0)
        new_pro = adj.get("new_protein_target", 0)
        update  = {}
        if new_cal > 0: update["target_calories"]   = new_cal
        if new_pro > 0: update["protein_target_g"]  = new_pro
        if update:
            UserStore(db).update_profile(uid, **update)

        db.close()
        return {**state, "checkin_result": report, "error": ""}

    except Exception as e:
        return {**state, "checkin_result": {}, "error": f"checkin: {e}"}
