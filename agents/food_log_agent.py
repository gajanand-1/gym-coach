"""
Food Logging Agent Node — Expanded (40+ foods, full non-veg support)
---------------------------------------------------------------------
Parses natural-language food descriptions, calculates calories + macros,
updates today's running totals, persists to FOOD_LOG_FILE.

Example inputs:
  "4 boiled eggs, 2 roti, 1 banana"
  "200g chicken breast, 1 cup rice, salad"
  "mutton curry 150g, 3 roti, curd 100g"
"""

from __future__ import annotations

import json
from datetime import date
from langchain_core.messages import SystemMessage, HumanMessage

from config import FOOD_LOG_FILE, USER_PROFILE_FILE
from state  import GymCoachState, FoodLogEntry, DailyFoodSummary
from utils  import get_llm, load_json, save_json, calculate_tdee, calculate_macros

SYSTEM_PROMPT = """
You are a nutrition tracking assistant specialised in Indian food — both vegetarian and non-vegetarian.

Parse the user's food description and return ONLY a valid JSON object.

Use these standard Indian portion sizes when no weight is given:
  Grains / Carbs:
    1 roti        ≈ 35g      | 1 paratha     ≈ 80g
    1 bowl rice   ≈ 200g     | 1 bowl poha   ≈ 150g
    1 idli        ≈ 40g      | 1 dosa        ≈ 100g
    1 slice bread ≈ 30g
  Dairy:
    1 glass milk  ≈ 250ml    | 1 bowl curd   ≈ 150g
    1 cup tea/coffee ≈ 150ml (ignore kcal unless milk heavy)
  Fruits:
    1 banana      ≈ 100g     | 1 apple       ≈ 150g
    1 orange      ≈ 130g     | 1 mango       ≈ 200g
  NON-VEG:
    1 boiled egg  ≈ 50g      | 1 omelette (2 eggs) ≈ 100g
    1 piece chicken breast ≈ 150g
    1 piece chicken leg    ≈ 120g
    1 bowl chicken curry   ≈ 200g
    1 bowl mutton curry    ≈ 200g
    1 fish piece (rohu)    ≈ 120g
    1 tuna can             ≈ 185g
    1 bowl prawn curry     ≈ 150g
  Veg Protein:
    1 bowl dal    ≈ 150g     | 1 cup soy chunks (dry) ≈ 50g
    1 bowl rajma  ≈ 150g     | 1 bowl chana          ≈ 150g

Nutrient values per 100g:
  --- GRAINS ---
  roti:           106 kcal, 3g P, 20g C, 2g F
  rice:           130 kcal, 3g P, 28g C, 0g F
  brown_rice:     123 kcal, 3g P, 26g C, 1g F
  oats:           389 kcal, 17g P, 66g C, 7g F
  bread:          265 kcal, 9g P, 49g C, 3g F
  paratha:        257 kcal, 5g P, 35g C, 11g F
  poha:           110 kcal, 2g P, 24g C, 1g F
  idli:            58 kcal, 2g P, 11g C, 0g F
  dosa:           133 kcal, 3g P, 23g C, 3g F
  pasta:          131 kcal, 5g P, 25g C, 1g F
  sweet_potato:    86 kcal, 2g P, 20g C, 0g F
  upma:           105 kcal, 3g P, 18g C, 3g F
  --- DAIRY ---
  milk:            61 kcal, 3g P, 5g C, 3g F
  curd:            98 kcal, 11g P, 4g C, 5g F
  paneer:         265 kcal, 18g P, 3g C, 20g F
  cheese:         402 kcal, 25g P, 1g C, 33g F
  butter:         717 kcal, 1g P, 0g C, 81g F
  ghee:           900 kcal, 0g P, 0g C, 99g F
  whey_protein:   120 kcal, 24g P, 3g C, 2g F
  --- FRUITS ---
  banana:          89 kcal, 1g P, 23g C, 0g F
  apple:           52 kcal, 0g P, 14g C, 0g F
  orange:          47 kcal, 1g P, 12g C, 0g F
  mango:           60 kcal, 1g P, 15g C, 0g F
  --- VEG PROTEIN ---
  dal:            116 kcal, 9g P, 20g C, 1g F
  soy_chunks:     345 kcal, 52g P, 33g C, 1g F
  tofu:            76 kcal, 8g P, 2g C, 5g F
  peanuts:        567 kcal, 26g P, 16g C, 49g F
  sattu:          406 kcal, 22g P, 65g C, 6g F
  chickpeas:      164 kcal, 9g P, 27g C, 3g F
  kidney_beans:   127 kcal, 9g P, 23g C, 0g F
  --- NON-VEG ---
  chicken_breast: 165 kcal, 31g P, 0g C, 4g F
  chicken_leg:    184 kcal, 26g P, 0g C, 9g F
  chicken_thigh:  209 kcal, 26g P, 0g C, 11g F
  whole_chicken:  215 kcal, 18g P, 0g C, 15g F
  eggs:           155 kcal, 13g P, 1g C, 11g F
  egg_white:       52 kcal, 11g P, 1g C, 0g F
  fish:           136 kcal, 22g P, 0g C, 5g F
  rohu_fish:       97 kcal, 16g P, 0g C, 3g F
  tuna_canned:    116 kcal, 26g P, 0g C, 1g F
  salmon:         208 kcal, 20g P, 0g C, 13g F
  prawns:          99 kcal, 24g P, 0g C, 1g F
  mutton:         294 kcal, 25g P, 0g C, 21g F
  turkey:         189 kcal, 29g P, 0g C, 7g F
  --- NUTS & FATS ---
  almonds:        579 kcal, 21g P, 22g C, 50g F
  walnuts:        654 kcal, 15g P, 14g C, 65g F
  cashews:        553 kcal, 18g P, 30g C, 44g F

Output schema:
{
  "meal_name": "Lunch",
  "items": ["200g chicken breast", "1 bowl rice (200g)", "salad 80g"],
  "kcal":      <float>,
  "protein_g": <float>,
  "carbs_g":   <float>,
  "fat_g":     <float>
}
Return ONLY JSON — no explanations.
""".strip()


