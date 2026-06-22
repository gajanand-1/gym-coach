"""
Pure-function nutrition calculations.
No LLM calls here — these are deterministic helpers used by agent nodes.
"""

from __future__ import annotations
from config import ACTIVITY_MULTIPLIERS, NUTRIENT_DB, FAT_LOSS_DEFICIT_KCAL, BULK_SURPLUS_KCAL, PROTEIN_PER_KG


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor BMR formula."""
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(weight_kg: float, height_cm: float, age: int,
                   gender: str, activity_level: str) -> float:
    """Total Daily Energy Expenditure."""
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)


def calculate_macros(tdee: float, weight_kg: float, goal: str) -> dict:
    """
    Returns target kcal and macro breakdown.

    Protein: 1.8g/kg bodyweight
    Fat:     25% of target kcal
    Carbs:   remainder
    """
    protein_g = round(weight_kg * PROTEIN_PER_KG, 1)

    if goal == "fat_loss":
        target_kcal = tdee - FAT_LOSS_DEFICIT_KCAL
    elif goal == "muscle_gain":
        target_kcal = tdee + BULK_SURPLUS_KCAL
    else:
        target_kcal = tdee

    fat_g    = round((target_kcal * 0.25) / 9, 1)
    carbs_g  = round((target_kcal - protein_g * 4 - fat_g * 9) / 4, 1)

    return {
        "tdee_kcal":    round(tdee, 1),
        "target_kcal":  round(target_kcal, 1),
        "protein_g":    protein_g,
        "carbs_g":      max(carbs_g, 0),
        "fat_g":        fat_g,
    }


def lookup_nutrition(food_name: str, grams: float) -> dict:
    """
    Return kcal/macros for `grams` of `food_name`.
    Falls back to zeros if food not in DB.
    """
    key = food_name.lower().replace(" ", "_")
    db  = NUTRIENT_DB.get(key, {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0})
    factor = grams / 100.0
    return {
        "kcal":      round(db["kcal"]    * factor, 1),
        "protein_g": round(db["protein"] * factor, 1),
        "carbs_g":   round(db["carbs"]   * factor, 1),
        "fat_g":     round(db["fat"]     * factor, 1),
    }


def sum_nutrition(entries: list[dict]) -> dict:
    """Sum a list of nutrition dicts."""
    totals = {"kcal": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for e in entries:
        for k in totals:
            totals[k] = round(totals[k] + e.get(k, 0), 1)
    return totals
