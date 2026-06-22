"""
Dashboard Service
-----------------
Aggregates all data needed by the Dashboard page in a single call.
"""

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.storage.user_store import UserStore
from app.storage.food_store import FoodStore
from app.storage.water_store import WaterStore
from app.storage.weight_store import WeightStore
from app.storage.sleep_store import SleepStore
from app.storage.supplement_store import SupplementStore
from app.storage.workout_store import WorkoutStore
from app.storage.checkin_store import CheckInStore


class DashboardService:

    def __init__(self, db: Session):
        self.db = db

    def get_snapshot(self, user_id: int) -> dict:
        """
        Return everything the Dashboard page needs in one dict.
        """
        user_store = UserStore(self.db)
        user = user_store.get_by_id(user_id)
        if not user:
            return {}

        today = date.today()

        # ---- Food ----
        food_store = FoodStore(self.db)
        food_totals = food_store.get_daily_totals(user_id, today)
        food_entries = food_store.get_by_date(user_id, today)

        # ---- Water ----
        water_store = WaterStore(self.db)
        water = water_store.get_today(user_id, user.water_target_liters)

        # ---- Weight ----
        weight_store = WeightStore(self.db)
        latest_weight = weight_store.get_latest(user_id)
        weekly_weight = weight_store.get_trend_data(user_id, days=7)
        weight_rate = weight_store.calculate_rate_of_change(user_id, days=14)

        # ---- Sleep ----
        sleep_store = SleepStore(self.db)
        sleep_avg = sleep_store.get_average_hours(user_id, days=7)
        sleep_today = sleep_store.get_recent(user_id, days=1)

        # ---- Supplements ----
        supp_store = SupplementStore(self.db)
        supps = supp_store.get_today(user_id)

        # ---- Workout ----
        workout_store = WorkoutStore(self.db)
        today_workouts = workout_store.get_by_date(user_id, today)
        recent_workouts = workout_store.get_recent(user_id, days=7)

        # ---- Check-in ----
        checkin_store = CheckInStore(self.db)
        checkin_due = checkin_store.is_due(user_id)

        # ---- Weekly food summary ----
        weekly_food = food_store.get_weekly_summary(user_id)

        # ---- Remaining calculations ----
        cal_consumed = food_totals.get("calories", 0)
        cal_target = user.target_calories or 0
        cal_remaining = max(0, cal_target - cal_consumed)
        cal_pct = round(cal_consumed / cal_target * 100, 1) if cal_target else 0

        pro_consumed = food_totals.get("protein", 0)
        pro_target = user.protein_target_g or 0
        pro_remaining = max(0, pro_target - pro_consumed)
        pro_pct = round(pro_consumed / pro_target * 100, 1) if pro_target else 0

        water_pct = round(
            water.consumed_liters / water.target_liters * 100, 1
        ) if water.target_liters else 0

        return {
            # User
            "user": {
                "name": user.name,
                "goal": user.goal,
                "weight_kg": user.weight_kg,
                "target_weight_kg": user.target_weight_kg,
                "target_calories": cal_target,
                "protein_target_g": pro_target,
                "carbs_target_g": user.carbs_target_g,
                "fat_target_g": user.fat_target_g,
                "water_target_liters": user.water_target_liters,
                "bmr": user.bmr,
                "tdee": user.tdee,
            },
            # Today food
            "food": {
                "consumed": food_totals,
                "remaining_calories": cal_remaining,
                "remaining_protein": pro_remaining,
                "calories_pct": cal_pct,
                "protein_pct": pro_pct,
                "entries": [
                    {
                        "meal_type": e.meal_type,
                        "total_calories": e.total_calories,
                        "total_protein": e.total_protein,
                        "raw_input": e.raw_input,
                    }
                    for e in food_entries
                ],
            },
            # Water
            "water": {
                "consumed_liters": water.consumed_liters,
                "target_liters": water.target_liters,
                "remaining_liters": max(0, water.target_liters - water.consumed_liters),
                "pct": water_pct,
            },
            # Weight
            "weight": {
                "current_kg": latest_weight.weight_kg if latest_weight else user.weight_kg,
                "target_kg": user.target_weight_kg,
                "weekly_trend": weekly_weight,
                "rate_kg_per_week": weight_rate,
            },
            # Sleep
            "sleep": {
                "avg_hours_7d": sleep_avg,
                "today_hours": sleep_today[0].hours if sleep_today else None,
            },
            # Supplements
            "supplements": {
                "items": supps.supplements,
                "whey": supps.whey_protein,
                "creatine": supps.creatine,
                "fish_oil": supps.fish_oil,
                "multivitamin": supps.multivitamin,
            },
            # Workout
            "workout": {
                "done_today": len(today_workouts) > 0,
                "sessions_today": [w.session_name for w in today_workouts],
                "sessions_this_week": len(recent_workouts),
            },
            # Weekly food chart data
            "weekly_food_summary": weekly_food,
            # Check-in
            "checkin_due": checkin_due,
        }
