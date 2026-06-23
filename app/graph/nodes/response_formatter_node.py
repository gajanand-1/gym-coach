"""
Response Formatter Node
-----------------------
Runs AFTER every feature node.
Converts raw node outputs into a standardised UI-ready response dict.

response = {
  "success":       bool,
  "intent":        str,
  "message":       str,   ← human-readable summary
  "display_type":  str,   ← hint for the UI: "text"|"macros"|"plan"|"chart"|"table"|"chat"
  "data":          dict,  ← the full structured data for the UI to render
  "error":         str,
}
"""

from app.graph.gym_state import GymCoachState


# ── Per-intent formatter helpers ──────────────────────────────────────────

def _fmt_food_log(state: GymCoachState) -> dict:
    r = state.get("food_log_result", {})
    p = r.get("parsed", {})
    t = r.get("updated_totals", {})
    profile = state.get("user_profile", {})
    cal_target = profile.get("target_calories", 0)
    pro_target = profile.get("protein_target_g", 0)
    cal_remaining = max(0, cal_target - t.get("calories", 0))
    pro_remaining = max(0, pro_target - t.get("protein", 0))
    msg = (
        f"✅ Logged **{p.get('total_calories', 0):.0f} kcal** | "
        f"**{p.get('total_protein', 0):.1f}g protein** | "
        f"**{p.get('total_carbs', 0):.1f}g carbs** | "
        f"**{p.get('total_fat', 0):.1f}g fat**\n\n"
        f"📊 Today so far: **{t.get('calories',0):.0f}** kcal "
        f"({cal_remaining:.0f} remaining) | "
        f"**{t.get('protein',0):.1f}g** protein "
        f"({pro_remaining:.1f}g remaining)"
    )
    return {"message": msg, "display_type": "macros", "data": r}


def _fmt_diet_plan(state: GymCoachState) -> dict:
    r    = state.get("diet_plan_result", {})
    plan = r.get("plan", {})
    days = list(plan.keys())
    msg  = (
        f"🥗 Your 7-day meal plan is ready!\n"
        f"Days covered: {', '.join(days)}\n"
        f"Grocery list updated with **{len(r.get('grocery_items', []))}** items."
    )
    return {"message": msg, "display_type": "plan", "data": r}


def _fmt_workout_plan(state: GymCoachState) -> dict:
    r     = state.get("workout_plan_result", {})
    split = r.get("split_type", "").replace("_", " ").title()
    msg   = f"💪 Your {split} workout plan is ready! Check the Workout Planner page."
    return {"message": msg, "display_type": "plan", "data": r}


def _fmt_workout_log(state: GymCoachState) -> dict:
    r   = state.get("workout_log_result", {})
    msg = (
        f"📋 Workout logged: **{r.get('session_name','Session')}**\n"
        f"Volume: **{r.get('total_volume_kg', 0):.0f} kg** | "
        f"{r.get('exercises_count', 0)} exercises"
    )
    return {"message": msg, "display_type": "text", "data": r}


def _fmt_overload(state: GymCoachState) -> dict:
    r    = state.get("overload_result", {})
    recs = r.get("recommendations", [])
    msg  = (
        f"📈 **Progressive Overload Analysis**\n"
        f"{r.get('overall_assessment','')}\n\n"
        + "\n".join(
            f"• **{rec['exercise']}**: {rec.get('current_weight_kg',0)}kg → "
            f"**{rec.get('next_weight_kg',0)}kg** "
            f"({rec.get('status','').replace('_',' ')})"
            for rec in recs[:5]
        )
    )
    return {"message": msg, "display_type": "table", "data": r}


def _fmt_weight(state: GymCoachState) -> dict:
    r   = state.get("weight_result", {})
    msg = (
        f"⚖️ Weight logged: **{r.get('weight_kg', 0):.1f} kg** "
        f"on {r.get('log_date','today')}\n"
        f"Weekly rate: **{r.get('rate_per_week', 0):+.2f} kg/week**"
    )
    return {"message": msg, "display_type": "chart", "data": r}


def _fmt_water(state: GymCoachState) -> dict:
    r   = state.get("water_result", {})
    pct = r.get("pct", 0)
    msg = (
        f"💧 Added **{r.get('added_liters', 0):.2f}L** → "
        f"Total today: **{r.get('consumed_liters', 0):.1f}L** / "
        f"{r.get('target_liters', 3.5):.1f}L ({pct:.0f}%)"
    )
    return {"message": msg, "display_type": "text", "data": r}


