from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.models.water_log import WaterLog


class WaterStore:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create(self, user_id: int, log_date: date, target: float) -> WaterLog:
        entry = (
            self.db.query(WaterLog)
            .filter(WaterLog.user_id == user_id, WaterLog.log_date == log_date)
            .first()
        )
        if not entry:
            entry = WaterLog(user_id=user_id, log_date=log_date,
                             consumed_liters=0.0, target_liters=target)
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
        return entry

    def add_water(self, user_id: int, liters: float,
                  target: float = 3.5, log_date: Optional[date] = None) -> WaterLog:
        log_date = log_date or date.today()
        entry = self._get_or_create(user_id, log_date, target)
        entry.consumed_liters = round(entry.consumed_liters + liters, 2)
        entry.target_liters = target
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def set_water(self, user_id: int, liters: float,
                  target: float = 3.5, log_date: Optional[date] = None) -> WaterLog:
        log_date = log_date or date.today()
        entry = self._get_or_create(user_id, log_date, target)
        entry.consumed_liters = round(liters, 2)
        entry.target_liters = target
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_today(self, user_id: int, target: float = 3.5) -> WaterLog:
        return self._get_or_create(user_id, date.today(), target)

    def reset_today(self, user_id: int) -> WaterLog:
        entry = self.get_today(user_id)
        entry.consumed_liters = 0.0
        self.db.commit()
        self.db.refresh(entry)
        return entry
