"""
Diet Planning Agent
-------------------
Generates a full 7-day non-vegetarian meal plan tailored to the user's
goals, macros, and available mess menu items.
"""

import json
from typing import Optional
from app.agents.base import BaseAgent, extract_json

SYSTEM_PROMPT = """You are an expert sports nutritionist AI specializing in high-protein non-vegetarian meal plans for Indian gym-goers.

Generate a complete 7-day meal plan in strict JSON format. Follow these rules:
1. Return ONLY valid JSON — no prose, no markdown fences.
2. Every meal must include breakfast, lunch, dinner, and snacks.
3. Each meal entry must have: name, quantity (human-readable), calories, protein, carbs, fat.
4. Prefer high-protein foods: eggs, chicken breast, paneer, dal, fish, whey protein.
5. Use Indian foods and hostel-friendly options where possible.
6. Meet the provided calorie and protein targets (within ±50 kcal / ±5g protein per day).
7. If a mess menu is provided, prioritize those foods and only add extra items to meet targets.

Return this exact structure:
{
  "Monday": {
    "breakfast": [{"name":"...", "quantity":"...", "calories":0, "protein":0, "carbs":0, "fat":0}],
    "lunch":     [...],
    "dinner":    [...],
    "snacks":    [...],
    "daily_total": {"calories":0, "protein":0, "carbs":0, "fat":0}
  },
  "Tuesday": { ... },
  "Wednesday": { ... },
  "Thursday": { ... },
  "Friday": { ... },
  "Saturday": { ... },
  "Sunday": { ... }
}"""


class DietPlannerAgent(BaseAgent):

    def generate_plan(
        self,
        target_calories: float,
        target_protein: float,
        target_carbs: float,
        target_fat: float,
        goal: str = "fat_loss",
        experience: str = "beginner",
        mess_menu: Optional[dict] = None,
        allergies: Optional[list] = None,
    ) -> dict:
        """
        Generate a 7-day meal plan.

        Returns:
            dict with days as keys and meal sub-dicts as values.
        """
        allergies = allergies or []

        mess_context = ""
        if mess_menu:
            lines = ["Available hostel mess menu (use these foods as priority):"]
            for day, meals in mess_menu.items():
                day_items = []
                for meal_type, items in meals.items():
                    if items:
                        items_str = ", ".join(items) if isinstance(items, list) else str(items)
                        day_items.append(f"    {meal_type}: {items_str}")
                if day_items:
                    lines.append(f"  {day}:")
                    lines.extend(day_items)
            mess_context = "\n".join(lines)

        allergy_context = (
            f"Allergies / foods to AVOID: {', '.join(allergies)}" if allergies else ""
        )

        user_message = f"""Generate a 7-day high-protein NON-VEGETARIAN meal plan with these targets:
- Daily Calories: {int(target_calories)} kcal
- Protein: {int(target_protein)}g
- Carbohydrates: {int(target_carbs)}g
- Fat: {int(target_fat)}g
- Goal: {goal.replace('_', ' ').title()}
- Experience level: {experience}
- Diet type: Non-vegetarian (include eggs, chicken, fish, meat)

{mess_context}
{allergy_context}

Return the complete 7-day plan in the specified JSON format."""

        raw = self._call(SYSTEM_PROMPT, user_message, max_tokens=4096)

        try:
            return extract_json(raw)
        except ValueError:
            return self._fallback_plan(target_calories, target_protein)

    def _fallback_plan(self, target_calories: float, target_protein: float) -> dict:
        """Minimal fallback plan if JSON parsing fails."""
        base_meal = [
            {"name": "Oats with milk", "quantity": "80g oats + 200ml milk",
             "calories": 400, "protein": 20, "carbs": 55, "fat": 8},
        ]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return {
            day: {
                "breakfast": base_meal,
                "lunch": [{"name": "Rice + Dal + Chicken", "quantity": "1 serving",
                           "calories": int(target_calories * 0.35),
                           "protein": int(target_protein * 0.35), "carbs": 60, "fat": 15}],
                "dinner": [{"name": "Roti + Chicken + Sabzi", "quantity": "1 serving",
                            "calories": int(target_calories * 0.30),
                            "protein": int(target_protein * 0.30), "carbs": 45, "fat": 12}],
                "snacks": [{"name": "Whey Protein Shake", "quantity": "30g in water",
                            "calories": 120, "protein": 24, "carbs": 3, "fat": 2}],
                "daily_total": {
                    "calories": int(target_calories),
                    "protein": int(target_protein),
                    "carbs": int(target_calories * 0.4 / 4),
                    "fat": int(target_calories * 0.25 / 9),
                },
            }
            for day in days
        }
