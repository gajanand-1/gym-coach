"""
AI Coach Chat Agent
-------------------
A conversational personal trainer / nutritionist with full context access.
"""

from typing import Optional
from app.agents.base import BaseAgent

SYSTEM_TEMPLATE = """You are an expert AI Personal Fitness Coach named "CoachAI".

You have access to the user's complete fitness data and must use it in every response.
Your role combines: Personal Trainer + Nutritionist + Progress Coach.

COMMUNICATION STYLE:
- Be direct, motivating, and specific.
- Always reference the user's actual data when answering.
- Give actionable recommendations, not generic advice.
- Keep responses concise but complete (200-400 words max unless a detailed plan is requested).
- Use emojis sparingly for readability.

USER PROFILE:
{profile}

TODAY'S STATS:
{today_stats}

RECENT DATA CONTEXT:
{recent_context}

ACTIVE PLANS:
{active_plans}

When the user asks about:
- Food/nutrition → check today's logs vs targets, give specific meal suggestions
- Workouts → reference their plan and recent performance
- Weight → analyse their trend data
- "Why isn't weight dropping" → analyse calorie adherence, NEAT, water retention
- Progressive overload → check their specific lift history
- Supplements → give evidence-based advice

Always sign off with one specific actionable tip for today."""


class CoachChatAgent(BaseAgent):

    def __init__(self):
        super().__init__()

    def chat(
        self,
        user_message: str,
        chat_history: list[dict],
        # Context injected from stores
        user_profile: dict,
        today_food_totals: dict,
        today_water: dict,
        recent_weight: list[dict],
        active_diet_plan: Optional[dict],
        active_workout_plan: Optional[dict],
        recent_workouts: list[dict],
        sleep_avg: float,
    ) -> str:
        """
        Send a message to the coach and get a contextual response.

        Args:
            user_message:       Current user message.
            chat_history:       List of {"role": ..., "content": ...} dicts.
            user_profile:       User's profile dict.
            today_food_totals:  {calories, protein, carbs, fat}.
            today_water:        {consumed_liters, target_liters}.
            recent_weight:      Last 7 weight entries [{date, weight_kg}].
            active_diet_plan:   Current meal plan dict or None.
            active_workout_plan: Current workout plan dict or None.
            recent_workouts:    Last 3 workout sessions.
            sleep_avg:          Average sleep hours past 7 days.

        Returns:
            Coach's text response.
        """
        # Build profile section
        profile_lines = [
            f"Name: {user_profile.get('name', 'User')}",
            f"Age: {user_profile.get('age', '?')} | Gender: {user_profile.get('gender', '?')}",
            f"Weight: {user_profile.get('weight_kg', '?')}kg | Target: {user_profile.get('target_weight_kg', '?')}kg",
            f"Goal: {user_profile.get('goal', '?').replace('_', ' ').title()}",
            f"Targets: {user_profile.get('target_calories', 0):.0f} kcal | "
            f"{user_profile.get('protein_target_g', 0):.0f}g protein",
            f"Split: {user_profile.get('workout_split', '?').replace('_', ' ').title()}",
            f"Experience: {user_profile.get('gym_experience', '?').title()}",
        ]

        # Build today's stats
        cal_remaining = user_profile.get("target_calories", 0) - today_food_totals.get("calories", 0)
        pro_remaining = user_profile.get("protein_target_g", 0) - today_food_totals.get("protein", 0)
        water_remaining = today_water.get("target_liters", 3.5) - today_water.get("consumed_liters", 0)
        today_lines = [
            f"Calories consumed: {today_food_totals.get('calories', 0):.0f} kcal "
            f"(remaining: {cal_remaining:.0f})",
            f"Protein consumed: {today_food_totals.get('protein', 0):.0f}g "
            f"(remaining: {pro_remaining:.0f}g)",
            f"Water: {today_water.get('consumed_liters', 0):.1f}L "
            f"(need {water_remaining:.1f}L more)",
            f"Average sleep (7d): {sleep_avg:.1f}h",
        ]

        # Build recent context
        context_lines = []
        if recent_weight:
            latest = recent_weight[-1]
            context_lines.append(f"Latest weight: {latest.get('weight_kg', '?')}kg on {latest.get('date', '?')}")
            if len(recent_weight) >= 2:
                change = recent_weight[-1]["weight_kg"] - recent_weight[0]["weight_kg"]
                context_lines.append(f"Weight change (7d): {change:+.1f}kg")

        if recent_workouts:
            last_workout = recent_workouts[0] if recent_workouts else None
            if last_workout:
                context_lines.append(
                    f"Last workout: {last_workout.get('session_name', '?')} "
                    f"on {last_workout.get('log_date', '?')}"
                )

        # Build active plans summary
        plan_lines = []
        if active_diet_plan:
            plan_lines.append("Active diet plan: YES (7-day meal plan available)")
        else:
            plan_lines.append("Active diet plan: NONE (recommend generating one)")

        if active_workout_plan:
            plan_lines.append(
                f"Active workout plan: {active_workout_plan.get('split_type', '?').replace('_', ' ').title()}"
            )
        else:
            plan_lines.append("Active workout plan: NONE")

        system = SYSTEM_TEMPLATE.format(
            profile="\n".join(profile_lines),
            today_stats="\n".join(today_lines),
            recent_context="\n".join(context_lines) or "No recent data.",
            active_plans="\n".join(plan_lines),
        )

        # Build message history (last 10 exchanges to stay within context)
        messages = []
        for msg in chat_history[-20:]:
            role = msg.get("role", "user")
            if role in ("user", "assistant"):
                messages.append({"role": role, "content": msg["content"]})

        # Add current message
        messages.append({"role": "user", "content": user_message})

        return self._call_with_history(system, messages, max_tokens=1024)
