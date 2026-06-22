import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.graph.diet_plan_graph import run_diet_plan_graph
from app.storage.diet_store import DietStore
from app.storage.mess_store import MessStore

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MEALS = ["breakfast","lunch","dinner","snacks"]

st.set_page_config(page_title="Diet Planner", page_icon="🥗", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user = get_current_user()

st.markdown("## 🥗 AI Diet Planner")
st.markdown("Generate a personalised 7-day non-vegetarian meal plan tailored to your goals.")
st.divider()

# ── Generate Plan ────────────────────────────────────────────────────────
with st.expander("⚙️ Generate New Plan", expanded=False):
    st.info("This will replace your current active plan.")
    if st.button("🤖 Generate 7-Day Meal Plan", type="primary", use_container_width=True):
        with st.spinner("🤖 AI is creating your personalised meal plan... (30-60 seconds)"):
            db = SessionLocal()
            mess_store = MessStore(db)
            mess_menu = None
            active_mess = mess_store.get_active(user_id)
            if active_mess:
                mess_menu = active_mess.menu_data
            db.close()

            result = run_diet_plan_graph(
                user_id=user_id,
                target_calories=user.target_calories or 2000,
                target_protein=user.protein_target_g or 150,
                target_carbs=user.carbs_target_g or 200,
                target_fat=user.fat_target_g or 60,
                goal=user.goal or "fat_loss",
                experience=user.gym_experience or "beginner",
                allergies=user.allergies or [],
                mess_menu=mess_menu,
            )

        if result.get("error"):
            st.error(f"Error: {result['error']}")
        elif result.get("plan_saved"):
            st.success("✅ New 7-day meal plan generated and saved!")
            st.rerun()
        else:
            st.warning("Plan generated but could not be saved.")

# ── Show Active Plan ─────────────────────────────────────────────────────
db = SessionLocal()
diet_store = DietStore(db)
active_plan = diet_store.get_active(user_id)
db.close()

if not active_plan:
    st.info("No meal plan yet. Click **Generate 7-Day Meal Plan** above to create one.")
    st.stop()

plan = active_plan.plan_data
st.markdown(f"**Plan created:** {active_plan.created_at.strftime('%d %b %Y')} &nbsp;|&nbsp; "
            f"**Target:** {active_plan.target_calories} kcal | {active_plan.target_protein}g protein")

# ── Day tabs ─────────────────────────────────────────────────────────────
tabs = st.tabs(DAYS)
for i, (tab, day) in enumerate(zip(tabs, DAYS)):
    with tab:
        day_data = plan.get(day, {})
        daily_total = day_data.get("daily_total", {})

        # Daily summary row
        if daily_total:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", f"{daily_total.get('calories', 0):.0f} kcal")
            c2.metric("Protein",  f"{daily_total.get('protein', 0):.0f}g")
            c3.metric("Carbs",    f"{daily_total.get('carbs', 0):.0f}g")
            c4.metric("Fat",      f"{daily_total.get('fat', 0):.0f}g")

        st.divider()

        for meal in MEALS:
            items = day_data.get(meal, [])
            if items:
                st.markdown(f"**{meal.title()}**")
                for item in items:
                    name = item.get("name", "Unknown")
                    qty  = item.get("quantity", "")
                    cal  = item.get("calories", 0)
                    pro  = item.get("protein", 0)
                    carb = item.get("carbs", 0)
                    fat  = item.get("fat", 0)
                    st.markdown(
                        f'<div class="food-card">'
                        f'<strong>{name}</strong> <span style="color:#8892A4">— {qty}</span>'
                        f'<span style="float:right">'
                        f'<span style="color:#00D4FF">{cal:.0f} kcal</span> | '
                        f'<span style="color:#00E676">{pro:.1f}g P</span> | '
                        f'<span style="color:#FFB300">{carb:.1f}g C</span> | '
                        f'<span style="color:#FF7043">{fat:.1f}g F</span>'
                        f'</span></div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("")
