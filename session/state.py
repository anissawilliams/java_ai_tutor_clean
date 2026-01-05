# session/state.py

import streamlit as st


def init_session_state():
    """Initialize all required session state keys."""

    defaults = {
        "logged_in": False,
        "user": None,
        "user_id": None,
        "email": None,

        # Navigation / routing
        "phase": "dashboard",
        "session_active": False,
        "current_session_id": None,

        # Learning flow
        "flow": None,
        "ai_client": None,
        "messages": [],
        "start_time": None,

        # Quiz
        "quiz_answers": {},
        "quiz_submitted": False,
        "quiz_score": None,
        "quiz_total": None,
        "quiz_results": None,

        # Survey
        "survey_responses": {},

        # Admin testing
        "is_admin_test": False,
        "admin_test_condition": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value