"""
Profile Node
------------
Updates user profile fields and recalculates BMR / TDEE / macro targets.
"""

from app.graph.gym_state import GymCoachState
from app.models.database import SessionLocal
from app.services.auth_service import AuthService
from app.services.macro_calculator import MacroCalculator


def profile_node(state: GymCoachState) -> GymCoachState:
    uid         = state["user_id"]
    intent_data = state.get("intent_data", {})
    profile     = state.get("user_profile", {})

    # Merge any fields present in intent_data
    update_fields = {k: v for k, v in intent_data.items()
                     if k in ("name","age","gender","height_cm","weight_kg",
                              "target_weight_kg","goal","activity_level",
                              "gym_experience","workout_split","sleep_hours",
                              "allergies","diet_type") and v}

    try:
        db   = SessionLocal()
        auth = AuthService(db)

        if update_fields:
            updated = auth.save_profile_and_recalculate(uid, **update_fields)
        else:
            # Just fetch current profile + recalculate macros
            from app.storage.user_store import UserStore
            updated = UserStore(db).get_by_id(uid)
            result_obj = MacroCalculator.calculate_targets(
                weight_kg      = updated.weight_kg,
                height_cm      = updated.height_cm,
                age            = updated.age,
                gender         = updated.gender,
                activity_level = updated.activity_level,
                goal           = updated.goal,
            )
            from app.storage.user_store import UserStore
            UserStore(db).update_macros(
                uid,
                bmr=result_obj.bmr, tdee=result_obj.tdee,
                target_calories=result_obj.target_calories,
                protein_target_g=result_obj.protein_g,
                carbs_target_g=result_obj.carbs_g,
                fat_target_g=result_obj.fat_g,
                water_target_liters=result_obj.water_liters,
            )

        db.close()
        new_profile = {
            "name": updated.name, "age": updated.age,
            "gender": updated.gender, "weight_kg": updated.weight_kg,
            "target_weight_kg": updated.target_weight_kg,
            "goal": updated.goal, "activity_level": updated.activity_level,
            "gym_experience": updated.gym_experience,
            "target_calories": updated.target_calories,
            "protein_target_g": updated.protein_target_g,
            "carbs_target_g": updated.carbs_target_g,
            "fat_target_g": updated.fat_target_g,
            "bmr": updated.bmr, "tdee": updated.tdee,
            "water_target_liters": updated.water_target_liters,
        }
        return {**state, "profile_result": new_profile,
                "user_profile": new_profile, "error": ""}

    except Exception as e:
        return {**state, "profile_result": {}, "error": f"profile: {e}"}
