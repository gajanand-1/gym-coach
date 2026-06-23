import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.workout_store import WorkoutStore
from app.services.chart_service import ChartService

st.set_page_config(page_title="Workout Log", page_icon="📋", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 📋 Workout Log")
st.markdown("Log a session — the LangGraph **workout_log_node** stores it with volume tracking.")
st.divider()

st.markdown(section_header("➕ Log Workout"), unsafe_allow_html=True)

# ── Natural language shortcut ─────────────────────────────────────────────
nl_input = st.text_area(
    "Describe your workout naturally:",
    placeholder='"Push day: Bench 70kg 4×10, Incline DB 22kg 3×12, OHP 50kg 3×10"',
    height=80,
)
if st.button("🤖 Log via AI", use_container_width=True, type="primary") and nl_input.strip():
    with st.spinner("🤖 LangGraph routing → Workout Log node…"):
        result = run_gym_coach(user_id, nl_input.strip(), intent_override="workout_log")
    if result.get("error"):
        st.error(result["error"])
    else:
        st.success(result["response"].get("message", "Workout logged!"))
        st.rerun()

st.divider()

# ── Manual structured form ────────────────────────────────────────────────
with st.expander("📝 Structured Form"):
    with st.form("wlog_form"):
        c1, c2, c3 = st.columns(3)
        with c1: session_name = st.text_input("Session Name", "Workout")
        with c2: split_type   = st.selectbox("Split", ["push","pull","legs","upper","lower","full_body","other"])
        with c3: duration     = st.number_input("Duration (min)", 0, 300, 60)
        notes = st.text_area("Notes", height=50)

        if "num_ex" not in st.session_state: st.session_state["num_ex"] = 3
        exercises = []
        for i in range(st.session_state["num_ex"]):
            ec1,ec2,ec3,ec4 = st.columns([3,1,2,1])
            with ec1: name_i   = st.text_input(f"Exercise {i+1}", key=f"en{i}")
            with ec2: weight_i = st.number_input("kg", 0.0, 500.0, 0.0, key=f"ew{i}")
            with ec3: sets_i   = st.text_input("Reps (10,10,8)", key=f"es{i}")
            with ec4: rpe_i    = st.number_input("RPE", 0.0, 10.0, 7.0, key=f"er{i}")
            if name_i.strip():
                try:   sets_list = [int(r.strip()) for r in sets_i.split(",") if r.strip().isdigit()]
                except: sets_list = []
                exercises.append({"exercise": name_i, "weight_kg": weight_i,
                                   "sets": sets_list, "rpe": rpe_i})

        add_row = st.form_submit_button("➕ Add Row")
        submit  = st.form_submit_button("💾 Save Workout", type="primary")

    if add_row:
        st.session_state["num_ex"] = st.session_state.get("num_ex", 3) + 1
        st.rerun()

    if submit and exercises:
        import json
        raw = f"{session_name}: " + ", ".join(
            f"{e['exercise']} {e['weight_kg']}kg {len(e['sets'])} sets" for e in exercises)
        with st.spinner("Logging…"):
            result = run_gym_coach(user_id, raw, intent_override="workout_log")
        if result.get("error"):
            st.error(result["error"])
        else:
            st.success(result["response"].get("message","Logged!"))
            st.session_state["num_ex"] = 3
            st.rerun()

# ── Recent sessions ────────────────────────────────────────────────────────
st.divider()
st.markdown(section_header("📅 Recent Sessions"), unsafe_allow_html=True)

db      = SessionLocal()
sessions= WorkoutStore(db).get_recent(user_id, days=14)
db.close()

if not sessions:
    st.info("No workouts logged yet.")
else:
    fig = ChartService.workout_volume_chart([{
        "date": w.log_date.isoformat(), "volume_kg": w.total_volume_kg,
        "session_name": w.session_name} for w in sessions])
    st.plotly_chart(fig, use_container_width=True)
    for w in sessions:
        with st.expander(f"📅 {w.log_date} — {w.session_name} ({w.total_volume_kg:.0f}kg volume)"):
            for ex in w.exercises or []:
                reps_str = ", ".join(str(r) for r in ex.get("sets",[]))
                st.markdown(
                    f'<div class="exercise-card">'
                    f'<strong>{ex.get("exercise","")}</strong> — '
                    f'<span style="color:#00D4FF">{ex.get("weight_kg",0)}kg</span> × [{reps_str}]'
                    f'</div>', unsafe_allow_html=True)
            if w.notes:
                st.caption(f"Notes: {w.notes[:200]}")
