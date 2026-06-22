import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.services.food_service import FoodService

st.set_page_config(page_title="Food Log", page_icon="🍽️", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user = get_current_user()

st.markdown("## 🍽️ Food Log")
st.markdown("Type what you ate naturally — the AI will parse it for you.")
st.divider()

# ── Log Entry ────────────────────────────────────────────────────────────
st.markdown(section_header("➕ Log Food"), unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    food_input = st.text_area(
        "What did you eat?",
        placeholder='e.g. "4 roti, 2 eggs, 200g chicken breast and 1 cup dal"',
        height=80,
    )
with col2:
    meal_type = st.selectbox("Meal Type", ["general", "breakfast", "lunch", "dinner", "snack"])
    log_btn = st.button("🤖 Parse & Log", use_container_width=True, type="primary")

# Handle pending clarification from mess-meal detection
if st.session_state.get("food_log_pending_clarification"):
    st.info(st.session_state["food_log_clarification_msg"])
    clarification_input = st.text_area("Your response:", height=60, key="clarification_response")
    if st.button("✅ Submit Clarification"):
        combined = clarification_input
        st.session_state["food_log_pending_clarification"] = False
        db = SessionLocal()
        svc = FoodService(db)
        result = svc.log_food(user_id, combined,
                               st.session_state.get("food_log_pending_meal_type"))
        db.close()
        if result.get("error"):
            st.error(f"Error: {result['error']}")
        else:
            st.success("✅ Food logged successfully!")
            st.rerun()

elif log_btn and food_input.strip():
    with st.spinner("🤖 AI is parsing your food..."):
        db = SessionLocal()
        svc = FoodService(db)
        result = svc.log_food(user_id, food_input, meal_type)
        db.close()

    if result.get("needs_clarification"):
        st.session_state["food_log_pending_clarification"] = True
        st.session_state["food_log_clarification_msg"] = result["clarification_message"]
        st.session_state["food_log_pending_meal_type"] = result.get("meal_type")
        st.rerun()
    elif result.get("error"):
        st.error(f"Error: {result['error']}")
    else:
        parsed = result.get("parsed_result", {})
        st.success("✅ Food logged!")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", f"{parsed.get('total_calories', 0):.0f} kcal")
        c2.metric("Protein",  f"{parsed.get('total_protein', 0):.1f}g")
        c3.metric("Carbs",    f"{parsed.get('total_carbs', 0):.1f}g")
        c4.metric("Fat",      f"{parsed.get('total_fat', 0):.1f}g")

        if parsed.get("food_items"):
            with st.expander("📋 Parsed food items"):
                for item in parsed["food_items"]:
                    st.markdown(
                        f"**{item.get('name')}** — {item.get('unit_description', '')} | "
                        f"{item.get('calories', 0):.0f} kcal | "
                        f"{item.get('protein', 0):.1f}g protein"
                    )
        st.rerun()

# ── Today's Log ──────────────────────────────────────────────────────────
st.divider()
st.markdown(section_header("📋 Today's Food Log"), unsafe_allow_html=True)

db = SessionLocal()
svc = FoodService(db)
entries = svc.get_today_entries(user_id)
totals  = svc.get_today_summary(user_id)
db.close()

# Daily total bar
if totals["calories"] > 0:
    target_cal = user.target_calories or 2000
    pct = min(totals["calories"] / target_cal * 100, 100)
    col_t = st.columns(4)
    col_t[0].metric("Total Calories", f"{totals['calories']:.0f}", f"/ {target_cal:.0f}")
    col_t[1].metric("Protein",  f"{totals['protein']:.1f}g",  f"/ {user.protein_target_g:.0f}g")
    col_t[2].metric("Carbs",    f"{totals['carbs']:.1f}g",    f"/ {user.carbs_target_g:.0f}g")
    col_t[3].metric("Fat",      f"{totals['fat']:.1f}g",      f"/ {user.fat_target_g:.0f}g")

if not entries:
    st.info("No food logged today. Start by entering what you ate above.")
else:
    meal_groups = {}
    for e in entries:
        meal_groups.setdefault(e["meal_type"].title(), []).append(e)

    for meal, items in meal_groups.items():
        st.markdown(f"**{meal}**")
        for item in items:
            col_e1, col_e2, col_e3 = st.columns([4, 2, 1])
            with col_e1:
                st.markdown(
                    f'<div class="food-card"><strong>{item["raw_input"][:60]}</strong>'
                    f'<br><small style="color:#8892A4">{item["time"]}</small></div>',
                    unsafe_allow_html=True,
                )
            with col_e2:
                st.markdown(
                    f'<div style="text-align:center;padding-top:12px">'
                    f'<span style="color:#00D4FF">{item["calories"]:.0f} kcal</span> | '
                    f'<span style="color:#00E676">{item["protein"]:.1f}g P</span></div>',
                    unsafe_allow_html=True,
                )
            with col_e3:
                if st.button("🗑️", key=f"del_{item['id']}", help="Delete this entry"):
                    db2 = SessionLocal()
                    FoodService(db2).delete_entry(item["id"], user_id)
                    db2.close()
                    st.rerun()
