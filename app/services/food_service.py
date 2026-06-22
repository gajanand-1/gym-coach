"""
Food Service
------------
Orchestrates food logging via the LangGraph pipeline,
and provides helpers for the Food Log / Calorie Tracker UI.
"""

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.graph.food_log_graph import run_food_log_graph
from app.storage.food_store import FoodStore
from app.storage.mess_store import MessStore


class FoodService:

    def __init__(self, db: Session):
        self.db = db
        self.food_store = FoodStore(db)
        self.mess_store = MessStore(db)

    def log_food(
        self,
        user_id: int,
        raw_input: str,
        meal_type: Optional[str] = None,
    ) -> dict:
        """
        Main entry point for logging food.
        Returns the final graph state (includes parsed_result, error,
        needs_clarification, clarification_message).
        """
        # Get today's mess menu if available
        mess_today = self.mess_store.get_today_meals(user_id)

        result = run_food_log_graph(
            user_id=user_id,
            raw_input=raw_input,
            meal_type=meal_type,
            mess_menu_today=mess_today,
        )
        return result

    def get_today_summary(self, user_id: int) -> dict:
        return self.food_store.get_daily_totals(user_id, date.today())

    def get_today_entries(self, user_id: int) -> list:
        entries = self.food_store.get_by_date(user_id, date.today())
        return [
            {
                "id": e.id,
                "meal_type": e.meal_type,
                "raw_input": e.raw_input,
                "food_items": e.food_items,
                "calories": e.total_calories,
                "protein": e.total_protein,
                "carbs": e.total_carbs,
                "fat": e.total_fat,
                "source": e.source,
                "time": e.created_at.strftime("%H:%M") if e.created_at else "",
            }
            for e in entries
        ]

    def delete_entry(self, entry_id: int, user_id: int) -> bool:
        return self.food_store.delete_entry(entry_id, user_id)

    def get_weekly_summary(self, user_id: int) -> list:
        return self.food_store.get_weekly_summary(user_id)

    def get_calorie_tracker_data(self, user_id: int, target_calories: float,
                                  target_protein: float, target_carbs: float,
                                  target_fat: float) -> dict:
        """Return consumed vs remaining vs target for Calorie Tracker page."""
        totals = self.food_store.get_daily_totals(user_id, date.today())
        return {
            "calories": {
                "consumed": totals["calories"],
                "target": target_calories,
                "remaining": max(0, target_calories - totals["calories"]),
                "pct": round(totals["calories"] / target_calories * 100, 1) if target_calories else 0,
            },
            "protein": {
                "consumed": totals["protein"],
                "target": target_protein,
                "remaining": max(0, target_protein - totals["protein"]),
                "pct": round(totals["protein"] / target_protein * 100, 1) if target_protein else 0,
            },
            "carbs": {
                "consumed": totals["carbs"],
                "target": target_carbs,
                "remaining": max(0, target_carbs - totals["carbs"]),
                "pct": round(totals["carbs"] / target_carbs * 100, 1) if target_carbs else 0,
            },
            "fat": {
                "consumed": totals["fat"],
                "target": target_fat,
                "remaining": max(0, target_fat - totals["fat"]),
                "pct": round(totals["fat"] / target_fat * 100, 1) if target_fat else 0,
            },
        }
