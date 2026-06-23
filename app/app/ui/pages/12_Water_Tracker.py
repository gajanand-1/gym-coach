import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.storage.water_store import WaterStore
from app.services.chart_service import ChartService

st.set_page_config(page_title="Water Tracker", page_icon="💧", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user = get_current_user()

st.markdown("## 💧 Water Tracker")
st.divider()

target = user.water_target_liters or 3.5

db = SessionLocal()
store = WaterStore(db)
entry = store.get_today(user_id, target)
consumed = entry.consumed_liters
remaining = max(0, target - consumed)
pct = min(consumed / target * 100, 100) if target else 0
db.close()

# ── Gauge ────────────────────────────────────────────────────────────────
col_gauge, col_btns = st.columns([2, 3])
with col_gauge:
    fig = ChartService.water_gauge(consumed, target)
    st.plotly_chart(fig, use_container_width=True)

with col_btns:
    st.markdown(section_header("Quick Add"), unsafe_allow_html=True)
    btn_cols = st.columns(4)
    quick_adds = [0.25, 0.5, 0.75, 1.0]
    for col, amt in zip(btn_cols, quick_adds):
        if col.button(f"+{amt:.2f}L", use_container_width=True):
            db2 = SessionLocal()
            WaterStore(db2).add_water(user_id, amt, target)
            db2.close()
            st.rerun()

    st.markdown(f"**Remaining:** {remaining:.1f}L of {target:.1f}L target")
    st.progress(pct / 100)

    st.divider()
    with st.form("custom_water"):
        custom_amt = st.number_input("Custom Amount (L)", min_value=0.1, max_value=5.0,
                                      step=0.1, value=0.25)
        custom_target = st.number_input("Daily Target (L)", min_value=1.0, max_value=10.0,
                                         step=0.1, value=target)
        add_btn = st.form_submit_button("Add Water", use_container_width=True, type="primary")

    if add_btn:
        db3 = SessionLocal()
        WaterStore(db3).add_water(user_id, custom_amt, custom_target)
        db3.close()
        st.rerun()

    if st.button("🔄 Reset Today", use_container_width=True):
        db4 = SessionLocal()
        WaterStore(db4).reset_today(user_id)
        db4.close()
        st.rerun()

# ── Status message ───────────────────────────────────────────────────────
st.divider()
if pct >= 100:
    st.success("🎉 Daily water target reached! Great job staying hydrated.")
elif pct >= 75:
    st.info(f"💧 Almost there! Just {remaining:.1f}L more to reach your target.")
elif pct >= 50:
    st.warning(f"⚠️ Halfway there. Drink {remaining:.1f}L more today.")
else:
    st.error(f"🚫 Only {consumed:.1f}L consumed. You need {remaining:.1f}L more!")

# ── Hydration tips ───────────────────────────────────────────────────────
with st.expander("💡 Hydration Tips"):
    st.markdown("""
    - Drink **1 glass (250ml)** immediately after waking up
    - Carry a **1L bottle** to the gym — aim to finish it during your workout
    - Add a glass of water with every meal
    - Set hourly reminders on your phone
    - Your target of **{:.1f}L** is based on your body weight ({:.0f}kg × 35ml/kg)
    """.format(target, user.weight_kg or 75))
