import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.workout_plan_store import WorkoutPlanStore
import datetime

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

st.set_page_config(page_title="Workout Planner", page_icon="💪", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user    = get_current_user()

st.markdown("## 💪 AI Workout Planner")
st.markdown("The LangGraph **workout_plan_node** generates your training programme.")
st.divider()

with st.expander("⚙️ Generate New Plan", expanded=False):
    if st.button("🤖 Generate Workout Plan", type="primary", use_container_width=True):
        with st.spinner("🤖 LangGraph routing → Workout Plan node…"):
            result = run_gym_coach(user_id, "Generate my weekly workout plan",
                                   intent_override="workout_plan")
        if result.get("error"):
            st.error(result["error"])
        else:
            st.success(result["response"].get("message","Plan ready!"))
            st.rerun()

db     = SessionLocal()
active = WorkoutPlanStore(db).get_active(user_id)
db.close()

if not active:
    st.info("No workout plan yet. Click **Generate Workout Plan** above.")
    st.stop()

plan     = active.plan_data
today_day= datetime.date.today().strftime("%A")

st.markdown(f"**Split:** {active.split_type.replace('_',' ').title()} "
            f"| **Created:** {active.created_at.strftime('%d %b %Y')}")

tabs = st.tabs(DAYS)
for tab, day in zip(tabs, DAYS):
    with tab:
        session  = plan.get(day, {})
        name     = session.get("session","Rest")
        exs      = session.get("exercises",[])
        is_today = day == today_day
        badge    = " 🟢 TODAY" if is_today else ""
        st.markdown(f"### {name}{badge}")
        if not exs:
            st.markdown("🛌 Rest Day — Active recovery, stretching or light cardio.")
        else:
            for ex in exs:
                rest_m = ex.get("rest_seconds",90)//60
                rest_s = ex.get("rest_seconds",90)%60
                rest_str = f"{rest_m}:{rest_s:02d}m" if rest_m else f"{ex.get('rest_seconds',90)}s"
                st.markdown(
                    f'<div class="exercise-card">'
                    f'<strong style="color:#FAFAFA">{ex["name"]}</strong>&nbsp;'
                    f'<span style="color:#00D4FF">{ex["sets"]}×{ex["reps"]} reps</span>&nbsp;'
                    f'<span style="color:#8892A4">Rest: {rest_str}</span><br>'
                    f'<small style="color:#6B7280">{ex.get("notes","")}</small>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
