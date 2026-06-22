import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.models.database import SessionLocal
from app.services.workout_service import WorkoutService
from app.services.chart_service import ChartService

STATUS_ICONS = {
    "ready_to_progress": "🟢",
    "maintain":          "🟡",
    "stalled":           "🔴",
    "deload":            "⚪",
}

st.set_page_config(page_title="Progressive Overload", page_icon="📈", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 📈 Progressive Overload")
st.markdown("AI analysis of your last 2 weeks of training — know exactly when and how to progress.")
st.divider()

if st.button("🤖 Analyse My Workouts", type="primary", use_container_width=True):
    with st.spinner("🤖 Analysing your workout history..."):
        db = SessionLocal()
        svc = WorkoutService(db)
        recs = svc.get_progressive_overload_recommendations(user_id)
        db.close()
    st.session_state["po_recs"] = recs
    st.rerun()

recs = st.session_state.get("po_recs")
if not recs:
    st.info("Click **Analyse My Workouts** to get personalised progressive overload recommendations.")
    st.stop()

# ── Overall Assessment ───────────────────────────────────────────────────
st.markdown(section_header("🧠 Overall Assessment"), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Volume Change", recs.get("weekly_volume_change", "N/A"))
col2.metric("Deload Needed", "Yes ⚠️" if recs.get("deload_needed") else "No ✅")
col3.metric("Exercises Analysed", len(recs.get("recommendations", [])))

st.markdown(f"_{recs.get('overall_assessment', '')}_")

if recs.get("deload_needed") and recs.get("deload_reason"):
    st.warning(f"⚠️ **Deload recommended:** {recs['deload_reason']}")

st.divider()

# ── Per-Exercise Recommendations ─────────────────────────────────────────
st.markdown(section_header("💪 Exercise Recommendations"), unsafe_allow_html=True)

for rec in recs.get("recommendations", []):
    status = rec.get("status", "maintain")
    icon = STATUS_ICONS.get(status, "⚪")
    border_color = {
        "ready_to_progress": "#00E676",
        "maintain":          "#FFB300",
        "stalled":           "#FF5252",
        "deload":            "#8892A4",
    }.get(status, "#2A2F45")

    with st.container():
        st.markdown(
            f'<div style="background:#1E2130;border-radius:12px;padding:16px 20px;'
            f'border-left:4px solid {border_color};margin-bottom:12px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<h4 style="color:#FAFAFA;margin:0">{icon} {rec.get("exercise","")}</h4>'
            f'<span style="color:{border_color};font-size:0.85rem">'
            f'{status.replace("_"," ").title()}</span>'
            f'</div>'
            f'<div style="margin-top:10px;display:flex;gap:30px">'
            f'<div><div style="color:#8892A4;font-size:0.75rem">CURRENT</div>'
            f'<div style="color:#FAFAFA">{rec.get("current_weight_kg",0)}kg × [{rec.get("current_reps","")}]</div></div>'
            f'<div style="color:#8892A4;font-size:1.5rem">→</div>'
            f'<div><div style="color:#8892A4;font-size:0.75rem">NEXT SESSION</div>'
            f'<div style="color:{border_color}">{rec.get("next_weight_kg",0)}kg × {rec.get("next_reps_target","")} reps</div></div>'
            f'</div>'
            f'<div style="margin-top:10px;color:#B0B8C8;font-size:0.85rem">'
            f'💡 {rec.get("reasoning","")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Show exercise history chart inline
    db = SessionLocal()
    svc = WorkoutService(db)
    history = svc.get_exercise_history(user_id, rec.get("exercise", ""))
    db.close()

    if history:
        fig = ChartService.exercise_history_chart(history, rec.get("exercise", ""))
        st.plotly_chart(fig, use_container_width=True)
