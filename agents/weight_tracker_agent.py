"""
Body Weight Tracking Agent Node
--------------------------------
Records today's weight, computes a 7-day trend, predicts goal completion,
and optionally generates an ASCII trend chart.
"""

from __future__ import annotations

import re
from datetime import date

from config import WEIGHT_LOG_FILE, USER_PROFILE_FILE
from state  import GymCoachState, WeightEntry
from utils  import load_json, save_json


def _ascii_chart(weights: list[float], width: int = 40) -> str:
    """Minimal ASCII line chart."""
    if len(weights) < 2:
        return ""
    lo, hi = min(weights), max(weights)
    span   = hi - lo or 1
    lines  = []
    for w in weights[-width:]:
        bar_len = int(((w - lo) / span) * 20)
        bar     = "█" * bar_len
        lines.append(f"  {w:5.1f} │{bar}")
    return "\n".join(lines)


def _predict_goal_weeks(current: float, target: float, trend: list[float]) -> str:
    """Estimate weeks to goal based on recent trend."""
    if len(trend) < 2:
        return "Need more data for prediction."
    recent = trend[-min(7, len(trend)):]
    weekly_change = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
    if abs(weekly_change) < 0.05:
        return "Weight is stable — adjust calories to resume progress."
    weeks_needed = (target - current) / weekly_change
    if weeks_needed < 0:
        return "You've already passed your target weight — update your goal!"
    return f"At current pace: ~{weeks_needed:.0f} weeks to reach {target} kg."


def weight_tracker_node(state: GymCoachState) -> dict:
    """LangGraph node: log weight, show trend, predict goal date."""

    user_input = state.get("user_input", "")
    today      = date.today().isoformat()

    # ── Extract weight from user input (e.g. "81.5" or "81.5kg") ─────────────
    match = re.search(r"(\d{2,3}(?:\.\d{1,2})?)", user_input)
    if not match:
        return {
            "agent_response": (
                "⚠️  Please tell me your weight, e.g. 'Weight today: 81.5 kg'"
            )
        }

    weight_today = float(match.group(1))

    # ── Load existing log ─────────────────────────────────────────────────────
    log: list[WeightEntry] = load_json(WEIGHT_LOG_FILE, default=[])

    # Update today's entry if it already exists
    existing_today = next((e for e in log if e["date"] == today), None)
    if existing_today:
        existing_today["weight_kg"] = weight_today
    else:
        log.append({"date": today, "weight_kg": weight_today})

    save_json(WEIGHT_LOG_FILE, log)

    weights = [e["weight_kg"] for e in log]
    trend   = weights[-14:]   # last 2 weeks

    # ── Profile for goal context ──────────────────────────────────────────────
    profile = state.get("user_profile") or load_json(USER_PROFILE_FILE, default={})
    target  = profile.get("target_weight_kg")

    # ── Build response ────────────────────────────────────────────────────────
    lines = [
        f"⚖️   Weight logged: {weight_today} kg  ({today})",
        "",
        "📊  Recent Trend:",
    ]

    if len(trend) >= 2:
        change = trend[-1] - trend[0]
        arrow  = "📉" if change < 0 else "📈"
        lines.append(
            f"  {arrow}  {trend[0]:.1f} kg  →  {trend[-1]:.1f} kg  "
            f"({'−' if change < 0 else '+'}{abs(change):.1f} kg "
            f"over {len(trend)} days)"
        )
        lines.append("")
        lines.append(_ascii_chart(trend))
    else:
        lines.append("  (Log more days to see a trend)")

    if target:
        diff = weight_today - float(target)
        lines.append(f"\n🎯  Target: {target} kg  |  Remaining: {abs(diff):.1f} kg")
        lines.append(f"   {_predict_goal_weeks(weight_today, float(target), trend)}")

    return {
        "weight_log":    [{"date": today, "weight_kg": weight_today}],
        "weight_trend":  trend,
        "agent_response": "\n".join(lines),
    }
