# session/auth_handler.py

import streamlit as st
from utils.auth import firebase_login, set_session, logout_user as legacy_logout


def login(email: str, password: str):
    """Handle login using Firebase email/password."""
    try:
        user_data = firebase_login(email, password)
        set_session(user_data)

        # Reset admin flags
        st.session_state.is_admin_test = False
        st.session_state.admin_test_condition = None

        # Move to dashboard
        st.session_state.phase = "dashboard"
        st.rerun()

    except Exception as e:
        st.error(f"Login failed: {e}")


def logout():
    """Clear session state and redirect to login."""
    legacy_logout()

    for key in [
        "condition", "admin_test_condition", "is_admin_test",
        "session_active", "current_session_id", "messages",
        "flow", "phase", "ai_client", "start_time",
        "quiz_answers", "survey_responses", "quiz_submitted"
    ]:
        st.session_state.pop(key, None)

    st.session_state.logged_in = False
    st.session_state.phase = "dashboard"
    st.rerun()


def expose_handlers():
    """Make login/logout functions available to views."""
    st.session_state.handle_login = login
    st.session_state.handle_logout = logout