from typing import List
from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory


class ChatStore:
    def __init__(self, db: Session):
        self.db = db

    def add_message(self, user_id: int, role: str, content: str,
                    session_id: str = "default") -> ChatHistory:
        msg = ChatHistory(user_id=user_id, role=role,
                          content=content, session_id=session_id)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_history(self, user_id: int, session_id: str = "default",
                    limit: int = 50) -> List[ChatHistory]:
        return (
            self.db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id,
                    ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at)
            .limit(limit)
            .all()
        )

    def get_last_n(self, user_id: int, n: int = 10,
                   session_id: str = "default") -> List[ChatHistory]:
        rows = (
            self.db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id,
                    ChatHistory.session_id == session_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(n)
            .all()
        )
        return list(reversed(rows))

    def clear_session(self, user_id: int, session_id: str = "default") -> int:
        deleted = (
            self.db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id,
                    ChatHistory.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return deleted

    def get_as_langchain_messages(self, user_id: int,
                                   session_id: str = "default",
                                   limit: int = 20) -> List[dict]:
        msgs = self.get_last_n(user_id, limit, session_id)
        return [{"role": m.role, "content": m.content} for m in msgs]
