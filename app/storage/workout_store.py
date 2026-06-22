from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.workout_log import WorkoutLog, WorkoutSet


class WorkoutStore:
    def __init__(self, db: Session):
        self.db = db

    def log_session(
        self,
        user_id: int,
        session_name: str,
        split_type: str,
        exercises: List[Dict[str, Any]],
        notes: str = "",
        log_date: Optional[date] = None,
        duration_minutes: int = 0,
    ) -> WorkoutLog:
        log_date = log_date or date.today()

        # Calculate total volume
        total_volume = 0.0
        for ex in exercises:
            w = ex.get("weight_kg", 0)
            for reps in ex.get("sets", []):
                total_volume += w * reps

        wl = WorkoutLog(
            user_id=user_id,
            session_name=session_name,
            split_type=split_type,
            exercises=exercises,
            notes=notes,
            log_date=log_date,
            total_volume_kg=total_volume,
            duration_minutes=duration_minutes,
        )
        self.db.add(wl)
        self.db.flush()  # get wl.id before creating sets

        # Mirror to flat WorkoutSet table
        for ex in exercises:
            for i, reps in enumerate(ex.get("sets", []), start=1):
                ws = WorkoutSet(
                    workout_log_id=wl.id,
                    user_id=user_id,
                    log_date=log_date,
                    exercise_name=ex.get("exercise", ""),
                    weight_kg=ex.get("weight_kg", 0),
                    set_number=i,
                    reps=reps,
                    rpe=ex.get("rpe", 0),
                )
                self.db.add(ws)

        self.db.commit()
        self.db.refresh(wl)
        return wl

    def get_by_date(self, user_id: int, log_date: date) -> List[WorkoutLog]:
        return (
            self.db.query(WorkoutLog)
            .filter(WorkoutLog.user_id == user_id, WorkoutLog.log_date == log_date)
            .order_by(WorkoutLog.created_at)
            .all()
        )

    def get_recent(self, user_id: int, days: int = 30) -> List[WorkoutLog]:
        cutoff = date.today() - timedelta(days=days)
        return (
            self.db.query(WorkoutLog)
            .filter(WorkoutLog.user_id == user_id, WorkoutLog.log_date >= cutoff)
            .order_by(WorkoutLog.log_date.desc())
            .all()
        )

    def get_exercise_history(
        self, user_id: int, exercise_name: str, limit: int = 10
    ) -> List[WorkoutSet]:
        """Return last N sets for a specific exercise for progressive overload analysis."""
        return (
            self.db.query(WorkoutSet)
            .filter(
                WorkoutSet.user_id == user_id,
                WorkoutSet.exercise_name.ilike(f"%{exercise_name}%"),
            )
            .order_by(WorkoutSet.log_date.desc(), WorkoutSet.set_number)
            .limit(limit * 4)  # ~4 sets per session
            .all()
        )

    def get_all_exercises_last_two_weeks(self, user_id: int) -> Dict[str, List[Dict]]:
        """Group sets by exercise for the last 14 days — used by progressive overload agent."""
        cutoff = date.today() - timedelta(days=14)
        sets = (
            self.db.query(WorkoutSet)
            .filter(WorkoutSet.user_id == user_id, WorkoutSet.log_date >= cutoff)
            .order_by(WorkoutSet.exercise_name, WorkoutSet.log_date, WorkoutSet.set_number)
            .all()
        )
        grouped: Dict[str, List[Dict]] = {}
        for s in sets:
            ex = s.exercise_name.lower()
            grouped.setdefault(ex, []).append(
                {
                    "date": s.log_date.isoformat(),
                    "set": s.set_number,
                    "weight_kg": s.weight_kg,
                    "reps": s.reps,
                }
            )
        return grouped

    def delete_session(self, session_id: int, user_id: int) -> bool:
        wl = (
            self.db.query(WorkoutLog)
            .filter(WorkoutLog.id == session_id, WorkoutLog.user_id == user_id)
            .first()
        )
        if wl:
            self.db.query(WorkoutSet).filter(WorkoutSet.workout_log_id == wl.id).delete()
            self.db.delete(wl)
            self.db.commit()
            return True
        return False
