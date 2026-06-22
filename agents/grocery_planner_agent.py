"""
Grocery Planner Agent Node
---------------------------
Derives a weekly shopping list from the active 7-day diet plan
(or falls back to LLM generation if no plan exists).
Estimates costs using the price DB from config.
Persists the list to GROCERY_LIST_FILE.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from langchain_core.messages import SystemMessage, HumanMessage

from config import GROCERY_LIST_FILE, DIET_PLAN_FILE, USER_PROFILE_FILE, FOOD_PRICES_PER_100G
from state  import GymCoachState, GroceryItem
from utils  import get_llm, load_json, save_json


# ── LLM fallback when no diet plan exists ─────────────────────────────────────
SYSTEM_PROMPT = """
You are an Indian grocery planning assistant.

Given the user's diet preferences and budget, generate a weekly grocery list.
Return ONLY a valid JSON array — no prose, no markdown.

Schema per item:
{
  "item": "Oats",
  "quantity": "1 kg",
  "estimated_cost": 80
}
""".strip()


def _parse_grams(quantity_str: str) -> float:
    """Try to extract grams or ml from a string like '80g', '200ml', '1 bowl'."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:g|ml|gm)", quantity_str, re.IGNORECASE)
    if m:
        return float(m.group(1))
    # rough bowl/cup estimates
    if "bowl" in quantity_str.lower():
        return 150.0
    if "cup" in quantity_str.lower():
        return 200.0
    if "glass" in quantity_str.lower():
        return 250.0
    return 0.0


def _build_from_plan(plan: list[dict]) -> list[GroceryItem]:
    """
    Aggregate all meal items across the 7-day plan into a shopping list.
    We tally grams per food and convert to purchase quantities.
    """
    totals: dict[str, float] = defaultdict(float)

    for day in plan:
        for meal in day.get("meals", []):
            for item_str in meal.get("items", []):
                # e.g. "Oats 80g", "Paneer 200g", "Banana 1"
                parts = item_str.strip().split()
                if not parts:
                    continue
                food_key = parts[0].lower()
                grams    = _parse_grams(item_str)
                if grams == 0 and len(parts) > 1:
                    # try numeric quantity (e.g. "Banana 2")
                    try:
                        grams = float(parts[-1]) * 100  # 1 piece ≈ 100g
                    except ValueError:
                        grams = 100.0
                totals[food_key] += grams

    grocery_items: list[GroceryItem] = []
    for food, total_grams in sorted(totals.items()):
        if total_grams < 10:
            continue
        # Determine display quantity
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
    """LangGraph node: generate weekly grocery list."""

    # ── Try to build from existing diet plan ─────────────────────────────────
    plan = state.get("weekly_diet_plan") or load_json(DIET_PLAN_FILE, default=[])

    if plan:
        items = _build_from_plan(plan)
    else:
        # ── LLM fallback ──────────────────────────────────────────────────────
        llm     = get_llm(temperature=0.3)
        profile = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})
        prompt  = (
            f"Diet type      : {profile.get('diet_type', 'vegetarian')}\n"
            f"Monthly budget : ₹{profile.get('monthly_budget_inr', 4000)}\n"
            f"Goal           : {profile.get('goal', 'fat_loss')}\n"
            f"Generate a 7-day grocery list for one person."
        )
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
                return {
                    "agent_response": f"⚠️  Could not generate grocery list.\n{raw}",
                    "error": "grocery_parse_error",
                }

    save_json(GROCERY_LIST_FILE, items)

    # ── Format ────────────────────────────────────────────────────────────────
    total_cost = sum(i.get("estimated_cost", 0) for i in items)
    lines = [
        "🛒  Weekly Grocery List\n" + "═" * 45,
        f"  {'Item':<22}  {'Qty':<12}  {'Cost (₹)':>8}",
        "─" * 45,
    ]
    for item in items:
        lines.append(
            f"  {item['item']:<22}  {item['quantity']:<12}  "
            f"₹{item.get('estimated_cost', 0):>6.0f}"
        )
    lines.append("─" * 45)
    lines.append(f"  {'TOTAL':<22}  {'':12}  ₹{total_cost:>6.0f}")
    lines.append(f"\n  Monthly estimate: ₹{total_cost * 4:.0f}")

    return {
        "grocery_list":   items,
        "agent_response": "\n".join(lines),
    }
