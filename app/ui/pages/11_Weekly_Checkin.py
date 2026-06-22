import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.storage.checkin_store import CheckInStore
from app.graph.checkin_graph import run_checkin_graph

st.set_page_config(page_title="Weekly Check-In", page_icon="📊", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user = get_current_user()

st.markdown("## 📊 Weekly Check-In")
st.markdown("Answer a few quick questions — the AI analyses your week and adjusts your targets.")
st.divider()

db = SessionLocal()
ci_store = CheckInStore(db)
last_ci = ci_store.get_last(user_id)
is_due   = ci_store.is_due(user_id)
db.close()

if last_ci:
    from datetime import date
    days_since = (date.today() - last_ci.checkin_date).days
    status_color = "#00E676" if not is_due else "#FFB300"
    st.markdown(
        f'<div style="background:#1E2130;border-radius:10px;padding:12px 16px;'
        f'border-left:4px solid {status_color};margin-bottom:16px">'
        f'Last check-in: <strong>{last_ci.checkin_date}</strong> '
        f'({days_since} days ago) &nbsp;|&nbsp; '
        f'{"⚠️ Due now!" if is_due else "✅ Next due in " + str(7 - days_since) + " days"}'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Check-In Form ────────────────────────────────────────────────────────
st.markdown(section_header("📝 This Week's Check-In"), unsafe_allow_html=True)

with st.form("checkin_form"):
    col1, col2 = st.columns(2)
    with col1:
        current_weight = st.number_input("Current Weight (kg)",
            value=float(user.weight_kg), min_value=30.0, max_value=300.0, step=0.1)
        energy = st.slider("Energy Level (1=exhausted, 10=great)", 1, 10, 6)
        hunger = st.slider("Hunger Level (1=never hungry, 10=always hungry)", 1, 10, 5)

    with col2:
        sleep_q = st.slider("Sleep Quality (1=terrible, 10=perfect)", 1, 10, 6)
        recovery = st.slider("Recovery Quality (1=always sore, 10=fresh)", 1, 10, 6)

    additional = st.text_area("Anything else to tell your coach?",
        placeholder="Stressed at work, sleep was bad Tuesday, hit a new PR on bench…",
        height=80)

    submitted = st.form_submit_button("🤖 Submit & Get AI Analysis", type="primary",
                                       use_container_width=True)

if submitted:
    with st.spinner("🤖 AI Coach is analysing your week... (30-60 seconds)"):
        result = run_checkin_graph(
            user_id=user_id,
            current_weight_kg=current_weight,
            target_weight_kg=user.target_weight_kg or 70,
            goal=user.goal or "fat_loss",
            current_calories_target=user.target_calories or 2000,
            current_protein_target=user.protein_target_g or 150,
            energy_level=energy,
            hunger_level=hunger,
            sleep_quality=sleep_q,
            recovery_quality=recovery,
        )

    if result.get("error"):
        st.error(f"Error: {result['error']}")
    else:
        report = result.get("report", {})
        st.success("✅ Check-in complete! See your personalised report below.")

        # ── Report ──────────────────────────────────────────────────────
        st.markdown(section_header("📋 Your Weekly Report"), unsafe_allow_html=True)
        st.markdown(f"_{report.get('weekly_summary','')}_")

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            wa = report.get("weight_analysis", {})
            st.markdown("**⚖️ Weight Analysis**")
            st.write(wa.get("summary", ""))

            na = report.get("nutrition_analysis", {})
            st.markdown("**🥗 Nutrition Analysis**")
            st.write(na.get("summary", ""))

        with r_col2:
            ta = report.get("training_analysis", {})
            st.markdown("**💪 Training Analysis**")
            st.write(ta.get("summary", ""))

            sa = report.get("sleep_analysis", {})
            st.markdown("**😴 Sleep Analysis**")
            st.write(sa.get("summary", ""))

        # ── Adjustments ─────────────────────────────────────────────────
        adj = report.get("adjustments", {})
        if adj:
            st.divider()
            st.markdown(section_header("🔧 Adjustments Applied"), unsafe_allow_html=True)
            a1, a2 = st.columns(2)
            with a1:
                cal_chg = adj.get("calorie_change", 0)
                st.metric("New Calorie Target",
                    f"{adj.get('new_daily_calories',0):.0f} kcal",
                    f"{cal_chg:+.0f}" if cal_chg else "No change")
                if adj.get("cardio_recommendation"):
                    st.markdown(f"**Cardio:** {adj['cardio_recommendation']}")
            with a2:
                pro_chg = adj.get("protein_change", 0)
                st.metric("New Protein Target",
                    f"{adj.get('new_protein_target',0):.0f}g",
                    f"{pro_chg:+.0f}g" if pro_chg else "No change")
                if adj.get("volume_recommendation"):
                    st.markdown(f"**Training Volume:** {adj['volume_recommendation']}")

        # ── Next week priorities ─────────────────────────────────────────
        priorities = report.get("top_priorities_next_week", [])
        if priorities:
            st.divider()
            st.markdown(section_header("🎯 Top Priorities Next Week"), unsafe_allow_html=True)
            for i, p in enumerate(priorities, 1):
                st.markdown(f"**{i}.** {p}")

        if result.get("adjustments_applied"):
            st.info("✅ Your calorie/protein targets have been automatically updated.")
