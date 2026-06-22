"""
Macro Calculator Service
------------------------
All BMR / TDEE / target macro calculations in one place.
"""

from dataclasses import dataclass


ACTIVITY_MULTIPLIERS = {
    "sedentary":   1.2,    # Little or no exercise
    "light":       1.375,  # Light exercise 1-3 days/week
    "moderate":    1.55,   # Moderate exercise 3-5 days/week
    "active":      1.725,  # Hard exercise 6-7 days/week
    "very_active": 1.9,    # Very hard exercise + physical job
}

GOAL_CALORIE_ADJUSTMENTS = {
    "fat_loss":    -500,   # 500 kcal deficit → ~0.5 kg/week loss
    "muscle_gain": +300,   # 300 kcal surplus → lean bulk
    "maintenance":   0,
}

# Protein targets (g/kg bodyweight)
PROTEIN_TARGETS = {
    "fat_loss":    2.2,    # High protein to preserve muscle in deficit
    "muscle_gain": 2.0,
    "maintenance": 1.8,
}


@dataclass
class MacroResult:
    bmr: float
    tdee: float
    target_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    water_liters: float


class MacroCalculator:

    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float,
                      age: int, gender: str) -> float:
        """
        Mifflin-St Jeor equation.
        Male:   BMR = 10W + 6.25H - 5A + 5
        Female: BMR = 10W + 6.25H - 5A - 161
        """
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
        if gender.lower() == "male":
            bmr += 5
        else:
            bmr -= 161
        return round(bmr, 1)

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
        return round(bmr * multiplier, 1)

    @classmethod
    def calculate_targets(
        cls,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
        activity_level: str,
        goal: str,
    ) -> MacroResult:
        bmr = cls.calculate_bmr(weight_kg, height_cm, age, gender)
        tdee = cls.calculate_tdee(bmr, activity_level)

        calorie_adj = GOAL_CALORIE_ADJUSTMENTS.get(goal, 0)
        target_calories = max(1200, tdee + calorie_adj)  # Floor at 1200 kcal

        protein_per_kg = PROTEIN_TARGETS.get(goal, 2.0)
        protein_g = round(weight_kg * protein_per_kg, 1)

        # Fat: 25% of calories
        fat_g = round((target_calories * 0.25) / 9, 1)

        # Carbs: fill remaining calories
        protein_cal = protein_g * 4
        fat_cal = fat_g * 9
        carb_cal = max(0, target_calories - protein_cal - fat_cal)
        carbs_g = round(carb_cal / 4, 1)

        # Water: 35ml/kg bodyweight
        water_liters = round(weight_kg * 0.035, 1)

        return MacroResult(
            bmr=bmr,
            tdee=tdee,
            target_calories=round(target_calories, 1),
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            water_liters=water_liters,
        )

    @staticmethod
    def estimate_goal_date(
        current_weight: float,
        target_weight: float,
        weekly_rate_kg: float = 0.5,
    ) -> str:
        """Estimate weeks to reach target weight."""
        from datetime import date, timedelta
        diff = abs(current_weight - target_weight)
        if weekly_rate_kg <= 0 or diff == 0:
            return "N/A"
        weeks = diff / weekly_rate_kg
        eta = date.today() + timedelta(weeks=weeks)
        return eta.strftime("%d %b %Y")

    @staticmethod
    def calories_from_macros(protein_g: float, carbs_g: float, fat_g: float) -> float:
        return round(protein_g * 4 + carbs_g * 4 + fat_g * 9, 1)

    @staticmethod
    def macro_split_percentages(protein_g: float, carbs_g: float,
                                fat_g: float) -> dict:
        total_cal = protein_g * 4 + carbs_g * 4 + fat_g * 9
        if total_cal == 0:
            return {"protein_pct": 0, "carbs_pct": 0, "fat_pct": 0}
        return {
            "protein_pct": round(protein_g * 4 / total_cal * 100, 1),
            "carbs_pct": round(carbs_g * 4 / total_cal * 100, 1),
            "fat_pct": round(fat_g * 9 / total_cal * 100, 1),
        }
