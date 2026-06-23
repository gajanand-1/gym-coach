import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.services.workout_service import WorkoutService
from app.services.chart_service import ChartService

st.set_page_config(page_title="Workout Log", page_icon="📋", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user = get_current_user()

st.markdown("## 📋 Workout Log")
st.divider()

db = SessionLocal()
svc = WorkoutService(db)

# ── Today's planned session hint ─────────────────────────────────────────
today_session = svc.get_today_session(user_id)
if today_session:
    session_name = today_session.get("session", "Workout")
    exercises_planned = today_session.get("exercises", [])
    if exercises_planned:
        st.info(f"📅 Today's planned session: **{session_name}**")

# ── Log New Session ──────────────────────────────────────────────────────
st.markdown(section_header("➕ Log Workout"), unsafe_allow_html=True)

with st.form("workout_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        session_name_input = st.text_input("Session Name",
            value=today_session.get("session","") if today_session else "")
    with col2:
        split_type = st.selectbox("Split Type",
            ["push","pull","legs","upper","lower","full_body","other"])
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=0, max_value=300, value=60)

    notes = st.text_area("Notes", placeholder="How did it feel? Any PRs?", height=60)

    st.markdown("**Exercises** — add as many as needed")

    # Dynamic exercise rows
    if "num_exercises" not in st.session_state:
        st.session_state["num_exercises"] = 3

    exercises_data = []
    for i in range(st.session_state["num_exercises"]):
        ec1, ec2, ec3, ec4 = st.columns([3, 1, 2, 1])
        with ec1:
            ex_name = st.text_input(f"Exercise {i+1}", key=f"ex_name_{i}",
                placeholder="e.g. Bench Press")
        with ec2:
            weight_kg = st.number_input(f"Weight (kg)", key=f"ex_weight_{i}",
                min_value=0.0, max_value=500.0, step=2.5, value=0.0)
        with ec3:
            sets_str = st.text_input(f"Reps per set", key=f"ex_sets_{i}",
                placeholder="e.g. 10,10,8,7")
        with ec4:
            rpe = st.number_input(f"RPE", key=f"ex_rpe_{i}",
                min_value=0.0, max_value=10.0, step=0.5, value=7.0)

        if ex_name.strip():
            try:
                sets_list = [int(r.strip()) for r in sets_str.split(",") if r.strip().isdigit()]
            except Exception:
                sets_list = []
            exercises_data.append({
                "exercise": ex_name.strip(),
                "weight_kg": weight_kg,
                "sets": sets_list,
                "rpe": rpe,
            })

    col_add, col_sub = st.columns([1, 1])
    with col_add:
        add_ex = st.form_submit_button("➕ Add Exercise Row")
    with col_sub:
        submitted = st.form_submit_button("💾 Save Workout", type="primary")

if add_ex:
    st.session_state["num_exercises"] += 1
    st.rerun()

if submitted:
    valid_exercises = [e for e in exercises_data if e["sets"]]
    if not valid_exercises:
        st.error("Please add at least one exercise with reps.")
    else:
        result = svc.log_session(
            user_id=user_id,
            session_name=session_name_input or "Workout",
            split_type=split_type,
            exercises=valid_exercises,
            notes=notes,
            duration_minutes=duration,
        )
        db.close()
        db = SessionLocal()
        svc = WorkoutService(db)
        st.success(f"✅ Workout logged! Total volume: **{result['total_volume_kg']:.0f} kg**")
        st.session_state["num_exercises"] = 3
        st.rerun()

# ── Recent Sessions ──────────────────────────────────────────────────────
st.divider()
st.markdown(section_header("📅 Recent Sessions"), unsafe_allow_html=True)

recent = svc.get_recent_sessions(user_id, days=14)
db.close()

if not recent:
    st.info("No workouts logged yet. Log your first session above!")
else:
    # Volume chart
    fig = ChartService.workout_volume_chart(recent)
    st.plotly_chart(fig, use_container_width=True)

    for session in recent:
        with st.expander(f"📅 {session['date']} — {session['session_name']} ({session['volume_kg']:.0f}kg volume)"):
            for ex in session.get("exercises", []):
                reps_str = ", ".join(str(r) for r in ex.get("sets", []))
                st.markdown(
                    f'<div class="exercise-card">'
                    f'<strong>{ex.get("exercise","")}</strong> — '
                    f'<span style="color:#00D4FF">{ex.get("weight_kg",0)}kg</span> × '
                    f'[{reps_str}]'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            if session.get("notes"):
                st.caption(f"Notes: {session['notes']}")
            if st.button("🗑️ Delete", key=f"del_session_{session['id']}"):
                db2 = SessionLocal()
                WorkoutService(db2).delete_session(session["id"], user_id)
                db2.close()
                st.rerun()
