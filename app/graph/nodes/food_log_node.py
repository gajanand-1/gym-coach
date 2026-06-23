"""
Food Log Node
-------------
Parses natural-language food description, cross-references today's mess menu,
calculates macros, saves entry to DB, and returns summary.
"""

from app.graph.gym_state import GymCoachState
from app.agents.food_parser import FoodParserAgent
from app.models.database import SessionLocal
from app.storage.food_store import FoodStore


def food_log_node(state: GymCoachState) -> GymCoachState:
    uid          = state["user_id"]
    intent_data  = state.get("intent_data", {})
    raw_input    = intent_data.get("food_description") or state["user_input"]
    meal_type    = intent_data.get("meal_type", "general")
    mess_today   = state.get("mess_menu_today", {})

    try:
        # Parse macros via AI agent
        agent   = FoodParserAgent()
        parsed  = agent.parse(
            user_input      = raw_input,
            mess_menu_today = mess_today,
            meal_type       = meal_type,
        )

        # Save to DB
        db    = SessionLocal()
        store = FoodStore(db)
        entry = store.add_entry(
            user_id        = uid,
            raw_input      = raw_input,
            food_items     = parsed.get("food_items", []),
            total_calories = parsed.get("total_calories", 0),
            total_protein  = parsed.get("total_protein",  0),
            total_carbs    = parsed.get("total_carbs",    0),
            total_fat      = parsed.get("total_fat",      0),
            meal_type      = parsed.get("meal_type", meal_type),
            source         = "ai_parsed",
        )
        # Refresh today totals
        from datetime import date
        updated_totals = store.get_daily_totals(uid, date.today())
        db.close()

        result = {
            "parsed":           parsed,
            "entry_id":         entry.id,
            "updated_totals":   updated_totals,
            "calories_logged":  parsed.get("total_calories", 0),
            "protein_logged":   parsed.get("total_protein",  0),
        }
        return {**state, "food_log_result": result,
                "today_food": updated_totals, "error": ""}

    except Exception as e:
        return {**state, "food_log_result": {}, "error": f"food_log: {e}"}
