from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from app.models.database import Base


class GroceryPlan(Base):
    __tablename__ = "grocery_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    diet_plan_id = Column(Integer, ForeignKey("diet_plans.id"), nullable=True)

    is_active = Column(Boolean, default=True)
    week_start = Column(String, default="")

    # List of grocery items
    # [{name, quantity, unit, weekly_requirement, available_in_mess}]
    items = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<GroceryPlan id={self.id} user_id={self.user_id}>"
