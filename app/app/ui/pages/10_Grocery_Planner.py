import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.models.database import SessionLocal
from app.storage.grocery_store import GroceryStore

st.set_page_config(page_title="Grocery Planner", page_icon="🛒", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 🛒 Grocery Planner")
st.markdown("Auto-generated from your active meal plan. Mess-available items are excluded.")
st.divider()

db = SessionLocal()
store = GroceryStore(db)
plan = store.get_active(user_id)
db.close()

if not plan or not plan.items:
    st.info("No grocery plan yet. Generate a **Diet Plan** first — the grocery list is built automatically.")
    st.stop()

items = plan.items

# ── Summary ──────────────────────────────────────────────────────────────
st.markdown(section_header("🧾 Weekly Grocery List"), unsafe_allow_html=True)
st.caption(f"Generated on: {plan.created_at.strftime('%d %b %Y')}")

# Group by category (infer from name)
protein_items = [i for i in items if any(p in i.get("name","").lower()
    for p in ["chicken","egg","tuna","fish","whey","protein","meat","mutton","paneer"])]
carb_items    = [i for i in items if any(p in i.get("name","").lower()
    for p in ["rice","roti","bread","oats","pasta","potato","flour"])]
fat_items     = [i for i in items if any(p in i.get("name","").lower()
    for p in ["oil","ghee","almond","walnut","peanut","butter"])]
other_items   = [i for i in items
    if i not in protein_items and i not in carb_items and i not in fat_items]

def render_items(title: str, items_list: list, color: str = "#00D4FF"):
    if not items_list:
        return
    st.markdown(f'<div style="color:{color};font-weight:700;margin:12px 0 6px">{title}</div>',
                unsafe_allow_html=True)
    for item in items_list:
        name = item.get("name", "Unknown")
        qty  = item.get("weekly_servings", 1)
        unit = item.get("unit", "servings")
        st.markdown(
            f'<div class="food-card">'
            f'<strong>{name}</strong>'
            f'<span style="float:right;color:#8892A4">{qty}× per week — {unit}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

col1, col2 = st.columns(2)
with col1:
    render_items("🥩 Proteins", protein_items, "#00E676")
    render_items("⚡ Fats & Nuts", fat_items, "#FF7043")
with col2:
    render_items("🌾 Carbohydrates", carb_items, "#FFB300")
    render_items("🥬 Other", other_items, "#8892A4")

# ── Full list as downloadable CSV ─────────────────────────────────────────
st.divider()
import pandas as pd
df = pd.DataFrame([
    {"Item": i.get("name",""), "Weekly Servings": i.get("weekly_servings",""),
     "Unit": i.get("unit",""), "In Mess": i.get("available_in_mess", False)}
    for i in items
])
st.download_button(
    "📥 Download Grocery List (CSV)",
    df.to_csv(index=False),
    file_name="grocery_list.csv",
    mime="text/csv",
    use_container_width=True,
)
st.dataframe(df, use_container_width=True, hide_index=True)
