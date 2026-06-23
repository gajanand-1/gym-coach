import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.models.database import SessionLocal
from app.storage.supplement_store import SupplementStore

st.set_page_config(page_title="Supplement Tracker", page_icon="💊", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 💊 Supplement Tracker")
st.markdown("Track your daily supplement adherence.")
st.divider()

db = SessionLocal()
store = SupplementStore(db)
entry = store.get_today(user_id)

SUPPLEMENT_INFO = {
    "Whey Protein":  {"dose": "30g",  "timing": "Post-workout",  "benefit": "Muscle protein synthesis", "icon": "🥛"},
    "Creatine":      {"dose": "5g",   "timing": "Any time",       "benefit": "Strength & power output",  "icon": "⚡"},
    "Fish Oil":      {"dose": "2g",   "timing": "With meals",     "benefit": "Omega-3, joint health",    "icon": "🐟"},
    "Multivitamin":  {"dose": "1 tab","timing": "Morning",        "benefit": "Micronutrient coverage",   "icon": "💊"},
}

supps = list(entry.supplements)
updated = False

st.markdown(section_header("✅ Today's Supplements"), unsafe_allow_html=True)

for i, supp in enumerate(supps):
    name   = supp.get("name", f"Supplement {i+1}")
    taken  = supp.get("taken", False)
    info   = SUPPLEMENT_INFO.get(name, {})
    icon   = info.get("icon", "💊")

    col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
    with col1:
        st.markdown(f"<div style='font-size:1.8rem;text-align:center'>{icon}</div>",
                    unsafe_allow_html=True)
    with col2:
        st.markdown(f"**{name}**")
        st.caption(info.get("benefit", ""))
    with col3:
        st.markdown(f"Dose: **{supp.get('dose_g','')}g** / {info.get('dose','')}")
        st.caption(f"Timing: {supp.get('time_of_day','').replace('_',' ').title()}")
    with col4:
        pill_class = "pill-taken" if taken else "pill-miss"
        status_text = "✅ Taken" if taken else "❌ Not taken"
        st.markdown(f'<span class="{pill_class}">{status_text}</span>',
                    unsafe_allow_html=True)
    with col5:
        btn_label = "Mark Not Taken" if taken else "Mark Taken"
        if st.button(btn_label, key=f"supp_{i}", use_container_width=True):
            supps[i]["taken"] = not taken
            updated = True

    st.divider()

if updated:
    db2 = SessionLocal()
    SupplementStore(db2).save_today(user_id, supps)
    db2.close()
    st.rerun()

# ── Adherence score ──────────────────────────────────────────────────────
taken_count = sum(1 for s in supps if s.get("taken"))
total_count = len(supps)
score_pct   = int(taken_count / total_count * 100) if total_count else 0

color = "#00E676" if score_pct == 100 else ("#FFB300" if score_pct >= 50 else "#FF5252")
st.markdown(
    f'<div style="background:#1E2130;border-radius:10px;padding:16px;text-align:center;'
    f'border:1px solid #2A2F45">'
    f'<div style="color:#8892A4;font-size:0.8rem;text-transform:uppercase">Today\'s Adherence</div>'
    f'<div style="color:{color};font-size:2.5rem;font-weight:700">{score_pct}%</div>'
    f'<div style="color:#B0B8C8">{taken_count} of {total_count} supplements taken</div>'
    f'</div>',
    unsafe_allow_html=True,
)

db.close()

# ── Supplement guide ──────────────────────────────────────────────────────
st.divider()
with st.expander("📚 Supplement Guide"):
    st.markdown("""
    | Supplement | Evidence | Timing | Key Benefit |
    |---|---|---|---|
    | **Whey Protein** | ⭐⭐⭐⭐⭐ | Post-workout | Fastest-absorbing protein source |
    | **Creatine Monohydrate** | ⭐⭐⭐⭐⭐ | Any time (5g/day) | #1 studied performance supplement |
    | **Fish Oil (Omega-3)** | ⭐⭐⭐⭐ | With fat-containing meal | Reduces inflammation, joint support |
    | **Multivitamin** | ⭐⭐⭐ | Morning with food | Fills micronutrient gaps |

    > **Note:** Creatine requires a 5-7 day loading phase (20g/day) OR steady 5g/day for 4 weeks to saturate muscles.
    """)
