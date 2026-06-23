from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, JSON, Text
from app.models.database import Base


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    log_date = Column(Date, default=date.today, index=True)
    meal_type = Column(String, default="general")   # breakfast / lunch / dinner / snack / general

    # Raw user input
    raw_input = Column(Text, default="")

    # Parsed food items stored as JSON list of dicts
    # [{name, quantity, unit, calories, protein, carbs, fat}]
    food_items = Column(JSON, default=list)

    # Aggregated totals for this log entry
    total_calories = Column(Float, default=0.0)
    total_protein = Column(Float, default=0.0)
    total_carbs = Column(Float, default=0.0)
    total_fat = Column(Float, default=0.0)

    # Source flag: manual / mess / ai_parsed
    source = Column(String, default="ai_parsed")

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FoodLog id={self.id} date={self.log_date} cal={self.total_calories}>"
