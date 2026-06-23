import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.ui.style import inject_css, metric_card, progress_html, section_header
from app.utils.session import require_login, init_session_defaults
from app.models.database import SessionLocal
from app.services.dashboard_service import DashboardService
from app.services.chart_service import ChartService
from app.utils.helpers import goal_label

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

db = SessionLocal()
svc = DashboardService(db)
snap = svc.get_snapshot(user_id)
db.close()

if not snap:
    st.error("Could not load dashboard. Please complete your profile.")
    st.stop()

user   = snap["user"]
food   = snap["food"]
water  = snap["water"]
weight = snap["weight"]
sleep_ = snap["sleep"]
supps  = snap["supplements"]
workout= snap["workout"]

# ── Header ──────────────────────────────────────────────────────────────
st.markdown(f"## 👋 Welcome back, **{user['name'] or 'Athlete'}**!")
st.markdown(f"Goal: {goal_label(user['goal'])} &nbsp;|&nbsp; "
            f"Current: **{weight['current_kg']:.1f} kg** &nbsp;→&nbsp; "
            f"Target: **{weight['target_kg']:.1f} kg**")

if snap.get("checkin_due"):
    st.warning("⏰ Your **weekly check-in** is due! Head to the Check-In page.", icon="⚠️")

st.divider()

# ── Row 1: Calorie & Macro Cards ─────────────────────────────────────────
st.markdown(section_header("📊 Today's Nutrition"), unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

cal_color = "#00E676" if food["calories_pct"] >= 80 else ("#FFB300" if food["calories_pct"] >= 50 else "#FF5252")
with c1:
    st.markdown(metric_card("Calories", f"{food['consumed']['calories']:.0f}",
                             f"of {user['target_calories']:.0f} kcal", cal_color), unsafe_allow_html=True)
    st.markdown(progress_html(food["calories_pct"], cal_color), unsafe_allow_html=True)

pro_color = "#00E676" if food["protein_pct"] >= 80 else ("#FFB300" if food["protein_pct"] >= 50 else "#FF5252")
with c2:
    st.markdown(metric_card("Protein", f"{food['consumed']['protein']:.0f}g",
                             f"of {user['protein_target_g']:.0f}g", pro_color), unsafe_allow_html=True)
    st.markdown(progress_html(food["protein_pct"], pro_color), unsafe_allow_html=True)

with c3:
    st.markdown(metric_card("Carbs", f"{food['consumed']['carbs']:.0f}g",
                             f"of {user['carbs_target_g']:.0f}g", "#FFB300"), unsafe_allow_html=True)
    carb_pct = food["consumed"]["carbs"] / user["carbs_target_g"] * 100 if user["carbs_target_g"] else 0
    st.markdown(progress_html(carb_pct, "#FFB300"), unsafe_allow_html=True)

with c4:
    st.markdown(metric_card("Fat", f"{food['consumed']['fat']:.0f}g",
                             f"of {user['fat_target_g']:.0f}g", "#FF7043"), unsafe_allow_html=True)
    fat_pct = food["consumed"]["fat"] / user["fat_target_g"] * 100 if user["fat_target_g"] else 0
    st.markdown(progress_html(fat_pct, "#FF7043"), unsafe_allow_html=True)

# ── Row 2: Water, Sleep, Workout, Supplements ────────────────────────────
st.markdown(section_header("💧 Wellness Snapshot"), unsafe_allow_html=True)
w1, w2, w3, w4 = st.columns(4)

water_color = "#00E676" if water["pct"] >= 80 else "#FFB300"
with w1:
    st.markdown(metric_card("Water", f"{water['consumed_liters']:.1f}L",
                             f"of {water['target_liters']:.1f}L target", water_color), unsafe_allow_html=True)
    st.markdown(progress_html(water["pct"], water_color), unsafe_allow_html=True)

with w2:
    sleep_val = sleep_["today_hours"] or sleep_["avg_hours_7d"]
    sleep_color = "#00E676" if (sleep_val or 0) >= 7 else "#FFB300"
    st.markdown(metric_card("Sleep", f"{sleep_val:.1f}h" if sleep_val else "—",
                             "7-day avg" if not sleep_["today_hours"] else "tonight", sleep_color),
                unsafe_allow_html=True)

with w3:
    wo_color = "#00E676" if workout["done_today"] else "#FF5252"
    wo_val = "✅ Done" if workout["done_today"] else "⏳ Pending"
    st.markdown(metric_card("Workout", wo_val,
                             f"{workout['sessions_this_week']} sessions this week", wo_color),
                unsafe_allow_html=True)

with w4:
    taken = sum(1 for s in supps["items"] if s.get("taken"))
    total = len(supps["items"])
    sup_color = "#00E676" if taken == total else "#FFB300"
    st.markdown(metric_card("Supplements", f"{taken}/{total}",
                             "taken today", sup_color), unsafe_allow_html=True)

# ── Row 3: Charts ────────────────────────────────────────────────────────
st.divider()
ch1, ch2 = st.columns([2, 1])

with ch1:
    st.markdown(section_header("📈 Weekly Calories"), unsafe_allow_html=True)
    fig = ChartService.weekly_calories_chart(snap["weekly_food_summary"], user["target_calories"])
    st.plotly_chart(fig, use_container_width=True)

with ch2:
    st.markdown(section_header("🥗 Today's Macros"), unsafe_allow_html=True)
    fig2 = ChartService.macro_donut(
        food["consumed"]["protein"],
        food["consumed"]["carbs"],
        food["consumed"]["fat"],
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 4: Weight Trend ──────────────────────────────────────────────────
st.markdown(section_header("⚖️ Weight Trend (7 Days)"), unsafe_allow_html=True)
fig3 = ChartService.weight_progress_chart(weight["weekly_trend"], weight["target_kg"])
st.plotly_chart(fig3, use_container_width=True)

# ── Today's Meal Log ─────────────────────────────────────────────────────
if food["entries"]:
    st.markdown(section_header("🍽️ Today's Meals"), unsafe_allow_html=True)
    for entry in food["entries"]:
        st.markdown(
            f'<div class="food-card">'
            f'<strong>{entry["meal_type"].title()}</strong> — {entry["raw_input"][:80]}'
            f'<span style="float:right;color:#00D4FF">'
            f'{entry["total_calories"]:.0f} kcal | {entry["total_protein"]:.0f}g protein</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
