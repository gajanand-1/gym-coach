"""
User Profile Agent Node
-----------------------
Collects or updates the user's profile via a conversational LLM prompt.
On first run it asks for every field; on subsequent runs it merges updates.
Persists the profile to USER_PROFILE_FILE.
"""

from __future__ import annotations

import json
from langchain_core.messages import SystemMessage, HumanMessage

from config import USER_PROFILE_FILE
from state  import GymCoachState
from utils  import get_llm, load_json, save_json


SYSTEM_PROMPT = """
You are a friendly fitness onboarding assistant.

Your job is to collect or update a user's fitness profile. Extract the following
fields from the user's message and return ONLY a valid JSON object — no prose,
no markdown fences, just raw JSON.

Fields to extract (use null if not mentioned):
{
  "name":                <string>,
  "age":                 <int>,
  "gender":              <"male"|"female"|"other">,
  "height_cm":           <float>,
  "weight_kg":           <float>,
  "target_weight_kg":    <float>,
  "goal":                <"fat_loss"|"muscle_gain"|"maintenance">,
  "activity_level":      <"sedentary"|"light"|"moderate"|"active"|"very_active">,
  "diet_type":           <"vegetarian"|"non_vegetarian"|"vegan"|"eggetarian">,
  "monthly_budget_inr":  <float>,
  "gym_experience":      <"beginner"|"intermediate"|"advanced">,
  "allergies":           <list[string]>,
  "cooking_facilities":  <list[string]>,
  "sleep_hours":         <float>
}

If a field is genuinely absent from the user message output null for it.
Merge with existing data — never overwrite known fields with null.
""".strip()


def profile_agent_node(state: GymCoachState) -> dict:
    """LangGraph node: parse / update user profile."""
    llm         = get_llm(temperature=0.1)
    user_input  = state.get("user_input", "")
    existing    = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Existing profile:\n{json.dumps(existing, indent=2)}\n\n"
            f"User message:\n{user_input}"
        )),
    ]

    raw = llm.invoke(messages).content.strip()

    # ── parse LLM response ────────────────────────────────────────────────────
    try:
        updates = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON substring in case of extra text
        start, end = raw.find("{"), raw.rfind("}") + 1
        try:
            updates = json.loads(raw[start:end])
        except Exception:
            return {
                "agent_response": f"⚠️  Could not parse profile update. Raw response:\n{raw}",
                "error": "profile_parse_error",
            }

    # ── merge: existing wins over null ────────────────────────────────────────
    merged = {**existing}
    for k, v in updates.items():
        if v is not None:
            merged[k] = v

    save_json(USER_PROFILE_FILE, merged)

    # ── build a human-readable confirmation ──────────────────────────────────
    lines = ["✅  Profile saved!\n"]
    label_map = {
        "name":               "Name",
        "age":                "Age",
        "gender":             "Gender",
        "height_cm":          "Height",
        "weight_kg":          "Weight",
        "target_weight_kg":   "Target Weight",
        "goal":               "Goal",
        "activity_level":     "Activity Level",
        "diet_type":          "Diet Type",
        "monthly_budget_inr": "Monthly Budget",
        "gym_experience":     "Gym Experience",
        "allergies":          "Allergies",
        "sleep_hours":        "Sleep (hrs)",
    }
    for key, label in label_map.items():
        val = merged.get(key)
        if val is not None:
            if key == "height_cm":
                val = f"{val} cm"
            elif key in ("weight_kg", "target_weight_kg"):
                val = f"{val} kg"
            elif key == "monthly_budget_inr":
                val = f"₹{val:,.0f}"
            elif key == "sleep_hours":
                val = f"{val} hrs"
            lines.append(f"  {label:<20}: {val}")

    missing = [k for k in label_map if merged.get(k) is None]
    if missing:
        lines.append(
            f"\n⚠️  Still missing: {', '.join(missing)}\n"
            "   Tell me these to complete your profile."
        )

    return {
        "user_profile":  merged,
        "agent_response": "\n".join(lines),
    }
