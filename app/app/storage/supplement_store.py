from datetime import date
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.supplement_log import SupplementLog


class SupplementStore:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create(self, user_id: int, log_date: date) -> SupplementLog:
        entry = (
            self.db.query(SupplementLog)
            .filter(SupplementLog.user_id == user_id, SupplementLog.log_date == log_date)
            .first()
        )
        if not entry:
            default_supplements = [
                {"name": "Whey Protein", "taken": False, "dose_g": 30, "time_of_day": "post_workout"},
                {"name": "Creatine", "taken": False, "dose_g": 5, "time_of_day": "any"},
                {"name": "Fish Oil", "taken": False, "dose_g": 2, "time_of_day": "with_meal"},
                {"name": "Multivitamin", "taken": False, "dose_g": 1, "time_of_day": "morning"},
            ]
            entry = SupplementLog(
                user_id=user_id,
                log_date=log_date,
                supplements=default_supplements,
            )
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
        return entry

    def get_today(self, user_id: int) -> SupplementLog:
        return self._get_or_create(user_id, date.today())

    def update_supplement(self, user_id: int, supplement_name: str,
                          taken: bool, log_date: Optional[date] = None) -> SupplementLog:
        log_date = log_date or date.today()
        entry = self._get_or_create(user_id, log_date)

        # Update in list
        supps = list(entry.supplements)
        for s in supps:
            if s["name"].lower() == supplement_name.lower():
                s["taken"] = taken
        entry.supplements = supps

        # Update convenience booleans
        name_lower = supplement_name.lower()
        if "whey" in name_lower:
            entry.whey_protein = taken
        elif "creatine" in name_lower:
            entry.creatine = taken
        elif "fish" in name_lower:
            entry.fish_oil = taken
        elif "multivitamin" in name_lower or "multi" in name_lower:
            entry.multivitamin = taken

        self.db.commit()
        self.db.refresh(entry)
        return entry

    def save_today(self, user_id: int, supplements: List[Dict[str, Any]]) -> SupplementLog:
        entry = self._get_or_create(user_id, date.today())
        entry.supplements = supplements
        entry.whey_protein = any(
            s.get("taken") and "whey" in s.get("name", "").lower() for s in supplements
        )
        entry.creatine = any(
            s.get("taken") and "creatine" in s.get("name", "").lower() for s in supplements
        )
        entry.fish_oil = any(
            s.get("taken") and "fish" in s.get("name", "").lower() for s in supplements
        )
        entry.multivitamin = any(
            s.get("taken") and "multi" in s.get("name", "").lower() for s in supplements
        )
        self.db.commit()
        self.db.refresh(entry)
        return entry
