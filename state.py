"""
Shared LangGraph state schema.

Every agent node reads from and writes back to this single TypedDict.
Only the keys a node touches need to be updated — LangGraph merges the rest.
"""

from __future__ import annotations

from typing import Any, Literal, Optional
from typing_extensions import TypedDict, Annotated
import operator


# ─────────────────────────────────────────────────────────────────────────────
# Sub-models (plain dicts so they serialise cleanly with json.dumps)
# ─────────────────────────────────────────────────────────────────────────────

class UserProfile(TypedDict, total=False):
    name:                   str
    age:                    int
    gender:                 Literal["male", "female", "other"]
    height_cm:              float
    weight_kg:              float
    target_weight_kg:       float
    goal:                   Literal["fat_loss", "muscle_gain", "maintenance"]
    activity_level:         Literal["sedentary", "light", "moderate", "active", "very_active"]
    diet_type:              Literal["vegetarian", "non_vegetarian", "vegan", "eggetarian"]
    monthly_budget_inr:     float
    gym_experience:         Literal["beginner", "intermediate", "advanced"]
    allergies:              list[str]
    cooking_facilities:     list[str]   # e.g. ["stove", "microwave"]
    sleep_hours:            float


class MacroTargets(TypedDict, total=False):
    tdee_kcal:              float
    target_kcal:            float
    protein_g:              float
    carbs_g:                float
    fat_g:                  float


class Meal(TypedDict, total=False):
    name:       str          # e.g. "Breakfast"
    items:      list[str]    # e.g. ["Oats 80g", "Milk 200ml", "Banana 1"]
    kcal:       float
    protein_g:  float
    carbs_g:    float
    fat_g:      float


class DayPlan(TypedDict, total=False):
    day:        str          # "Monday"
    meals:      list[Meal]
    total_kcal: float
    daily_cost: float        # ₹


class FoodLogEntry(TypedDict, total=False):
    date:       str          # ISO "2024-06-22"
    meal_name:  str
    items:      list[str]
    kcal:       float
    protein_g:  float
    carbs_g:    float
    fat_g:      float


class DailyFoodSummary(TypedDict, total=False):
    date:               str
    total_kcal:         float
    total_protein_g:    float
    total_carbs_g:      float
    total_fat_g:        float
    remaining_kcal:     float
    remaining_protein:  float


class ExerciseSet(TypedDict, total=False):
    weight_kg:  float
    reps:       list[int]


class WorkoutLogEntry(TypedDict, total=False):
    date:       str
    exercise:   str
    sets:       list[ExerciseSet]
    notes:      str


class ProgressiveOverloadSuggestion(TypedDict, total=False):
    exercise:           str
    previous_weight_kg: float
    previous_reps:      list[int]
    current_weight_kg:  float
    current_reps:       list[int]
    recommendation:     str          # e.g. "Increase to 62.5 kg next week"


class WeightEntry(TypedDict, total=False):
    date:       str
    weight_kg:  float


class GroceryItem(TypedDict, total=False):
    item:           str
    quantity:       str   # e.g. "1 kg", "7 litres"
    estimated_cost: float


class WeeklyCheckin(TypedDict, total=False):
    date:               str
    weight_kg:          float
    energy_level:       Literal["low", "medium", "high"]
    hunger_level:       Literal["low", "medium", "high"]
    sleep_hours:        float
    notes:              str
    adjustments:        dict[str, Any]   # what the agent recommends changing


# ─────────────────────────────────────────────────────────────────────────────
# Top-level Graph State
# ─────────────────────────────────────────────────────────────────────────────

class GymCoachState(TypedDict, total=False):
    # ── routing ──────────────────────────────────────────────────────────────
    intent: str          # which feature the user wants to use
    user_input: str      # raw message from the user

    # ── profile & macros ─────────────────────────────────────────────────────
    user_profile:       UserProfile
    macro_targets:      MacroTargets

    # ── diet ─────────────────────────────────────────────────────────────────
    weekly_diet_plan:   list[DayPlan]   # 7-day plan

    # ── food logging (daily running totals) ──────────────────────────────────
    food_log:           Annotated[list[FoodLogEntry], operator.add]
    daily_summary:      DailyFoodSummary

    # ── workout ──────────────────────────────────────────────────────────────
    weekly_workout_plan: list[dict]     # day → exercises list
    workout_log:        Annotated[list[WorkoutLogEntry], operator.add]
    overload_suggestions: list[ProgressiveOverloadSuggestion]

    # ── weight ───────────────────────────────────────────────────────────────
    weight_log:         Annotated[list[WeightEntry], operator.add]
    weight_trend:       list[float]     # last N weights

    # ── grocery ──────────────────────────────────────────────────────────────
    grocery_list:       list[GroceryItem]

    # ── check-in ─────────────────────────────────────────────────────────────
    latest_checkin:     WeeklyCheckin
    checkin_history:    Annotated[list[WeeklyCheckin], operator.add]

    # ── agent response (what gets printed to the user) ───────────────────────
    agent_response:     str

    # ── error / debug ────────────────────────────────────────────────────────
    error:              Optional[str]
