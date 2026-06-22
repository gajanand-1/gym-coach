"""
Weekly Diet Planner Agent Node
-------------------------------
Uses the LLM to generate a personalised 7-day Indian meal plan based on:
  - Macro targets
  - Diet type (veg / non-veg / vegan)
  - Monthly budget
  - Allergies

Returns a structured list[DayPlan] and a formatted text response.
Persists the plan to DIET_PLAN_FILE.
"""

from __future__ import annotations

import json
from datetime import date
from langchain_core.messages import SystemMessage, HumanMessage

from config import USER_PROFILE_FILE, DIET_PLAN_FILE
from state  import GymCoachState
from utils  import get_llm, load_json, save_json, calculate_tdee, calculate_macros


SYSTEM_PROMPT = """
You are an expert Indian sports nutritionist.

Generate a 7-day weekly meal plan (Mon–Sun) that:
1. Hits the given calorie and macro targets every day.
2. Uses only foods available in India within the given monthly budget.
3. Respects the diet type (vegetarian / non_vegetarian / vegan / eggetarian).
4. Avoids all listed allergies.
5. Includes Breakfast, Lunch, Dinner (and an optional Snack).
6. Shows the estimated daily food cost in ₹.

Return ONLY a valid JSON array — no prose, no markdown fences.

Schema for each day:
{
  "day": "Monday",
  "meals": [
    {
      "name": "Breakfast",
      "items": ["Oats 80g", "Milk 200ml", "Banana 1"],
      "kcal": 420,
      "protein_g": 18,
      "carbs_g": 68,
      "fat_g": 8
    }
  ],
  "total_kcal": 2000,
  "daily_cost": 120
}
""".strip()


def diet_planner_node(state: GymCoachState) -> dict:
    """LangGraph node: generate a 7-day diet plan."""

    llm     = get_llm(temperature=0.4)
    profile = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})
    macros  = state.get("macro_targets")

    # ── auto-calculate macros if not already in state ─────────────────────────
    if not macros and profile.get("weight_kg"):
        tdee   = calculate_tdee(
            float(profile["weight_kg"]),
            float(profile.get("height_cm", 170)),
            int(profile.get("age", 25)),
            profile.get("gender", "male"),
            profile.get("activity_level", "moderate"),
        )
        macros = calculate_macros(tdee, float(profile["weight_kg"]),
                                  profile.get("goal", "maintenance"))

    if not macros:
        return {
            "agent_response": (
                "⚠️  Please complete your profile first so I can calculate your macros."
            )
        }

    daily_budget = round(
        float(profile.get("monthly_budget_inr", 4000)) / 30, 0
    )

    prompt = (
        f"Diet type       : {profile.get('diet_type', 'vegetarian')}\n"
        f"Goal            : {profile.get('goal', 'fat_loss')}\n"
        f"Daily calories  : {macros['target_kcal']:.0f} kcal\n"
        f"Protein target  : {macros['protein_g']:.0f} g\n"
        f"Carbs target    : {macros['carbs_g']:.0f} g\n"
        f"Fat target      : {macros['fat_g']:.0f} g\n"
        f"Daily budget    : ₹{daily_budget:.0f}\n"
        f"Allergies       : {', '.join(profile.get('allergies', [])) or 'None'}\n"
        f"Today's date    : {date.today().isoformat()}\n"
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
        start = raw.find("[")
        end   = raw.rfind("]") + 1
        try:
            plan = json.loads(raw[start:end])
        except Exception:
            return {
                "agent_response": f"⚠️  Could not parse diet plan.\n{raw}",
                "error": "diet_plan_parse_error",
            }

    save_json(DIET_PLAN_FILE, plan)

    # ── format for display ────────────────────────────────────────────────────
    lines = ["🥗  7-Day Meal Plan\n" + "═" * 50]
    for day_plan in plan:
        lines.append(f"\n📅  {day_plan['day']}")
        for meal in day_plan.get("meals", []):
            lines.append(f"  🍽️  {meal['name']}")
            for item in meal.get("items", []):
                lines.append(f"       • {item}")
            lines.append(
                f"       ↳ {meal.get('kcal', 0):.0f} kcal  |  "
                f"P: {meal.get('protein_g', 0):.0f}g  "
                f"C: {meal.get('carbs_g', 0):.0f}g  "
                f"F: {meal.get('fat_g', 0):.0f}g"
            )
        lines.append(
            f"  💰 Daily cost: ₹{day_plan.get('daily_cost', 0):.0f}  |  "
            f"Total: {day_plan.get('total_kcal', 0):.0f} kcal"
        )
        lines.append("─" * 50)

    return {
        "weekly_diet_plan": plan,
        "agent_response":   "\n".join(lines),
    }
