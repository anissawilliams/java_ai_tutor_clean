# views/survey.py

import streamlit as st

from content.research_topics import get_research_topic
from content.survey import render_survey, validate_survey_complete
from utils.database import save_survey_responses, complete_session


def render_survey_page():
    """Render the post-learning survey."""

    session_id = st.session_state.current_session_id
    topic = get_research_topic(session_id)
    condition = st.session_state.condition

    # ---------------------------------------------------------
    # Render survey questions (UI comes from content/survey.py)
    # ---------------------------------------------------------
    responses = render_survey(topic.name, condition)
    st.session_state.survey_responses = responses

    # ---------------------------------------------------------
    # Validate completeness
    # ---------------------------------------------------------
    is_complete, missing = validate_survey_complete(responses)

    st.write("---")

    # ---------------------------------------------------------
    # Submit button
    # ---------------------------------------------------------
    if st.button("Submit Survey", type="primary", disabled=not is_complete):

        # Save unless admin test
        if not st.session_state.get("is_admin_test", False):
            save_survey_responses(
                st.session_state.user_id,
                session_id,
                responses
            )
            complete_session(
                st.session_state.user_id,
                session_id
            )

        # Move to completion screen
        st.session_state.phase = "complete"
        st.rerun()

    # ---------------------------------------------------------
    # Warning if incomplete
    # ---------------------------------------------------------
    if not is_complete:
        st.warning(
            f"Please answer all required questions "
            f"({missing} remaining)"
        )