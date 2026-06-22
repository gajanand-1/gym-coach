"""
Nutrient database for the AI Gym Coach.
All values are per 100g unless noted.
Keys: calories (kcal), protein (g), carbs (g), fat (g), fiber (g)
serving_size_g: typical serving size in grams.
"""

# -----------------------------------------------------------------------
# Structure:
#   FOOD_DB[food_key] = {
#       "name": str,
#       "aliases": [str, ...],          # alternate names used in parsing
#       "calories": float,              # per 100 g
#       "protein": float,
#       "carbs": float,
#       "fat": float,
#       "fiber": float,
#       "serving_size_g": float,
#       "category": str,
#   }
# -----------------------------------------------------------------------

FOOD_DB: dict = {
    # ===================================================================
    # PROTEINS – Animal
    # ===================================================================
    "chicken_breast": {
        "name": "Chicken Breast",
        "aliases": ["chicken breast", "boneless chicken", "grilled chicken"],
        "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0,
        "serving_size_g": 150, "category": "protein",
    },
    "chicken_leg": {
        "name": "Chicken Leg / Thigh",
        "aliases": ["chicken leg", "chicken thigh", "chicken piece"],
        "calories": 209, "protein": 26, "carbs": 0, "fat": 11, "fiber": 0,
        "serving_size_g": 120, "category": "protein",
    },
    "chicken_curry": {
        "name": "Chicken Curry",
        "aliases": ["chicken curry", "murgh curry", "chicken gravy"],
        "calories": 150, "protein": 14, "carbs": 5, "fat": 9, "fiber": 0.5,
        "serving_size_g": 200, "category": "protein",
    },
    "egg_whole": {
        "name": "Whole Egg",
        "aliases": ["egg", "boiled egg", "fried egg", "scrambled egg", "omelette",
                    "anda", "anday"],
        "calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0,
        "serving_size_g": 55, "category": "protein",
    },
    "egg_white": {
        "name": "Egg White",
        "aliases": ["egg white", "egg whites"],
        "calories": 52, "protein": 11, "carbs": 0.7, "fat": 0.2, "fiber": 0,
        "serving_size_g": 33, "category": "protein",
    },

    "tuna_canned": {
        "name": "Tuna (Canned)",
        "aliases": ["tuna", "canned tuna", "tuna fish"],
        "calories": 116, "protein": 26, "carbs": 0, "fat": 1, "fiber": 0,
        "serving_size_g": 85, "category": "protein",
    },
    "salmon": {
        "name": "Salmon",
        "aliases": ["salmon", "grilled salmon", "baked salmon"],
        "calories": 208, "protein": 20, "carbs": 0, "fat": 13, "fiber": 0,
        "serving_size_g": 150, "category": "protein",
    },
    "mutton": {
        "name": "Mutton / Lamb",
        "aliases": ["mutton", "lamb", "gosht", "mutton curry"],
        "calories": 294, "protein": 25, "carbs": 0, "fat": 21, "fiber": 0,
        "serving_size_g": 150, "category": "protein",
    },
    "whey_protein": {
        "name": "Whey Protein Powder",
        "aliases": ["whey protein", "protein powder", "whey shake", "protein shake"],
        "calories": 400, "protein": 80, "carbs": 8, "fat": 6, "fiber": 0,
        "serving_size_g": 30, "category": "supplement",
    },
    # ===================================================================
    # PROTEINS – Dairy
    # ===================================================================
    "paneer": {
        "name": "Paneer (Cottage Cheese)",
        "aliases": ["paneer", "cottage cheese", "paneer curry", "shahi paneer"],
        "calories": 265, "protein": 18, "carbs": 3.4, "fat": 20, "fiber": 0,
        "serving_size_g": 100, "category": "protein",
    },
    "milk_whole": {
        "name": "Whole Milk",
        "aliases": ["milk", "whole milk", "doodh", "full cream milk"],
        "calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "fiber": 0,
        "serving_size_g": 200, "category": "dairy",
    },
    "milk_toned": {
        "name": "Toned Milk",
        "aliases": ["toned milk", "skimmed milk", "low fat milk"],
        "calories": 42, "protein": 3.5, "carbs": 5, "fat": 1.5, "fiber": 0,
        "serving_size_g": 200, "category": "dairy",
    },
    "curd": {
        "name": "Curd / Yogurt",
        "aliases": ["curd", "dahi", "yogurt", "yoghurt"],
        "calories": 60, "protein": 3.5, "carbs": 4.7, "fat": 3.3, "fiber": 0,
        "serving_size_g": 150, "category": "dairy",
    },
    "greek_yogurt": {
        "name": "Greek Yogurt",
        "aliases": ["greek yogurt", "hung curd", "greek curd"],
        "calories": 59, "protein": 10, "carbs": 3.6, "fat": 0.4, "fiber": 0,
        "serving_size_g": 150, "category": "dairy",
    },

    # ===================================================================
    # CARBOHYDRATES – Grains & Staples
    # ===================================================================
    "rice_cooked": {
        "name": "Rice (Cooked)",
        "aliases": ["rice", "cooked rice", "plain rice", "steamed rice", "chawal"],
        "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4,
        "serving_size_g": 200, "category": "carbs",
    },
    "brown_rice": {
        "name": "Brown Rice (Cooked)",
        "aliases": ["brown rice", "whole grain rice"],
        "calories": 112, "protein": 2.6, "carbs": 24, "fat": 0.9, "fiber": 1.8,
        "serving_size_g": 200, "category": "carbs",
    },
    "roti_wheat": {
        "name": "Wheat Roti / Chapati",
        "aliases": ["roti", "chapati", "chapatti", "phulka", "wheat roti", "rotis"],
        "calories": 297, "protein": 9, "carbs": 60, "fat": 3.7, "fiber": 2.7,
        "serving_size_g": 40, "category": "carbs",
    },
    "paratha": {
        "name": "Paratha",
        "aliases": ["paratha", "aloo paratha", "stuffed paratha", "plain paratha"],
        "calories": 270, "protein": 6, "carbs": 38, "fat": 10, "fiber": 2,
        "serving_size_g": 80, "category": "carbs",
    },
    "bread_white": {
        "name": "White Bread",
        "aliases": ["bread", "white bread", "toast", "bread slice"],
        "calories": 265, "protein": 9, "carbs": 49, "fat": 3.2, "fiber": 2.7,
        "serving_size_g": 30, "category": "carbs",
    },
    "bread_brown": {
        "name": "Brown / Whole Wheat Bread",
        "aliases": ["brown bread", "whole wheat bread", "multigrain bread"],
        "calories": 247, "protein": 13, "carbs": 41, "fat": 4.2, "fiber": 6,
        "serving_size_g": 30, "category": "carbs",
    },
    "oats": {
        "name": "Oats (Rolled, Dry)",
        "aliases": ["oats", "rolled oats", "oatmeal", "porridge", "quaker oats"],
        "calories": 389, "protein": 17, "carbs": 66, "fat": 7, "fiber": 11,
        "serving_size_g": 80, "category": "carbs",
    },
    "poha": {
        "name": "Poha (Flattened Rice, Cooked)",
        "aliases": ["poha", "beaten rice", "flattened rice"],
        "calories": 130, "protein": 3, "carbs": 27, "fat": 1.5, "fiber": 1,
        "serving_size_g": 150, "category": "carbs",
    },
    "upma": {
        "name": "Upma",
        "aliases": ["upma", "semolina upma", "suji upma"],
        "calories": 130, "protein": 3.5, "carbs": 20, "fat": 4.5, "fiber": 1.5,
        "serving_size_g": 200, "category": "carbs",
    },
    "idli": {
        "name": "Idli",
        "aliases": ["idli", "idly"],
        "calories": 58, "protein": 2, "carbs": 11, "fat": 0.4, "fiber": 0.5,
        "serving_size_g": 40, "category": "carbs",
    },
    "dosa": {
        "name": "Dosa",
        "aliases": ["dosa", "plain dosa", "masala dosa"],
        "calories": 168, "protein": 3.8, "carbs": 26, "fat": 5.5, "fiber": 0.5,
        "serving_size_g": 100, "category": "carbs",
    },
    "pasta": {
        "name": "Pasta (Cooked)",
        "aliases": ["pasta", "macaroni", "spaghetti", "noodles"],
        "calories": 131, "protein": 5, "carbs": 25, "fat": 1.1, "fiber": 1.8,
        "serving_size_g": 180, "category": "carbs",
    },
    "sweet_potato": {
        "name": "Sweet Potato (Cooked)",
        "aliases": ["sweet potato", "shakarkandi", "yam"],
        "calories": 86, "protein": 1.6, "carbs": 20, "fat": 0.1, "fiber": 3,
        "serving_size_g": 150, "category": "carbs",
    },

    # ===================================================================
    # LEGUMES & PULSES
    # ===================================================================
    "dal_cooked": {
        "name": "Dal (Cooked)",
        "aliases": ["dal", "daal", "lentils", "masoor dal", "moong dal",
                    "dal fry", "dal tadka", "dal makhani", "toor dal",
                    "arhar dal", "chana dal"],
        "calories": 116, "protein": 9, "carbs": 20, "fat": 0.4, "fiber": 8,
        "serving_size_g": 200, "category": "legumes",
    },
    "rajma_cooked": {
        "name": "Rajma (Kidney Beans, Cooked)",
        "aliases": ["rajma", "kidney beans", "red kidney beans"],
        "calories": 127, "protein": 8.7, "carbs": 22, "fat": 0.5, "fiber": 7.4,
        "serving_size_g": 200, "category": "legumes",
    },
    "chana_cooked": {
        "name": "Chana / Chickpeas (Cooked)",
        "aliases": ["chana", "chickpeas", "chole", "chhole", "kabuli chana"],
        "calories": 164, "protein": 8.9, "carbs": 27, "fat": 2.6, "fiber": 7.6,
        "serving_size_g": 200, "category": "legumes",
    },
    "moong_sprouts": {
        "name": "Moong Sprouts",
        "aliases": ["moong sprouts", "sprouts", "germinated moong"],
        "calories": 30, "protein": 3, "carbs": 4, "fat": 0.2, "fiber": 1.8,
        "serving_size_g": 100, "category": "legumes",
    },
    # ===================================================================
    # VEGETABLES
    # ===================================================================
    "spinach": {
        "name": "Spinach",
        "aliases": ["spinach", "palak", "palak sabzi"],
        "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2,
        "serving_size_g": 100, "category": "vegetable",
    },
    "broccoli": {
        "name": "Broccoli",
        "aliases": ["broccoli"],
        "calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "fiber": 2.6,
        "serving_size_g": 100, "category": "vegetable",
    },
    "bhindi": {
        "name": "Bhindi (Okra)",
        "aliases": ["bhindi", "okra", "bhindi fry", "ladies finger"],
        "calories": 33, "protein": 1.9, "carbs": 7.5, "fat": 0.1, "fiber": 3.2,
        "serving_size_g": 100, "category": "vegetable",
    },
    "mixed_sabzi": {
        "name": "Mixed Vegetable Sabzi",
        "aliases": ["sabzi", "mixed vegetables", "mix sabzi", "subzi", "veg curry"],
        "calories": 80, "protein": 2.5, "carbs": 10, "fat": 3.5, "fiber": 2,
        "serving_size_g": 150, "category": "vegetable",
    },
    "salad": {
        "name": "Green Salad",
        "aliases": ["salad", "green salad", "garden salad", "cucumber salad"],
        "calories": 20, "protein": 1, "carbs": 3.5, "fat": 0.2, "fiber": 1.5,
        "serving_size_g": 150, "category": "vegetable",
    },
    # ===================================================================
    # FRUITS
    # ===================================================================
    "banana": {
        "name": "Banana",
        "aliases": ["banana", "kela", "raw banana"],
        "calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "fiber": 2.6,
        "serving_size_g": 120, "category": "fruit",
    },
    "apple": {
        "name": "Apple",
        "aliases": ["apple", "seb"],
        "calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4,
        "serving_size_g": 150, "category": "fruit",
    },
    "mango": {
        "name": "Mango",
        "aliases": ["mango", "aam"],
        "calories": 60, "protein": 0.8, "carbs": 15, "fat": 0.4, "fiber": 1.6,
        "serving_size_g": 150, "category": "fruit",
    },

    # ===================================================================
    # FATS & NUTS
    # ===================================================================
    "peanut_butter": {
        "name": "Peanut Butter",
        "aliases": ["peanut butter", "groundnut butter", "pb"],
        "calories": 588, "protein": 25, "carbs": 20, "fat": 50, "fiber": 6,
        "serving_size_g": 32, "category": "fat",
    },
    "almonds": {
        "name": "Almonds",
        "aliases": ["almonds", "badam"],
        "calories": 579, "protein": 21, "carbs": 22, "fat": 50, "fiber": 12.5,
        "serving_size_g": 30, "category": "fat",
    },
    "walnuts": {
        "name": "Walnuts",
        "aliases": ["walnuts", "akhrot"],
        "calories": 654, "protein": 15, "carbs": 14, "fat": 65, "fiber": 6.7,
        "serving_size_g": 30, "category": "fat",
    },
    "ghee": {
        "name": "Ghee",
        "aliases": ["ghee", "clarified butter", "desi ghee"],
        "calories": 900, "protein": 0, "carbs": 0, "fat": 100, "fiber": 0,
        "serving_size_g": 10, "category": "fat",
    },
    "olive_oil": {
        "name": "Olive Oil",
        "aliases": ["olive oil"],
        "calories": 884, "protein": 0, "carbs": 0, "fat": 100, "fiber": 0,
        "serving_size_g": 10, "category": "fat",
    },
    # ===================================================================
    # MESS MENU SPECIALS (common Indian hostel foods)
    # ===================================================================
    "sambar": {
        "name": "Sambar",
        "aliases": ["sambar", "sambhar"],
        "calories": 50, "protein": 2.5, "carbs": 8, "fat": 1.2, "fiber": 2,
        "serving_size_g": 200, "category": "legumes",
    },
    "rasam": {
        "name": "Rasam",
        "aliases": ["rasam", "pepper soup"],
        "calories": 20, "protein": 0.8, "carbs": 4, "fat": 0.3, "fiber": 0.5,
        "serving_size_g": 200, "category": "vegetable",
    },
    "puri": {
        "name": "Puri",
        "aliases": ["puri", "poori"],
        "calories": 340, "protein": 7, "carbs": 47, "fat": 14, "fiber": 2.3,
        "serving_size_g": 40, "category": "carbs",
    },
    "aloo_curry": {
        "name": "Aloo Curry",
        "aliases": ["aloo", "potato curry", "aloo sabzi", "aloo ki sabzi"],
        "calories": 90, "protein": 2, "carbs": 17, "fat": 2.5, "fiber": 2,
        "serving_size_g": 150, "category": "vegetable",
    },
    "methi_sabzi": {
        "name": "Methi Sabzi",
        "aliases": ["methi", "fenugreek", "methi sabzi", "methi paratha"],
        "calories": 49, "protein": 4.4, "carbs": 6, "fat": 0.9, "fiber": 2.7,
        "serving_size_g": 100, "category": "vegetable",
    },
    "biryani_chicken": {
        "name": "Chicken Biryani",
        "aliases": ["chicken biryani", "biryani", "murgh biryani"],
        "calories": 200, "protein": 13, "carbs": 25, "fat": 6, "fiber": 1,
        "serving_size_g": 300, "category": "mixed",
    },
    "fried_rice": {
        "name": "Fried Rice",
        "aliases": ["fried rice", "egg fried rice", "veg fried rice"],
        "calories": 163, "protein": 4, "carbs": 30, "fat": 3.5, "fiber": 1.5,
        "serving_size_g": 200, "category": "carbs",
    },
    "halwa": {
        "name": "Halwa / Sheera",
        "aliases": ["halwa", "sheera", "suji halwa", "gajar halwa", "moong dal halwa"],
        "calories": 280, "protein": 4, "carbs": 38, "fat": 12, "fiber": 1,
        "serving_size_g": 100, "category": "dessert",
    },
    "khichdi": {
        "name": "Khichdi",
        "aliases": ["khichdi", "khichri"],
        "calories": 120, "protein": 4.5, "carbs": 22, "fat": 2, "fiber": 2,
        "serving_size_g": 200, "category": "mixed",
    },
    # ===================================================================
    # BEVERAGES
    # ===================================================================
    "chai": {
        "name": "Masala Chai (with milk & sugar)",
        "aliases": ["chai", "tea", "masala chai", "milk tea"],
        "calories": 50, "protein": 1.5, "carbs": 7, "fat": 1.5, "fiber": 0,
        "serving_size_g": 200, "category": "beverage",
    },
    "protein_shake": {
        "name": "Protein Shake (whey in water)",
        "aliases": ["protein shake", "shake", "whey shake"],
        "calories": 120, "protein": 24, "carbs": 3, "fat": 2, "fiber": 0,
        "serving_size_g": 300, "category": "supplement",
    },
}



