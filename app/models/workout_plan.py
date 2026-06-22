from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean
from app.models.database import Base


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    plan_name = Column(String, default="Weekly Workout Plan")
    split_type = Column(String, default="push_pull_legs")   # push_pull_legs / upper_lower / full_body
    is_active = Column(Boolean, default=True)

    # Full plan stored as JSON
    # {
    #   "Monday": {
    #     "session": "Push Day A",
    #     "exercises": [
    #       {name, sets, reps, rest_seconds, notes}
    #     ]
    #   },
    #   "Tuesday": {"session": "Rest", "exercises": []},
    #   ...
    # }
    plan_data = Column(JSON, default=dict)

    raw_response = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WorkoutPlan id={self.id} split={self.split_type} active={self.is_active}>"
