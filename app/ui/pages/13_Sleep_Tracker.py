import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from datetime import date
from app.ui.style import inject_css, metric_card, section_header
from app.utils.session import require_login, init_session_defaults
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.sleep_store import SleepStore
from app.services.chart_service import ChartService

st.set_page_config(page_title="Sleep Tracker", page_icon="😴", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 😴 Sleep Tracker")
st.divider()

st.markdown(section_header("📝 Log Sleep"), unsafe_allow_html=True)
with st.form("sleep_form"):
    c1, c2, c3, c4 = st.columns(4)
    with c1: hours   = st.number_input("Hours", 0.0, 16.0, 7.0, 0.5)
    with c2: quality = st.selectbox("Quality", ["poor","fair","good","excellent"], index=2)
    with c3: log_dt  = st.date_input("Date", date.today())
    with c4: notes   = st.text_input("Notes")
    if st.form_submit_button("💾 Log Sleep", use_container_width=True, type="primary"):
        with st.spinner("🤖 LangGraph routing → Sleep Log node…"):
            result = run_gym_coach(user_id,
                f"Slept {hours} hours, quality {quality}",
                intent_override="sleep_log")
        if result.get("error"):
            st.error(result["error"])
        else:
            st.success(result["response"].get("message", f"Logged {hours}h sleep!"))
            st.rerun()

db     = SessionLocal()
store  = SleepStore(db)
avg7d  = store.get_average_hours(user_id, 7)
avg14d = store.get_average_hours(user_id, 14)
recent = store.get_recent(user_id, 14)
trend  = store.get_trend(user_id, 14)
db.close()

st.divider()
c1,c2,c3,c4 = st.columns(4)
color = lambda h: "#00E676" if h >= 7 else ("#FFB300" if h >= 6 else "#FF5252")
c1.markdown(metric_card("7-Day Avg",  f"{avg7d:.1f}h",  "", color(avg7d)),  unsafe_allow_html=True)
c2.markdown(metric_card("14-Day Avg", f"{avg14d:.1f}h", "", color(avg14d)), unsafe_allow_html=True)
good = sum(1 for e in recent if e.hours >= 7)
c3.markdown(metric_card("Good Nights", f"{good}/{len(recent)}", "≥7h"), unsafe_allow_html=True)
deficit = max(0, 7 - avg7d)
c4.markdown(metric_card("Sleep Debt", f"{deficit:.1f}h", "vs 7h target"), unsafe_allow_html=True)

st.divider()
st.plotly_chart(ChartService.sleep_trend_chart(trend), use_container_width=True)

if avg7d < 6:
    st.error("🚨 Critical sleep deficit — under 6h severely impacts recovery.")
elif avg7d < 7:
    st.warning("⚠️ Below 7h target. Poor sleep increases cortisol and stalls fat loss.")
else:
    st.success("✅ Great sleep! Keep it up for optimal recovery and muscle growth.")