def _get_macro_targets(state: GymCoachState) -> dict:
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
    llm        = get_llm(temperature=0.1)
    user_input = state.get("user_input", "")
    today      = date.today().isoformat()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]
    raw = llm.invoke(messages).content.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        s, e = raw.find("{"), raw.rfind("}") + 1
        try:
            parsed = json.loads(raw[s:e])
        except Exception:
            return {"agent_response": f"⚠️  Couldn't parse your food input.\n{raw}",
                    "error": "food_log_parse_error"}

    entry: FoodLogEntry = {
        "date":      today,
        "meal_name": parsed.get("meal_name", "Meal"),
        "items":     parsed.get("items", []),
        "kcal":      float(parsed.get("kcal", 0)),
        "protein_g": float(parsed.get("protein_g", 0)),
        "carbs_g":   float(parsed.get("carbs_g", 0)),
        "fat_g":     float(parsed.get("fat_g", 0)),
    }

    all_logs: list = load_json(FOOD_LOG_FILE, default=[])
    all_logs.append(entry)
    save_json(FOOD_LOG_FILE, all_logs)

    today_logs     = [e for e in all_logs if e.get("date") == today]
    total_kcal     = sum(e["kcal"]      for e in today_logs)
    total_protein  = sum(e["protein_g"] for e in today_logs)
    total_carbs    = sum(e["carbs_g"]   for e in today_logs)
    total_fat      = sum(e["fat_g"]     for e in today_logs)

    targets     = _get_macro_targets(state)
    rem_kcal    = round(targets["target_kcal"] - total_kcal, 1)
    rem_protein = round(targets["protein_g"]   - total_protein, 1)

    summary: DailyFoodSummary = {
        "date":              today,
        "total_kcal":        round(total_kcal, 1),
        "total_protein_g":   round(total_protein, 1),
        "total_carbs_g":     round(total_carbs, 1),
        "total_fat_g":       round(total_fat, 1),
        "remaining_kcal":    rem_kcal,
        "remaining_protein": rem_protein,
    }

    items_str = "\n".join(f"    • {i}" for i in entry["items"])
    response = (
        f"✅  Logged: {entry['meal_name']}\n"
        f"{items_str}\n\n"
        f"  This meal  →  {entry['kcal']:.0f} kcal  |  "
        f"P: {entry['protein_g']:.0f}g  C: {entry['carbs_g']:.0f}g  F: {entry['fat_g']:.0f}g\n\n"
        f"{'─'*48}\n"
        f"  Today so far   →  {total_kcal:.0f} kcal  |  "
        f"P: {total_protein:.0f}g  C: {total_carbs:.0f}g  F: {total_fat:.0f}g\n"
        f"  Remaining      →  {rem_kcal:.0f} kcal  |  Protein: {rem_protein:.0f}g\n"
    )

    # All meals logged today
    if len(today_logs) > 1:
        response += f"\n  📋 Meals today ({len(today_logs)}):\n"
        for m in today_logs:
            response += f"     • {m['meal_name']:<12} {m['kcal']:.0f} kcal  P:{m['protein_g']:.0f}g\n"

    if rem_kcal < 0:
        response += f"\n  ⚠️  You're {abs(rem_kcal):.0f} kcal over target today."
    elif rem_kcal < 200:
        response += "\n  🎯  Almost at your calorie target for the day!"
    else:
        pct = int((total_kcal / targets["target_kcal"]) * 100)
        response += f"\n  📊  Progress: {pct}% of daily target"

    return {
        "food_log":       [entry],
        "daily_summary":  summary,
        "agent_response": response,
    }
