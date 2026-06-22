"""
Weight Service
--------------
Weight logging + trend analysis helpers.
"""

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.storage.weight_store import WeightStore
from app.services.macro_calculator import MacroCalculator


class WeightService:

    def __init__(self, db: Session):
        self.db = db
        self.store = WeightStore(db)

    def log_weight(
        self,
        user_id: int,
        weight_kg: float,
        body_fat_pct: float = 0.0,
        notes: str = "",
        log_date: Optional[date] = None,
    ) -> dict:
        entry = self.store.log_weight(
            user_id, weight_kg, log_date, body_fat_pct, notes
        )
        return {
            "id": entry.id,
            "date": entry.log_date.isoformat(),
            "weight_kg": entry.weight_kg,
            "body_fat_pct": entry.body_fat_pct,
        }

    def get_trend(self, user_id: int, days: int = 30) -> list:
        return self.store.get_trend_data(user_id, days)

    def get_all(self, user_id: int) -> list:
        entries = self.store.get_all(user_id)
        return [
            {
                "date": e.log_date.isoformat(),
                "weight_kg": e.weight_kg,
                "body_fat_pct": e.body_fat_pct,
            }
            for e in entries
        ]

    def get_stats(self, user_id: int, target_weight_kg: float,
                   goal: str = "fat_loss") -> dict:
        """Return a full stats dict for the Weight Tracker page."""
        latest = self.store.get_latest(user_id)
        current_weight = latest.weight_kg if latest else 0.0
        rate = self.store.calculate_rate_of_change(user_id, days=14)

        # Use sensible default rates if no data yet
        if rate == 0.0:
            default_rate = -0.5 if goal == "fat_loss" else 0.25
            eta = MacroCalculator.estimate_goal_date(
                current_weight, target_weight_kg, abs(default_rate)
            )
        else:
            eta = MacroCalculator.estimate_goal_date(
                current_weight, target_weight_kg, abs(rate)
            )

        remaining = round(abs(current_weight - target_weight_kg), 1)

        # 7 / 30 / 90 day trends
        trend_7d = self.store.get_trend_data(user_id, days=7)
        trend_30d = self.store.get_trend_data(user_id, days=30)

        # Weekly average weights
        weekly_avg = self._calc_weekly_averages(trend_30d)

        return {
            "current_kg": current_weight,
            "target_kg": target_weight_kg,
            "remaining_kg": remaining,
            "rate_per_week": rate,
            "eta": eta,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d,
            "weekly_averages": weekly_avg,
        }

    @staticmethod
    def _calc_weekly_averages(trend: list) -> list:
        """Bucket trend data into weekly averages."""
        from datetime import datetime, timedelta
        if not trend:
            return []

        # Group by week number
        weeks: dict = {}
        for entry in trend:
            d = datetime.fromisoformat(entry["date"])
            week_key = d.strftime("%Y-W%U")
            weeks.setdefault(week_key, []).append(entry["weight_kg"])

        return [
            {"week": week, "avg_kg": round(sum(weights) / len(weights), 2)}
            for week, weights in sorted(weeks.items())
        ]
