from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.food_log import FoodLog


class FoodStore:
    def __init__(self, db: Session):
        self.db = db

    def add_entry(
        self,
        user_id: int,
        raw_input: str,
        food_items: List[Dict[str, Any]],
        total_calories: float,
        total_protein: float,
        total_carbs: float,
        total_fat: float,
        meal_type: str = "general",
        log_date: Optional[date] = None,
        source: str = "ai_parsed",
    ) -> FoodLog:
        entry = FoodLog(
            user_id=user_id,
            raw_input=raw_input,
            food_items=food_items,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            meal_type=meal_type,
            log_date=log_date or date.today(),
            source=source,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_by_date(self, user_id: int, log_date: date) -> List[FoodLog]:
        return (
            self.db.query(FoodLog)
            .filter(FoodLog.user_id == user_id, FoodLog.log_date == log_date)
            .order_by(FoodLog.created_at)
            .all()
        )

    def get_daily_totals(self, user_id: int, log_date: date) -> Dict[str, float]:
        rows = self.get_by_date(user_id, log_date)
        return {
            "calories": sum(r.total_calories for r in rows),
            "protein": sum(r.total_protein for r in rows),
            "carbs": sum(r.total_carbs for r in rows),
            "fat": sum(r.total_fat for r in rows),
        }

    def get_range(self, user_id: int, start: date, end: date) -> List[FoodLog]:
        return (
            self.db.query(FoodLog)
            .filter(
                FoodLog.user_id == user_id,
                FoodLog.log_date >= start,
                FoodLog.log_date <= end,
            )
            .order_by(FoodLog.log_date, FoodLog.created_at)
            .all()
        )

    def get_weekly_summary(self, user_id: int) -> List[Dict[str, Any]]:
        """Returns per-day aggregated totals for the last 7 days."""
        end = date.today()
        start = end - timedelta(days=6)
        rows = self.get_range(user_id, start, end)

        summary: Dict[date, Dict[str, float]] = {}
        for r in rows:
            d = r.log_date
            if d not in summary:
                summary[d] = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
            summary[d]["calories"] += r.total_calories
            summary[d]["protein"] += r.total_protein
            summary[d]["carbs"] += r.total_carbs
            summary[d]["fat"] += r.total_fat

        result = []
        for i in range(7):
            d = start + timedelta(days=i)
            totals = summary.get(d, {"calories": 0, "protein": 0, "carbs": 0, "fat": 0})
            result.append({"date": d.isoformat(), **totals})
        return result

    def delete_entry(self, entry_id: int, user_id: int) -> bool:
        entry = (
            self.db.query(FoodLog)
            .filter(FoodLog.id == entry_id, FoodLog.user_id == user_id)
            .first()
        )
        if entry:
            self.db.delete(entry)
            self.db.commit()
            return True
        return False
