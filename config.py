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
    # Grains & Carbs
    "oats":             8,
    "rice":             5,
    "roti":             5,
    "bread":            6,
    "brown_rice":       8,
    "poha":             6,
    "upma":             5,
    "idli":             4,
    "dosa":             5,
    "paratha":          8,
    "pasta":            12,
    "quinoa":           30,
    "sweet_potato":     5,
    "potato":           3,

    # Dairy
    "milk":             6,
    "curd":             8,
    "paneer":           40,
    "cheese":           50,
    "butter":           45,
    "ghee":             60,
    "whey_protein":     80,

    # Fruits & Veg
    "banana":           5,
    "apple":            10,
    "orange":           6,
    "mango":            8,
    "spinach":          4,
    "broccoli":         15,
    "tomato":           3,
    "onion":            3,
    "cucumber":         3,

    # Vegetarian Protein
    "dal":              10,
    "soy_chunks":       12,
    "tofu":             20,
    "peanuts":          12,
    "sattu":            10,
    "chickpeas":        12,
    "kidney_beans":     12,
    "lentils":          10,

    # NON-VEG PROTEIN ─────────────────────────────────────────────────
    "chicken_breast":   30,
    "chicken_leg":      22,
    "chicken_thigh":    22,
    "whole_chicken":    18,
    "eggs":             8,
    "egg_white":        5,
    "fish":             20,
    "rohu_fish":        18,
    "tuna_canned":      25,
    "salmon":           60,
    "prawns":           35,
    "mutton":           55,
    "lamb":             55,
    "turkey":           40,
    "beef":             35,

    # Fats & Nuts
    "almonds":          70,
    "walnuts":          80,
    "cashews":          60,
    "olive_oil":        50,
}

