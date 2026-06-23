"""
Diet Plan Node
--------------
Generates a 7-day AI meal plan and saves it.
Also triggers grocery list generation.
"""

from datetime import date
from app.graph.gym_state import GymCoachState
from app.agents.diet_planner import DietPlannerAgent
from app.models.database import SessionLocal
from app.storage.diet_store    import DietStore
from app.storage.grocery_store import GroceryStore


DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


def diet_plan_node(state: GymCoachState) -> GymCoachState:
    uid     = state["user_id"]
    profile = state.get("user_profile", {})
    mess    = state.get("active_diet_plan")   # reuse today's mess context

    # Pull mess_menu from state (set by mess_menu_node or context_loader)
    mess_menu = None
    db = SessionLocal()
    from app.storage.mess_store import MessStore
    active_mess = MessStore(db).get_active(uid)
    if active_mess:
        mess_menu = active_mess.menu_data

    try:
        agent = DietPlannerAgent()
        plan  = agent.generate_plan(
            target_calories = profile.get("target_calories", 2000),
            target_protein  = profile.get("protein_target_g", 150),
            target_carbs    = profile.get("carbs_target_g", 200),
            target_fat      = profile.get("fat_target_g", 60),
            goal            = profile.get("goal", "fat_loss"),
            experience      = profile.get("gym_experience", "beginner"),
            mess_menu       = mess_menu,
            allergies       = profile.get("allergies", []),
        )

        # Ensure all 7 days present
        for day in DAYS:
            if day not in plan:
                plan[day] = {"breakfast":[],"lunch":[],"dinner":[],"snacks":[],
                             "daily_total":{"calories":0,"protein":0,"carbs":0,"fat":0}}
            if "daily_total" not in plan[day]:
                total = {"calories":0,"protein":0,"carbs":0,"fat":0}
                for meal in ["breakfast","lunch","dinner","snacks"]:
                    for item in plan[day].get(meal, []):
                        for k in total:
                            total[k] += item.get(k, 0)
                plan[day]["daily_total"] = {k: round(v,1) for k,v in total.items()}

        # Save plan
        diet_store = DietStore(db)
        db.query(diet_store.__class__) # flush
        saved = diet_store.save_plan(
            user_id         = uid,
            plan_data       = plan,
            target_calories = int(profile.get("target_calories", 2000)),
            target_protein  = int(profile.get("protein_target_g", 150)),
            week_start      = date.today().isoformat(),
        )

        # Generate grocery list (exclude mess items)
        mess_foods: set = set()
        if mess_menu:
            for day_meals in mess_menu.values():
                for items in day_meals.values():
                    if isinstance(items, list):
                        mess_foods.update(i.lower() for i in items)

        food_totals: dict = {}
        for day in DAYS:
            for meal in ["breakfast","lunch","dinner","snacks"]:
                for item in plan.get(day, {}).get(meal, []):
                    name = item.get("name","")
                    if any(m in name.lower() or name.lower() in m for m in mess_foods):
                        continue
                    food_totals.setdefault(name, {"name": name,
                        "weekly_servings": 0, "unit": item.get("quantity","1 serving"),
                        "available_in_mess": False})
                    food_totals[name]["weekly_servings"] += 1

        grocery_items = list(food_totals.values())
        GroceryStore(db).save_plan(uid, grocery_items,
                                   diet_plan_id=saved.id,
                                   week_start=date.today().isoformat())
        db.close()

        return {**state,
                "diet_plan_result": {"plan": plan, "plan_id": saved.id,
                                     "grocery_items": grocery_items},
                "active_diet_plan": {"id": saved.id, "plan_data": plan},
                "error": ""}

    except Exception as e:
        db.close()
        return {**state, "diet_plan_result": {}, "error": f"diet_plan: {e}"}
