"""
Application startup utilities.
Called once when main.py first loads.
"""

import os
import sys

def ensure_project_on_path():
    """Add project root to sys.path so all imports work."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root not in sys.path:
        sys.path.insert(0, root)


def init_database():
    """Create all DB tables (idempotent — safe to call every start)."""
    from app.models.database import init_db
    init_db()


def verify_env():
    """Warn if critical env vars are missing."""
    import streamlit as st
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error(
            "⚠️ **ANTHROPIC_API_KEY is not set.**\n\n"
            "Add it to your `.env` file:\n```\nANTHROPIC_API_KEY=sk-ant-...\n```\n\n"
            "AI features (food parsing, diet plans, workout plans, coach chat) "
            "will not work until this is set.",
            icon="🔑",
        )
        return False
    return True


def run_startup():
    ensure_project_on_path()
    init_database()
