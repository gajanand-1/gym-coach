from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean
from app.models.database import Base


class DietPlan(Base):
    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    plan_name = Column(String, default="Weekly Meal Plan")
    is_active = Column(Boolean, default=True)
    week_start = Column(String, default="")     # ISO date string

    # Full plan stored as JSON
    # {
    #   "Monday": {
    #     "breakfast": [{name, quantity, unit, calories, protein, carbs, fat}],
    #     "lunch": [...],
    #     "dinner": [...],
    #     "snacks": [...]
    #   }, ...
    # }
    plan_data = Column(JSON, default=dict)

    # Aggregated daily targets used when generating plan
    target_calories = Column(Integer, default=0)
    target_protein = Column(Integer, default=0)

    # Raw AI response (for debugging / regeneration context)
    raw_response = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DietPlan id={self.id} user_id={self.user_id} active={self.is_active}>"
