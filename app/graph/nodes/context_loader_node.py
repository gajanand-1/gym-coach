"""
Context Loader Node
-------------------
Runs BEFORE the router.
Loads all relevant user data from the database into the shared state
so every downstream node has full context without repeating DB calls.
"""

from datetime import date
from app.graph.gym_state import GymCoachState
from app.models.database import SessionLocal
from app.storage.user_store    import UserStore
from app.storage.food_store    import FoodStore
from app.storage.water_store   import WaterStore
from app.storage.weight_store  import WeightStore
from app.storage.sleep_store   import SleepStore
from app.storage.workout_store import WorkoutStore
from app.storage.workout_plan_store import WorkoutPlanStore
from app.storage.diet_store    import DietStore
from app.storage.mess_store    import MessStore
from app.storage.chat_store    import ChatStore


def context_loader_node(state: GymCoachState) -> GymCoachState:
    uid        = state["user_id"]
    session_id = state.get("session_id", "default")

    try:
        db = SessionLocal()

        # ── User profile ──────────────────────────────────────────────────
        user = UserStore(db).get_by_id(uid)
        profile = {}
        if user:
            profile = {
                "name":              user.name,
                "age":               user.age,
                "gender":            user.gender,
                "weight_kg":         user.weight_kg,
                "height_cm":         user.height_cm,
                "target_weight_kg":  user.target_weight_kg,
                "goal":              user.goal,
                "activity_level":    user.activity_level,
                "gym_experience":    user.gym_experience,
                "workout_split":     user.workout_split,
                "diet_type":         user.diet_type,
                "allergies":         user.allergies or [],
                "target_calories":   user.target_calories,
                "protein_target_g":  user.protein_target_g,
                "carbs_target_g":    user.carbs_target_g,
                "fat_target_g":      user.fat_target_g,
                "water_target_liters": user.water_target_liters,
                "bmr":               user.bmr,
                "tdee":              user.tdee,
                "sleep_hours":       user.sleep_hours,
            }

        # ── Today's food totals ───────────────────────────────────────────
        today_food = FoodStore(db).get_daily_totals(uid, date.today())

        # ── Water ─────────────────────────────────────────────────────────
        target_water = profile.get("water_target_liters", 3.5)
        water_entry  = WaterStore(db).get_today(uid, target_water)
        today_water  = {
            "consumed_liters": water_entry.consumed_liters,
            "target_liters":   water_entry.target_liters,
        }

        # ── Weight trend (7 days) ─────────────────────────────────────────
        recent_weight = WeightStore(db).get_trend_data(uid, days=7)

        # ── Sleep average ─────────────────────────────────────────────────
        sleep_avg = SleepStore(db).get_average_hours(uid, days=7)

        # ── Active plans ──────────────────────────────────────────────────
        diet_obj = DietStore(db).get_active(uid)
        active_diet_plan = (
            {"id": diet_obj.id, "week_start": diet_obj.week_start,
             "plan_data": diet_obj.plan_data,
             "target_calories": diet_obj.target_calories,
             "target_protein":  diet_obj.target_protein}
            if diet_obj else None
        )

        wp_obj = WorkoutPlanStore(db).get_active(uid)
        active_workout_plan = (
            {"id": wp_obj.id, "split_type": wp_obj.split_type,
             "plan_name": wp_obj.plan_name, "plan_data": wp_obj.plan_data}
            if wp_obj else None
        )

        # ── Recent workouts (last 3) ──────────────────────────────────────
        recent_workouts = [
            {"session_name":   w.session_name,
             "log_date":       w.log_date.isoformat(),
             "total_volume_kg": w.total_volume_kg,
             "exercises":      w.exercises}
            for w in WorkoutStore(db).get_recent(uid, days=14)[:3]
        ]

        # ── Today's mess menu ─────────────────────────────────────────────
        mess_menu_today = MessStore(db).get_today_meals(uid)

        # ── Chat history (last 20) ────────────────────────────────────────
        chat_history = ChatStore(db).get_as_langchain_messages(
            uid, session_id, limit=20
        )

        db.close()

        return {
            **state,
            "user_profile":       profile,
            "today_food":         today_food,
            "today_water":        today_water,
            "recent_weight":      recent_weight,
            "sleep_avg":          sleep_avg,
            "active_diet_plan":   active_diet_plan,
            "active_workout_plan": active_workout_plan,
            "recent_workouts":    recent_workouts,
            "mess_menu_today":    mess_menu_today,
            "chat_history":       chat_history,
            "error":              "",
        }

    except Exception as e:
        return {**state, "error": f"context_loader: {e}"}
