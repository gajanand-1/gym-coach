"""General-purpose UI helper utilities."""


def format_kg(value: float) -> str:
    return f"{value:.1f} kg"


def format_kcal(value: float) -> str:
    return f"{value:.0f} kcal"


def format_liters(value: float) -> str:
    return f"{value:.1f} L"


def goal_label(goal: str) -> str:
    return {
        "fat_loss": "🔥 Fat Loss",
        "muscle_gain": "💪 Muscle Gain",
        "maintenance": "⚖️ Maintenance",
    }.get(goal, goal.replace("_", " ").title())


def activity_label(level: str) -> str:
    return {
        "sedentary": "Sedentary (desk job, no exercise)",
        "light": "Light (1-3 days/week)",
        "moderate": "Moderate (3-5 days/week)",
        "active": "Active (6-7 days/week)",
        "very_active": "Very Active (physical job + training)",
    }.get(level, level.replace("_", " ").title())


def progress_color(pct: float) -> str:
    """Return a CSS color string based on progress percentage."""
    if pct >= 90:
        return "#00E676"   # green
    elif pct >= 60:
        return "#FFB300"   # amber
    else:
        return "#FF5252"   # red


def days_of_week() -> list[str]:
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_db_session():
    """Convenience helper to open a new DB session in UI code."""
    from app.models.database import SessionLocal
    return SessionLocal()
