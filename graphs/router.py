"""
Intent Router Node
------------------
Sits at the START of the graph.
Classifies the user's raw message into one of the known intents
so the graph can route to the right agent node.

Uses a fast LLM call (low temperature) for accuracy.
Falls back to keyword matching if the API is unavailable.
"""

from __future__ import annotations

import re
from langchain_core.messages import SystemMessage, HumanMessage

from state import GymCoachState
from utils import get_llm


# ── All valid intents (= node names they route to) ────────────────────────────
INTENTS = [
    "profile",          # create / update user profile
    "macros",           # calculate TDEE + macro targets
    "diet_plan",        # generate weekly diet plan
    "food_log",         # log food eaten today
    "workout_plan",     # generate weekly workout plan
    "workout_log",      # log a workout session
    "weight_log",       # log today's body weight
    "grocery",          # generate grocery list
    "checkin",          # weekly check-in
    "unknown",          # catch-all
]

SYSTEM_PROMPT = f"""
You are an intent classifier for a personal fitness app.

Classify the user message into EXACTLY ONE of these intents:
{", ".join(INTENTS)}

Rules:
- "profile"      → user is setting up or updating their profile (age, weight, goal, etc.)
- "macros"       → user wants to know their calorie/macro targets
- "diet_plan"    → user wants a meal plan or diet schedule
- "food_log"     → user is describing food they ate / logging a meal
- "workout_plan" → user wants a workout schedule or exercise programme
- "workout_log"  → user is logging a completed workout session (sets/reps/weight)
- "weight_log"   → user is logging their body weight for today
- "grocery"      → user wants a shopping list or grocery plan
- "checkin"      → user is doing a weekly check-in (energy, hunger, sleep, weight update)
- "unknown"      → anything else

Respond with ONLY the intent string — no explanation, no punctuation.
""".strip()


# ── Keyword fallback (no API required) ───────────────────────────────────────
_KEYWORD_MAP: list[tuple[list[str], str]] = [
    (["profile", "age", "height", "my name", "goal is", "i am",
      "i'm", "update profile", "setup", "set up"], "profile"),
    (["tdee", "macro", "calorie target", "how many calories",
      "protein target", "carbs", "calculate"], "macros"),
    (["diet plan", "meal plan", "what to eat", "weekly food",
      "generate diet", "meal schedule"], "diet_plan"),
    (["i ate", "i had", "for breakfast", "for lunch", "for dinner",
      "log food", "food log", "ate today", "drank"], "food_log"),
    (["workout plan", "exercise plan", "gym schedule", "training plan",
      "generate workout", "give me a programme"], "workout_plan"),
    (["bench press", "squat", "deadlift", "sets", "reps", "kg",
      "log workout", "today i did", "trained"], "workout_log"),
    (["weight today", "i weigh", "my weight is", "weight:",
      "logged weight", "scale says", "kg today"], "weight_log"),
    (["grocery", "shopping list", "buy this week",
      "what to buy", "shopping"], "grocery"),
    (["check in", "check-in", "weekly review", "energy level",
      "hunger", "sleep hours", "how am i doing"], "checkin"),
]


def _keyword_intent(text: str) -> str:
    lower = text.lower()
    for keywords, intent in _KEYWORD_MAP:
        if any(kw in lower for kw in keywords):
            return intent
    return "unknown"


def router_node(state: GymCoachState) -> dict:
    """Classify the user's message and set state['intent']."""
    user_input = state.get("user_input", "").strip()
    if not user_input:
        return {"intent": "unknown", "agent_response": "Please tell me what you'd like to do!"}

    # ── Try LLM classification first ─────────────────────────────────────────
    try:
        llm = get_llm(temperature=0.0)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input),
        ]
        raw    = llm.invoke(messages).content.strip().lower()
        intent = raw if raw in INTENTS else _keyword_intent(user_input)
    except Exception:
        intent = _keyword_intent(user_input)

    return {"intent": intent}
