"""
Food Log LangGraph
------------------
Nodes:
  1. check_mess_context  — detect if user is logging a mess meal
  2. parse_food          — call FoodParserAgent
  3. validate_result     — sanity-check macros
  4. save_to_db          — persist via FoodStore

Entry: check_mess_context
Exit:  save_to_db (or clarify if mess meal detected with no quantities)
"""

from langgraph.graph import StateGraph, END
from app.graph.state import FoodLogState
from app.agents.food_parser import FoodParserAgent
from app.models.database import SessionLocal
from app.storage.food_store import FoodStore

# -----------------------------------------------------------------------
# Node functions
# -----------------------------------------------------------------------

def check_mess_context(state: FoodLogState) -> FoodLogState:
    """Detect if the input refers to a mess meal (e.g. 'I ate lunch')."""
    raw = state["raw_input"].lower().strip()
    mess_keywords = ["mess lunch", "mess dinner", "mess breakfast",
                     "ate lunch", "ate dinner", "ate breakfast",
                     "had lunch", "had dinner", "had breakfast",
                     "hostel lunch", "hostel dinner", "hostel breakfast"]

    is_mess_reference = any(kw in raw for kw in mess_keywords)
    menu = state.get("mess_menu_today") or {}

    if is_mess_reference and menu:
        # Detect which meal was referenced
        meal_type = state.get("meal_type")
        if not meal_type:
            if "breakfast" in raw:
                meal_type = "breakfast"
            elif "lunch" in raw:
                meal_type = "lunch"
            elif "dinner" in raw:
                meal_type = "dinner"
            else:
                meal_type = "general"

        meal_items = menu.get(meal_type, [])

        # If items exist and no quantities given → need clarification
        vague_terms = ["ate lunch", "ate dinner", "ate breakfast",
                       "had lunch", "had dinner", "had breakfast"]
        is_vague = any(t == raw.strip() for t in vague_terms)

        if meal_items and is_vague:
            items_str = "\n".join(f"  • {item}" for item in meal_items)
            clarification = (
                f"Today's mess **{meal_type}** was:\n{items_str}\n\n"
                "How many servings did you have? (Say 'standard' for 1 serving each)"
            )
            return {
                **state,
                "needs_clarification": True,
                "clarification_message": clarification,
                "meal_type": meal_type,
            }

    return {**state, "needs_clarification": False, "clarification_message": ""}


def parse_food(state: FoodLogState) -> FoodLogState:
    """Call FoodParserAgent to parse the food description."""
    if state.get("needs_clarification"):
        return state  # Skip parsing — waiting for user clarification

    try:
        agent = FoodParserAgent()
        result = agent.parse(
            user_input=state["raw_input"],
            mess_menu_today=state.get("mess_menu_today"),
            meal_type=state.get("meal_type"),
        )
        return {**state, "parsed_result": result, "error": ""}
    except Exception as e:
        return {**state, "parsed_result": {}, "error": str(e)}


def validate_result(state: FoodLogState) -> FoodLogState:
    """Sanity-check parsed macros — cap unrealistic values."""
    if state.get("needs_clarification") or state.get("error"):
        return state

    result = state.get("parsed_result", {})

    # Cap implausible values (single meal shouldn't exceed 3000 kcal)
    total_cal = result.get("total_calories", 0)
    if total_cal > 3000:
        result["total_calories"] = 3000
        result["notes"] = (result.get("notes", "") +
                           " [Capped at 3000 kcal — please verify quantities]")

    # Ensure all macro keys exist
    for key in ["total_calories", "total_protein", "total_carbs", "total_fat"]:
        if key not in result:
            result[key] = 0.0

    return {**state, "parsed_result": result}


def save_to_db(state: FoodLogState) -> FoodLogState:
    """Persist the food log entry to the database."""
    if state.get("needs_clarification") or state.get("error"):
        return state

    result = state.get("parsed_result", {})
    if not result:
        return {**state, "error": "No parsed result to save."}

    try:
        db = SessionLocal()
        store = FoodStore(db)
        store.add_entry(
            user_id=state["user_id"],
            raw_input=state["raw_input"],
            food_items=result.get("food_items", []),
            total_calories=result.get("total_calories", 0),
            total_protein=result.get("total_protein", 0),
            total_carbs=result.get("total_carbs", 0),
            total_fat=result.get("total_fat", 0),
            meal_type=result.get("meal_type", state.get("meal_type", "general")),
            source="ai_parsed",
        )
        db.close()
        return {**state, "error": ""}
    except Exception as e:
        return {**state, "error": str(e)}


# -----------------------------------------------------------------------
# Conditional edge
# -----------------------------------------------------------------------

def route_after_context_check(state: FoodLogState) -> str:
    if state.get("needs_clarification"):
        return "end"          # Surface clarification message to UI
    return "parse_food"


# -----------------------------------------------------------------------
# Graph assembly
# -----------------------------------------------------------------------

def build_food_log_graph() -> StateGraph:
    g = StateGraph(FoodLogState)

    g.add_node("check_mess_context", check_mess_context)
    g.add_node("parse_food", parse_food)
    g.add_node("validate_result", validate_result)
    g.add_node("save_to_db", save_to_db)

    g.set_entry_point("check_mess_context")
    g.add_conditional_edges(
        "check_mess_context",
        route_after_context_check,
        {"parse_food": "parse_food", "end": END},
    )
    g.add_edge("parse_food", "validate_result")
    g.add_edge("validate_result", "save_to_db")
    g.add_edge("save_to_db", END)

    return g.compile()


# -----------------------------------------------------------------------
# Public runner
# -----------------------------------------------------------------------
_graph = None


def run_food_log_graph(
    user_id: int,
    raw_input: str,
    meal_type: str = None,
    mess_menu_today: dict = None,
) -> FoodLogState:
    global _graph
    if _graph is None:
        _graph = build_food_log_graph()

    initial_state: FoodLogState = {
        "user_id": user_id,
        "raw_input": raw_input,
        "meal_type": meal_type,
        "mess_menu_today": mess_menu_today or {},
        "needs_clarification": False,
        "clarification_message": "",
        "parsed_result": {},
        "error": "",
    }
    return _graph.invoke(initial_state)
