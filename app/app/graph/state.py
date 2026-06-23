"""
Shared TypedDict state definitions for all LangGraph graphs.
Each graph imports the state type it needs from here.
"""

from typing import TypedDict, Optional, Any


# -----------------------------------------------------------------------
# Food Log Graph State
# -----------------------------------------------------------------------
class FoodLogState(TypedDict):
    # Inputs
    user_id: int
    raw_input: str
    meal_type: Optional[str]
    mess_menu_today: Optional[dict]

    # Intermediate
    needs_clarification: bool
    clarification_message: str

    # Output
    parsed_result: dict          # {food_items, total_calories, total_protein, ...}
    error: str


# -----------------------------------------------------------------------
# Diet Plan Graph State
# -----------------------------------------------------------------------
class DietPlanState(TypedDict):
    # Inputs
    user_id: int
    target_calories: float
    target_protein: float
    target_carbs: float
    target_fat: float
    goal: str
    experience: str
    allergies: list
    mess_menu: Optional[dict]

    # Output
    plan_data: dict
    plan_saved: bool
    grocery_items: list
    error: str


# -----------------------------------------------------------------------
# Workout Plan Graph State
# -----------------------------------------------------------------------
class WorkoutPlanState(TypedDict):
    # Inputs
    user_id: int
    split_type: str
    experience: str
    goal: str
    current_weight_kg: float
    age: int
    gender: str

    # Output
    plan_data: dict
    plan_saved: bool
    error: str


# -----------------------------------------------------------------------
# Progressive Overload Graph State
# -----------------------------------------------------------------------
class ProgressiveOverloadState(TypedDict):
    # Inputs
    user_id: int

    # Intermediate
    exercise_history: dict       # {exercise_name: [{date, set, weight_kg, reps}]}

    # Output
    recommendations: dict        # full AI response
    error: str


# -----------------------------------------------------------------------
# Weekly Check-In Graph State
# -----------------------------------------------------------------------
class CheckInState(TypedDict):
    # Inputs
    user_id: int
    current_weight_kg: float
    target_weight_kg: float
    goal: str
    current_calories_target: float
    current_protein_target: float
    energy_level: int
    hunger_level: int
    sleep_quality: int
    recovery_quality: int

    # Collected from stores
    food_log_summary: list
    weight_log: list
    workout_log_summary: list
    sleep_log: list

    # Output
    report: dict
    adjustments_applied: bool
    error: str


# -----------------------------------------------------------------------
# Coach Chat Graph State
# -----------------------------------------------------------------------
class CoachChatState(TypedDict):
    # Inputs
    user_id: int
    user_message: str
    session_id: str

    # Context loaded from stores
    chat_history: list
    user_profile: dict
    today_food_totals: dict
    today_water: dict
    recent_weight: list
    active_diet_plan: Optional[dict]
    active_workout_plan: Optional[dict]
    recent_workouts: list
    sleep_avg: float

    # Output
    response: str
    error: str
