from datetime import datetime, date
from sqlalchemy import Column, Integer, Float, String, DateTime, Date, ForeignKey, Text
from app.models.database import Base


class SleepLog(Base):
    __tablename__ = "sleep_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    log_date = Column(Date, default=date.today, index=True)
    hours = Column(Float, nullable=False)
    quality = Column(String, default="good")    # poor / fair / good / excellent
    notes = Column(Text, default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SleepLog id={self.id} date={self.log_date} hours={self.hours}>"
