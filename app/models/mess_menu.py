from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean
from app.models.database import Base


class MessMenu(Base):
    __tablename__ = "mess_menus"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    menu_name = Column(String, default="Hostel Mess Menu")
    is_active = Column(Boolean, default=True)

    # Structured weekly menu
    # {
    #   "Monday": {
    #     "breakfast": ["Aloo Paratha", "Dahi", "Egg"],
    #     "lunch": ["Rice", "Dal", "Sabzi"],
    #     "dinner": ["Roti", "Dal Tadka", "Sabzi"]
    #   },
    #   ...
    # }
    menu_data = Column(JSON, default=dict)

    # Raw text/source used for parsing
    raw_input = Column(Text, default="")
    source_type = Column(String, default="text")    # text / pdf / image

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<MessMenu id={self.id} user_id={self.user_id} active={self.is_active}>"
