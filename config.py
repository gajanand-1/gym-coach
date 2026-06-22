"""
Central configuration for the AI Gym Coach.
All tuneable constants live here.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str   = os.getenv("OPENAI_MODEL", "gpt-4o")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).parent
DATA_DIR: Path = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

USER_PROFILE_FILE   = DATA_DIR / "user_profile.json"
FOOD_LOG_FILE       = DATA_DIR / "food_log.json"
WORKOUT_LOG_FILE    = DATA_DIR / "workout_log.json"
WEIGHT_LOG_FILE     = DATA_DIR / "weight_log.json"
DIET_PLAN_FILE      = DATA_DIR / "diet_plan.json"
WORKOUT_PLAN_FILE   = DATA_DIR / "workout_plan.json"
GROCERY_LIST_FILE   = DATA_DIR / "grocery_list.json"
CHECKIN_LOG_FILE    = DATA_DIR / "checkin_log.json"

# ── Fitness defaults ──────────────────────────────────────────────────────────
PROTEIN_PER_KG          = 1.8   # g per kg bodyweight
FAT_LOSS_DEFICIT_KCAL   = 500   # kcal below TDEE
BULK_SURPLUS_KCAL       = 300   # kcal above TDEE

# Activity level multipliers (Mifflin-St Jeor)
ACTIVITY_MULTIPLIERS = {
    "sedentary":    1.2,
    "light":        1.375,
    "moderate":     1.55,
    "active":       1.725,
    "very_active":  1.9,
}

# ── Indian food prices (₹ per 100g unless noted) ──────────────────────────────
FOOD_PRICES_PER_100G = {
    "oats":         8,
    "milk":         6,    # per 100ml
    "banana":       5,    # per piece (~100g)
    "rice":         5,
    "dal":          10,
    "paneer":       40,
    "roti":         5,    # per piece (~35g)
    "soy_chunks":   12,
    "eggs":         8,    # per egg (~50g)
    "peanuts":      12,
    "sattu":        10,
    "curd":         8,
    "bread":        6,
    "potato":       3,
    "spinach":      4,
    "tomato":       3,
    "onion":        3,
    "chicken":      25,
    "fish":         20,
    "whey_protein": 80,   # per 30g scoop
}

# ── Nutrient DB (per 100g) ────────────────────────────────────────────────────
# {food: {kcal, protein_g, carbs_g, fat_g}}
NUTRIENT_DB = {
    "oats":         {"kcal": 389, "protein": 17, "carbs": 66, "fat": 7},
    "milk":         {"kcal": 61,  "protein": 3,  "carbs": 5,  "fat": 3},
    "banana":       {"kcal": 89,  "protein": 1,  "carbs": 23, "fat": 0},
    "rice":         {"kcal": 130, "protein": 3,  "carbs": 28, "fat": 0},
    "dal":          {"kcal": 116, "protein": 9,  "carbs": 20, "fat": 1},
    "paneer":       {"kcal": 265, "protein": 18, "carbs": 3,  "fat": 20},
    "roti":         {"kcal": 106, "protein": 3,  "carbs": 20, "fat": 2},
    "soy_chunks":   {"kcal": 345, "protein": 52, "carbs": 33, "fat": 1},
    "eggs":         {"kcal": 155, "protein": 13, "carbs": 1,  "fat": 11},
    "peanuts":      {"kcal": 567, "protein": 26, "carbs": 16, "fat": 49},
    "sattu":        {"kcal": 406, "protein": 22, "carbs": 65, "fat": 6},
    "curd":         {"kcal": 98,  "protein": 11, "carbs": 4,  "fat": 5},
    "bread":        {"kcal": 265, "protein": 9,  "carbs": 49, "fat": 3},
    "potato":       {"kcal": 77,  "protein": 2,  "carbs": 17, "fat": 0},
    "spinach":      {"kcal": 23,  "protein": 3,  "carbs": 4,  "fat": 0},
    "chicken":      {"kcal": 165, "protein": 31, "carbs": 0,  "fat": 4},
    "fish":         {"kcal": 136, "protein": 22, "carbs": 0,  "fat": 5},
    "whey_protein": {"kcal": 120, "protein": 24, "carbs": 3,  "fat": 2},
}
