from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Personal info
    name = Column(String, default="")
    age = Column(Integer, default=22)
    gender = Column(String, default="male")          # male / female
    height_cm = Column(Float, default=175.0)
    weight_kg = Column(Float, default=82.0)
    target_weight_kg = Column(Float, default=75.0)

    # Goals & activity
    goal = Column(String, default="fat_loss")        # fat_loss / muscle_gain / maintenance
    activity_level = Column(String, default="moderate")  # sedentary / light / moderate / active / very_active
    gym_experience = Column(String, default="beginner")  # beginner / intermediate / advanced
    workout_split = Column(String, default="push_pull_legs")  # push_pull_legs / upper_lower / full_body

    # Diet
    diet_type = Column(String, default="non_vegetarian")
    allergies = Column(JSON, default=list)
    sleep_hours = Column(Float, default=7.0)

    # Calculated macros (cached, recomputed on profile save)
    bmr = Column(Float, default=0.0)
    tdee = Column(Float, default=0.0)
    target_calories = Column(Float, default=0.0)
    protein_target_g = Column(Float, default=0.0)
    carbs_target_g = Column(Float, default=0.0)
    fat_target_g = Column(Float, default=0.0)
    water_target_liters = Column(Float, default=3.5)

    # Auth / meta
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"
