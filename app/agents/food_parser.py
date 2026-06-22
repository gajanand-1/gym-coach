"""
Food Parsing Agent
------------------
Parses a natural-language food description into structured macro data.
Optionally cross-references the hostel mess menu for today's meals.
"""

import json
from typing import Optional
from app.agents.base import BaseAgent, extract_json

SYSTEM_PROMPT = """You are a precise nutritionist AI that parses food descriptions into structured JSON.

Given a natural language description of food eaten, extract each food item and calculate its macros.
Use standard Indian food nutrition data where applicable.

IMPORTANT RULES:
1. Return ONLY valid JSON — no prose, no markdown, no code fences.
2. For each food item estimate the quantity in grams if not specified (use typical serving sizes).
3. Calculate macros per 100g then scale to actual quantity.
4. Common Indian unit conversions to use:
   - 1 roti/chapati ≈ 40g
   - 1 medium egg ≈ 55g
   - 1 cup rice (cooked) ≈ 200g
   - 1 cup dal ≈ 200g
   - 1 glass milk ≈ 200ml
   - 1 tbsp ghee ≈ 10g
   - 1 medium banana ≈ 120g

Return this exact JSON structure:
{
  "food_items": [
    {
      "name": "Food Name",
      "quantity_g": 150,
      "unit_description": "1 serving / 2 rotis / 200g",
      "calories": 245,
      "protein": 18.5,
      "carbs": 28.0,
      "fat": 6.5
    }
  ],
  "total_calories": 245,
  "total_protein": 18.5,
  "total_carbs": 28.0,
  "total_fat": 6.5,
  "meal_type": "lunch",
  "confidence": "high",
  "notes": "optional notes about assumptions made"
}"""


class FoodParserAgent(BaseAgent):

    def parse(
        self,
        user_input: str,
        mess_menu_today: Optional[dict] = None,
        meal_type: Optional[str] = None,
    ) -> dict:
        """
        Parse a natural-language food log entry.

        Args:
            user_input:       e.g. "I ate 4 roti, 2 eggs and 200g chicken"
            mess_menu_today:  dict with keys breakfast/lunch/dinner/snacks
                              (injected when user says "I ate lunch")
            meal_type:        override meal type (breakfast/lunch/dinner/snacks)

        Returns:
            Parsed dict with food_items list and total macros.
        """
        context_lines = []

        # Inject mess menu context if available
        if mess_menu_today:
            context_lines.append("Today's hostel mess menu:")
            for meal, items in mess_menu_today.items():
                if items:
                    items_str = ", ".join(items) if isinstance(items, list) else str(items)
                    context_lines.append(f"  {meal.title()}: {items_str}")
            context_lines.append(
                "\nIf the user says they ate a mess meal (e.g. 'I ate lunch'), "
                "use the items listed above for that meal and estimate typical hostel serving sizes."
            )

        if meal_type:
            context_lines.append(f"\nMeal type context: {meal_type}")

        context = "\n".join(context_lines)
        user_message = f"{context}\n\nUser food log: {user_input}" if context else f"User food log: {user_input}"

        raw = self._call(SYSTEM_PROMPT, user_message, max_tokens=2048)

        try:
            result = extract_json(raw)
        except ValueError:
            # Fallback: return zero-macro structure
            result = {
                "food_items": [{"name": user_input, "quantity_g": 0,
                                "unit_description": "unknown",
                                "calories": 0, "protein": 0, "carbs": 0, "fat": 0}],
                "total_calories": 0,
                "total_protein": 0,
                "total_carbs": 0,
                "total_fat": 0,
                "meal_type": meal_type or "general",
                "confidence": "low",
                "notes": f"Could not parse: {raw[:200]}",
            }

        # Ensure meal_type is set
        if meal_type and "meal_type" not in result:
            result["meal_type"] = meal_type

        return result

    def clarify_mess_meal(self, meal_type: str, mess_menu_today: dict) -> str:
        """
        Generate a clarification message listing today's mess items and asking for servings.
        """
        items = mess_menu_today.get(meal_type, [])
        if not items:
            return f"I don't have today's mess {meal_type} menu. Please describe what you ate."

        items_str = "\n".join(f"  • {item}" for item in items)
        return (
            f"Today's mess **{meal_type}** was:\n{items_str}\n\n"
            "How many servings of each did you have? "
            "(If you had a standard serving of everything, just say 'standard' or '1 serving each'.)"
        )
