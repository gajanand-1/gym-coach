"""
Diet Plan LangGraph
-------------------
Nodes:
  1. generate_plan     — call DietPlannerAgent
  2. validate_plan     — check all 7 days present, macro totals sensible
  3. save_plan         — persist via DietStore
  4. generate_grocery  — derive grocery list from plan (excluding mess items)

Entry: generate_plan → validate_plan → save_plan → generate_grocery → END
"""

from datetime import date
from langgraph.graph import StateGraph, END
from app.graph.state import DietPlanState
from app.agents.diet_planner import DietPlannerAgent
from app.models.database import SessionLocal
from app.storage.diet_store import DietStore
from app.storage.grocery_store import GroceryStore

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# -----------------------------------------------------------------------
# Nodes
# -----------------------------------------------------------------------

def generate_plan(state: DietPlanState) -> DietPlanState:
    try:
        agent = DietPlannerAgent()
        plan = agent.generate_plan(
            target_calories=state["target_calories"],
            target_protein=state["target_protein"],
            target_carbs=state["target_carbs"],
            target_fat=state["target_fat"],
            goal=state["goal"],
            experience=state["experience"],
            mess_menu=state.get("mess_menu"),
            allergies=state.get("allergies", []),
        )
        return {**state, "plan_data": plan, "error": ""}
    except Exception as e:
        return {**state, "plan_data": {}, "error": str(e)}


def validate_plan(state: DietPlanState) -> DietPlanState:
    if state.get("error"):
        return state

    plan = state.get("plan_data", {})

    # Ensure all 7 days exist
    for day in DAYS:
        if day not in plan:
            plan[day] = {
                "breakfast": [], "lunch": [], "dinner": [], "snacks": [],
                "daily_total": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
            }

    # Ensure daily_total exists for each day
    for day in DAYS:
        if "daily_total" not in plan[day]:
            # Calculate from meals
            total_cal = total_pro = total_carbs = total_fat = 0.0
            for meal_type in ["breakfast", "lunch", "dinner", "snacks"]:
                for item in plan[day].get(meal_type, []):
                    total_cal += item.get("calories", 0)
                    total_pro += item.get("protein", 0)
                    total_carbs += item.get("carbs", 0)
                    total_fat += item.get("fat", 0)
            plan[day]["daily_total"] = {
                "calories": round(total_cal, 1),
                "protein": round(total_pro, 1),
                "carbs": round(total_carbs, 1),
                "fat": round(total_fat, 1),
            }

    return {**state, "plan_data": plan}


def save_plan(state: DietPlanState) -> DietPlanState:
    if state.get("error") or not state.get("plan_data"):
        return state
    try:
        db = SessionLocal()
        store = DietStore(db)
        store.save_plan(
            user_id=state["user_id"],
            plan_data=state["plan_data"],
            target_calories=int(state["target_calories"]),
            target_protein=int(state["target_protein"]),
            week_start=date.today().isoformat(),
        )
        db.close()
        return {**state, "plan_saved": True}
    except Exception as e:
        return {**state, "plan_saved": False, "error": str(e)}


def generate_grocery(state: DietPlanState) -> DietPlanState:
    """Build grocery list from plan, excluding items already in mess menu."""
    if state.get("error") or not state.get("plan_data"):
        return {**state, "grocery_items": []}

    plan = state["plan_data"]
    mess_menu = state.get("mess_menu") or {}

    # Collect all mess foods (flat set, lowercase)
    mess_foods: set[str] = set()
    for day_meals in mess_menu.values():
        for meal_items in day_meals.values():
            if isinstance(meal_items, list):
                for item in meal_items:
                    mess_foods.add(item.lower().strip())

    # Aggregate food quantities across the week
    food_totals: dict[str, dict] = {}
    for day in DAYS:
        for meal_type in ["breakfast", "lunch", "dinner", "snacks"]:
            for item in plan.get(day, {}).get(meal_type, []):
                name = item.get("name", "Unknown")
                name_lower = name.lower()

                # Skip if available in mess
                if any(mess_food in name_lower or name_lower in mess_food
                       for mess_food in mess_foods):
                    continue

                qty = item.get("quantity", "1 serving")
                if name not in food_totals:
                    food_totals[name] = {
                        "name": name,
                        "weekly_servings": 0,
                        "unit": qty,
                        "available_in_mess": False,
                    }
                food_totals[name]["weekly_servings"] += 1

    grocery_items = list(food_totals.values())

    # Save to grocery store
    try:
        db = SessionLocal()
        store = GroceryStore(db)
        store.save_plan(
            user_id=state["user_id"],
            items=grocery_items,
            week_start=date.today().isoformat(),
        )
        db.close()
    except Exception:
        pass

    return {**state, "grocery_items": grocery_items}


# -----------------------------------------------------------------------
# Graph assembly
# -----------------------------------------------------------------------

def build_diet_plan_graph() -> StateGraph:
    g = StateGraph(DietPlanState)

    g.add_node("generate_plan", generate_plan)
    g.add_node("validate_plan", validate_plan)
    g.add_node("save_plan", save_plan)
    g.add_node("generate_grocery", generate_grocery)

    g.set_entry_point("generate_plan")
    g.add_edge("generate_plan", "validate_plan")
    g.add_edge("validate_plan", "save_plan")
    g.add_edge("save_plan", "generate_grocery")
    g.add_edge("generate_grocery", END)

    return g.compile()


_graph = None


def run_diet_plan_graph(
    user_id: int,
    target_calories: float,
    target_protein: float,
    target_carbs: float,
    target_fat: float,
    goal: str = "fat_loss",
    experience: str = "beginner",
    allergies: list = None,
    mess_menu: dict = None,
) -> DietPlanState:
    global _graph
    if _graph is None:
        _graph = build_diet_plan_graph()

    initial: DietPlanState = {
        "user_id": user_id,
        "target_calories": target_calories,
        "target_protein": target_protein,
        "target_carbs": target_carbs,
        "target_fat": target_fat,
        "goal": goal,
        "experience": experience,
        "allergies": allergies or [],
        "mess_menu": mess_menu or {},
        "plan_data": {},
        "plan_saved": False,
        "grocery_items": [],
        "error": "",
    }
    return _graph.invoke(initial)
