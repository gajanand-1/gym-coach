"""
Food Logging Agent Node
-----------------------
Parses a natural-language description of what the user ate,
calculates calories + macros, updates today's running totals,
and persists to FOOD_LOG_FILE.

Example input: "4 roti, 1 bowl dal, 200g paneer"
"""

from __future__ import annotations

import json
from datetime import date
from langchain_core.messages import SystemMessage, HumanMessage

from config import FOOD_LOG_FILE, USER_PROFILE_FILE
from state  import GymCoachState, FoodLogEntry, DailyFoodSummary
from utils  import get_llm, load_json, save_json, append_to_list, calculate_tdee, calculate_macros


SYSTEM_PROMPT = """
You are a nutrition tracking assistant specialised in Indian food.

Parse the user's food description and return ONLY a valid JSON object.
Use Indian-standard portion sizes when no weight is given:
  - 1 roti ≈ 35 g
  - 1 bowl dal ≈ 150 g (cooked)
  - 1 bowl rice ≈ 200 g (cooked)
  - 1 glass milk ≈ 250 ml
  - 1 banana ≈ 100 g

Schema:
{
  "meal_name": "Lunch",
  "items": ["4 roti (140g)", "1 bowl dal (150g)", "200g paneer"],
  "kcal":      <float>,
  "protein_g": <float>,
  "carbs_g":   <float>,
  "fat_g":     <float>
}

Use these approximate values per 100g for common foods:
  roti:        106 kcal, 3g protein, 20g carbs, 2g fat
  dal:         116 kcal, 9g protein, 20g carbs, 1g fat
  paneer:      265 kcal, 18g protein, 3g carbs, 20g fat
  rice:        130 kcal, 3g protein, 28g carbs, 0g fat
  oats:        389 kcal, 17g protein, 66g carbs, 7g fat
  milk:         61 kcal, 3g protein, 5g carbs, 3g fat
  banana:       89 kcal, 1g protein, 23g carbs, 0g fat
  egg:         155 kcal, 13g protein, 1g carbs, 11g fat
  soy_chunks:  345 kcal, 52g protein, 33g carbs, 1g fat
  chicken:     165 kcal, 31g protein, 0g carbs, 4g fat
  curd:         98 kcal, 11g protein, 4g carbs, 5g fat
  peanuts:     567 kcal, 26g protein, 16g carbs, 49g fat

Return ONLY JSON — no explanations.
""".strip()


def _get_macro_targets(state: GymCoachState) -> dict:
    """Best-effort macro target retrieval."""
    if state.get("macro_targets"):
        return state["macro_targets"]
    profile = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})
    if profile.get("weight_kg"):
        tdee = calculate_tdee(
            float(profile["weight_kg"]),
            float(profile.get("height_cm", 170)),
            int(profile.get("age", 25)),
            profile.get("gender", "male"),
            profile.get("activity_level", "moderate"),
        )
        return calculate_macros(tdee, float(profile["weight_kg"]),
                                profile.get("goal", "maintenance"))
    return {"target_kcal": 2000, "protein_g": 140, "carbs_g": 220, "fat_g": 55}


def food_log_node(state: GymCoachState) -> dict:
    """LangGraph node: parse food input and update daily totals."""

    llm        = get_llm(temperature=0.1)
    user_input = state.get("user_input", "")
    today      = date.today().isoformat()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]

    raw = llm.invoke(messages).content.strip()

    # ── parse ─────────────────────────────────────────────────────────────────
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        s, e = raw.find("{"), raw.rfind("}") + 1
        try:
            parsed = json.loads(raw[s:e])
        except Exception:
            return {
                "agent_response": f"⚠️  Couldn't parse your food input.\n{raw}",
                "error": "food_log_parse_error",
            }

    entry: FoodLogEntry = {
        "date":      today,
        "meal_name": parsed.get("meal_name", "Meal"),
        "items":     parsed.get("items", []),
        "kcal":      float(parsed.get("kcal", 0)),
        "protein_g": float(parsed.get("protein_g", 0)),
        "carbs_g":   float(parsed.get("carbs_g", 0)),
        "fat_g":     float(parsed.get("fat_g", 0)),
    }

    # ── persist & compute today's running total ───────────────────────────────
    all_logs: list = load_json(FOOD_LOG_FILE, default=[])
    all_logs.append(entry)
    save_json(FOOD_LOG_FILE, all_logs)

    today_logs = [e for e in all_logs if e.get("date") == today]
    total_kcal     = sum(e["kcal"]      for e in today_logs)
    total_protein  = sum(e["protein_g"] for e in today_logs)
    total_carbs    = sum(e["carbs_g"]   for e in today_logs)
    total_fat      = sum(e["fat_g"]     for e in today_logs)

    targets = _get_macro_targets(state)
    rem_kcal    = round(targets["target_kcal"] - total_kcal, 1)
    rem_protein = round(targets["protein_g"]   - total_protein, 1)

    summary: DailyFoodSummary = {
        "date":             today,
        "total_kcal":       round(total_kcal, 1),
        "total_protein_g":  round(total_protein, 1),
        "total_carbs_g":    round(total_carbs, 1),
        "total_fat_g":      round(total_fat, 1),
        "remaining_kcal":   rem_kcal,
        "remaining_protein": rem_protein,
    }

    # ── format response ───────────────────────────────────────────────────────
    items_str = "\n".join(f"    • {i}" for i in entry["items"])
    response = (
        f"✅  Logged: {entry['meal_name']}\n"
        f"{items_str}\n\n"
        f"  This meal  →  {entry['kcal']:.0f} kcal  |  "
        f"P: {entry['protein_g']:.0f}g  C: {entry['carbs_g']:.0f}g  F: {entry['fat_g']:.0f}g\n\n"
        f"{'─'*45}\n"
        f"  Today so far   →  {total_kcal:.0f} kcal  |  "
        f"P: {total_protein:.0f}g  C: {total_carbs:.0f}g  F: {total_fat:.0f}g\n"
        f"  Remaining      →  {rem_kcal:.0f} kcal  |  Protein: {rem_protein:.0f}g\n"
    )

    if rem_kcal < 0:
        response += f"\n  ⚠️  You're {abs(rem_kcal):.0f} kcal over target today."
    elif rem_kcal < 200:
        response += "\n  🎯  Almost at your calorie target for the day!"

    return {
        "food_log":       [entry],   # Annotated list — gets appended by graph
        "daily_summary":  summary,
        "agent_response": response,
    }
