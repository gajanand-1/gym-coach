import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.grocery_store import GroceryStore
import pandas as pd

st.set_page_config(page_title="Grocery Planner", page_icon="🛒", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 🛒 Grocery Planner")
st.markdown("Auto-generated from your active meal plan. Mess items excluded.")
st.divider()

if st.button("🔄 Refresh List", use_container_width=True):
    with st.spinner("🤖 LangGraph routing → Grocery node…"):
        run_gym_coach(user_id, "Show my grocery list", intent_override="grocery")
    st.rerun()

db   = SessionLocal()
plan = GroceryStore(db).get_active(user_id)
db.close()

if not plan or not plan.items:
    st.info("No grocery list yet. Generate a **Diet Plan** first.")
    st.stop()

items = plan.items

def _cat(name):
    n = name.lower()
    if any(p in n for p in ["chicken","egg","tuna","fish","whey","protein","mutton","paneer"]): return "protein"
    if any(p in n for p in ["rice","roti","bread","oats","pasta","potato"]): return "carbs"
    if any(p in n for p in ["oil","ghee","almond","walnut","peanut"]): return "fat"
    return "other"

proteins = [i for i in items if _cat(i["name"]) == "protein"]
carbs    = [i for i in items if _cat(i["name"]) == "carbs"]
fats     = [i for i in items if _cat(i["name"]) == "fat"]
others   = [i for i in items if _cat(i["name"]) == "other"]

def _render(title, lst, color):
    if not lst: return
    st.markdown(f'<div style="color:{color};font-weight:700;margin:12px 0 6px">{title}</div>',
                unsafe_allow_html=True)
    for item in lst:
        st.markdown(
            f'<div class="food-card"><strong>{item["name"]}</strong>'
            f'<span style="float:right;color:#8892A4">'
            f'{item["weekly_servings"]}× per week — {item.get("unit","serving")}'
            f'</span></div>',
            unsafe_allow_html=True,
        )

c1, c2 = st.columns(2)
with c1:
    _render("🥩 Proteins",    proteins, "#00E676")
    _render("⚡ Fats & Nuts", fats,     "#FF7043")
with c2:
    _render("🌾 Carbohydrates",carbs,   "#FFB300")
    _render("🥬 Other",        others,  "#8892A4")

st.divider()
df = pd.DataFrame([{"Item": i["name"], "Servings/Week": i["weekly_servings"],
                     "Unit": i.get("unit","")} for i in items])
st.download_button("📥 Download CSV", df.to_csv(index=False),
                   "grocery_list.csv", "text/csv", use_container_width=True)
st.dataframe(df, use_container_width=True, hide_index=True)
