"""
Router Node
-----------
Uses GPT-4o to classify the user's intent and extract structured data.
Returns the updated state with `intent` and `intent_data` filled in.

Supported intents:
  food_log           – logging food eaten
  diet_plan          – generate / view meal plan
  workout_plan       – generate / view workout programme
  workout_log        – log a completed workout session
  progressive_overload – analyse strength progression
  weight_log         – log body weight
  water_log          – log water intake
  sleep_log          – log sleep
  supplement_log     – update supplement checklist
  weekly_checkin     – weekly check-in & adjustment
  coach_chat         – general question / conversation
  mess_menu          – upload / view mess menu
  profile            – view / update user profile & macros
  grocery            – view grocery list
"""

import json
from app.graph.gym_state import GymCoachState
from app.agents.base import BaseAgent, extract_json

# ── intent → human-readable description ──────────────────────────────────
INTENT_DESCRIPTIONS = {
    "food_log":            "User is logging food they ate",
    "diet_plan":           "User wants to generate or see their meal plan",
    "workout_plan":        "User wants to generate or see their workout programme",
    "workout_log":         "User is logging a completed workout session",
    "progressive_overload":"User wants strength progression / overload analysis",
    "weight_log":          "User is logging their body weight",
    "water_log":           "User is logging water intake",
    "sleep_log":           "User is logging sleep",
    "supplement_log":      "User is tracking supplements",
    "weekly_checkin":      "User wants their weekly check-in / progress review",
    "coach_chat":          "General fitness question or conversation",
    "mess_menu":           "User is uploading or asking about the hostel mess menu",
    "profile":             "User wants to view or update their profile / macros",
    "grocery":             "User wants to see their grocery list",
}

SYSTEM_PROMPT = f"""You are a routing agent for an AI gym coach app.

Given the user's message, classify it into exactly ONE intent from this list:
{json.dumps(INTENT_DESCRIPTIONS, indent=2)}

Also extract any structured data present in the message.

Return ONLY valid JSON — no prose, no markdown fences:
{{
  "intent": "<one of the intent keys above>",
  "intent_data": {{
    "food_description": "...",   // if food_log
    "meal_type": "...",          // breakfast/lunch/dinner/snack
    "weight_kg": 0,              // if weight_log
    "water_liters": 0,           // if water_log
    "sleep_hours": 0,            // if sleep_log
    "sleep_quality": "good",     // poor/fair/good/excellent
    "exercises": [],             // if workout_log: [{{name, weight_kg, sets:[reps...]}}]
    "session_name": "",          // if workout_log
    "duration_minutes": 0,       // if workout_log
    "query": "..."               // if coach_chat
  }},
  "reason": "one sentence explaining why you chose this intent"
}}"""


class RouterAgent(BaseAgent):
    def route(self, user_input: str, user_profile: dict) -> dict:
        goal   = user_profile.get("goal", "fat_loss")
        name   = user_profile.get("name", "User")

        user_msg = (
            f"User profile summary: name={name}, goal={goal}\n\n"
            f"User message: {user_input}"
        )
        raw = self._call(SYSTEM_PROMPT, user_msg, max_tokens=512)
        try:
            return extract_json(raw)
        except ValueError:
            return {
                "intent":      "coach_chat",
                "intent_data": {"query": user_input},
                "reason":      "Fallback to coach_chat — could not parse router response",
            }


# ── LangGraph node function ────────────────────────────────────────────────
def router_node(state: GymCoachState) -> GymCoachState:
    agent  = RouterAgent()
    result = agent.route(
        user_input   = state["user_input"],
        user_profile = state.get("user_profile", {}),
    )
    return {
        **state,
        "intent":       result.get("intent", "coach_chat"),
        "intent_data":  result.get("intent_data", {}),
        "route_reason": result.get("reason", ""),
        "error":        "",
    }
