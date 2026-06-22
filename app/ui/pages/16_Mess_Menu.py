import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.models.database import SessionLocal
from app.storage.mess_store import MessStore
from app.agents.mess_parser import MessParserAgent
from datetime import date

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MEALS = ["breakfast","lunch","dinner","snacks"]

st.set_page_config(page_title="Mess Menu", page_icon="🏫", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 🏫 Hostel Mess Menu")
st.markdown("Upload or enter your mess menu — the AI will parse it and use it for food logging & diet planning.")
st.divider()

# ── Upload / Input ───────────────────────────────────────────────────────
tab_text, tab_pdf, tab_img = st.tabs(["📝 Manual Input", "📄 PDF Upload", "🖼️ Image Upload"])

with tab_text:
    st.markdown(section_header("Enter Menu as Text"), unsafe_allow_html=True)
    sample = """Monday:
  Breakfast: Aloo Paratha, Dahi, Boiled Eggs
  Lunch: Rice, Palak Dal, Bhindi Fry, Roti
  Dinner: Methi Paratha, Dal Tadka, Salad

Tuesday:
  Breakfast: Poha, Chai, Eggs
  Lunch: Rice, Rajma, Sabzi, Roti
  Dinner: Roti, Dal Fry, Aloo Sabzi"""

    menu_text = st.text_area("Paste your weekly mess menu here:",
        placeholder=sample, height=200)

    if st.button("🤖 Parse & Save Menu", type="primary", use_container_width=True):
        if not menu_text.strip():
            st.error("Please enter menu text.")
        else:
            with st.spinner("🤖 AI is parsing your mess menu..."):
                agent = MessParserAgent()
                parsed = agent.parse_menu(menu_text)
            db = SessionLocal()
            MessStore(db).save_menu(user_id, parsed, raw_input=menu_text, source_type="text")
            db.close()
            st.success("✅ Mess menu saved!")
            st.rerun()

with tab_pdf:
    st.markdown(section_header("Upload PDF"), unsafe_allow_html=True)
    pdf_file = st.file_uploader("Upload mess menu PDF", type=["pdf"])
    if pdf_file and st.button("🤖 Parse PDF", type="primary"):
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name
        with st.spinner("Parsing PDF..."):
            agent = MessParserAgent()
            parsed = agent.parse_from_pdf(tmp_path)
        os.unlink(tmp_path)
        db = SessionLocal()
        MessStore(db).save_menu(user_id, parsed, source_type="pdf")
        db.close()
        st.success("✅ PDF menu parsed and saved!")
        st.rerun()

with tab_img:
    st.markdown(section_header("Upload Image"), unsafe_allow_html=True)
    img_file = st.file_uploader("Upload mess menu photo", type=["jpg","jpeg","png"])
    if img_file and st.button("🤖 Parse Image", type="primary"):
        with st.spinner("Running OCR and parsing..."):
            agent = MessParserAgent()
            parsed = agent.parse_from_image(img_file.read())
        db = SessionLocal()
        MessStore(db).save_menu(user_id, parsed, source_type="image")
        db.close()
        st.success("✅ Image menu parsed and saved!")
        st.rerun()

# ── Show Active Menu ─────────────────────────────────────────────────────
st.divider()
db = SessionLocal()
store = MessStore(db)
active = store.get_active(user_id)
db.close()

if not active or not active.menu_data:
    st.info("No mess menu uploaded yet. Use the tabs above to add your menu.")
    st.stop()

st.markdown(section_header("📋 Current Mess Menu"), unsafe_allow_html=True)
st.caption(f"Saved on: {active.created_at.strftime('%d %b %Y')} via {active.source_type}")

# Highlight today
today_day = date.today().strftime("%A")

tabs = st.tabs(DAYS)
for tab, day in zip(tabs, DAYS):
    with tab:
        day_data = active.menu_data.get(day, {})
        is_today = (day == today_day)
        if is_today:
            st.success(f"📅 **Today is {day}**")

        for meal in MEALS:
            items = day_data.get(meal, [])
            if items:
                items_str = " • ".join(items) if isinstance(items, list) else str(items)
                st.markdown(f"**{meal.title()}:** {items_str}")

# ── Delete menu ──────────────────────────────────────────────────────────
st.divider()
if st.button("🗑️ Delete Active Menu", type="secondary"):
    db2 = SessionLocal()
    MessStore(db2).delete_active(user_id)
    db2.close()
    st.success("Menu deleted.")
    st.rerun()
