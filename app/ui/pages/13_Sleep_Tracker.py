import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, metric_card, section_header
from app.utils.session import require_login, init_session_defaults
from app.models.database import SessionLocal
from app.storage.sleep_store import SleepStore
from app.services.chart_service import ChartService
from datetime import date

st.set_page_config(page_title="Sleep Tracker", page_icon="😴", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 😴 Sleep Tracker")
st.divider()

db = SessionLocal()
store = SleepStore(db)

# ── Log Sleep ────────────────────────────────────────────────────────────
st.markdown(section_header("📝 Log Sleep"), unsafe_allow_html=True)

with st.form("sleep_form"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        hours = st.number_input("Hours Slept", min_value=0.0, max_value=16.0, step=0.5, value=7.0)
    with col2:
        quality = st.selectbox("Sleep Quality", ["poor","fair","good","excellent"], index=2)
    with col3:
        log_date = st.date_input("Date", value=date.today())
    with col4:
        notes = st.text_input("Notes", placeholder="Had a late night…")

    submitted = st.form_submit_button("💾 Log Sleep", use_container_width=True, type="primary")

if submitted:
    store.log_sleep(user_id, hours, quality, notes, log_date)
    st.success(f"✅ Sleep logged: {hours}h ({quality})")
    st.rerun()

# ── Stats ────────────────────────────────────────────────────────────────
avg_7d  = store.get_average_hours(user_id, 7)
avg_14d = store.get_average_hours(user_id, 14)
recent  = store.get_recent(user_id, 14)
trend   = store.get_trend(user_id, 14)
db.close()

st.divider()
st.markdown(section_header("📊 Sleep Stats"), unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    color = "#00E676" if avg_7d >= 7 else ("#FFB300" if avg_7d >= 6 else "#FF5252")
    st.markdown(metric_card("7-Day Avg", f"{avg_7d:.1f}h", "per night", color), unsafe_allow_html=True)
with c2:
    color2 = "#00E676" if avg_14d >= 7 else ("#FFB300" if avg_14d >= 6 else "#FF5252")
    st.markdown(metric_card("14-Day Avg", f"{avg_14d:.1f}h", "per night", color2), unsafe_allow_html=True)
with c3:
    nights_good = sum(1 for e in recent if e.hours >= 7)
    st.markdown(metric_card("Good Nights", f"{nights_good}/{len(recent)}",
                             "≥7h in 14d"), unsafe_allow_html=True)
with c4:
    deficit = max(0, 7 - avg_7d)
    st.markdown(metric_card("Sleep Debt", f"{deficit:.1f}h",
                             "vs 7h target"), unsafe_allow_html=True)

# ── Chart ────────────────────────────────────────────────────────────────
st.divider()
fig = ChartService.sleep_trend_chart(trend)
st.plotly_chart(fig, use_container_width=True)

# ── Recovery insights ─────────────────────────────────────────────────────
st.markdown(section_header("🧠 Recovery Insights"), unsafe_allow_html=True)

if avg_7d < 6:
    st.error("🚨 **Critical sleep deficit.** Less than 6h/night severely impacts recovery, "
             "hormone levels, and muscle building. Prioritise sleep above all else.")
elif avg_7d < 7:
    st.warning("⚠️ **Below target.** Aim for 7-9 hours. "
               "Poor sleep increases cortisol, reduces testosterone, and stalls fat loss.")
elif avg_7d >= 8:
    st.success("✅ **Excellent sleep!** 8h+ optimises muscle protein synthesis "
               "and growth hormone release. Keep it up!")
else:
    st.success("✅ **Good sleep.** You're meeting the 7h minimum. "
               "Try to consistently hit 7.5-8h for optimal recovery.")

with st.expander("💡 Sleep Optimisation Tips"):
    st.markdown("""
    - **Sleep at the same time** every night — circadian rhythm is critical
    - **No screens 1h before bed** — blue light suppresses melatonin
    - **Keep your room cool** (18-20°C optimal for sleep)
    - **No caffeine after 2pm** — it has a 6-hour half-life
    - **Magnesium glycinate** (200-400mg before bed) improves sleep quality
    - **Protein before bed** — slow-digesting casein supports overnight muscle repair
    """)
