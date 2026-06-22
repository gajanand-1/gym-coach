from typing import Optional
from sqlalchemy.orm import Session
from app.models.mess_menu import MessMenu


class MessStore:
    def __init__(self, db: Session):
        self.db = db

    def save_menu(
        self,
        user_id: int,
        menu_data: dict,
        raw_input: str = "",
        source_type: str = "text",
        menu_name: str = "Hostel Mess Menu",
    ) -> MessMenu:
        # Deactivate old menus
        (
            self.db.query(MessMenu)
            .filter(MessMenu.user_id == user_id, MessMenu.is_active == True)  # noqa: E712
            .update({"is_active": False})
        )

        menu = MessMenu(
            user_id=user_id,
            menu_data=menu_data,
            raw_input=raw_input,
            source_type=source_type,
            menu_name=menu_name,
            is_active=True,
        )
        self.db.add(menu)
        self.db.commit()
        self.db.refresh(menu)
        return menu

    def get_active(self, user_id: int) -> Optional[MessMenu]:
        return (
            self.db.query(MessMenu)
            .filter(MessMenu.user_id == user_id, MessMenu.is_active == True)  # noqa: E712
            .order_by(MessMenu.created_at.desc())
            .first()
        )

    def get_today_meals(self, user_id: int) -> dict:
        """Return today's breakfast/lunch/dinner from the active mess menu."""
        from datetime import date
        menu = self.get_active(user_id)
        if not menu or not menu.menu_data:
            return {}
        day_name = date.today().strftime("%A")  # Monday, Tuesday…
        return menu.menu_data.get(day_name, {})

    def delete_active(self, user_id: int) -> bool:
        menu = self.get_active(user_id)
        if menu:
            self.db.delete(menu)
            self.db.commit()
            return True
        return False
