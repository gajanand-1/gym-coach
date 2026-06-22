"""
Calorie & Macro Calculator Node
--------------------------------
Pure-math node — no LLM call needed.
Reads the user profile, runs Mifflin-St Jeor TDEE, and derives macro targets.
Persists nothing on its own; the graph stores macros in state.
"""

from __future__ import annotations

from config import USER_PROFILE_FILE
from state  import GymCoachState
from utils  import load_json, calculate_tdee, calculate_macros


def macro_agent_node(state: GymCoachState) -> dict:
    """LangGraph node: compute TDEE + macro targets from user profile."""

    profile = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})

    # ── guard: need minimum fields ────────────────────────────────────────────
    required = ["weight_kg", "height_cm", "age", "gender", "activity_level", "goal"]
    missing  = [f for f in required if not profile.get(f)]
    if missing:
        return {
            "agent_response": (
                f"⚠️  Cannot calculate macros — missing profile fields: "
                f"{', '.join(missing)}.\n"
                "Please update your profile first."
            )
        }

    tdee   = calculate_tdee(
        weight_kg      = float(profile["weight_kg"]),
        height_cm      = float(profile["height_cm"]),
        age            = int(profile["age"]),
        gender         = profile["gender"],
        activity_level = profile["activity_level"],
    )
    macros = calculate_macros(tdee, float(profile["weight_kg"]), profile["goal"])

    goal_label = {
        "fat_loss":     "Fat Loss  (-500 kcal deficit)",
        "muscle_gain":  "Muscle Gain  (+300 kcal surplus)",
        "maintenance":  "Maintenance",
    }.get(profile["goal"], profile["goal"])

    response = (
        f"🔢  Calorie & Macro Targets  —  Goal: {goal_label}\n"
        f"{'─'*50}\n"
        f"  Maintenance (TDEE) : {macros['tdee_kcal']:.0f} kcal\n"
        f"  Daily Target       : {macros['target_kcal']:.0f} kcal\n"
        f"{'─'*50}\n"
        f"  Protein            : {macros['protein_g']:.0f} g\n"
        f"  Carbohydrates      : {macros['carbs_g']:.0f} g\n"
        f"  Fat                : {macros['fat_g']:.0f} g\n"
        f"{'─'*50}\n"
        f"  Protein : Carbs : Fat  ≈  "
        f"{macros['protein_g']*4:.0f} : {macros['carbs_g']*4:.0f} : {macros['fat_g']*9:.0f} kcal"
    )

    return {
        "macro_targets":  macros,
        "agent_response": response,
    }
