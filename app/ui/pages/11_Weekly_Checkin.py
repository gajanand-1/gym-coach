import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.checkin_store import CheckInStore

st.set_page_config(page_title="Weekly Check-In", page_icon="📊", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user    = get_current_user()

st.markdown("## 📊 Weekly Check-In")
st.markdown("LangGraph: `context_loader → router → checkin_node → response_formatter`")
st.divider()

db     = SessionLocal()
store  = CheckInStore(db)
last   = store.get_last(user_id)
is_due = store.is_due(user_id)
db.close()

if last:
    from datetime import date
    days_since = (date.today() - last.checkin_date).days
    color = "#00E676" if not is_due else "#FFB300"
    st.markdown(
        f'<div style="background:#1E2130;border-radius:10px;padding:12px 16px;'
        f'border-left:4px solid {color};margin-bottom:16px">'
        f'Last check-in: <strong>{last.checkin_date}</strong> ({days_since}d ago) — '
        f'{"⚠️ Due now!" if is_due else "Next due in " + str(7-days_since) + "d"}'
        f'</div>', unsafe_allow_html=True,
    )

with st.form("checkin_form"):
    c1, c2 = st.columns(2)
    with c1:
        cur_weight = st.number_input("Current Weight (kg)", float(user.weight_kg), 30.0, 300.0, 0.1)
        energy     = st.slider("Energy Level (1–10)", 1, 10, 6)
        hunger     = st.slider("Hunger Level (1–10)", 1, 10, 5)
    with c2:
        sleep_q    = st.slider("Sleep Quality (1–10)", 1, 10, 6)
        recovery   = st.slider("Recovery Quality (1–10)", 1, 10, 6)
    notes = st.text_area("Anything extra for your coach?", height=60)
    submit = st.form_submit_button("🤖 Submit & Get AI Analysis",
                                   type="primary", use_container_width=True)

if submit:
    msg = (
        f"Weekly check-in: weight {cur_weight}kg, "
        f"energy {energy}/10, hunger {hunger}/10, "
        f"sleep quality {sleep_q}/10, recovery {recovery}/10. {notes}"
    )
    with st.spinner("🤖 LangGraph routing → Weekly Check-In node… (may take 30-60s)"):
        result   = run_gym_coach(user_id, msg, intent_override="weekly_checkin")
        response = result.get("response", {})

    if result.get("error"):
        st.error(result["error"])
    else:
        st.success("✅ Check-in complete!")
        st.markdown(f"_{response.get('message','')}_")

        data = response.get("data", {})
        adj  = data.get("adjustments", {})

        if adj:
            st.divider()
            st.markdown(section_header("🔧 Adjustments"), unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("New Calories",
                    f"{adj.get('new_daily_calories',0):.0f} kcal",
                    f"{adj.get('calorie_change',0):+.0f}")
                st.markdown(f"**Cardio:** {adj.get('cardio_recommendation','')}")
            with c2:
                st.metric("New Protein",
                    f"{adj.get('new_protein_target',0):.0f}g",
                    f"{adj.get('protein_change',0):+.0f}g")
                st.markdown(f"**Volume:** {adj.get('volume_recommendation','')}")

        priorities = data.get("top_priorities_next_week", [])
        if priorities:
            st.divider()
            st.markdown(section_header("🎯 Top Priorities Next Week"), unsafe_allow_html=True)
            for i, p in enumerate(priorities, 1):
                st.markdown(f"**{i}.** {p}")
