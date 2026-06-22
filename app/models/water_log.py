from datetime import datetime, date
from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey
from app.models.database import Base


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    log_date = Column(Date, default=date.today, index=True, unique=False)
    consumed_liters = Column(Float, default=0.0)
    target_liters = Column(Float, default=3.5)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WaterLog id={self.id} date={self.log_date} consumed={self.consumed_liters}L>"
