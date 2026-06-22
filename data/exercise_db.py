"""
Exercise database used by the Workout Planning Agent.
Each exercise contains default sets/reps/rest per experience level.
"""

EXERCISE_DB: dict = {
    # ===================================================================
    # PUSH – Chest, Shoulders, Triceps
    # ===================================================================
    "bench_press": {
        "name": "Bench Press",
        "muscle_group": "chest",
        "equipment": "barbell",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "8-10",  "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "6-10",  "rest_sec": 120},
        "advanced":     {"sets": 5, "reps": "4-8",   "rest_sec": 180},
    },
    "incline_dumbbell_press": {
        "name": "Incline Dumbbell Press",
        "muscle_group": "chest_upper",
        "equipment": "dumbbell",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "8-12",  "rest_sec": 90},
        "advanced":     {"sets": 4, "reps": "8-10",  "rest_sec": 120},
    },
    "cable_fly": {
        "name": "Cable Fly",
        "muscle_group": "chest",
        "equipment": "cable",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "12-15", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "12-15", "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "10-15", "rest_sec": 60},
    },
    "overhead_press": {
        "name": "Overhead Press (Barbell)",
        "muscle_group": "shoulders",
        "equipment": "barbell",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "8-10",  "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "6-10",  "rest_sec": 120},
        "advanced":     {"sets": 5, "reps": "4-8",   "rest_sec": 180},
    },
    "dumbbell_shoulder_press": {
        "name": "Dumbbell Shoulder Press",
        "muscle_group": "shoulders",
        "equipment": "dumbbell",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "8-12",  "rest_sec": 90},
        "advanced":     {"sets": 4, "reps": "8-12",  "rest_sec": 90},
    },
    "lateral_raise": {
        "name": "Lateral Raise",
        "muscle_group": "shoulders_lateral",
        "equipment": "dumbbell",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "12-15", "rest_sec": 60},
        "intermediate": {"sets": 4, "reps": "12-15", "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "12-20", "rest_sec": 60},
    },
    "tricep_pushdown": {
        "name": "Tricep Pushdown",
        "muscle_group": "triceps",
        "equipment": "cable",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "12-15", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "10-15", "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "10-15", "rest_sec": 60},
    },
    "skull_crushers": {
        "name": "Skull Crushers (EZ Bar)",
        "muscle_group": "triceps",
        "equipment": "barbell",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "8-12",  "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "8-12",  "rest_sec": 60},
    },
    "dips": {
        "name": "Tricep Dips",
        "muscle_group": "triceps",
        "equipment": "bodyweight",
        "category": "push",
        "beginner":     {"sets": 3, "reps": "8-10",  "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "10-12", "rest_sec": 90},
        "advanced":     {"sets": 4, "reps": "12-15", "rest_sec": 90},
    },
    # ===================================================================
    # PULL – Back, Biceps
    # ===================================================================
    "deadlift": {
        "name": "Deadlift",
        "muscle_group": "back_lower",
        "equipment": "barbell",
        "category": "pull",
        "beginner":     {"sets": 3, "reps": "5",     "rest_sec": 180},
        "intermediate": {"sets": 4, "reps": "4-6",   "rest_sec": 180},
        "advanced":     {"sets": 5, "reps": "3-5",   "rest_sec": 240},
    },
    "pull_up": {
        "name": "Pull-Up",
        "muscle_group": "back_upper",
        "equipment": "bodyweight",
        "category": "pull",
        "beginner":     {"sets": 3, "reps": "5-8",   "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "8-12",  "rest_sec": 90},
        "advanced":     {"sets": 5, "reps": "10-15", "rest_sec": 90},
    },
    "lat_pulldown": {
        "name": "Lat Pulldown",
        "muscle_group": "back_upper",
        "equipment": "cable",
        "category": "pull",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "8-12",  "rest_sec": 90},
        "advanced":     {"sets": 4, "reps": "8-12",  "rest_sec": 90},
    },
    "barbell_row": {
        "name": "Barbell Row",
        "muscle_group": "back_mid",
        "equipment": "barbell",
        "category": "pull",
        "beginner":     {"sets": 3, "reps": "8-10",  "rest_sec": 120},
        "intermediate": {"sets": 4, "reps": "6-10",  "rest_sec": 120},
        "advanced":     {"sets": 5, "reps": "6-8",   "rest_sec": 150},
    },
    "cable_row": {
        "name": "Seated Cable Row",
        "muscle_group": "back_mid",
        "equipment": "cable",
        "category": "pull",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "8-12",  "rest_sec": 90},
        "advanced":     {"sets": 4, "reps": "8-12",  "rest_sec": 90},
    },
    "face_pull": {
        "name": "Face Pull",
        "muscle_group": "shoulders_rear",
        "equipment": "cable",
        "category": "pull",
        "beginner":     {"sets": 3, "reps": "12-15", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "15-20", "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "15-20", "rest_sec": 60},
    },
    "barbell_curl": {
        "name": "Barbell Curl",
        "muscle_group": "biceps",
        "equipment": "barbell",
        "category": "pull",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "8-12",  "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "8-12",  "rest_sec": 60},
    },
    "hammer_curl": {
        "name": "Hammer Curl",
        "muscle_group": "biceps",
        "equipment": "dumbbell",
        "category": "pull",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "10-12", "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "10-12", "rest_sec": 60},
    },
    # ===================================================================
    # LEGS – Quads, Hamstrings, Glutes, Calves
    # ===================================================================
    "squat": {
        "name": "Barbell Back Squat",
        "muscle_group": "quads",
        "equipment": "barbell",
        "category": "legs",
        "beginner":     {"sets": 3, "reps": "8-10",  "rest_sec": 180},
        "intermediate": {"sets": 4, "reps": "6-10",  "rest_sec": 180},
        "advanced":     {"sets": 5, "reps": "4-8",   "rest_sec": 240},
    },
    "leg_press": {
        "name": "Leg Press",
        "muscle_group": "quads",
        "equipment": "machine",
        "category": "legs",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 120},
        "intermediate": {"sets": 4, "reps": "8-12",  "rest_sec": 120},
        "advanced":     {"sets": 4, "reps": "8-15",  "rest_sec": 120},
    },
    "romanian_deadlift": {
        "name": "Romanian Deadlift",
        "muscle_group": "hamstrings",
        "equipment": "barbell",
        "category": "legs",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 120},
        "intermediate": {"sets": 4, "reps": "8-12",  "rest_sec": 120},
        "advanced":     {"sets": 4, "reps": "6-10",  "rest_sec": 150},
    },
    "leg_curl": {
        "name": "Leg Curl (Machine)",
        "muscle_group": "hamstrings",
        "equipment": "machine",
        "category": "legs",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 90},
        "intermediate": {"sets": 3, "reps": "10-12", "rest_sec": 90},
        "advanced":     {"sets": 4, "reps": "10-12", "rest_sec": 90},
    },
    "leg_extension": {
        "name": "Leg Extension (Machine)",
        "muscle_group": "quads",
        "equipment": "machine",
        "category": "legs",
        "beginner":     {"sets": 3, "reps": "12-15", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "12-15", "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "10-15", "rest_sec": 60},
    },
    "hip_thrust": {
        "name": "Hip Thrust",
        "muscle_group": "glutes",
        "equipment": "barbell",
        "category": "legs",
        "beginner":     {"sets": 3, "reps": "10-12", "rest_sec": 90},
        "intermediate": {"sets": 4, "reps": "8-12",  "rest_sec": 90},
        "advanced":     {"sets": 4, "reps": "8-15",  "rest_sec": 90},
    },
    "calf_raise": {
        "name": "Standing Calf Raise",
        "muscle_group": "calves",
        "equipment": "machine",
        "category": "legs",
        "beginner":     {"sets": 3, "reps": "15-20", "rest_sec": 60},
        "intermediate": {"sets": 4, "reps": "15-20", "rest_sec": 60},
        "advanced":     {"sets": 5, "reps": "15-25", "rest_sec": 60},
    },
    # ===================================================================
    # CORE
    # ===================================================================
    "plank": {
        "name": "Plank",
        "muscle_group": "core",
        "equipment": "bodyweight",
        "category": "core",
        "beginner":     {"sets": 3, "reps": "30sec", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "60sec", "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "90sec", "rest_sec": 60},
    },
    "cable_crunch": {
        "name": "Cable Crunch",
        "muscle_group": "core",
        "equipment": "cable",
        "category": "core",
        "beginner":     {"sets": 3, "reps": "12-15", "rest_sec": 60},
        "intermediate": {"sets": 3, "reps": "15-20", "rest_sec": 60},
        "advanced":     {"sets": 4, "reps": "15-20", "rest_sec": 60},
    },
}

# -----------------------------------------------------------------------
# Split definitions — which exercises go on which days
# -----------------------------------------------------------------------

SPLITS: dict = {
    "push_pull_legs": {
        "Monday":    {"session": "Push Day A", "exercises": [
            "bench_press", "incline_dumbbell_press", "cable_fly",
            "overhead_press", "lateral_raise", "tricep_pushdown", "skull_crushers",
        ]},
        "Tuesday":   {"session": "Pull Day A", "exercises": [
            "deadlift", "pull_up", "lat_pulldown",
            "barbell_row", "face_pull", "barbell_curl", "hammer_curl",
        ]},
        "Wednesday": {"session": "Legs Day A", "exercises": [
            "squat", "leg_press", "romanian_deadlift",
            "leg_curl", "leg_extension", "calf_raise",
        ]},
        "Thursday":  {"session": "Rest / Cardio", "exercises": []},
        "Friday":    {"session": "Push Day B", "exercises": [
            "bench_press", "dips", "cable_fly",
            "dumbbell_shoulder_press", "lateral_raise", "tricep_pushdown",
        ]},
        "Saturday":  {"session": "Pull Day B", "exercises": [
            "barbell_row", "lat_pulldown", "cable_row",
            "face_pull", "barbell_curl", "hammer_curl",
        ]},
        "Sunday":    {"session": "Legs Day B", "exercises": [
            "squat", "leg_press", "hip_thrust",
            "leg_curl", "calf_raise", "plank",
        ]},
    },
    "upper_lower": {
        "Monday":    {"session": "Upper A", "exercises": [
            "bench_press", "barbell_row", "overhead_press",
            "lat_pulldown", "barbell_curl", "tricep_pushdown",
        ]},
        "Tuesday":   {"session": "Lower A", "exercises": [
            "squat", "romanian_deadlift", "leg_press",
            "leg_curl", "calf_raise",
        ]},
        "Wednesday": {"session": "Rest", "exercises": []},
        "Thursday":  {"session": "Upper B", "exercises": [
            "incline_dumbbell_press", "cable_row", "dumbbell_shoulder_press",
            "pull_up", "hammer_curl", "skull_crushers",
        ]},
        "Friday":    {"session": "Lower B", "exercises": [
            "deadlift", "leg_press", "leg_extension",
            "hip_thrust", "calf_raise",
        ]},
        "Saturday":  {"session": "Optional Cardio / Core", "exercises": ["plank", "cable_crunch"]},
        "Sunday":    {"session": "Rest", "exercises": []},
    },
    "full_body": {
        "Monday":    {"session": "Full Body A", "exercises": [
            "squat", "bench_press", "barbell_row",
            "overhead_press", "barbell_curl", "calf_raise",
        ]},
        "Tuesday":   {"session": "Rest", "exercises": []},
        "Wednesday": {"session": "Full Body B", "exercises": [
            "deadlift", "incline_dumbbell_press", "lat_pulldown",
            "lateral_raise", "hammer_curl", "plank",
        ]},
        "Thursday":  {"session": "Rest", "exercises": []},
        "Friday":    {"session": "Full Body C", "exercises": [
            "squat", "cable_row", "dumbbell_shoulder_press",
            "romanian_deadlift", "tricep_pushdown", "calf_raise",
        ]},
        "Saturday":  {"session": "Optional Cardio / Mobility", "exercises": []},
        "Sunday":    {"session": "Rest", "exercises": []},
    },
}


def get_exercises_for_split(split_type: str, experience: str = "beginner") -> dict:
    """
    Return the full weekly plan with exercise details (sets/reps/rest)
    populated from EXERCISE_DB for the given split and experience level.
    """
    split = SPLITS.get(split_type, SPLITS["push_pull_legs"])
    result = {}
    for day, session_info in split.items():
        exercises = []
        for ex_key in session_info["exercises"]:
            ex_data = EXERCISE_DB.get(ex_key, {})
            level_data = ex_data.get(experience, ex_data.get("beginner", {}))
            exercises.append({
                "key": ex_key,
                "name": ex_data.get("name", ex_key),
                "muscle_group": ex_data.get("muscle_group", ""),
                "equipment": ex_data.get("equipment", ""),
                "sets": level_data.get("sets", 3),
                "reps": level_data.get("reps", "10"),
                "rest_sec": level_data.get("rest_sec", 90),
            })
        result[day] = {
            "session": session_info["session"],
            "exercises": exercises,
        }
    return result
