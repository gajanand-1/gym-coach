from datetime import datetime, date
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Text, JSON
from app.models.database import Base


class WeeklyCheckIn(Base):
    __tablename__ = "weekly_checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    checkin_date = Column(Date, default=date.today, index=True)

    # User-reported metrics (1-10 scale where applicable)
    current_weight_kg = Column(Float, default=0.0)
    energy_level = Column(Integer, default=5)       # 1-10
    hunger_level = Column(Integer, default=5)       # 1-10
    sleep_quality = Column(Integer, default=5)      # 1-10
    recovery_quality = Column(Integer, default=5)   # 1-10

    # AI-generated analysis and adjustments
    ai_analysis = Column(Text, default="")
    calorie_adjustment = Column(Float, default=0.0)
    protein_adjustment = Column(Float, default=0.0)
    cardio_recommendation = Column(Text, default="")
    volume_recommendation = Column(Text, default="")

    # Full AI report as JSON
    report = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WeeklyCheckIn id={self.id} date={self.checkin_date}>"
