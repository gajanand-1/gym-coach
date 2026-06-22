"""
Main LangGraph Graph
--------------------
Wires the router + all 9 agent nodes into a single compiled graph.

Flow:
  START
    └─► router_node          (classifies intent)
          ├─► profile_node
          ├─► macro_node
          ├─► diet_plan_node
          ├─► food_log_node
          ├─► workout_plan_node
          ├─► workout_log_node
          ├─► weight_log_node
          ├─► grocery_node
          ├─► checkin_node
          └─► unknown_node
                └─► END  (all paths terminate here)
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from state import GymCoachState

# ── Agent nodes ───────────────────────────────────────────────────────────────
from agents import (
    profile_agent_node,
    macro_agent_node,
    diet_planner_node,
    food_log_node,
    workout_planner_node,
    workout_log_node,
    weight_tracker_node,
    grocery_planner_node,
    checkin_node,
)

# ── Router ────────────────────────────────────────────────────────────────────
from graphs.router import router_node


# ── Fallback node for unrecognised intents ────────────────────────────────────
def unknown_node(state: GymCoachState) -> dict:
    return {
        "agent_response": (
            "🤔  I didn't understand that. Here's what I can help with:\n\n"
            "  • 'Set up my profile'          → User Profile\n"
            "  • 'Calculate my macros'        → Calorie & Macro Targets\n"
            "  • 'Generate a diet plan'       → Weekly Meal Plan\n"
            "  • 'I ate 4 roti and dal'       → Food Logging\n"
            "  • 'Create my workout plan'     → Workout Programme\n"
            "  • 'Log: Bench Press 60kg …'   → Workout Logging\n"
            "  • 'Weight today: 81.5 kg'     → Weight Tracking\n"
            "  • 'Show grocery list'          → Grocery Planner\n"
            "  • 'Weekly check-in'            → Check-In & Adjustments\n"
        )
    }


# ── Routing function (conditional edge) ──────────────────────────────────────
def route_by_intent(state: GymCoachState) -> str:
    """Return the name of the next node based on the classified intent."""
    intent_to_node = {
        "profile":      "profile_node",
        "macros":       "macro_node",
        "diet_plan":    "diet_plan_node",
        "food_log":     "food_log_node",
        "workout_plan": "workout_plan_node",
        "workout_log":  "workout_log_node",
        "weight_log":   "weight_log_node",
        "grocery":      "grocery_node",
        "checkin":      "checkin_node",
    }
    return intent_to_node.get(state.get("intent", ""), "unknown_node")


# ── Build the graph ───────────────────────────────────────────────────────────
def build_graph() -> StateGraph:
    builder = StateGraph(GymCoachState)

    # Add nodes
    builder.add_node("router_node",       router_node)
    builder.add_node("profile_node",      profile_agent_node)
    builder.add_node("macro_node",        macro_agent_node)
    builder.add_node("diet_plan_node",    diet_planner_node)
    builder.add_node("food_log_node",     food_log_node)
    builder.add_node("workout_plan_node", workout_planner_node)
    builder.add_node("workout_log_node",  workout_log_node)
    builder.add_node("weight_log_node",   weight_tracker_node)
    builder.add_node("grocery_node",      grocery_planner_node)
    builder.add_node("checkin_node",      checkin_node)
    builder.add_node("unknown_node",      unknown_node)

    # START → router
    builder.add_edge(START, "router_node")

    # router → agent node (conditional)
    builder.add_conditional_edges(
        "router_node",
        route_by_intent,
        {
            "profile_node":      "profile_node",
            "macro_node":        "macro_node",
            "diet_plan_node":    "diet_plan_node",
            "food_log_node":     "food_log_node",
            "workout_plan_node": "workout_plan_node",
            "workout_log_node":  "workout_log_node",
            "weight_log_node":   "weight_log_node",
            "grocery_node":      "grocery_node",
            "checkin_node":      "checkin_node",
            "unknown_node":      "unknown_node",
        },
    )

    # Every agent node → END
    for node in [
        "profile_node", "macro_node", "diet_plan_node", "food_log_node",
        "workout_plan_node", "workout_log_node", "weight_log_node",
        "grocery_node", "checkin_node", "unknown_node",
    ]:
        builder.add_edge(node, END)

    return builder.compile()


# ── Singleton compiled graph (import this) ───────────────────────────────────
gym_coach_graph = build_graph()
