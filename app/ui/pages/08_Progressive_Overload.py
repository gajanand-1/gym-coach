import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.workout_store import WorkoutStore
from app.services.chart_service import ChartService

STATUS_COLOR = {
    "ready_to_progress": "#00E676",
    "maintain":          "#FFB300",
    "stalled":           "#FF5252",
    "deload":            "#8892A4",
}

st.set_page_config(page_title="Progressive Overload", page_icon="📈", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 📈 Progressive Overload")
st.markdown("LangGraph routes through **context_loader → router → overload_node → response_formatter**.")
st.divider()

if st.button("🤖 Analyse My Workouts", type="primary", use_container_width=True):
    with st.spinner("🤖 LangGraph routing → Progressive Overload node…"):
        result = run_gym_coach(user_id, "Analyse my progressive overload",
                               intent_override="progressive_overload")
    if result.get("error"):
        st.error(result["error"])
    else:
        st.session_state["po_result"] = result.get("response", {}).get("data", {})
        st.rerun()

recs_data = st.session_state.get("po_result")
if not recs_data:
    st.info("Click **Analyse My Workouts** to get personalised recommendations.")
    st.stop()

recs = recs_data.get("recommendations", [])
c1, c2, c3 = st.columns(3)
c1.metric("Volume Change",     recs_data.get("weekly_volume_change","N/A"))
c2.metric("Deload Needed",     "Yes ⚠️" if recs_data.get("deload_needed") else "No ✅")
c3.metric("Exercises Analysed", len(recs))
st.markdown(f"_{recs_data.get('overall_assessment','')}_")

st.divider()
st.markdown(section_header("💪 Exercise Recommendations"), unsafe_allow_html=True)

for rec in recs:
    status = rec.get("status","maintain")
    color  = STATUS_COLOR.get(status, "#2A2F45")
    st.markdown(
        f'<div style="background:#1E2130;border-radius:12px;padding:16px 20px;'
        f'border-left:4px solid {color};margin-bottom:12px">'
        f'<h4 style="color:#FAFAFA;margin:0">{rec.get("exercise","")}</h4>'
        f'<div style="margin-top:10px;display:flex;gap:30px">'
        f'<div><div style="color:#8892A4;font-size:0.75rem">CURRENT</div>'
        f'<div style="color:#FAFAFA">{rec.get("current_weight_kg",0)}kg × [{rec.get("current_reps","")}]</div></div>'
        f'<div style="color:#8892A4;font-size:1.5rem">→</div>'
        f'<div><div style="color:#8892A4;font-size:0.75rem">NEXT SESSION</div>'
        f'<div style="color:{color}">{rec.get("next_weight_kg",0)}kg × {rec.get("next_reps_target","")} reps</div></div>'
        f'</div>'
        f'<div style="margin-top:8px;color:#B0B8C8;font-size:0.85rem">💡 {rec.get("reasoning","")}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    db = SessionLocal()
    history = WorkoutStore(db).get_exercise_history(user_id, rec.get("exercise",""))
    db.close()
    if history:
        fig = ChartService.exercise_history_chart(
            [{"date": s.log_date.isoformat(), "weight_kg": s.weight_kg,
              "reps": s.reps} for s in history],
            rec.get("exercise","")
        )
        st.plotly_chart(fig, use_container_width=True)
