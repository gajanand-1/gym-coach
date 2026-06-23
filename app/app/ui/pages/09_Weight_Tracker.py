import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, metric_card, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.services.weight_service import WeightService
from app.services.chart_service import ChartService
from datetime import date

st.set_page_config(page_title="Weight Tracker", page_icon="⚖️", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user = get_current_user()

st.markdown("## ⚖️ Weight Tracker")
st.divider()

db = SessionLocal()
svc = WeightService(db)

# ── Log Today's Weight ───────────────────────────────────────────────────
st.markdown(section_header("📝 Log Weight"), unsafe_allow_html=True)

with st.form("weight_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        weight_val = st.number_input("Body Weight (kg)", value=float(user.weight_kg),
                                      min_value=20.0, max_value=300.0, step=0.1)
    with col2:
        bf_pct = st.number_input("Body Fat % (optional)", value=0.0,
                                  min_value=0.0, max_value=60.0, step=0.1)
    with col3:
        log_date = st.date_input("Date", value=date.today())

    notes = st.text_input("Notes (optional)", placeholder="Morning weight, after workout, etc.")
    submitted = st.form_submit_button("💾 Log Weight", use_container_width=True, type="primary")

if submitted:
    svc.log_weight(user_id, weight_val, bf_pct, notes, log_date)
    # Update user's current weight
    from app.storage.user_store import UserStore
    us = UserStore(db)
    us.update_profile(user_id, weight_kg=weight_val)
    st.success(f"✅ Weight logged: **{weight_val:.1f} kg** on {log_date}")
    st.rerun()

# ── Stats ────────────────────────────────────────────────────────────────
stats = svc.get_stats(user_id, user.target_weight_kg or 70, user.goal or "fat_loss")
db.close()

st.divider()
st.markdown(section_header("📊 Progress Stats"), unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(metric_card("Current",    f"{stats['current_kg']:.1f}kg", "body weight"), unsafe_allow_html=True)
with c2: st.markdown(metric_card("Target",     f"{stats['target_kg']:.1f}kg",  "goal weight"), unsafe_allow_html=True)
with c3: st.markdown(metric_card("Remaining",  f"{stats['remaining_kg']:.1f}kg", "to go"), unsafe_allow_html=True)
with c4:
    rate = stats["rate_per_week"]
    rate_color = "#00E676" if abs(rate) > 0.1 else "#FFB300"
    st.markdown(metric_card("Weekly Rate", f"{rate:+.2f}kg", "per week", rate_color), unsafe_allow_html=True)
with c5: st.markdown(metric_card("Est. Goal Date", stats["eta"], "at current rate"), unsafe_allow_html=True)

# ── Charts ───────────────────────────────────────────────────────────────
st.divider()
tab_30, tab_all = st.tabs(["30 Days", "All Time"])

with tab_30:
    fig = ChartService.weight_progress_chart(stats["trend_30d"], stats["target_kg"])
    st.plotly_chart(fig, use_container_width=True)

with tab_all:
    db2 = SessionLocal()
    svc2 = WeightService(db2)
    all_data = svc2.get_all(user_id)
    db2.close()
    fig2 = ChartService.weight_progress_chart(all_data, stats["target_kg"])
    st.plotly_chart(fig2, use_container_width=True)

# ── Weekly Averages Table ────────────────────────────────────────────────
if stats["weekly_averages"]:
    st.markdown(section_header("📅 Weekly Averages"), unsafe_allow_html=True)
    import pandas as pd
    df = pd.DataFrame(stats["weekly_averages"])
    df.columns = ["Week", "Avg Weight (kg)"]
    df["Change"] = df["Avg Weight (kg)"].diff().apply(
        lambda x: f"{x:+.2f} kg" if pd.notna(x) else "—"
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
