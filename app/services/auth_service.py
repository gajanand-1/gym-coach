"""
Auth Service
------------
Wraps UserStore with session state helpers for Streamlit.
"""

from typing import Optional
import streamlit as st
from sqlalchemy.orm import Session
from app.models.user import User
from app.storage.user_store import UserStore
from app.services.macro_calculator import MacroCalculator


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.store = UserStore(db)

    def register(
        self,
        username: str,
        email: str,
        password: str,
        name: str = "",
    ) -> tuple[bool, str]:
        """Register a new user. Returns (success, message)."""
        if self.store.get_by_username(username):
            return False, "Username already taken."
        if self.store.get_by_email(email):
            return False, "Email already registered."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."

        user = self.store.create(username, email, password, name)
        return True, f"Account created! Welcome, {user.name or user.username}."

    def login(self, username: str, password: str) -> tuple[bool, str, Optional[User]]:
        """Authenticate user. Returns (success, message, user)."""
        user = self.store.authenticate(username, password)
        if not user:
            return False, "Invalid username or password.", None
        return True, f"Welcome back, {user.name or user.username}!", user

    def save_profile_and_recalculate(self, user_id: int, **profile_data) -> Optional[User]:
        """
        Save profile fields and recalculate all macro targets.
        Call this after any profile update so targets stay in sync.
        """
        # First update the raw profile fields
        user = self.store.update_profile(user_id, **profile_data)
        if not user:
            return None

        # Recalculate macros
        result = MacroCalculator.calculate_targets(
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            age=user.age,
            gender=user.gender,
            activity_level=user.activity_level,
            goal=user.goal,
        )

        # Persist calculated targets
        user = self.store.update_macros(
            user_id=user_id,
            bmr=result.bmr,
            tdee=result.tdee,
            target_calories=result.target_calories,
            protein_target_g=result.protein_g,
            carbs_target_g=result.carbs_g,
            fat_target_g=result.fat_g,
            water_target_liters=result.water_liters,
        )
        return user

    # ------------------------------------------------------------------
    # Streamlit session state helpers
    # ------------------------------------------------------------------

    @staticmethod
    def set_session_user(user: User):
        st.session_state["user_id"] = user.id
        st.session_state["username"] = user.username
        st.session_state["logged_in"] = True

    @staticmethod
    def clear_session():
        for key in ["user_id", "username", "logged_in"]:
            st.session_state.pop(key, None)

    @staticmethod
    def is_logged_in() -> bool:
        return st.session_state.get("logged_in", False)

    @staticmethod
    def current_user_id() -> Optional[int]:
        return st.session_state.get("user_id")