# ── Nutrient DB (per 100g) ────────────────────────────────────────────────────
# {food: {kcal, protein, carbs, fat}}
NUTRIENT_DB = {
    # ── Grains & Carbs ────────────────────────────────────────────────
    "oats":             {"kcal": 389, "protein": 17,  "carbs": 66,  "fat": 7},
    "rice":             {"kcal": 130, "protein": 3,   "carbs": 28,  "fat": 0},
    "brown_rice":       {"kcal": 123, "protein": 3,   "carbs": 26,  "fat": 1},
    "roti":             {"kcal": 106, "protein": 3,   "carbs": 20,  "fat": 2},
    "bread":            {"kcal": 265, "protein": 9,   "carbs": 49,  "fat": 3},
    "poha":             {"kcal": 110, "protein": 2,   "carbs": 24,  "fat": 1},
    "idli":             {"kcal": 58,  "protein": 2,   "carbs": 11,  "fat": 0},
    "dosa":             {"kcal": 133, "protein": 3,   "carbs": 23,  "fat": 3},
    "paratha":          {"kcal": 257, "protein": 5,   "carbs": 35,  "fat": 11},
    "pasta":            {"kcal": 131, "protein": 5,   "carbs": 25,  "fat": 1},
    "sweet_potato":     {"kcal": 86,  "protein": 2,   "carbs": 20,  "fat": 0},
    "potato":           {"kcal": 77,  "protein": 2,   "carbs": 17,  "fat": 0},

    # ── Dairy ─────────────────────────────────────────────────────────
    "milk":             {"kcal": 61,  "protein": 3,   "carbs": 5,   "fat": 3},
    "curd":             {"kcal": 98,  "protein": 11,  "carbs": 4,   "fat": 5},
    "paneer":           {"kcal": 265, "protein": 18,  "carbs": 3,   "fat": 20},
    "cheese":           {"kcal": 402, "protein": 25,  "carbs": 1,   "fat": 33},
    "butter":           {"kcal": 717, "protein": 1,   "carbs": 0,   "fat": 81},
    "ghee":             {"kcal": 900, "protein": 0,   "carbs": 0,   "fat": 99},
    "whey_protein":     {"kcal": 120, "protein": 24,  "carbs": 3,   "fat": 2},

    # ── Fruits ────────────────────────────────────────────────────────
    "banana":           {"kcal": 89,  "protein": 1,   "carbs": 23,  "fat": 0},
    "apple":            {"kcal": 52,  "protein": 0,   "carbs": 14,  "fat": 0},
    "orange":           {"kcal": 47,  "protein": 1,   "carbs": 12,  "fat": 0},
    "mango":            {"kcal": 60,  "protein": 1,   "carbs": 15,  "fat": 0},

    # ── Vegetables ────────────────────────────────────────────────────
    "spinach":          {"kcal": 23,  "protein": 3,   "carbs": 4,   "fat": 0},
    "broccoli":         {"kcal": 34,  "protein": 3,   "carbs": 7,   "fat": 0},
    "tomato":           {"kcal": 18,  "protein": 1,   "carbs": 4,   "fat": 0},
    "onion":            {"kcal": 40,  "protein": 1,   "carbs": 9,   "fat": 0},
    "cucumber":         {"kcal": 15,  "protein": 1,   "carbs": 4,   "fat": 0},

    # ── Vegetarian Protein ────────────────────────────────────────────
    "dal":              {"kcal": 116, "protein": 9,   "carbs": 20,  "fat": 1},
    "soy_chunks":       {"kcal": 345, "protein": 52,  "carbs": 33,  "fat": 1},
    "tofu":             {"kcal": 76,  "protein": 8,   "carbs": 2,   "fat": 5},
    "peanuts":          {"kcal": 567, "protein": 26,  "carbs": 16,  "fat": 49},
    "sattu":            {"kcal": 406, "protein": 22,  "carbs": 65,  "fat": 6},
    "chickpeas":        {"kcal": 164, "protein": 9,   "carbs": 27,  "fat": 3},
    "kidney_beans":     {"kcal": 127, "protein": 9,   "carbs": 23,  "fat": 0},
    "lentils":          {"kcal": 116, "protein": 9,   "carbs": 20,  "fat": 0},

    # ── NON-VEG PROTEIN ───────────────────────────────────────────────
    "chicken_breast":   {"kcal": 165, "protein": 31,  "carbs": 0,   "fat": 4},
    "chicken_leg":      {"kcal": 184, "protein": 26,  "carbs": 0,   "fat": 9},
    "chicken_thigh":    {"kcal": 209, "protein": 26,  "carbs": 0,   "fat": 11},
    "whole_chicken":    {"kcal": 215, "protein": 18,  "carbs": 0,   "fat": 15},
    "eggs":             {"kcal": 155, "protein": 13,  "carbs": 1,   "fat": 11},
    "egg_white":        {"kcal": 52,  "protein": 11,  "carbs": 1,   "fat": 0},
    "fish":             {"kcal": 136, "protein": 22,  "carbs": 0,   "fat": 5},
    "rohu_fish":        {"kcal": 97,  "protein": 16,  "carbs": 0,   "fat": 3},
    "tuna_canned":      {"kcal": 116, "protein": 26,  "carbs": 0,   "fat": 1},
    "salmon":           {"kcal": 208, "protein": 20,  "carbs": 0,   "fat": 13},
    "prawns":           {"kcal": 99,  "protein": 24,  "carbs": 0,   "fat": 1},
    "mutton":           {"kcal": 294, "protein": 25,  "carbs": 0,   "fat": 21},
    "lamb":             {"kcal": 282, "protein": 25,  "carbs": 0,   "fat": 20},
    "turkey":           {"kcal": 189, "protein": 29,  "carbs": 0,   "fat": 7},
    "beef":             {"kcal": 250, "protein": 26,  "carbs": 0,   "fat": 17},

    # ── Nuts & Fats ───────────────────────────────────────────────────
    "almonds":          {"kcal": 579, "protein": 21,  "carbs": 22,  "fat": 50},
    "walnuts":          {"kcal": 654, "protein": 15,  "carbs": 14,  "fat": 65},
    "cashews":          {"kcal": 553, "protein": 18,  "carbs": 30,  "fat": 44},
    "olive_oil":        {"kcal": 884, "protein": 0,   "carbs": 0,   "fat": 100},
}
