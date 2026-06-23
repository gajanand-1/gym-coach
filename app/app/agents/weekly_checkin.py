"""
Weekly Check-In Agent
---------------------
Analyses all data from the past 7 days and produces an adjustment report.
"""

import json
from typing import Optional
from app.agents.base import BaseAgent, extract_json

SYSTEM_PROMPT = """You are an expert fitness coach AI conducting a weekly progress check-in.

Analyse all the data provided and produce a comprehensive adjustment report.
Rules:
1. Return ONLY valid JSON — no prose, no markdown fences.
2. Base all recommendations on the actual data provided.
3. Calorie adjustments: ±100-200 kcal based on weight trend vs target rate.
4. For fat loss: target -0.5 to -0.75 kg/week. If losing faster → increase calories.
5. For muscle gain: target +0.25 to +0.5 kg/week. If not gaining → increase calories.
6. Protein should never drop below 1.8g/kg bodyweight.
7. Be specific and actionable in all recommendations.

Return this exact structure:
{
  "weight_analysis": {
    "start_weight": 0,
    "current_weight": 0,
    "change_kg": 0,
    "weekly_rate_kg": 0,
    "target_rate_kg": -0.5,
    "on_track": true,
    "summary": "..."
  },
  "nutrition_analysis": {
    "avg_daily_calories": 0,
    "avg_daily_protein": 0,
    "compliance_pct": 0,
    "summary": "..."
  },
  "training_analysis": {
    "sessions_completed": 0,
    "sessions_planned": 0,
    "compliance_pct": 0,
    "summary": "..."
  },
  "sleep_analysis": {
    "avg_hours": 0,
    "quality_score": 0,
    "summary": "..."
  },
  "adjustments": {
    "calorie_change": 0,
    "new_daily_calories": 0,
    "protein_change": 0,
    "new_protein_target": 0,
    "cardio_recommendation": "...",
    "volume_recommendation": "..."
  },
  "subjective_scores": {
    "energy": 0,
    "hunger": 0,
    "sleep_quality": 0,
    "recovery": 0
  },
  "weekly_summary": "...",
  "top_priorities_next_week": ["...", "...", "..."]
}"""


class WeeklyCheckInAgent(BaseAgent):

    def analyse(
        self,
        # User metrics
        current_weight_kg: float,
        target_weight_kg: float,
        goal: str,
        current_calories_target: float,
        current_protein_target: float,
        # Subjective scores (1-10)
        energy_level: int,
        hunger_level: int,
        sleep_quality: int,
        recovery_quality: int,
        # Weekly data summaries
        food_log_summary: list[dict],       # [{date, calories, protein, carbs, fat}]
        weight_log: list[dict],             # [{date, weight_kg}]
        workout_log_summary: list[dict],    # [{date, session_name, volume_kg}]
        sleep_log: list[dict],              # [{date, hours, quality}]
    ) -> dict:
        """Run the weekly check-in analysis and return structured report."""

        # Format data for prompt
        food_summary = "\n".join(
            f"  {d['date']}: {d.get('calories',0):.0f} kcal, "
            f"{d.get('protein',0):.0f}g protein"
            for d in food_log_summary
        ) or "  No food logs this week."

        weight_summary = "\n".join(
            f"  {d['date']}: {d['weight_kg']}kg" for d in weight_log
        ) or "  No weight logs this week."

        workout_summary = "\n".join(
            f"  {d['date']}: {d.get('session_name','Unknown')} "
            f"(volume: {d.get('total_volume_kg',0):.0f}kg)"
            for d in workout_log_summary
        ) or "  No workouts logged this week."

        sleep_summary = "\n".join(
            f"  {d['date']}: {d['hours']}h ({d.get('quality','?')})"
            for d in sleep_log
        ) or "  No sleep logs this week."

        user_message = f"""Weekly Check-In Data:

GOAL: {goal.replace('_', ' ').upper()}
Current Weight: {current_weight_kg}kg → Target: {target_weight_kg}kg
Current Targets: {current_calories_target:.0f} kcal/day, {current_protein_target:.0f}g protein/day

SUBJECTIVE SCORES (1-10):
  Energy Level: {energy_level}
  Hunger Level: {hunger_level}
  Sleep Quality: {sleep_quality}
  Recovery Quality: {recovery_quality}

FOOD LOG (last 7 days):
{food_summary}

WEIGHT LOG:
{weight_summary}

WORKOUTS:
{workout_summary}

SLEEP:
{sleep_summary}

Please analyse all data and provide a comprehensive adjustment report."""

        raw = self._call(SYSTEM_PROMPT, user_message, max_tokens=3000)

        try:
            return extract_json(raw)
        except ValueError:
            return {
                "weight_analysis": {"summary": "Unable to parse. Please check logs."},
                "nutrition_analysis": {"summary": raw[:300]},
                "training_analysis": {"summary": ""},
                "sleep_analysis": {"summary": ""},
                "adjustments": {
                    "calorie_change": 0,
                    "new_daily_calories": current_calories_target,
                    "protein_change": 0,
                    "new_protein_target": current_protein_target,
                    "cardio_recommendation": "Maintain current cardio.",
                    "volume_recommendation": "Maintain current training volume.",
                },
                "subjective_scores": {
                    "energy": energy_level,
                    "hunger": hunger_level,
                    "sleep_quality": sleep_quality,
                    "recovery": recovery_quality,
                },
                "weekly_summary": raw[:500],
                "top_priorities_next_week": ["Track food consistently", "Sleep 7-8 hours", "Stay hydrated"],
            }
