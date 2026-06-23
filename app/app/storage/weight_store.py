from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.weight_log import WeightLog


class WeightStore:
    def __init__(self, db: Session):
        self.db = db

    def log_weight(
        self,
        user_id: int,
        weight_kg: float,
        log_date: Optional[date] = None,
        body_fat_pct: float = 0.0,
        notes: str = "",
    ) -> WeightLog:
        log_date = log_date or date.today()
        # Upsert: update existing entry for same date
        existing = (
            self.db.query(WeightLog)
            .filter(WeightLog.user_id == user_id, WeightLog.log_date == log_date)
            .first()
        )
        if existing:
            existing.weight_kg = weight_kg
            existing.body_fat_pct = body_fat_pct
            existing.notes = notes
            self.db.commit()
            self.db.refresh(existing)
            return existing

        entry = WeightLog(
            user_id=user_id,
            weight_kg=weight_kg,
            log_date=log_date,
            body_fat_pct=body_fat_pct,
            notes=notes,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_latest(self, user_id: int) -> Optional[WeightLog]:
        return (
            self.db.query(WeightLog)
            .filter(WeightLog.user_id == user_id)
            .order_by(WeightLog.log_date.desc())
            .first()
        )

    def get_range(self, user_id: int, start: date, end: date) -> List[WeightLog]:
        return (
            self.db.query(WeightLog)
            .filter(
                WeightLog.user_id == user_id,
                WeightLog.log_date >= start,
                WeightLog.log_date <= end,
            )
            .order_by(WeightLog.log_date)
            .all()
        )

    def get_all(self, user_id: int) -> List[WeightLog]:
        return (
            self.db.query(WeightLog)
            .filter(WeightLog.user_id == user_id)
            .order_by(WeightLog.log_date)
            .all()
        )

    def get_trend_data(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        start = date.today() - timedelta(days=days)
        entries = self.get_range(user_id, start, date.today())
        return [
            {
                "date": e.log_date.isoformat(),
                "weight_kg": e.weight_kg,
                "body_fat_pct": e.body_fat_pct,
            }
            for e in entries
        ]

    def calculate_rate_of_change(self, user_id: int, days: int = 14) -> float:
        """Returns kg/week change (negative = losing weight)."""
        start = date.today() - timedelta(days=days)
        entries = self.get_range(user_id, start, date.today())
        if len(entries) < 2:
            return 0.0
        diff = entries[-1].weight_kg - entries[0].weight_kg
        weeks = days / 7
        return round(diff / weeks, 2) if weeks else 0.0
