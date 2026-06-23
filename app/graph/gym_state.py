"""
Master shared state for the entire GymCoach LangGraph workflow.

Every node reads from and writes back to this single TypedDict.
The state flows:

  user_input
      │
  context_loader   ← loads DB data into state
      │
  router           ← classifies intent
      │
  ┌───┼───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
  │   │   │   │   │   │   │   │   │   │   │   │   │   │
 food diet work wlog prog wght watr slp supp ci  chat mess prof groc
  │   │   │   │   │   │   │   │   │   │   │   │   │   │
  └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
      │
  response_formatter
      │
    END
"""

from __future__ import annotations
from typing import TypedDict, Optional, Any


class GymCoachState(TypedDict):
    # ── Input ─────────────────────────────────────────────────────────────
    user_id:        int
    user_input:     str          # raw natural-language input from user
    session_id:     str          # chat session id

    # ── Routing ──────────────────────────────────────────────────────────
    intent:         str          # classified intent (food_log, coach_chat, …)
    intent_data:    dict         # structured data extracted by router (dates, amounts etc.)
    route_reason:   str          # one-line reason the router chose this intent

    # ── User context (loaded by context_loader) ──────────────────────────
    user_profile:   dict         # full user profile dict
    today_food:     dict         # {calories, protein, carbs, fat} consumed today
    today_water:    dict         # {consumed_liters, target_liters}
    recent_weight:  list         # last 7 weight entries [{date, weight_kg}]
    sleep_avg:      float        # 7-day average sleep hours
    active_diet_plan:    Optional[dict]
    active_workout_plan: Optional[dict]
    recent_workouts:     list    # last 3 workout sessions
    mess_menu_today:     dict    # today's mess menu {breakfast, lunch, dinner}
    chat_history:        list    # last 20 messages [{role, content}]

    # ── Node outputs (one per feature node) ─────────────────────────────
    food_log_result:         dict   # parsed macros + saved entry
    diet_plan_result:        dict   # 7-day plan data
    workout_plan_result:     dict   # weekly programme
    workout_log_result:      dict   # logged session summary
    overload_result:         dict   # progression recommendations
    weight_result:           dict   # logged weight + trend
    water_result:            dict   # updated water intake
    sleep_result:            dict   # logged sleep entry
    supplement_result:       dict   # updated supplement status
    checkin_result:          dict   # weekly check-in report + adjustments
    chat_result:             str    # coach chat reply
    mess_result:             dict   # parsed/saved mess menu
    profile_result:          dict   # updated profile + recalculated macros
    grocery_result:          dict   # grocery list

    # ── Final formatted response (built by response_formatter) ───────────
    response:       dict         # {message, data, intent, success, display_type}
    error:          str          # any error message
