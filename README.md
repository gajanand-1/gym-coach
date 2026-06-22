# 🏋️ AI Personal Gym Coach — LangGraph MVP

A fully local, conversational AI gym coach built with **LangGraph**.  
Talk to it like a real coach. It plans your diet, tracks your food, designs your workouts, monitors your weight, and adjusts your plan week-by-week.

---

## Features (MVP v1)

| # | Feature | What it does |
|---|---------|-------------|
| 1 | **User Profile** | Stores age, weight, goal, budget, diet type, allergies |
| 2 | **Calorie & Macro Calculator** | Mifflin-St Jeor TDEE + protein/carbs/fat split |
| 3 | **Weekly Diet Planner** | LLM-generated 7-day Indian meal plan within budget |
| 4 | **Food Logging** | Natural-language food input → calories + macros + daily totals |
| 5 | **Workout Planner** | PPL / Upper-Lower / Full Body split based on experience |
| 6 | **Workout Logging** | Log sets/reps/weight in plain English |
| 7 | **Progressive Overload** | Auto-recommends weight increases based on last week |
| 8 | **Weight Tracking** | Daily weigh-in, trend chart, goal-date prediction |
| 9 | **Grocery Planner** | Weekly shopping list derived from diet plan with ₹ estimates |
| 10 | **Weekly Check-In** | Sunday review → auto-adjusts calories, cardio, volume |

---

## Project Structure

```
gym_coach/
├── main.py                  ← CLI entrypoint
├── config.py                ← All constants (nutrients, prices, paths)
├── state.py                 ← LangGraph state schema (TypedDicts)
│
├── agents/
│   ├── profile_agent.py     ← User profile (LLM JSON parse + merge)
│   ├── macro_agent.py       ← TDEE + macro math (no LLM)
│   ├── diet_planner_agent.py← 7-day meal plan (LLM)
│   ├── food_log_agent.py    ← Food logging (LLM parse + daily totals)
│   ├── workout_planner_agent.py ← Workout programme (LLM)
│   ├── workout_log_agent.py ← Workout log + progressive overload
│   ├── weight_tracker_agent.py  ← Weight log + trend + prediction
│   ├── grocery_planner_agent.py ← Grocery list from diet plan
│   └── checkin_agent.py     ← Weekly check-in + adjustments (LLM)
│
├── graphs/
│   ├── router.py            ← Intent classifier (LLM + keyword fallback)
│   └── gym_graph.py         ← StateGraph wiring all nodes
│
├── utils/
│   ├── persistence.py       ← load/save JSON helpers
│   ├── nutrition.py         ← BMR/TDEE/macro calculations
│   ├── llm.py               ← Cached ChatOpenAI factory
│   └── formatting.py        ← Rich tables / panels
│
└── data/                    ← Auto-created; all user data stored here
    ├── user_profile.json
    ├── food_log.json
    ├── workout_log.json
    ├── weight_log.json
    ├── diet_plan.json
    ├── workout_plan.json
    ├── grocery_list.json
    └── checkin_log.json
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run interactive mode
```bash
python3 main.py
```

### 4. Run demo walkthrough (all features)
```bash
python3 main.py --demo
```

### 5. Single command mode
```bash
python3 main.py --message "Calculate my macros"
```

---

## Example Conversations

```
You: My name is Arjun. I'm 22, male, 82kg, 175cm, fat loss goal,
     moderate activity, vegetarian, budget ₹4000, beginner, target 75kg

Coach: ✅ Profile saved!
  Name                : Arjun
  Age                 : 22
  Weight              : 82.0 kg
  Target Weight       : 75.0 kg
  Goal                : fat_loss
  ...

You: Calculate my macros

Coach: 🔢 Calorie & Macro Targets — Goal: Fat Loss (-500 kcal deficit)
  Maintenance (TDEE) : 2489 kcal
  Daily Target       : 1989 kcal
  Protein            : 148 g
  Carbohydrates      : 198 g
  Fat                : 55 g

You: For lunch I ate 4 roti, 1 bowl dal, 200g paneer

Coach: ✅ Logged: Lunch
    • 4 roti (140g)
    • 1 bowl dal (150g)
    • 200g paneer

  This meal  →  1092 kcal | P: 62g  C: 105g  F: 52g
  Today so far → 1092 kcal
  Remaining    → 897 kcal | Protein: 86g

You: Log workout: Bench Press 60kg 10 10 8 7, Shoulder Press 40kg 12 12 10

Coach: ✅ Workout Logged — 2024-06-22
  • Bench Press            60 kg × [10, 10, 8, 7]
  • Shoulder Press         40 kg × [12, 12, 10]

  📈 Progressive Overload Report
  🏋️ Bench Press
     This week: 60 kg × [10, 10, 8, 7]
     💡 First recorded session — keep notes and aim to beat this next week!

You: Weight today: 81.5 kg

Coach: ⚖️  Weight logged: 81.5 kg (2024-06-22)
  🎯 Target: 75 kg | Remaining: 6.5 kg
  At current pace: ~13 weeks to reach 75 kg.
```

---

## LangGraph Flow

```
START
  └─► router_node  (classifies intent via LLM + keyword fallback)
        ├─► profile_node       ─► END
        ├─► macro_node         ─► END
        ├─► diet_plan_node     ─► END
        ├─► food_log_node      ─► END
        ├─► workout_plan_node  ─► END
        ├─► workout_log_node   ─► END
        ├─► weight_log_node    ─► END
        ├─► grocery_node       ─► END
        ├─► checkin_node       ─► END
        └─► unknown_node       ─► END
```

---

## Adding More Features Later

To add a new feature (e.g. Water Tracker):
1. Create `agents/water_tracker_agent.py` with a node function
2. Add the node + edge in `graphs/gym_graph.py`
3. Add the intent + keywords in `graphs/router.py`
4. Add state fields to `state.py`

That's it — the graph handles the rest.
