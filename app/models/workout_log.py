from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, JSON, Text
from app.models.database import Base


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    log_date = Column(Date, default=date.today, index=True)
    session_name = Column(String, default="")       # e.g. "Push Day A"
    split_type = Column(String, default="")         # push / pull / legs / upper / lower / full_body
    notes = Column(Text, default="")

    # List of exercise objects
    # [{exercise, weight_kg, sets: [reps, ...], rpe}]
    exercises = Column(JSON, default=list)

    # Computed totals
    total_volume_kg = Column(Float, default=0.0)    # sum(weight * reps) across all sets
    duration_minutes = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WorkoutLog id={self.id} date={self.log_date} session={self.session_name}>"


class WorkoutSet(Base):
    """Flat table for easy per-exercise queries (mirrors workout_log.exercises JSON)."""
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_log_id = Column(Integer, ForeignKey("workout_logs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    log_date = Column(Date, default=date.today, index=True)
    exercise_name = Column(String, nullable=False, index=True)
    weight_kg = Column(Float, default=0.0)
    set_number = Column(Integer, default=1)
    reps = Column(Integer, default=0)
    rpe = Column(Float, default=0.0)        # Rate of perceived exertion 1-10

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<WorkoutSet id={self.id} exercise={self.exercise_name} "
            f"weight={self.weight_kg} reps={self.reps}>"
        )
