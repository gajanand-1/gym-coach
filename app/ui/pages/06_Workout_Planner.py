import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.services.workout_service import WorkoutService

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

st.set_page_config(page_title="Workout Planner", page_icon="💪", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user = get_current_user()

st.markdown("## 💪 AI Workout Planner")
st.markdown("Generate and view your personalised weekly training programme.")
st.divider()

db = SessionLocal()
svc = WorkoutService(db)

# ── Generate Plan ────────────────────────────────────────────────────────
with st.expander("⚙️ Generate New Plan", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        split = st.selectbox("Workout Split",
            ["push_pull_legs", "upper_lower", "full_body"],
            format_func=lambda x: x.replace("_", " ").title(),
            index=["push_pull_legs", "upper_lower", "full_body"].index(
                user.workout_split or "push_pull_legs"
            ),
        )
    with col2:
        exp_override = st.selectbox("Experience Level",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(
                user.gym_experience or "beginner"
            ),
        )

    if st.button("🤖 Generate Workout Plan", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is building your training programme..."):
            result = svc.generate_plan(
                user_id=user_id,
                split_type=split,
                experience=exp_override,
                goal=user.goal or "fat_loss",
                weight_kg=user.weight_kg or 75,
                age=user.age or 22,
                gender=user.gender or "male",
            )
        if result.get("error"):
            st.error(f"Error: {result['error']}")
        elif result.get("plan_saved"):
            st.success("✅ New workout plan generated!")
            st.rerun()

# ── Show Active Plan ─────────────────────────────────────────────────────
active = svc.get_active_plan(user_id)
db.close()

if not active:
    st.info("No workout plan yet. Click **Generate Workout Plan** above.")
    st.stop()

plan = active["plan_data"]
st.markdown(f"**Split:** {active['split_type'].replace('_',' ').title()} &nbsp;|&nbsp; "
            f"**Created:** {active['created_at'][:10]}")

import datetime
today_day = datetime.date.today().strftime("%A")

tabs = st.tabs(DAYS)
for tab, day in zip(tabs, DAYS):
    with tab:
        session = plan.get(day, {})
        session_name = session.get("session", "Rest")
        exercises = session.get("exercises", [])

        is_today = (day == today_day)
        badge = " 🟢 TODAY" if is_today else ""
        st.markdown(f"### {session_name}{badge}")

        if not exercises:
            st.markdown("🛌 **Rest Day** — Active recovery, stretching, or light cardio.")
        else:
            for ex in exercises:
                rest_min = ex.get("rest_seconds", 90) // 60
                rest_sec = ex.get("rest_seconds", 90) % 60
                rest_str = f"{rest_min}:{rest_sec:02d} min" if rest_min else f"{rest_sec}s"
                st.markdown(
                    f'<div class="exercise-card">'
                    f'<strong style="color:#FAFAFA">{ex["name"]}</strong> &nbsp;'
                    f'<span style="color:#00D4FF">{ex["sets"]} × {ex["reps"]} reps</span> &nbsp;'
                    f'<span style="color:#8892A4">Rest: {rest_str}</span><br>'
                    f'<small style="color:#6B7280">{ex.get("notes","")}</small>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