def _fmt_sleep(state: GymCoachState) -> dict:
    r   = state.get("sleep_result", {})
    msg = (
        f"😴 Sleep logged: **{r.get('hours', 0):.1f}h** "
        f"({r.get('quality','good')}) | 7-day avg: **{r.get('avg_7d', 0):.1f}h**"
    )
    return {"message": msg, "display_type": "text", "data": r}


def _fmt_supplement(state: GymCoachState) -> dict:
    r     = state.get("supplement_result", {})
    name  = r.get("updated", "Supplement")
    taken = r.get("taken", False)
    msg   = (
        f"💊 **{name}** marked as {'✅ taken' if taken else '❌ not taken'}\n"
        f"Today's adherence: **{r.get('taken_count',0)}/{r.get('total_count',0)}** "
        f"({r.get('adherence_pct',0)}%)"
    )
    return {"message": msg, "display_type": "text", "data": r}


def _fmt_checkin(state: GymCoachState) -> dict:
    r   = state.get("checkin_result", {})
    adj = r.get("adjustments", {})
    msg = (
        f"📊 **Weekly Check-In Complete**\n"
        f"{r.get('weekly_summary', '')}\n\n"
        f"Calorie adjustment: **{adj.get('calorie_change', 0):+.0f} kcal** → "
        f"New target: **{adj.get('new_daily_calories', 0):.0f} kcal**"
    )
    return {"message": msg, "display_type": "plan", "data": r}


def _fmt_chat(state: GymCoachState) -> dict:
    return {"message": state.get("chat_result", ""),
            "display_type": "chat",
            "data": {"response": state.get("chat_result", "")}}


def _fmt_mess(state: GymCoachState) -> dict:
    r    = state.get("mess_result", {})
    days = list(r.get("menu", {}).keys())
    msg  = f"🏫 Mess menu saved! {len(days)} days parsed."
    return {"message": msg, "display_type": "plan", "data": r}


def _fmt_profile(state: GymCoachState) -> dict:
    r   = state.get("profile_result", {})
    msg = (
        f"👤 Profile updated!\n"
        f"Targets → Calories: **{r.get('target_calories',0):.0f} kcal** | "
        f"Protein: **{r.get('protein_target_g',0):.0f}g** | "
        f"Water: **{r.get('water_target_liters',3.5):.1f}L**\n"
        f"BMR: {r.get('bmr',0):.0f} | TDEE: {r.get('tdee',0):.0f}"
    )
    return {"message": msg, "display_type": "text", "data": r}


def _fmt_grocery(state: GymCoachState) -> dict:
    r     = state.get("grocery_result", {})
    items = r.get("items", [])
    msg   = f"🛒 Your grocery list has **{len(items)}** items for the week."
    return {"message": msg, "display_type": "table", "data": r}


# ── Dispatch map ──────────────────────────────────────────────────────────
FORMATTERS = {
    "food_log":             _fmt_food_log,
    "diet_plan":            _fmt_diet_plan,
    "workout_plan":         _fmt_workout_plan,
    "workout_log":          _fmt_workout_log,
    "progressive_overload": _fmt_overload,
    "weight_log":           _fmt_weight,
    "water_log":            _fmt_water,
    "sleep_log":            _fmt_sleep,
    "supplement_log":       _fmt_supplement,
    "weekly_checkin":       _fmt_checkin,
    "coach_chat":           _fmt_chat,
    "mess_menu":            _fmt_mess,
    "profile":              _fmt_profile,
    "grocery":              _fmt_grocery,
}


def response_formatter_node(state: GymCoachState) -> GymCoachState:
    intent    = state.get("intent", "coach_chat")
    error     = state.get("error", "")
    formatter = FORMATTERS.get(intent, _fmt_chat)

    if error:
        formatted = {
            "message":      f"⚠️ Something went wrong: {error}",
            "display_type": "text",
            "data":         {},
        }
    else:
        formatted = formatter(state)

    response = {
        "success":      not bool(error),
        "intent":       intent,
        "route_reason": state.get("route_reason", ""),
        "message":      formatted["message"],
        "display_type": formatted["display_type"],
        "data":         formatted["data"],
        "error":        error,
    }
    return {**state, "response": response}
