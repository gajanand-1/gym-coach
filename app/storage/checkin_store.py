from datetime import date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.checkin import WeeklyCheckIn


class CheckInStore:
    def __init__(self, db: Session):
        self.db = db

    def save_checkin(
        self,
        user_id: int,
        current_weight_kg: float,
        energy_level: int,
        hunger_level: int,
        sleep_quality: int,
        recovery_quality: int,
        ai_analysis: str = "",
        calorie_adjustment: float = 0.0,
        protein_adjustment: float = 0.0,
        cardio_recommendation: str = "",
        volume_recommendation: str = "",
        report: dict = None,
        checkin_date: Optional[date] = None,
    ) -> WeeklyCheckIn:
        checkin_date = checkin_date or date.today()
        entry = WeeklyCheckIn(
            user_id=user_id,
            checkin_date=checkin_date,
            current_weight_kg=current_weight_kg,
            energy_level=energy_level,
            hunger_level=hunger_level,
            sleep_quality=sleep_quality,
            recovery_quality=recovery_quality,
            ai_analysis=ai_analysis,
            calorie_adjustment=calorie_adjustment,
            protein_adjustment=protein_adjustment,
            cardio_recommendation=cardio_recommendation,
            volume_recommendation=volume_recommendation,
            report=report or {},
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_last(self, user_id: int) -> Optional[WeeklyCheckIn]:
        return (
            self.db.query(WeeklyCheckIn)
            .filter(WeeklyCheckIn.user_id == user_id)
            .order_by(WeeklyCheckIn.checkin_date.desc())
            .first()
        )

    def is_due(self, user_id: int) -> bool:
        last = self.get_last(user_id)
        if not last:
            return True
        return (date.today() - last.checkin_date).days >= 7

    def get_all(self, user_id: int) -> List[WeeklyCheckIn]:
        return (
            self.db.query(WeeklyCheckIn)
            .filter(WeeklyCheckIn.user_id == user_id)
            .order_by(WeeklyCheckIn.checkin_date.desc())
            .all()
        )
