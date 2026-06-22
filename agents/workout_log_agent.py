"""
Workout Logging + Progressive Overload Agent Node
--------------------------------------------------
Parses a natural-language workout log entry, persists it,
then compares with last week's performance to generate progressive
overload recommendations.

Example input:
  "Bench Press 60kg: 10, 10, 8, 7
   Shoulder Press 40kg: 12, 12, 10"
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from langchain_core.messages import SystemMessage, HumanMessage

from config import WORKOUT_LOG_FILE
from state  import GymCoachState, WorkoutLogEntry, ProgressiveOverloadSuggestion
from utils  import get_llm, load_json, save_json


PARSE_PROMPT = """
You are a workout logging assistant.

Parse the user's workout description into a JSON array of exercise entries.
Return ONLY a valid JSON array — no prose, no markdown.

Schema per exercise:
{
  "exercise": "bench_press",        <- snake_case, lowercase
  "weight_kg": 60,
  "reps": [10, 10, 8, 7],
  "notes": ""
}

If weight is not mentioned, use 0.
If it's a bodyweight exercise, use 0 for weight_kg.
""".strip()


def _snake(name: str) -> str:
    return name.lower().replace(" ", "_")


def _progressive_overload_advice(
    exercise: str,
    prev_entry: dict | None,
    cur_weight: float,
    cur_reps: list[int],
) -> str:
    """Rule-based overload recommendation."""
    if not prev_entry:
        return "First recorded session — keep notes and aim to beat this next week!"

    prev_weight = prev_entry.get("weight_kg", 0)
    prev_reps   = prev_entry.get("reps", [])

    if not prev_reps:
        return "No previous rep data found."

    prev_avg = sum(prev_reps) / len(prev_reps)
    cur_avg  = sum(cur_reps)  / len(cur_reps) if cur_reps else 0

    # Same weight — check if reps improved enough to add weight
    if cur_weight == prev_weight:
        if cur_avg >= prev_avg + 1.5:
            increment = 2.5 if cur_weight >= 40 else 1.25
            return (
                f"Great progress! Reps improved from avg {prev_avg:.1f} → {cur_avg:.1f}. "
                f"Increase weight to {cur_weight + increment:.2g} kg next week. 🔺"
            )
        elif cur_avg < prev_avg - 1:
            return (
                f"Performance dipped (avg {prev_avg:.1f} → {cur_avg:.1f}). "
                "Prioritise sleep & nutrition. Keep same weight next week."
            )
        else:
            return (
                f"Consistent performance (avg {prev_avg:.1f} → {cur_avg:.1f}). "
                "Try to squeeze out 1 more rep per set next week."
            )
    # Weight already increased
    elif cur_weight > prev_weight:
        return (
            f"Weight increased {prev_weight} kg → {cur_weight} kg. "
            "Good overload! Aim to match last week's rep count at this new weight."
        )
    else:
        return (
            f"Weight decreased {prev_weight} kg → {cur_weight} kg. "
            "That's fine for a deload. Plan to return to {prev_weight} kg next session."
        )


def workout_log_node(state: GymCoachState) -> dict:
    """LangGraph node: log workout + generate overload suggestions."""

    llm        = get_llm(temperature=0.1)
    user_input = state.get("user_input", "")
    today      = date.today().isoformat()

    # ── Step 1: Parse workout from natural language ───────────────────────────
    messages = [
        SystemMessage(content=PARSE_PROMPT),
        HumanMessage(content=user_input),
    ]
    raw = llm.invoke(messages).content.strip()

    try:
        exercises = json.loads(raw)
    except json.JSONDecodeError:
        s, e = raw.find("["), raw.rfind("]") + 1
        try:
            exercises = json.loads(raw[s:e])
        except Exception:
            return {
                "agent_response": f"⚠️  Could not parse your workout.\n{raw}",
                "error": "workout_log_parse_error",
            }

    # ── Step 2: Build log entries & persist ───────────────────────────────────
    all_logs: list = load_json(WORKOUT_LOG_FILE, default=[])

    new_entries: list[WorkoutLogEntry] = []
    for ex in exercises:
        entry: WorkoutLogEntry = {
            "date":       today,
            "exercise":   _snake(ex.get("exercise", "unknown")),
            "sets": [
                {"weight_kg": float(ex.get("weight_kg", 0)), "reps": ex.get("reps", [])}
            ],
            "notes": ex.get("notes", ""),
        }
        new_entries.append(entry)
        all_logs.append(entry)

    save_json(WORKOUT_LOG_FILE, all_logs)

    # ── Step 3: Progressive overload analysis ─────────────────────────────────
    one_week_ago = (date.today() - timedelta(days=7)).isoformat()

    # Index previous week logs by exercise
    prev_week: dict[str, dict] = {}
    for log in all_logs:
        if log.get("date", "") >= one_week_ago and log.get("date", "") < today:
            ex_name = log["exercise"]
            if ex_name not in prev_week:
                prev_week[ex_name] = log

    suggestions: list[ProgressiveOverloadSuggestion] = []
    overload_lines = ["\n📈  Progressive Overload Report\n" + "─" * 45]

    for entry in new_entries:
        ex_name    = entry["exercise"]
        cur_weight = entry["sets"][0]["weight_kg"]
        cur_reps   = entry["sets"][0]["reps"]
        prev       = prev_week.get(ex_name)

        advice = _progressive_overload_advice(ex_name, prev, cur_weight, cur_reps)
        suggestions.append({
            "exercise":           ex_name,
            "previous_weight_kg": prev["sets"][0]["weight_kg"] if prev else 0,
            "previous_reps":      prev["sets"][0]["reps"]      if prev else [],
            "current_weight_kg":  cur_weight,
            "current_reps":       cur_reps,
            "recommendation":     advice,
        })
        overload_lines.append(f"  🏋️  {ex_name.replace('_', ' ').title()}")
        if prev:
            overload_lines.append(
                f"     Last week : {prev['sets'][0]['weight_kg']} kg × "
                f"{prev['sets'][0]['reps']}"
            )
        overload_lines.append(
            f"     This week : {cur_weight} kg × {cur_reps}"
        )
        overload_lines.append(f"     💡 {advice}\n")

    # ── Format full response ──────────────────────────────────────────────────
    log_lines = [f"✅  Workout Logged — {today}\n" + "═" * 45]
    for entry in new_entries:
        w = entry["sets"][0]["weight_kg"]
        r = entry["sets"][0]["reps"]
        log_lines.append(
            f"  • {entry['exercise'].replace('_', ' ').title():<28}"
            f"  {w} kg  ×  {r}"
        )

    response = "\n".join(log_lines) + "\n" + "\n".join(overload_lines)

    return {
        "workout_log":           new_entries,
        "overload_suggestions":  suggestions,
        "agent_response":        response,
    }
