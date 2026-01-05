# routing/router.py

import streamlit as st

from routing.guards import login_required, admin_only

# Views
from views.login import render_login_page
from views.dashboard import render_dashboard, render_character_selection
from views.learning import render_learning_session
from views.quiz import render_quiz
from views.survey import render_survey_page
from views.complete import render_complete
from views.admin import render_admin_dashboard


def route():
    """
    Central routing function.
    Determines which view to show based on session state and URL params.
    """
    # ---------------------------------------------------------
    # LOGIN GATE
    # ---------------------------------------------------------
    if not login_required():
        return render_login_page()

    # ---------------------------------------------------------
    # ADMIN DASHBOARD (explicit request)
    # ---------------------------------------------------------
    page = st.query_params.get("page", None)

    if page == "admin" and admin_only():
        return render_admin_dashboard()

    # ---------------------------------------------------------
    # PHASE-BASED ROUTING
    # ---------------------------------------------------------
    phase = st.session_state.get("phase", "dashboard")

    if phase == "dashboard":
        return render_dashboard()

    if phase == "character_selection":
        return render_character_selection()

    if phase == "learning":
        return render_learning_session()

    if phase == "quiz":
        return render_quiz()

    if phase == "survey":
        return render_survey_page()

    if phase == "complete":
        return render_complete()

    # ---------------------------------------------------------
    # FALLBACK
    # ---------------------------------------------------------
    return render_dashboard()