import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css, section_header
from app.utils.session import require_login, init_session_defaults
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.supplement_store import SupplementStore

st.set_page_config(page_title="Supplement Tracker", page_icon="💊", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

st.markdown("## 💊 Supplement Tracker")
st.divider()

db    = SessionLocal()
store = SupplementStore(db)
entry = store.get_today(user_id)
db.close()

INFO = {
    "Whey Protein": {"icon":"🥛","benefit":"Muscle protein synthesis","dose":"30g post-workout"},
    "Creatine":     {"icon":"⚡","benefit":"Strength & power output","dose":"5g/day"},
    "Fish Oil":     {"icon":"🐟","benefit":"Omega-3, joint health",  "dose":"2g with meals"},
    "Multivitamin": {"icon":"💊","benefit":"Micronutrient coverage", "dose":"1 tab morning"},
}

supps   = list(entry.supplements)
updated = False

st.markdown(section_header("✅ Today's Supplements"), unsafe_allow_html=True)
for i, supp in enumerate(supps):
    name   = supp.get("name", f"Supplement {i+1}")
    taken  = supp.get("taken", False)
    info   = INFO.get(name, {})
    c1,c2,c3,c4,c5 = st.columns([1,3,2,2,2])
    with c1: st.markdown(f'<div style="font-size:1.8rem;text-align:center">{info.get("icon","💊")}</div>',
                         unsafe_allow_html=True)
    with c2:
        st.markdown(f"**{name}**")
        st.caption(info.get("benefit",""))
    with c3: st.markdown(info.get("dose",""))
    with c4:
        cls  = "pill-taken" if taken else "pill-miss"
        txt  = "✅ Taken" if taken else "❌ Not taken"
        st.markdown(f'<span class="{cls}">{txt}</span>', unsafe_allow_html=True)
    with c5:
        label = "Mark Not Taken" if taken else "Mark Taken"
        if st.button(label, key=f"sup_{i}", use_container_width=True):
            action = "took" if not taken else "did not take"
            with st.spinner("Logging…"):
                run_gym_coach(user_id, f"I {action} {name} today",
                              intent_override="supplement_log")
            st.rerun()
    st.divider()

taken_count = sum(1 for s in supps if s.get("taken"))
total_count = len(supps)
pct         = int(taken_count / total_count * 100) if total_count else 0
color       = "#00E676" if pct == 100 else ("#FFB300" if pct >= 50 else "#FF5252")
st.markdown(
    f'<div style="background:#1E2130;border-radius:10px;padding:16px;text-align:center;'
    f'border:1px solid #2A2F45">'
    f'<div style="color:#8892A4;font-size:0.8rem;text-transform:uppercase">Adherence</div>'
    f'<div style="color:{color};font-size:2.5rem;font-weight:700">{pct}%</div>'
    f'<div style="color:#B0B8C8">{taken_count}/{total_count} supplements taken</div>'
    f'</div>',
    unsafe_allow_html=True,
)
