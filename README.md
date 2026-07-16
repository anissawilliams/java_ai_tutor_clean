# Java AI Tutor — Research System

A Streamlit-based intelligent tutoring system built for a CofC IRB-approved research study on AI-mediated Java instruction. Students learn Java topics through one of three experimental conditions, take a quiz, and complete a survey. All data is stored in Firebase Realtime Database.

**Study status:** Data collection complete (Spring 2026). System is in handoff mode — maintained for potential follow-up studies and ongoing paper writing.

---

## Quick Start

### Prerequisites
- Python 3.10+
- Firebase service account credentials (get from Anissa or the ITS Lab)
- OpenAI API key

### Setup

```bash
git clone https://github.com/anissawilliams/java_ai_tutor_clean.git
cd java_ai_tutor_clean
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml` using the template:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Then fill in real credentials
```

### Run

```bash
streamlit run app.py
```

### Debug tools (no login required)

- `/?debug=true` — Firebase debug dashboard, view raw data
- `/?export=true` — Export all session data as CSV

---

## Repo Structure

```
java_ai_tutor_clean/
│
├── app.py                        # Entry point — run this
├── requirements.txt
│
├── content/                      # Study content
│   ├── research_topics.py        # Topic definitions (ArrayList, Recursion, Queue)
│   ├── static_quiz.py            # Quiz questions with difficulty ratings (1–5)
│   ├── survey.py                 # Post-session survey questions
│   ├── visuals.py                # ASCII diagrams shown during scaffold steps
│   └── characters.py             # AI tutor personas (used in Condition 1 only)
│
├── tutor_flow/                   # Scaffold state machine
│   ├── steps.py                  # ScaffoldStep enum (7 steps)
│   ├── flow_manager.py           # TutorFlow class — tracks step, advances on signals
│   ├── step_guide.py             # Per-step system prompts for the AI
│   └── handlers.py               # Message handling for all 3 conditions
│
├── utils/
│   ├── config.py                 # ⚙️  All study settings — start here
│   ├── database.py               # Firebase read/write operations
│   ├── firebase_config.py        # Firebase init from secrets.toml
│   ├── firebase_debug.py         # Debug dashboard (/?debug=true)
│   ├── data_export.py            # CSV export (/?export=true)
│   └── auth.py                   # User auth + condition assignment
│
├── session/
│   ├── state.py                  # Streamlit session state initialization
│   ├── auth_handler.py           # Login/logout handlers
│   └── session_manager.py        # Session lifecycle
│
├── routing/
│   ├── router.py                 # Central routing — maps phase → view
│   └── guards.py                 # Login gate
│
├── views/                        # One file per UI screen
│   ├── login.py
│   ├── dashboard.py              # Post-login home; shows available sessions
│   ├── learning.py               # Main tutoring interface
│   ├── quiz.py
│   ├── survey.py
│   └── complete.py
│
├── client/
│   └── ai_client.py              # OpenAI API wrapper
│
├── scripts/                      # One-off admin scripts (not part of app)
│   ├── create_firebase_users.py  # Bulk user creation
│   ├── BULK_USER_CREATION_GUIDE.md
│   └── *.csv                     # Section rosters (Spring 2026)
│
└── data_visualization/           # Analysis scripts and raw data exports
    ├── all_data_array_list_session.json   # Full ArrayList session export
    ├── array_list_session_data.json       # Earlier partial export
    ├── trimmed_data.json                  # Redacted sample used for analysis dev
    ├── retrieve_session_data.py           # Pulls data from Firebase
    ├── real_analytics.py                  # Main analysis script
    ├── analyze_tutor_data.py              # Secondary analysis
    └── analytics.py / sandbox.py         # Exploratory work
```

---

## Configuration

**`utils/config.py` is the control panel.** Key settings:

| Setting | Purpose |
|---|---|
| `SESSION_DURATION` | Learning phase time limit (seconds) |
| `CONDITIONS` | Maps condition number to name |
| `MANUAL_CONDITION_ASSIGNMENTS` | Override random assignment for specific users |
| `SESSIONS` | Topic sequence, dates, ordering |
| `SHOW_DEBUG_INFO` | Set `True` for testing, `False` for production |
| `SHOW_SKIP_BUTTONS` | Shows "Skip to Quiz" button when `True` |

---

## Credentials

Never commit `.streamlit/secrets.toml`. It needs:

- `OPENAI_API_KEY` — OpenAI key for GPT-4
- `[firebase]` block — full Firebase service account JSON fields

See `.streamlit/secrets.toml.example` for the required structure.

Firebase project: `java-learning-study-d2e9b`

---

## Files to Ignore

These are in the repo but not part of the live system:

- `views/admin.py` and `client/admin_module.py` — dead code, admin system was removed
- `data_visualization/sandbox.py` — exploratory scratch work
- `scripts/*.csv` — Spring 2026 rosters, historical only
