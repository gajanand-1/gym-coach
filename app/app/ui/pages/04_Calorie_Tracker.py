import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, metric_card, progress_html, section_header
from app.utils.session import require_login, init_session_defaults, get_current_user
from app.models.database import SessionLocal
from app.services.food_service import FoodService
from app.services.chart_service import ChartService

st.set_page_config(page_title="Calorie Tracker", page_icon="🔥", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()
user = get_current_user()

st.markdown("## 🔥 Calorie Tracker")
st.divider()

db = SessionLocal()
svc = FoodService(db)
tracker = svc.get_calorie_tracker_data(
    user_id,
    user.target_calories or 2000,
    user.protein_target_g or 150,
    user.carbs_target_g or 200,
    user.fat_target_g or 60,
)
weekly = svc.get_weekly_summary(user_id)
db.close()

# ── Main macro cards with progress ──────────────────────────────────────
st.markdown(section_header("📊 Today's Progress"), unsafe_allow_html=True)

for macro, label, color in [
    ("calories", "🔥 Calories (kcal)", "#00D4FF"),
    ("protein",  "🥩 Protein (g)",     "#00E676"),
    ("carbs",    "🌾 Carbs (g)",        "#FFB300"),
    ("fat",      "🥑 Fat (g)",          "#FF7043"),
]:
    d = tracker[macro]
    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
    with col1:
        st.markdown(
            metric_card("Consumed", f"{d['consumed']:.0f}", label, color),
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            metric_card("Target", f"{d['target']:.0f}", label, "#8892A4"),
            unsafe_allow_html=True,
        )
    with col3:
        rem_color = "#00E676" if d["remaining"] == 0 else color
        st.markdown(
            metric_card("Remaining", f"{d['remaining']:.0f}", label, rem_color),
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(f"**{d['pct']:.1f}%** complete")
        st.markdown(progress_html(d["pct"], color), unsafe_allow_html=True)
        st.markdown("")

# ── Weekly charts ────────────────────────────────────────────────────────
st.divider()
st.markdown(section_header("📅 This Week"), unsafe_allow_html=True)

tab_cal, tab_pro, tab_macro = st.tabs(["Calories", "Protein", "Macro Split"])

with tab_cal:
    fig = ChartService.weekly_calories_chart(weekly, user.target_calories or 2000)
    st.plotly_chart(fig, use_container_width=True)

with tab_pro:
    fig2 = ChartService.weekly_protein_chart(weekly, user.protein_target_g or 150)
    st.plotly_chart(fig2, use_container_width=True)

with tab_macro:
    totals = {
        "protein": sum(d.get("protein", 0) for d in weekly),
        "carbs":   sum(d.get("carbs", 0) for d in weekly),
        "fat":     sum(d.get("fat", 0) for d in weekly),
    }
    fig3 = ChartService.macro_donut(totals["protein"], totals["carbs"], totals["fat"])
    st.markdown("#### Weekly Macro Split")
    st.plotly_chart(fig3, use_container_width=True)

# ── Macro targets reference ──────────────────────────────────────────────
st.divider()
st.markdown(section_header("🎯 Your Macro Targets"), unsafe_allow_html=True)
st.info(
    f"**Calories:** {user.target_calories:.0f} kcal  "
    f"| **Protein:** {user.protein_target_g:.0f}g  "
    f"| **Carbs:** {user.carbs_target_g:.0f}g  "
    f"| **Fat:** {user.fat_target_g:.0f}g  "
    f"| **BMR:** {user.bmr:.0f}  "
    f"| **TDEE:** {user.tdee:.0f}"
)
