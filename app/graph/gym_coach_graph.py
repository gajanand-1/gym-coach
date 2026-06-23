"""
Master GymCoach LangGraph
==========================

Full workflow:

  ┌─────────────────────────────────────────────┐
  │              GymCoachGraph                  │
  │                                             │
  │  START                                      │
  │    │                                        │
  │  context_loader  ← loads all DB data        │
  │    │                                        │
  │  router          ← classifies intent        │
  │    │                                        │
  │    ├─ food_log             ─┐               │
  │    ├─ diet_plan            ─┤               │
  │    ├─ workout_plan         ─┤               │
  │    ├─ workout_log          ─┤               │
  │    ├─ progressive_overload ─┤               │
  │    ├─ weight_log           ─┤               │
  │    ├─ water_log            ─┤→ response_    │
  │    ├─ sleep_log            ─┤   formatter   │
  │    ├─ supplement_log       ─┤               │
  │    ├─ weekly_checkin       ─┤      │        │
  │    ├─ coach_chat           ─┤    END        │
  │    ├─ mess_menu            ─┤               │
  │    ├─ profile              ─┤               │
  │    └─ grocery              ─┘               │
  │                                             │
  └─────────────────────────────────────────────┘
"""

from langgraph.graph import StateGraph, END

from app.graph.gym_state import GymCoachState
from app.graph.nodes import (
    context_loader_node,
    router_node,
    food_log_node,
    diet_plan_node,
    workout_plan_node,
    workout_log_node,
    overload_node,
    weight_log_node,
    water_log_node,
    sleep_log_node,
    supplement_node,
    checkin_node,
    coach_chat_node,
    mess_menu_node,
    profile_node,
    grocery_node,
    response_formatter_node,
)

# ── Routing function (reads state["intent"] set by router_node) ───────────
def _route_intent(state: GymCoachState) -> str:
    intent = state.get("intent", "coach_chat")
    valid  = {
        "food_log", "diet_plan", "workout_plan", "workout_log",
        "progressive_overload", "weight_log", "water_log", "sleep_log",
        "supplement_log", "weekly_checkin", "coach_chat", "mess_menu",
        "profile", "grocery",
    }
    return intent if intent in valid else "coach_chat"


# ── Build the compiled graph (called once at module load) ─────────────────
def build_gym_coach_graph() -> StateGraph:
    g = StateGraph(GymCoachState)

    # ── Nodes ─────────────────────────────────────────────────────────────
    g.add_node("context_loader",         context_loader_node)
    g.add_node("router",                 router_node)
    g.add_node("food_log",               food_log_node)
    g.add_node("diet_plan",              diet_plan_node)
    g.add_node("workout_plan",           workout_plan_node)
    g.add_node("workout_log",            workout_log_node)
    g.add_node("progressive_overload",   overload_node)
    g.add_node("weight_log",             weight_log_node)
    g.add_node("water_log",              water_log_node)
    g.add_node("sleep_log",              sleep_log_node)
    g.add_node("supplement_log",         supplement_node)
    g.add_node("weekly_checkin",         checkin_node)
    g.add_node("coach_chat",             coach_chat_node)
    g.add_node("mess_menu",              mess_menu_node)
    g.add_node("profile",                profile_node)
    g.add_node("grocery",                grocery_node)
    g.add_node("response_formatter",     response_formatter_node)

    # ── Entry ─────────────────────────────────────────────────────────────
    g.set_entry_point("context_loader")
    g.add_edge("context_loader", "router")

    # ── Conditional routing from router → feature nodes ───────────────────
    g.add_conditional_edges(
        "router",
        _route_intent,
        {
            "food_log":             "food_log",
            "diet_plan":            "diet_plan",
            "workout_plan":         "workout_plan",
            "workout_log":          "workout_log",
            "progressive_overload": "progressive_overload",
            "weight_log":           "weight_log",
            "water_log":            "water_log",
            "sleep_log":            "sleep_log",
            "supplement_log":       "supplement_log",
            "weekly_checkin":       "weekly_checkin",
            "coach_chat":           "coach_chat",
            "mess_menu":            "mess_menu",
            "profile":              "profile",
            "grocery":              "grocery",
        },
    )

    # ── Every feature node → response_formatter → END ─────────────────────
    for node in [
        "food_log", "diet_plan", "workout_plan", "workout_log",
        "progressive_overload", "weight_log", "water_log", "sleep_log",
        "supplement_log", "weekly_checkin", "coach_chat", "mess_menu",
        "profile", "grocery",
    ]:
        g.add_edge(node, "response_formatter")

    g.add_edge("response_formatter", END)

    return g.compile()


# ── Module-level compiled graph (singleton) ───────────────────────────────
_GYM_COACH_GRAPH = None


def get_gym_coach_graph():
    global _GYM_COACH_GRAPH
    if _GYM_COACH_GRAPH is None:
        _GYM_COACH_GRAPH = build_gym_coach_graph()
    return _GYM_COACH_GRAPH


# ── Public runner ─────────────────────────────────────────────────────────
def run_gym_coach(
    user_id:    int,
    user_input: str,
    session_id: str = "default",
    intent_override: str = None,   # optional: skip router and force intent
) -> GymCoachState:
    """
    Run the full GymCoach LangGraph for a given user input.

    Returns the final GymCoachState, from which callers can read:
      - state["response"]  → formatted UI-ready response dict
      - state["intent"]    → what the router classified
      - state["error"]     → any error string
    """
    graph = get_gym_coach_graph()

    initial: GymCoachState = {
        # Input
        "user_id":    user_id,
        "user_input": user_input,
        "session_id": session_id,

        # Routing
        "intent":       intent_override or "",
        "intent_data":  {},
        "route_reason": "",

        # Context (filled by context_loader)
        "user_profile":        {},
        "today_food":          {},
        "today_water":         {},
        "recent_weight":       [],
        "sleep_avg":           0.0,
        "active_diet_plan":    None,
        "active_workout_plan": None,
        "recent_workouts":     [],
        "mess_menu_today":     {},
        "chat_history":        [],

        # Node outputs (all empty initially)
        "food_log_result":      {},
        "diet_plan_result":     {},
        "workout_plan_result":  {},
        "workout_log_result":   {},
        "overload_result":      {},
        "weight_result":        {},
        "water_result":         {},
        "sleep_result":         {},
        "supplement_result":    {},
        "checkin_result":       {},
        "chat_result":          "",
        "mess_result":          {},
        "profile_result":       {},
        "grocery_result":       {},

        # Response
        "response": {},
        "error":    "",
    }

    # If intent_override is given, skip the router node by pre-filling intent
    if intent_override:
        initial["intent"] = intent_override

    return graph.invoke(initial)
