"""
Personal AI Gym Coach — Main Entry Point
=========================================
Run with:
    streamlit run main.py

This file serves as the home/login page.
All other pages live in app/ui/pages/ and are auto-discovered by Streamlit.
"""

import os
import sys

# ── Ensure project root is on sys.path so all imports resolve correctly ──
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config MUST be the very first Streamlit command ─────────────────
st.set_page_config(
    page_title="AI Gym Coach",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DB + path initialisation (runs once on startup) ─────────────────────
from app.startup import run_startup
run_startup()

# ── Session state bootstrap ──────────────────────────────────────────────
from app.utils.session import init_session_defaults
init_session_defaults()

# ── CSS ──────────────────────────────────────────────────────────────────
from app.ui.style import inject_css, section_header
inject_css()

# ── If already logged in → clickable navigation home ────────────────────
if st.session_state.get("logged_in"):
    user_name = st.session_state.get("username", "Athlete")

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1E2130,#161B27);
                border-radius:14px;padding:20px 24px;
                border:1px solid #2A2F45;margin-bottom:24px">
        <span style="font-size:1.5rem">👋</span>
        <span style="color:#FAFAFA;font-size:1.2rem;font-weight:700;margin-left:8px">
            Welcome back, {user_name}!
        </span><br>
        <span style="color:#8892A4;font-size:0.9rem">
            Click any page below to jump straight in.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Page navigation cards (2 columns) ────────────────────────────────
    PAGES = [
        ("app/ui/pages/00_Coach.py",               "🤖", "AI Coach (Unified)",  "⭐ Type anything — routes ALL commands through LangGraph"),
        ("app/ui/pages/01_Dashboard.py",          "🏠", "Dashboard",          "Daily snapshot — calories, macros, water, sleep, workout"),
        ("app/ui/pages/02_Profile.py",             "👤", "Profile",            "Update details & auto-recalculate macros"),
        ("app/ui/pages/03_Food_Log.py",            "🍽️", "Food Log",           "Log food — LangGraph food_log_node"),
        ("app/ui/pages/04_Calorie_Tracker.py",     "🔥", "Calorie Tracker",    "Live consumed vs remaining vs target"),
        ("app/ui/pages/05_Diet_Planner.py",        "🥗", "Diet Planner",       "LangGraph diet_plan_node → 7-day meal plan"),
        ("app/ui/pages/06_Workout_Planner.py",     "💪", "Workout Planner",    "LangGraph workout_plan_node → weekly programme"),
        ("app/ui/pages/07_Workout_Log.py",         "📋", "Workout Log",        "LangGraph workout_log_node → volume tracking"),
        ("app/ui/pages/08_Progressive_Overload.py","📈", "Progressive Overload","LangGraph overload_node → strength analysis"),
        ("app/ui/pages/09_Weight_Tracker.py",      "⚖️", "Weight Tracker",     "LangGraph weight_log_node → trend charts"),
        ("app/ui/pages/10_Grocery_Planner.py",     "🛒", "Grocery Planner",    "LangGraph grocery_node → auto grocery list"),
        ("app/ui/pages/11_Weekly_Checkin.py",      "📊", "Weekly Check-In",    "LangGraph checkin_node → AI weekly review"),
        ("app/ui/pages/12_Water_Tracker.py",       "💧", "Water Tracker",      "LangGraph water_log_node → hydration gauge"),
        ("app/ui/pages/13_Sleep_Tracker.py",       "😴", "Sleep Tracker",      "LangGraph sleep_log_node → recovery insights"),
        ("app/ui/pages/14_Supplement_Tracker.py",  "💊", "Supplement Tracker", "LangGraph supplement_node → daily adherence"),
        ("app/ui/pages/15_AI_Coach_Chat.py",       "💬", "AI Coach Chat",      "Classic chat with full context"),
        ("app/ui/pages/16_Mess_Menu.py",           "🏫", "Mess Menu",          "LangGraph mess_menu_node → menu parsing"),
    ]

    col_a, col_b = st.columns(2)
    for i, (page_path, icon, title, desc) in enumerate(PAGES):
        col = col_a if i % 2 == 0 else col_b
        with col:
            st.page_link(
                page_path,
                label=f"{icon} **{title}**  \n{desc}",
                use_container_width=True,
            )

    st.divider()
    if st.button("🚪 Logout", type="secondary"):
        from app.services.auth_service import AuthService
        AuthService.clear_session()
        st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════
# LOGIN / REGISTER  (shown only when NOT logged in)
# ══════════════════════════════════════════════════════════════════════════

# ── Hero ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 20px">
    <div style="font-size:4rem">🏋️</div>
    <h1 style="color:#FAFAFA;font-size:2.5rem;font-weight:800;margin:8px 0">
        Personal AI Gym Coach
    </h1>
    <p style="color:#8892A4;font-size:1.1rem;max-width:600px;margin:0 auto">
        Your AI-powered personal trainer, nutritionist & progress coach.<br>
        Tracks food, workouts, weight, sleep, supplements — and adapts to <em>you</em>.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Feature badges ────────────────────────────────────────────────────────
feat_cols = st.columns(4)
features = [
    ("🤖", "AI Food Parsing", "Log food in plain English"),
    ("💪", "Smart Workout Plans", "PPL / Upper-Lower / Full Body"),
    ("📈", "Progressive Overload", "Auto weight progression"),
    ("🥗", "7-Day Diet Plans", "Non-veg, high-protein meals"),
]
for col, (icon, title, desc) in zip(feat_cols, features):
    col.markdown(
        f'<div style="background:#1E2130;border-radius:10px;padding:16px;text-align:center;'
        f'border:1px solid #2A2F45;height:120px">'
        f'<div style="font-size:1.8rem">{icon}</div>'
        f'<div style="color:#FAFAFA;font-weight:600;font-size:0.95rem">{title}</div>'
        f'<div style="color:#8892A4;font-size:0.8rem">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── API key warning ───────────────────────────────────────────────────────
if not os.getenv("ANTHROPIC_API_KEY"):
    st.warning(
        "⚠️ **ANTHROPIC_API_KEY not set** — AI features won't work until you add it to `.env`",
        icon="🔑",
    )

# ── Auth tabs ─────────────────────────────────────────────────────────────
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

    # ── LOGIN ──
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="your_username")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            login_btn = st.form_submit_button("Login", use_container_width=True, type="primary")

        if login_btn:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                from app.models.database import SessionLocal
                from app.services.auth_service import AuthService
                db = SessionLocal()
                auth = AuthService(db)
                success, msg, user = auth.login(username, password)
                db.close()

                if success and user:
                    AuthService.set_session_user(user)
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # ── REGISTER ──
    with tab_register:
        with st.form("register_form"):
            reg_name     = st.text_input("Full Name",  placeholder="John Doe")
            reg_username = st.text_input("Username",   placeholder="johndoe")
            reg_email    = st.text_input("Email",      placeholder="john@example.com")
            reg_pw       = st.text_input("Password",   type="password", placeholder="Min 6 characters")
            reg_pw2      = st.text_input("Confirm Password", type="password")
            register_btn = st.form_submit_button("Create Account", use_container_width=True, type="primary")

        if register_btn:
            if not all([reg_name, reg_username, reg_email, reg_pw]):
                st.error("All fields are required.")
            elif reg_pw != reg_pw2:
                st.error("Passwords do not match.")
            else:
                from app.models.database import SessionLocal
                from app.services.auth_service import AuthService
                db = SessionLocal()
                auth = AuthService(db)
                success, msg = auth.register(reg_username, reg_email, reg_pw, reg_name)
                if success:
                    # Auto-login after registration
                    _, _, user = auth.login(reg_username, reg_pw)
                    db.close()
                    if user:
                        AuthService.set_session_user(user)
                        st.success(f"🎉 {msg} Setting up your profile…")
                        st.rerun()
                else:
                    db.close()
                    st.error(msg)
