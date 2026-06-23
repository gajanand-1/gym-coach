from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.sleep_log import SleepLog


class SleepStore:
    def __init__(self, db: Session):
        self.db = db

    def log_sleep(
        self,
        user_id: int,
        hours: float,
        quality: str = "good",
        notes: str = "",
        log_date: Optional[date] = None,
    ) -> SleepLog:
        log_date = log_date or date.today()
        existing = (
            self.db.query(SleepLog)
            .filter(SleepLog.user_id == user_id, SleepLog.log_date == log_date)
            .first()
        )
        if existing:
            existing.hours = hours
            existing.quality = quality
            existing.notes = notes
            self.db.commit()
            self.db.refresh(existing)
            return existing

        entry = SleepLog(user_id=user_id, hours=hours,
                         quality=quality, notes=notes, log_date=log_date)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_recent(self, user_id: int, days: int = 14) -> List[SleepLog]:
        cutoff = date.today() - timedelta(days=days)
        return (
            self.db.query(SleepLog)
            .filter(SleepLog.user_id == user_id, SleepLog.log_date >= cutoff)
            .order_by(SleepLog.log_date)
            .all()
        )

    def get_average_hours(self, user_id: int, days: int = 7) -> float:
        entries = self.get_recent(user_id, days)
        if not entries:
            return 0.0
        return round(sum(e.hours for e in entries) / len(entries), 1)

    def get_trend(self, user_id: int, days: int = 14) -> List[Dict[str, Any]]:
        return [
            {"date": e.log_date.isoformat(), "hours": e.hours, "quality": e.quality}
            for e in self.get_recent(user_id, days)
        ]
