import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from datetime import date
from app.ui.style import inject_css, metric_card, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.services.weight_service import WeightService
from app.services.chart_service import ChartService

st.set_page_config(page_title="Weight Tracker", page_icon="⚖️", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user    = get_current_user()

st.markdown("## ⚖️ Weight Tracker")
st.divider()

st.markdown(section_header("📝 Log Weight"), unsafe_allow_html=True)
with st.form("weight_form"):
    c1, c2, c3 = st.columns(3)
    with c1: weight_val = st.number_input("Body Weight (kg)", value=float(user.weight_kg),
                              min_value=20.0, max_value=300.0, step=0.1)
    with c2: bf_pct     = st.number_input("Body Fat % (optional)", 0.0, 60.0, 0.0, 0.1)
    with c3: log_date   = st.date_input("Date", value=date.today())
    notes   = st.text_input("Notes", placeholder="Morning, after workout…")
    submit  = st.form_submit_button("💾 Log Weight", use_container_width=True, type="primary")

if submit:
    with st.spinner("🤖 LangGraph routing → Weight Log node…"):
        result = run_gym_coach(user_id, f"Log weight {weight_val} kg",
                               intent_override="weight_log")
    if result.get("error"):
        st.error(result["error"])
    else:
        st.success(result["response"].get("message","Weight logged!"))
        st.rerun()

# ── Stats & charts ─────────────────────────────────────────────────────────
db   = SessionLocal()
svc  = WeightService(db)
stats= svc.get_stats(user_id, user.target_weight_kg or 70, user.goal or "fat_loss")
db.close()

st.divider()
st.markdown(section_header("📊 Progress"), unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns(5)
c1.markdown(metric_card("Current",   f"{stats['current_kg']:.1f}kg", "body weight"), unsafe_allow_html=True)
c2.markdown(metric_card("Target",    f"{stats['target_kg']:.1f}kg",  "goal weight"), unsafe_allow_html=True)
c3.markdown(metric_card("Remaining", f"{stats['remaining_kg']:.1f}kg","to go"),      unsafe_allow_html=True)
c4.markdown(metric_card("Rate",      f"{stats['rate_per_week']:+.2f}kg","per week"),  unsafe_allow_html=True)
c5.markdown(metric_card("ETA",       stats["eta"],                    "at this rate"),unsafe_allow_html=True)

st.divider()
t30, tall = st.tabs(["30 Days","All Time"])
with t30:
    st.plotly_chart(ChartService.weight_progress_chart(
        stats["trend_30d"], stats["target_kg"]), use_container_width=True)
with tall:
    db2 = SessionLocal()
    all_data = WeightService(db2).get_all(user_id)
    db2.close()
    st.plotly_chart(ChartService.weight_progress_chart(
        all_data, stats["target_kg"]), use_container_width=True)
