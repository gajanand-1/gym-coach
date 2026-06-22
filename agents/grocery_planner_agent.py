"""
Grocery Planner Agent Node — Non-Veg aware
-------------------------------------------
Derives a weekly shopping list from the active 7-day diet plan.
Falls back to LLM generation if no plan exists.
Supports both vegetarian and non-vegetarian grocery lists.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from langchain_core.messages import SystemMessage, HumanMessage

from config import GROCERY_LIST_FILE, DIET_PLAN_FILE, USER_PROFILE_FILE, FOOD_PRICES_PER_100G
from state  import GymCoachState, GroceryItem
from utils  import get_llm, load_json, save_json


SYSTEM_PROMPT = """
You are an Indian grocery planning assistant.

Given the user's diet preferences, budget and diet type, generate a 7-day weekly grocery list.
For NON-VEGETARIAN plans, include: chicken breast, eggs, fish/tuna, and optionally mutton or prawns.
Return ONLY a valid JSON array — no prose, no markdown.

Schema per item:
{
  "item": "Chicken Breast",
  "quantity": "1 kg",
  "estimated_cost": 300
}
""".strip()


def _parse_grams(quantity_str: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:g|ml|gm)", quantity_str, re.IGNORECASE)
    if m:
        return float(m.group(1))
    if "bowl" in quantity_str.lower():  return 150.0
    if "cup"  in quantity_str.lower():  return 200.0
    if "glass" in quantity_str.lower(): return 250.0
    if "piece" in quantity_str.lower(): return 120.0
    if "can"  in quantity_str.lower():  return 185.0
    return 0.0


def _build_from_plan(plan: list[dict]) -> list[GroceryItem]:
    totals: dict[str, float] = defaultdict(float)

    for day in plan:
        for meal in day.get("meals", []):
            for item_str in meal.get("items", []):
                parts    = item_str.strip().split()
                if not parts:
                    continue
                food_key = parts[0].lower().replace(" ", "_")
                grams    = _parse_grams(item_str)
                if grams == 0 and len(parts) > 1:
                    try:
                        grams = float(parts[-1]) * 100
                    except ValueError:
                        grams = 100.0
                totals[food_key] += grams

    grocery_items: list[GroceryItem] = []
    for food, total_grams in sorted(totals.items()):
        if total_grams < 10:
            continue
        if total_grams >= 1000:
            qty_str = f"{total_grams/1000:.1f} kg"
        elif food in ("milk",):
            qty_str = f"{total_grams/1000:.1f} litres"
        else:
            qty_str = f"{total_grams:.0f} g"

        price_per_100g = FOOD_PRICES_PER_100G.get(food, 10)
        cost           = round((total_grams / 100) * price_per_100g, 0)

        grocery_items.append({
            "item":           food.replace("_", " ").title(),
            "quantity":       qty_str,
            "estimated_cost": cost,
        })

    return grocery_items


def grocery_planner_node(state: GymCoachState) -> dict:
    plan    = state.get("weekly_diet_plan") or load_json(DIET_PLAN_FILE, default=[])
    profile = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})
    diet_type = profile.get("diet_type", "non_vegetarian")

    if plan:
        items = _build_from_plan(plan)
    else:
        llm    = get_llm(temperature=0.3)
        prompt = (
            f"Diet type      : {diet_type}\n"
            f"Monthly budget : ₹{profile.get('monthly_budget_inr', 4000)}\n"
            f"Goal           : {profile.get('goal', 'fat_loss')}\n"
        )
        if diet_type == "non_vegetarian":
            prompt += (
                "Include in the list: chicken breast (1kg), eggs (12 pcs), "
                "rohu fish (500g), tuna cans (2), mutton (500g optional).\n"
            )
        prompt += "Generate a complete 7-day grocery list for one person."

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
        raw = llm.invoke(messages).content.strip()
        try:
            items = json.loads(raw)
        except json.JSONDecodeError:
            s, e = raw.find("["), raw.rfind("]") + 1
            try:
                items = json.loads(raw[s:e])
            except Exception:
                return {"agent_response": f"⚠️  Could not generate grocery list.\n{raw}",
                        "error": "grocery_parse_error"}

    save_json(GROCERY_LIST_FILE, items)

    total_cost = sum(i.get("estimated_cost", 0) for i in items)

    # Group items by category
    non_veg_keywords = {"chicken", "egg", "fish", "tuna", "mutton", "prawn",
                        "salmon", "turkey", "lamb", "beef", "rohu"}

    veg_items    = [i for i in items if not any(k in i["item"].lower() for k in non_veg_keywords)]
    nonveg_items = [i for i in items if  any(k in i["item"].lower() for k in non_veg_keywords)]

    lines = [
        f"🛒  Weekly Grocery List  ({diet_type.replace('_',' ').title()})\n" + "═" * 50,
        f"  {'Item':<25}  {'Qty':<12}  {'Cost (₹)':>8}",
        "─" * 50,
    ]

    if nonveg_items:
        lines.append("  🍗 NON-VEG PROTEINS")
        for item in nonveg_items:
            lines.append(f"  {item['item']:<25}  {item['quantity']:<12}  ₹{item.get('estimated_cost',0):>6.0f}")
        lines.append("─" * 50)

    if veg_items:
        lines.append("  🥦 PANTRY / VEG")
        for item in veg_items:
            lines.append(f"  {item['item']:<25}  {item['quantity']:<12}  ₹{item.get('estimated_cost',0):>6.0f}")
        lines.append("─" * 50)

    lines.append(f"  {'TOTAL':<25}  {'':12}  ₹{total_cost:>6.0f}")
    lines.append(f"\n  Monthly estimate: ₹{total_cost * 4:.0f}")

    return {
        "grocery_list":   items,
        "agent_response": "\n".join(lines),
    }
