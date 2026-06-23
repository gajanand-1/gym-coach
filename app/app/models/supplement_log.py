from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, JSON
from app.models.database import Base


class SupplementLog(Base):
    __tablename__ = "supplement_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    log_date = Column(Date, default=date.today, index=True)

    # Each entry is a dict: {name, taken, dose_g, time_of_day}
    supplements = Column(JSON, default=list)

    # Convenience boolean flags
    whey_protein = Column(Boolean, default=False)
    creatine = Column(Boolean, default=False)
    fish_oil = Column(Boolean, default=False)
    multivitamin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SupplementLog id={self.id} date={self.log_date}>"
