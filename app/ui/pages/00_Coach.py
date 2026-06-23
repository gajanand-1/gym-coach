"""
🤖 AI Coach — Unified Conversational Interface
================================================
Single chat window that routes EVERY command through the
master GymCoachGraph. No need to navigate between pages.

Examples the user can type:
  "I ate 4 roti, 2 eggs and 200g chicken"
  "Log weight 82 kg"
  "Drank 1.5 litres of water"
  "Slept 7 hours last night"
  "Generate my meal plan"
  "Generate workout plan"
  "Show my grocery list"
  "Why is my weight not dropping?"
  "Took creatine and whey today"
  "Start weekly check-in"
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

import streamlit as st
from app.ui.style import inject_css
from app.utils.session import require_login, init_session_defaults
from app.graph.gym_coach_graph import run_gym_coach
from app.models.database import SessionLocal
from app.storage.chat_store import ChatStore

st.set_page_config(page_title="AI Coach", page_icon="🤖", layout="wide")
inject_css()
init_session_defaults()
user_id = require_login()

# ── Sidebar: intent legend ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧭 What can I say?")
    examples = {
        "🍽️ Food":     '"I ate 4 roti and 2 eggs"',
        "🥗 Diet plan": '"Generate my meal plan"',
        "💪 Workout":  '"Generate workout plan"',
        "📋 Log workout": '"Logged bench 60kg 4×10"',
        "📈 Progress": '"Show overload analysis"',
        "⚖️ Weight":   '"Log weight 82 kg"',
        "💧 Water":    '"Drank 500ml water"',
        "😴 Sleep":    '"Slept 7.5 hours"',
        "💊 Supplements": '"Took creatine today"',
        "📊 Check-in": '"Start weekly check-in"',
        "🛒 Grocery":  '"Show grocery list"',
        "👤 Profile":  '"Show my macros"',
        "🏫 Mess":     '"Upload mess menu"',
    }
    for label, ex in examples.items():
        st.markdown(
            f'<div style="margin:4px 0">'
            f'<span style="color:#00D4FF;font-size:0.85rem">{label}</span><br>'
            f'<span style="color:#8892A4;font-size:0.78rem">{ex}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        db = SessionLocal()
        ChatStore(db).clear_session(user_id, "coach_unified")
        db.close()
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:linear-gradient(135deg,#1a1f35,#0E1117);'
    'border-radius:14px;padding:18px 24px;border:1px solid #2A2F45;margin-bottom:20px">'
    '<h2 style="color:#FAFAFA;margin:0">🤖 AI Gym Coach</h2>'
    '<p style="color:#8892A4;margin:4px 0 0">Type anything — food logs, workouts, '
    'questions, plan requests. I handle everything.</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Load and render chat history ──────────────────────────────────────────
db = SessionLocal()
messages = ChatStore(db).get_as_langchain_messages(user_id, "coach_unified", limit=40)
db.close()

INTRO = (
    "👋 Hey! I'm your AI Gym Coach.\n\n"
    "Tell me what you ate, log your workout, ask a question, or say **'generate meal plan'** — "
    "I understand everything and route it to the right tool automatically.\n\n"
    "**Try:** *'I ate 3 rotis, 2 eggs and 1 cup dal for lunch'*"
)

if not messages:
    st.markdown(
        f'<div class="chat-ai">{INTRO}</div>',
        unsafe_allow_html=True,
    )
else:
    for msg in messages:
        role    = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(
                f'<div class="chat-user">🧑 {content}</div>',
                unsafe_allow_html=True,
            )
        elif role == "assistant":
            st.markdown(
                f'<div class="chat-ai">🤖 {content}</div>',
                unsafe_allow_html=True,
            )

# ── Quick-action chips ────────────────────────────────────────────────────
st.markdown("**Quick actions:**")
chips = [
    "Generate meal plan",
    "Generate workout plan",
    "Show overload analysis",
    "Show grocery list",
    "Start weekly check-in",
    "Show my macros",
]
chip_cols = st.columns(len(chips))
for col, chip in zip(chip_cols, chips):
    if col.button(chip, use_container_width=True, key=f"chip_{chip}"):
        st.session_state["coach_prefill"] = chip

# ── Chat input ────────────────────────────────────────────────────────────
user_input = st.chat_input("Talk to your AI coach…")

if "coach_prefill" in st.session_state:
    user_input = st.session_state.pop("coach_prefill")

if user_input and user_input.strip():
    # Show user bubble immediately
    st.markdown(
        f'<div class="chat-user">🧑 {user_input}</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("🤖 Thinking…"):
        result   = run_gym_coach(user_id, user_input.strip(), session_id="coach_unified")
        response = result.get("response", {})
        intent   = result.get("intent", "")
        error    = result.get("error", "")

    # ── Render response bubble ────────────────────────────────────────────
    message      = response.get("message", "")
    display_type = response.get("display_type", "text")
    data         = response.get("data", {})

    st.markdown(
        f'<div class="chat-ai">🤖 {message}</div>',
        unsafe_allow_html=True,
    )

    # ── Rich data renders below the bubble ───────────────────────────────
    if display_type == "macros" and data.get("parsed", {}).get("food_items"):
        with st.expander("📋 Parsed food items", expanded=False):
            for item in data["parsed"].get("food_items", []):
                st.markdown(
                    f"**{item.get('name','')}** — "
                    f"{item.get('unit_description','')} | "
                    f"{item.get('calories',0):.0f} kcal | "
                    f"{item.get('protein',0):.1f}g P"
                )

    elif display_type == "plan" and intent == "diet_plan":
        plan = data.get("plan", {})
        if plan:
            with st.expander("📅 View 7-day meal plan", expanded=False):
                days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                tabs = st.tabs(days)
                for tab, day in zip(tabs, days):
                    with tab:
                        day_data = plan.get(day, {})
                        for meal in ["breakfast","lunch","dinner","snacks"]:
                            items = day_data.get(meal, [])
                            if items:
                                st.markdown(f"**{meal.title()}**")
                                for item in items:
                                    st.markdown(
                                        f"- {item.get('name','')} "
                                        f"({item.get('quantity','')}) — "
                                        f"{item.get('calories',0):.0f} kcal | "
                                        f"{item.get('protein',0):.1f}g P"
                                    )

    elif display_type == "plan" and intent == "workout_plan":
        plan = data.get("plan", {})
        if plan:
            with st.expander("🏋️ View workout plan", expanded=False):
                days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                for day in days:
                    session = plan.get(day, {})
                    exs     = session.get("exercises", [])
                    st.markdown(f"**{day}** — {session.get('session','Rest')}")
                    for ex in exs:
                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;• {ex['name']} "
                            f"{ex['sets']}×{ex['reps']} "
                            f"(rest {ex['rest_seconds']}s)"
                        )

    elif display_type == "table" and intent == "progressive_overload":
        recs = data.get("recommendations", [])
        if recs:
            import pandas as pd
            df = pd.DataFrame([{
                "Exercise":   r.get("exercise",""),
                "Current":    f"{r.get('current_weight_kg',0)}kg × {r.get('current_reps','')}",
                "Next":       f"{r.get('next_weight_kg',0)}kg × {r.get('next_reps_target','')}",
                "Status":     r.get("status","").replace("_"," ").title(),
                "Reasoning":  r.get("reasoning",""),
            } for r in recs])
            with st.expander("📊 Full overload table", expanded=True):
                st.dataframe(df, use_container_width=True, hide_index=True)

    elif display_type == "table" and intent == "grocery":
        items = data.get("items", [])
        if items:
            import pandas as pd
            df = pd.DataFrame([{
                "Item":     i.get("name",""),
                "Servings": i.get("weekly_servings",""),
                "Unit":     i.get("unit",""),
            } for i in items])
            with st.expander("🛒 Full grocery list", expanded=True):
                st.dataframe(df, use_container_width=True, hide_index=True)

    elif display_type == "chart" and intent == "weight_log":
        trend = data.get("trend_30d", [])
        if trend:
            from app.services.chart_service import ChartService
            profile = result.get("user_profile", {})
            fig = ChartService.weight_progress_chart(trend, profile.get("target_weight_kg", 70))
            st.plotly_chart(fig, use_container_width=True)

    elif display_type == "plan" and intent == "weekly_checkin":
        report = data
        if report:
            adj = report.get("adjustments", {})
            cols = st.columns(2)
            with cols[0]:
                st.metric("New Calories",
                    f"{adj.get('new_daily_calories',0):.0f} kcal",
                    f"{adj.get('calorie_change',0):+.0f}")
            with cols[1]:
                st.metric("New Protein",
                    f"{adj.get('new_protein_target',0):.0f}g",
                    f"{adj.get('protein_change',0):+.0f}g")
            if adj.get("cardio_recommendation"):
                st.info(f"🏃 **Cardio:** {adj['cardio_recommendation']}")

    # ── Intent badge ──────────────────────────────────────────────────────
    reason = response.get("route_reason", "")
    st.markdown(
        f'<div style="margin-top:8px">'
        f'<span style="background:#1a2035;border:1px solid #2A2F45;'
        f'border-radius:99px;padding:2px 10px;font-size:0.75rem;color:#8892A4">'
        f'🧭 routed → <strong style="color:#00D4FF">{intent}</strong>'
        f'{" · " + reason[:60] if reason else ""}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    if error:
        st.error(f"⚠️ {error}")

    st.rerun()
