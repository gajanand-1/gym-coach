"""
Workout Planning Agent
----------------------
Generates a detailed weekly gym programme tailored to the user's
experience level, goal, and chosen split style.
Falls back to exercise_db data if the AI response cannot be parsed.
"""

from typing import Optional
from app.agents.base import BaseAgent, extract_json
from data.exercise_db import get_exercises_for_split

SYSTEM_PROMPT = """You are an elite strength and conditioning coach AI.

Generate a detailed 7-day gym workout plan in strict JSON format.
Rules:
1. Return ONLY valid JSON — no prose, no markdown fences.
2. Each workout day must include: session name, exercises list.
3. Each exercise must include: name, sets (int), reps (string), rest_seconds (int), notes (string).
4. Rest days must still appear as {"session": "Rest", "exercises": []}.
5. For beginners: focus on compound movements, 3-4 sets, moderate reps (8-12).
6. For intermediate: add isolation work, 4 sets, varied rep ranges.
7. For advanced: high volume, periodisation notes, strength and hypertrophy blocks.
8. Goal adjustments:
   - fat_loss: add cardio notes, supersets suggested
   - muscle_gain: higher volume, progressive overload cues
   - maintenance: balanced volume

Return this exact structure:
{
  "Monday":    {"session": "Push Day A", "exercises": [{"name":"Bench Press","sets":4,"reps":"8-10","rest_seconds":120,"notes":"..."}]},
  "Tuesday":   {"session": "Pull Day A", "exercises": [...]},
  "Wednesday": {"session": "Legs Day A", "exercises": [...]},
  "Thursday":  {"session": "Rest", "exercises": []},
  "Friday":    {"session": "Push Day B", "exercises": [...]},
  "Saturday":  {"session": "Pull Day B", "exercises": [...]},
  "Sunday":    {"session": "Legs Day B / Rest", "exercises": [...]}
}"""


class WorkoutPlannerAgent(BaseAgent):

    def generate_plan(
        self,
        split_type: str = "push_pull_legs",
        experience: str = "beginner",
        goal: str = "fat_loss",
        current_weight_kg: float = 80,
        age: int = 22,
        gender: str = "male",
    ) -> dict:
        """
        Generate a weekly workout plan.
        Falls back to exercise_db defaults if Claude response is unparseable.
        """
        user_message = f"""Generate a 7-day workout plan with these parameters:
- Split: {split_type.replace('_', ' ').title()}
- Experience Level: {experience.title()}
- Goal: {goal.replace('_', ' ').title()}
- Athlete: {age} year old {gender}, {current_weight_kg}kg

Include warm-up notes, progressive overload cues, and form tips in the exercise notes.
Structure the plan for maximum results given the {experience} level and {goal} goal.
Return the complete plan in the specified JSON format."""

        raw = self._call(SYSTEM_PROMPT, user_message, max_tokens=4096)

        try:
            result = extract_json(raw)
            # Validate structure — ensure all 7 days present
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if all(d in result for d in days):
                return result
        except ValueError:
            pass

        # Fallback to exercise_db
        return self._db_fallback(split_type, experience)

    def _db_fallback(self, split_type: str, experience: str) -> dict:
        """Build plan directly from exercise_db without Claude."""
        base = get_exercises_for_split(split_type, experience)
        result = {}
        for day, data in base.items():
            result[day] = {
                "session": data["session"],
                "exercises": [
                    {
                        "name": ex["name"],
                        "sets": ex["sets"],
                        "reps": str(ex["reps"]),
                        "rest_seconds": ex["rest_sec"],
                        "notes": f"Focus on form. Muscle: {ex['muscle_group']}",
                    }
                    for ex in data["exercises"]
                ],
            }
        return result
