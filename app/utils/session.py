"""
Streamlit session-state management helpers.
All pages use these to access the current user without repeating auth checks.
"""

import streamlit as st
from typing import Optional
from app.models.database import SessionLocal
from app.storage.user_store import UserStore
from app.models.user import User


def require_login() -> Optional[int]:
    """
    Check if user is logged in. If not, redirect to login page.
    Returns user_id if authenticated, else None (and stops execution).
    """
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to continue.")
        st.stop()
    return st.session_state.get("user_id")


def get_current_user() -> Optional[User]:
    """Fetch the full User object for the logged-in user."""
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    db = SessionLocal()
    user = UserStore(db).get_by_id(user_id)
    db.close()
    return user


def init_session_defaults():
    """Initialise session state keys used across the app."""
    defaults = {
        "logged_in": False,
        "user_id": None,
        "username": None,
        "chat_session_id": "default",
        "food_log_pending_clarification": False,
        "food_log_clarification_msg": "",
        "food_log_pending_meal_type": None,
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default
