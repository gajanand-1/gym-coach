import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.water_store import WaterStore
from app.services.chart_service import ChartService

st.set_page_config(page_title="Water Tracker", page_icon="💧", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user    = get_current_user()
target  = user.water_target_liters or 3.5

st.markdown("## 💧 Water Tracker")
st.divider()

db    = SessionLocal()
entry = WaterStore(db).get_today(user_id, target)
db.close()
consumed  = entry.consumed_liters
remaining = max(0, target - consumed)
pct       = min(consumed / target * 100, 100) if target else 0

# ── Gauge ─────────────────────────────────────────────────────────────────
col_gauge, col_btns = st.columns([2, 3])
with col_gauge:
    st.plotly_chart(ChartService.water_gauge(consumed, target), use_container_width=True)

with col_btns:
    st.markdown(section_header("Quick Add"), unsafe_allow_html=True)
    btn_cols = st.columns(4)
    for col, amt in zip(btn_cols, [0.25, 0.5, 0.75, 1.0]):
        if col.button(f"+{amt:.2f}L", use_container_width=True):
            with st.spinner("Logging…"):
                run_gym_coach(user_id, f"Drank {amt} litres of water",
                              intent_override="water_log")
            st.rerun()

    st.markdown(f"**Remaining:** {remaining:.1f}L of {target:.1f}L")
    st.progress(pct / 100)

    with st.form("custom_water"):
        c1, c2 = st.columns(2)
        with c1: amt    = st.number_input("Amount (L)", 0.1, 5.0, 0.25, 0.1)
        with c2: new_tgt= st.number_input("Target (L)", 1.0, 10.0, target, 0.1)
        if st.form_submit_button("Add Water", use_container_width=True, type="primary"):
            with st.spinner("Logging…"):
                run_gym_coach(user_id, f"Drank {amt} litres of water",
                              intent_override="water_log")
            st.rerun()

    if st.button("🔄 Reset Today", use_container_width=True):
        db2 = SessionLocal()
        WaterStore(db2).reset_today(user_id)
        db2.close()
        st.rerun()

st.divider()
if pct >= 100:   st.success("🎉 Daily water target reached!")
elif pct >= 75:  st.info(f"💧 Almost there! {remaining:.1f}L more.")
elif pct >= 50:  st.warning(f"⚠️ Halfway. {remaining:.1f}L more to go.")
else:            st.error(f"🚫 Only {consumed:.1f}L. Need {remaining:.1f}L more!")
