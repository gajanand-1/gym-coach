import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.food_store import FoodStore
from app.storage.mess_store import MessStore

st.set_page_config(page_title="Food Log", page_icon="🍽️", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user    = get_current_user()

st.markdown("## 🍽️ Food Log")
st.markdown("Log what you ate — the LangGraph pipeline parses macros automatically.")
st.divider()

# ── Mess menu hint ─────────────────────────────────────────────────────────
db = SessionLocal()
mess_today = MessStore(db).get_today_meals(user_id)
db.close()
if mess_today:
    day = __import__("datetime").date.today().strftime("%A")
    items = []
    for meal, foods in mess_today.items():
        if foods:
            items.append(f"**{meal.title()}:** {', '.join(foods[:3])}")
    if items:
        st.info("🏫 Today's mess menu loaded — say 'I ate lunch' to auto-log!\n\n" +
                "\n".join(items))

# ── Log form ───────────────────────────────────────────────────────────────
st.markdown(section_header("➕ Log Food"), unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    food_input = st.text_area(
        "What did you eat?",
        placeholder='"4 roti, 2 eggs and 200g chicken breast"  or  "I ate lunch"',
        height=80,
    )
with col2:
    meal_type = st.selectbox("Meal Type",
        ["general","breakfast","lunch","dinner","snack"])
    log_btn = st.button("🤖 Parse & Log", use_container_width=True, type="primary")

if log_btn and food_input.strip():
    prompt = food_input.strip()
    if meal_type != "general":
        prompt = f"{meal_type}: {prompt}"
    with st.spinner("🤖 LangGraph routing → Food Log node…"):
        result   = run_gym_coach(user_id, prompt, intent_override="food_log")
        response = result.get("response", {})

    if result.get("error"):
        st.error(result["error"])
    else:
        st.success(response.get("message", "Logged!"))
        data   = response.get("data", {})
        parsed = data.get("parsed", {})
        if parsed:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Calories", f"{parsed.get('total_calories',0):.0f}")
            c2.metric("Protein",  f"{parsed.get('total_protein',0):.1f}g")
            c3.metric("Carbs",    f"{parsed.get('total_carbs',0):.1f}g")
            c4.metric("Fat",      f"{parsed.get('total_fat',0):.1f}g")
            with st.expander("📋 Parsed items"):
                for item in parsed.get("food_items", []):
                    st.markdown(
                        f"**{item.get('name','')}** — "
                        f"{item.get('unit_description','')} | "
                        f"{item.get('calories',0):.0f} kcal | "
                        f"{item.get('protein',0):.1f}g P"
                    )
        st.rerun()

# ── Today's log ────────────────────────────────────────────────────────────
st.divider()
st.markdown(section_header("📋 Today's Food Log"), unsafe_allow_html=True)

db      = SessionLocal()
store   = FoodStore(db)
entries = store.get_by_date(user_id, __import__("datetime").date.today())
totals  = store.get_daily_totals(user_id, __import__("datetime").date.today())
db.close()

if totals["calories"] > 0:
    t_cal = user.target_calories or 2000
    t_pro = user.protein_target_g or 150
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calories", f"{totals['calories']:.0f}", f"/ {t_cal:.0f}")
    c2.metric("Protein",  f"{totals['protein']:.1f}g", f"/ {t_pro:.0f}g")
    c3.metric("Carbs",    f"{totals['carbs']:.1f}g")
    c4.metric("Fat",      f"{totals['fat']:.1f}g")

if not entries:
    st.info("Nothing logged yet today. Type what you ate above.")
else:
    for e in entries:
        c1, c2, c3 = st.columns([4, 2, 1])
        with c1:
            st.markdown(
                f'<div class="food-card"><strong>{e.raw_input[:70]}</strong>'
                f'<br><small style="color:#8892A4">{e.meal_type.title()}'
                f' · {e.created_at.strftime("%H:%M") if e.created_at else ""}</small></div>',
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f'<div style="padding-top:12px;text-align:center">'
                f'<span style="color:#00D4FF">{e.total_calories:.0f} kcal</span> | '
                f'<span style="color:#00E676">{e.total_protein:.1f}g P</span></div>',
                unsafe_allow_html=True,
            )
        with c3:
            if st.button("🗑️", key=f"del_{e.id}"):
                db2 = SessionLocal()
                FoodStore(db2).delete_entry(e.id, user_id)
                db2.close()
                st.rerun()
