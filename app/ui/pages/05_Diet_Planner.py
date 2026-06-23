import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.diet_store import DietStore

DAYS  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MEALS = ["breakfast","lunch","dinner","snacks"]

st.set_page_config(page_title="Diet Planner", page_icon="🥗", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 🥗 AI Diet Planner")
st.markdown("The LangGraph **diet_plan_node** generates your 7-day meal plan.")
st.divider()

with st.expander("⚙️ Generate New Plan", expanded=False):
    st.info("Runs: context_loader → router → diet_plan_node → response_formatter")
    if st.button("🤖 Generate 7-Day Meal Plan", type="primary", use_container_width=True):
        with st.spinner("🤖 LangGraph routing → Diet Plan node…"):
            result = run_gym_coach(user_id, "Generate my weekly meal plan",
                                   intent_override="diet_plan")
        if result.get("error"):
            st.error(result["error"])
        else:
            st.success(result["response"].get("message","Plan generated!"))
            st.rerun()

db = SessionLocal()
active = DietStore(db).get_active(user_id)
db.close()

if not active:
    st.info("No plan yet. Click **Generate 7-Day Meal Plan** above.")
    st.stop()

plan = active.plan_data
st.markdown(f"**Target:** {active.target_calories} kcal | {active.target_protein}g protein "
            f"| **Created:** {active.created_at.strftime('%d %b %Y')}")

tabs = st.tabs(DAYS)
for tab, day in zip(tabs, DAYS):
    with tab:
        day_data    = plan.get(day, {})
        daily_total = day_data.get("daily_total", {})
        if daily_total:
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Calories", f"{daily_total.get('calories',0):.0f}")
            c2.metric("Protein",  f"{daily_total.get('protein',0):.0f}g")
            c3.metric("Carbs",    f"{daily_total.get('carbs',0):.0f}g")
            c4.metric("Fat",      f"{daily_total.get('fat',0):.0f}g")
        st.divider()
        for meal in MEALS:
            items = day_data.get(meal, [])
            if items:
                st.markdown(f"**{meal.title()}**")
                for item in items:
                    st.markdown(
                        f'<div class="food-card">'
                        f'<strong>{item.get("name","")}</strong>'
                        f' <span style="color:#8892A4">— {item.get("quantity","")}</span>'
                        f'<span style="float:right">'
                        f'<span style="color:#00D4FF">{item.get("calories",0):.0f} kcal</span> | '
                        f'<span style="color:#00E676">{item.get("protein",0):.1f}g P</span>'
                        f'</span></div>',
                        unsafe_allow_html=True,
                    )
