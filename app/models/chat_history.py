from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.models.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    role = Column(String, nullable=False)   # user / assistant / system
    content = Column(Text, nullable=False)

    # Session grouping so we can show separate "conversations"
    session_id = Column(String, default="default", index=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ChatHistory id={self.id} role={self.role} session={self.session_id}>"
