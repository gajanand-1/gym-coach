# 🏋️ Personal AI Gym Coach

A production-ready AI-powered fitness application that acts as your personal trainer, nutritionist, and progress coach — all in one.

Built with **Python · Streamlit · LangGraph · Claude (Anthropic) · SQLite**.

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Dashboard** | Real-time snapshot: calories, macros, water, sleep, workout status |
| 2 | **User Profile** | BMR / TDEE / macro targets auto-calculated (Mifflin-St Jeor) |
| 3 | **AI Food Log** | Log food in plain English — AI parses macros automatically |
| 4 | **Calorie Tracker** | Consumed vs remaining vs target for all 4 macros |
| 5 | **Diet Planner** | AI-generated 7-day non-vegetarian high-protein meal plan |
| 6 | **Workout Planner** | PPL / Upper-Lower / Full Body plans with sets, reps, rest |
| 7 | **Workout Log** | Log sessions with dynamic exercise rows; volume tracking |
| 8 | **Progressive Overload** | AI analysis of last 2 weeks — exact weight/rep progression |
| 9 | **Weight Tracker** | Daily logging, 30-day chart, weekly averages, goal ETA |
| 10 | **Grocery Planner** | Auto-generated from meal plan; mess items excluded |
| 11 | **Weekly Check-In** | AI weekly review with calorie/protein target adjustments |
| 12 | **Water Tracker** | Gauge + quick-add buttons; target = 35ml/kg bodyweight |
| 13 | **Sleep Tracker** | Log sleep hours/quality; recovery insights |
| 14 | **Supplement Tracker** | Whey, Creatine, Fish Oil, Multivitamin daily adherence |
| 15 | **AI Coach Chat** | Full conversational coach with access to ALL your data |
| 16 | **Mess Menu** | Upload hostel mess menu (text/PDF/image); AI-aware food logging |

---

## 🏗️ Architecture

```
gym-coach/
│
├── main.py                     # Entry point (Streamlit home + auth)
├── requirements.txt
├── .env.example
│
├── app/
│   ├── agents/                 # 7 Claude AI agents
│   │   ├── base.py             # Shared BaseAgent + Claude client
│   │   ├── food_parser.py      # Natural language → macros JSON
│   │   ├── diet_planner.py     # 7-day meal plan generator
│   │   ├── workout_planner.py  # Weekly training programme
│   │   ├── progressive_overload.py  # Strength progression analysis
│   │   ├── weekly_checkin.py   # Weekly review + adjustments
│   │   ├── coach_chat.py       # Conversational coach (full context)
│   │   └── mess_parser.py      # Menu text/PDF/image → structured JSON
│   │
│   ├── graph/                  # LangGraph stateful workflows
│   │   ├── state.py            # TypedDict state definitions
│   │   ├── food_log_graph.py   # check_mess → parse → validate → save
│   │   ├── diet_plan_graph.py  # generate → validate → save → grocery
│   │   ├── workout_plan_graph.py
│   │   ├── progressive_overload_graph.py
│   │   ├── checkin_graph.py    # collect_data → analyse → adjust → save
│   │   └── coach_chat_graph.py # load_context → chat → save_message
│   │
│   ├── models/                 # SQLAlchemy ORM models (14 tables)
│   │   ├── database.py         # Engine + SessionLocal + init_db()
│   │   ├── user.py
│   │   ├── food_log.py
│   │   ├── workout_log.py + workout_set
│   │   ├── weight_log.py
│   │   ├── water_log.py
│   │   ├── sleep_log.py
│   │   ├── supplement_log.py
│   │   ├── diet_plan.py
│   │   ├── workout_plan.py
│   │   ├── grocery_plan.py
│   │   ├── chat_history.py
│   │   ├── checkin.py
│   │   └── mess_menu.py
│   │
│   ├── storage/                # Repository pattern CRUD layer (13 stores)
│   ├── services/               # Business logic + chart builders
│   │   ├── macro_calculator.py # BMR / TDEE / macro splits
│   │   ├── auth_service.py     # Register / login / session
│   │   ├── dashboard_service.py
│   │   ├── food_service.py
│   │   ├── workout_service.py
│   │   ├── weight_service.py
│   │   └── chart_service.py    # 8 Plotly charts
│   │
│   ├── ui/
│   │   ├── style.py            # Global dark CSS
│   │   └── pages/              # 16 Streamlit pages (auto-discovered)
│   │
│   └── utils/
│       ├── helpers.py
│       └── session.py
│
├── data/
│   ├── nutrient_db.py          # 60+ foods (Indian + gym staples)
│   └── exercise_db.py          # 30 exercises + PPL/UL/FB split definitions
│
├── database/                   # SQLite DB file (auto-created, gitignored)
└── .streamlit/
    └── config.toml             # Dark theme + server config
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com/)

### 2. Clone & Install

```bash
git clone <your-repo-url>
cd gym-coach

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Open `.env` and set your API key:

