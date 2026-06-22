"""
Weekly Check-In Agent Node
---------------------------
Every Sunday (or on demand) the coach asks about:
  - Current weight
  - Energy level
  - Hunger level
  - Sleep hours

Then analyses the trend and recommends adjustments to:
  - Calorie targets (±100–200 kcal)
  - Cardio volume
  - Workout intensity
"""

from __future__ import annotations

import json
from datetime import date
from langchain_core.messages import SystemMessage, HumanMessage

from config import CHECKIN_LOG_FILE, USER_PROFILE_FILE, WEIGHT_LOG_FILE
from state  import GymCoachState, WeeklyCheckin
from utils  import get_llm, load_json, save_json, append_to_list, calculate_tdee, calculate_macros


SYSTEM_PROMPT = """
You are a personal fitness coach conducting a weekly check-in.

Given the user's check-in data and their history, provide ONLY a valid JSON object
with two keys:
1. "summary"      : 2-3 sentence plain-English summary of how they are doing.
2. "adjustments"  : an object with recommended changes, e.g.:
   {
     "calories":    -100,          <- kcal change (positive=increase, negative=decrease)
     "cardio_min":  +10,           <- extra cardio minutes per session
     "workout_vol": "maintain",    <- "increase" | "decrease" | "maintain"
     "notes":       "Sleep is a priority this week."
   }

Base your recommendations on these rules:
- Weight not moving for 2+ weeks → cut 100 kcal OR add 10 min cardio
- Energy/hunger both LOW → add 100 kcal (possible over-restriction)
- Sleep < 6 hrs → recommend sleep before adding volume
- Weight dropping fast (>1 kg/week) → add 150 kcal
- Weight gaining for fat_loss goal → cut 150 kcal
""".strip()


def _parse_checkin_from_input(user_input: str, llm) -> dict:
    """Use LLM to extract check-in fields from free-form input."""
    extract_prompt = """
Extract check-in data from the user message. Return ONLY JSON:
{
  "weight_kg":    <float or null>,
  "energy_level": <"low"|"medium"|"high" or null>,
  "hunger_level": <"low"|"medium"|"high" or null>,
  "sleep_hours":  <float or null>,
  "notes":        <string or "">
}
""".strip()
    from langchain_core.messages import SystemMessage as SM, HumanMessage as HM
    raw = llm.invoke([SM(content=extract_prompt), HM(content=user_input)]).content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        s, e = raw.find("{"), raw.rfind("}") + 1
        return json.loads(raw[s:e])


def checkin_node(state: GymCoachState) -> dict:
    """LangGraph node: process weekly check-in and adjust recommendations."""

    llm        = get_llm(temperature=0.3)
    user_input = state.get("user_input", "")
    today      = date.today().isoformat()

    # ── Extract structured check-in from user message ─────────────────────────
    try:
        parsed = _parse_checkin_from_input(user_input, llm)
    except Exception as ex:
        return {"agent_response": f"⚠️  Could not parse check-in: {ex}"}

    # ── Load context ──────────────────────────────────────────────────────────
    profile     = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})
    weight_log  = load_json(WEIGHT_LOG_FILE, default=[])
    checkin_log = load_json(CHECKIN_LOG_FILE, default=[])

    # Current weight from check-in or last weight log
    current_weight = parsed.get("weight_kg")
    if not current_weight and weight_log:
        current_weight = weight_log[-1].get("weight_kg")

    # Build context for LLM
    context = {
        "today":          today,
        "goal":           profile.get("goal", "fat_loss"),
        "current_weight": current_weight,
        "target_weight":  profile.get("target_weight_kg"),
        "checkin":        parsed,
        "weight_history": [e["weight_kg"] for e in weight_log[-7:]],
        "past_checkins":  checkin_log[-3:],   # last 3 for trend
    }

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(context, indent=2)),
    ]

    raw = llm.invoke(messages).content.strip()

    # ── Parse LLM recommendations ─────────────────────────────────────────────
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        s, e = raw.find("{"), raw.rfind("}") + 1
        try:
            result = json.loads(raw[s:e])
        except Exception:
            result = {"summary": raw, "adjustments": {}}

    # ── Persist check-in ──────────────────────────────────────────────────────
    checkin: WeeklyCheckin = {
        "date":         today,
        "weight_kg":    current_weight or 0,
        "energy_level": parsed.get("energy_level", "medium"),
        "hunger_level": parsed.get("hunger_level", "medium"),
        "sleep_hours":  parsed.get("sleep_hours", 7),
        "notes":        parsed.get("notes", ""),
        "adjustments":  result.get("adjustments", {}),
    }
    append_to_list(CHECKIN_LOG_FILE, checkin)

    # ── Format response ───────────────────────────────────────────────────────
    adj   = result.get("adjustments", {})
    lines = [
        f"📋  Weekly Check-In Summary — {today}",
        "═" * 50,
        f"  Weight      : {current_weight or 'N/A'} kg",
        f"  Energy      : {parsed.get('energy_level', 'N/A')}",
        f"  Hunger      : {parsed.get('hunger_level', 'N/A')}",
        f"  Sleep       : {parsed.get('sleep_hours', 'N/A')} hrs",
        "",
        "🤖  Coach's Analysis:",
        f"  {result.get('summary', '')}",
        "",
        "🔧  Recommended Adjustments:",
    ]

    if adj.get("calories"):
        sign = "+" if adj["calories"] > 0 else ""
        lines.append(f"  🍽️  Calories   : {sign}{adj['calories']} kcal/day")
    if adj.get("cardio_min"):
        sign = "+" if adj["cardio_min"] > 0 else ""
        lines.append(f"  🏃 Cardio     : {sign}{adj['cardio_min']} min/session")
    if adj.get("workout_vol"):
        lines.append(f"  💪 Volume     : {adj['workout_vol'].title()}")
    if adj.get("notes"):
        lines.append(f"  📝 Note       : {adj['notes']}")

    return {
        "latest_checkin":  checkin,
        "checkin_history": [checkin],
        "agent_response":  "\n".join(lines),
    }