# -----------------------------------------------------------------------
# Lookup helpers
# -----------------------------------------------------------------------

def search_food(query: str) -> list[dict]:
    """Fuzzy-search the DB by name or alias. Returns list of matches."""
    q = query.lower().strip()
    results = []
    for key, data in FOOD_DB.items():
        # Direct name match
        if q in data["name"].lower():
            results.append({"key": key, **data})
            continue
        # Alias match
        if any(q in alias for alias in data.get("aliases", [])):
            results.append({"key": key, **data})
    return results


def get_food(key: str) -> dict | None:
    """Get food by exact key."""
    return FOOD_DB.get(key)


def get_food_by_alias(alias: str) -> dict | None:
    """Find food by exact alias string."""
    alias_lower = alias.lower().strip()
    for key, data in FOOD_DB.items():
        if alias_lower == data["name"].lower():
            return {"key": key, **data}
        if alias_lower in [a.lower() for a in data.get("aliases", [])]:
            return {"key": key, **data}
    return None


def calculate_macros(food_key: str, quantity_g: float) -> dict:
    """
    Return macros for `quantity_g` grams of the given food.
    All values are scaled from the per-100g database.
    """
    food = get_food(food_key)
    if not food:
        return {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
    scale = quantity_g / 100.0
    return {
        "name": food["name"],
        "quantity_g": quantity_g,
        "calories": round(food["calories"] * scale, 1),
        "protein": round(food["protein"] * scale, 1),
        "carbs": round(food["carbs"] * scale, 1),
        "fat": round(food["fat"] * scale, 1),
        "fiber": round(food.get("fiber", 0) * scale, 1),
    }


def calculate_macros_by_alias(alias: str, quantity_g: float) -> dict:
    """Same as calculate_macros but accepts a name/alias string."""
    food = get_food_by_alias(alias)
    if not food:
        # Try fuzzy search fallback
        results = search_food(alias)
        if results:
            food = results[0]
        else:
            return {
                "name": alias, "quantity_g": quantity_g,
                "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0,
                "matched": False,
            }
    return calculate_macros(food["key"], quantity_g)


def get_all_food_names() -> list[str]:
    """Return flat list of all food names and aliases (for UI autocomplete)."""
    names = []
    for data in FOOD_DB.values():
        names.append(data["name"])
        names.extend(data.get("aliases", []))
    return sorted(set(names))


def get_foods_by_category(category: str) -> list[dict]:
    """Return all foods in a given category."""
    return [
        {"key": k, **v}
        for k, v in FOOD_DB.items()
        if v.get("category", "").lower() == category.lower()
    ]
