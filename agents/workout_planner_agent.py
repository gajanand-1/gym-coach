"""
Weekly Workout Planner Agent Node
----------------------------------
Generates a personalised 6-day gym programme (Push/Pull/Legs split or
Full Body for beginners) tailored to the user's goal and experience level.
Persists to WORKOUT_PLAN_FILE.
"""

from __future__ import annotations

import json
from langchain_core.messages import SystemMessage, HumanMessage

from config import WORKOUT_PLAN_FILE, USER_PROFILE_FILE
from state  import GymCoachState
from utils  import get_llm, load_json, save_json


SYSTEM_PROMPT = """
You are an expert strength & conditioning coach.

Generate a weekly gym workout plan based on the user's profile.

Rules:
- Beginners     → 3-day Full Body split
- Intermediate  → 4-day Upper/Lower split
- Advanced      → 6-day PPL (Push/Pull/Legs) split
- Fat loss goal → add 20-min cardio finisher on training days
- Muscle gain   → heavier compound lifts, lower rep ranges

Return ONLY a valid JSON array — no prose, no markdown fences.

Schema per day:
{
  "day": "Monday",
  "split": "Push",
  "exercises": [
    {
      "name": "Bench Press",
      "sets": 4,
      "reps": "8-10",
      "rest_sec": 90,
      "notes": "Keep elbows at 45°"
    }
  ],
  "cardio": "20 min treadmill walk at incline 5"
}

Include rest days with "split": "Rest" and empty exercises list.
Always generate exactly 7 entries (Mon–Sun).
""".strip()


def workout_planner_node(state: GymCoachState) -> dict:
    """LangGraph node: generate a personalised weekly workout plan."""

    llm     = get_llm(temperature=0.4)
    profile = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})

    experience = profile.get("gym_experience", "beginner")
    goal       = profile.get("goal", "fat_loss")
    weight     = profile.get("weight_kg", 70)

    prompt = (
        f"Experience level : {experience}\n"
        f"Goal             : {goal}\n"
        f"Body weight      : {weight} kg\n"
        f"Available days   : Monday to Sunday\n"
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]

    raw = llm.invoke(messages).content.strip()

    # ── parse ─────────────────────────────────────────────────────────────────
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        s, e = raw.find("["), raw.rfind("]") + 1
        try:
            plan = json.loads(raw[s:e])
        except Exception:
            return {
                "agent_response": f"⚠️  Could not parse workout plan.\n{raw}",
                "error": "workout_plan_parse_error",
            }

    save_json(WORKOUT_PLAN_FILE, plan)

    # ── format ────────────────────────────────────────────────────────────────
    lines = [f"💪  Weekly Workout Plan  ({experience.title()} / {goal.replace('_', ' ').title()})\n" + "═" * 55]
    for day in plan:
        split = day.get("split", "")
        if split == "Rest":
            lines.append(f"\n📅  {day['day']}  →  🛌 Rest Day")
            continue
        lines.append(f"\n📅  {day['day']}  —  {split}")
        for ex in day.get("exercises", []):
            lines.append(
                f"  • {ex['name']:<28}  {ex['sets']} × {ex['reps']}  "
                f"(rest {ex.get('rest_sec', 60)}s)"
            )
            if ex.get("notes"):
                lines.append(f"    ℹ️  {ex['notes']}")
        if day.get("cardio"):
            lines.append(f"  🏃 Cardio: {day['cardio']}")
        lines.append("─" * 55)

    return {
        "weekly_workout_plan": plan,
        "agent_response":      "\n".join(lines),
    }
