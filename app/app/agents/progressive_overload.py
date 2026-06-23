"""
Progressive Overload Agent
--------------------------
Analyses the last 2 weeks of workout logs and recommends weight/volume
progressions for each exercise.
"""

import json
from typing import Optional
from app.agents.base import BaseAgent, extract_json

SYSTEM_PROMPT = """You are an expert strength coach AI specializing in progressive overload programming.

Analyse the provided workout history and recommend specific progressions for next week.
Rules:
1. Return ONLY valid JSON — no prose, no markdown fences.
2. For each exercise evaluate: strength trend, consistency, stall detection.
3. Recommendations must be specific: exact weights, exact rep targets.
4. Stalled lift = same weight × same reps for 2+ consecutive sessions.
5. Ready to progress = hit top of rep range on all sets for 2 sessions.
6. Deload signal = form breakdown, reps dropping, or 4+ week plateau.

Return this exact structure:
{
  "recommendations": [
    {
      "exercise": "Bench Press",
      "current_weight_kg": 60,
      "current_reps": "10,10,8,7",
      "status": "ready_to_progress",
      "next_weight_kg": 62.5,
      "next_reps_target": "8-10",
      "reasoning": "Hit 10 reps on 2 of 4 sets consistently. Increase by 2.5kg."
    }
  ],
  "overall_assessment": "...",
  "weekly_volume_change": "+5%",
  "deload_needed": false,
  "deload_reason": ""
}"""


class ProgressiveOverloadAgent(BaseAgent):

    def analyse(self, exercise_history: dict[str, list[dict]]) -> dict:
        """
        Analyse workout history and return progression recommendations.

        Args:
            exercise_history: {
                "bench press": [
                    {"date": "2024-01-01", "set": 1, "weight_kg": 60, "reps": 10},
                    ...
                ],
                ...
            }

        Returns:
            dict with recommendations list and overall assessment.
        """
        if not exercise_history:
            return {
                "recommendations": [],
                "overall_assessment": "No workout data found. Log your workouts to get progressive overload recommendations.",
                "weekly_volume_change": "0%",
                "deload_needed": False,
                "deload_reason": "",
            }

        # Format history for prompt
        history_lines = []
        for exercise, sets in exercise_history.items():
            history_lines.append(f"\n{exercise.title()}:")
            # Group by date
            by_date: dict[str, list] = {}
            for s in sets:
                by_date.setdefault(s["date"], []).append(s)
            for date_str, date_sets in sorted(by_date.items()):
                reps_str = ", ".join(str(s["reps"]) for s in date_sets)
                weight = date_sets[0]["weight_kg"] if date_sets else 0
                history_lines.append(
                    f"  {date_str}: {weight}kg × [{reps_str}]"
                )

        history_text = "\n".join(history_lines)

        user_message = f"""Analyse this workout history from the last 2 weeks and provide progressive overload recommendations:

{history_text}

Provide specific weight and rep recommendations for next week's training session."""

        raw = self._call(SYSTEM_PROMPT, user_message, max_tokens=2048)

        try:
            return extract_json(raw)
        except ValueError:
            return {
                "recommendations": [],
                "overall_assessment": raw[:500],
                "weekly_volume_change": "N/A",
                "deload_needed": False,
                "deload_reason": "",
            }
