from datetime import datetime, date
from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, Text
from app.models.database import Base


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    log_date = Column(Date, default=date.today, index=True)
    weight_kg = Column(Float, nullable=False)
    body_fat_pct = Column(Float, default=0.0)   # optional
    notes = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WeightLog id={self.id} date={self.log_date} weight={self.weight_kg}>"