```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### 4. Run the App

```bash
streamlit run main.py
```

Open your browser at **http://localhost:8501**

---

## 📱 First-Time Setup

1. **Register** a new account on the login page
2. Go to **Profile** → fill in your details → click **Save & Recalculate Macros**
3. *(Optional)* Go to **Mess Menu** → upload your hostel mess menu
4. Go to **Workout Planner** → click **Generate Workout Plan**
5. Go to **Diet Planner** → click **Generate 7-Day Meal Plan**
6. Start logging food on the **Food Log** page!

---

## 🤖 AI Agents

All AI features use **Claude 3.5 Sonnet** via the Anthropic API.

| Agent | LangGraph Nodes | What it does |
|-------|----------------|--------------|
| `FoodParserAgent` | check_mess → parse → validate → save | Converts "4 roti 2 eggs 200g chicken" into macros JSON |
| `DietPlannerAgent` | generate → validate → save → grocery | Creates 7-day high-protein non-veg meal plan |
| `WorkoutPlannerAgent` | generate → validate → save | Builds PPL/UL/FB programme with sets/reps/rest |
| `ProgressiveOverloadAgent` | fetch_history → analyse → format | Recommends exact weights for next session |
| `WeeklyCheckInAgent` | collect_data → analyse → adjust → save | Reviews your week and updates calorie targets |
| `CoachChatAgent` | load_context → chat → save_message | Answers questions with full access to your data |
| `MessParserAgent` | direct call | Parses mess menu from text/PDF/image |

---

## 🍽️ Mess Menu Integration

The app has deep integration with hostel mess menus:

1. **Upload** your menu (text / PDF / image with OCR)
2. **Smart logging** — say "I ate lunch" and the AI lists today's mess items and asks for servings
3. **Mess-aware diet plans** — AI uses mess foods first, adds extras only if targets aren't met
4. **Mess-aware grocery lists** — only items NOT available in mess are listed

---

## 🧮 Macro Calculations

Uses the **Mifflin-St Jeor** equation:

| | Formula |
|---|---|
| **BMR (male)** | 10W + 6.25H − 5A + 5 |
| **BMR (female)** | 10W + 6.25H − 5A − 161 |
| **TDEE** | BMR × activity multiplier |
| **Fat Loss Target** | TDEE − 500 kcal |
| **Muscle Gain Target** | TDEE + 300 kcal |
| **Protein (fat loss)** | 2.2g × kg bodyweight |
| **Protein (muscle gain)** | 2.0g × kg bodyweight |
| **Water Target** | 35ml × kg bodyweight |

---

## 🗄️ Database

SQLite by default — stored at `database/gym_coach.db`.

**14 tables:**
`users` · `food_logs` · `workout_logs` · `workout_sets` · `weight_logs` · `water_logs` · `sleep_logs` · `supplement_logs` · `diet_plans` · `workout_plans` · `grocery_plans` · `chat_history` · `weekly_checkins` · `mess_menus`

All data survives app restarts. The DB is created automatically on first run.

---

## 🔒 Security

- Passwords hashed with **bcrypt** (never stored in plain text)
- Session state managed via Streamlit's `st.session_state`
- API key stored in `.env` (gitignored)
- No data sent to third parties except Anthropic (for AI calls)

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Multi-page web UI |
| `anthropic` | Claude API client |
| `langgraph` | Stateful AI workflow graphs |
| `langchain-anthropic` | LangChain ↔ Claude integration |
| `sqlalchemy` | ORM + database engine |
| `pydantic` | Data validation |
| `plotly` | Interactive charts |
| `pandas` | Data manipulation |
| `bcrypt` | Password hashing |
| `python-dotenv` | Environment variable loading |
| `pdfplumber` | PDF text extraction |
| `Pillow` | Image handling |

---

## 🛠️ Development

```bash
# Run with auto-reload
streamlit run main.py

# Check code style
ruff check app/

# Run type checking
pyright app/
```

---

## 🗺️ Roadmap

- [ ] PostgreSQL support for production deployments
- [ ] Barcode scanner for food logging
- [ ] Wearable device integration (step count, heart rate)
- [ ] Multiple user support / social features
- [ ] Export data as PDF progress report
- [ ] Mobile-optimised layout
- [ ] Notification reminders (water, supplements, workout)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ using Python, Streamlit, LangGraph, and Claude AI*
