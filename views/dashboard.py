# views/dashboard.py

import time
import streamlit as st

from utils.config import (
    SESSION_DURATION, CONDITIONS, SESSIONS, STUDY_INFO
)

from utils.auth import logout_user
from utils.database import (
    save_session_start, save_message, save_scaffold_progress,
    save_quiz_responses, save_survey_responses, complete_session,
    get_session_status, get_next_session
)

from client.admin_module import (
    should_show_admin_dashboard,
    render_admin_dashboard,
)

from content.research_topics import get_research_topic
from content.static_quiz import get_quiz, score_quiz
from content.survey import render_survey, validate_survey_complete

from client.ai_client import SimpleAIClient
import tutor_flow.flow_manager
from tutor_flow.handlers import (
    generate_initial_message,
    handle_user_message_scaffolded,
    handle_user_message_direct,
)
from characters import get_all_character_names, get_character


def render_dashboard():
    """Render the main dashboard showing session progress."""
    # Admin dashboard first
    if should_show_admin_dashboard(st.session_state.user_id, st.session_state.email):
        render_admin_dashboard()
        return

    # Regular student dashboard
    st.title(f"Welcome, {st.session_state.email}!")

    # Get user data and condition
    from utils.auth import get_user_data  # keep import here to avoid cycles
    user_data = get_user_data(st.session_state.user_id)
    condition = user_data.get("condition", 1)
    condition_name = CONDITIONS.get(condition, "Unknown")

    st.session_state.condition = condition

    # Study info
    with st.expander("ℹ️ About This Study"):
        st.write(STUDY_INFO["description"])
        st.write(f"**Estimated time:** {STUDY_INFO['estimated_time']}")
        st.write(f"**Your condition:** {condition_name}")

    st.write("---")

    # Next session
    next_session = get_next_session(st.session_state.user_id)

    if next_session is None:
        st.success("🎉 You've completed both sessions!")
        st.balloons()
        st.write("Thank you for participating in our research study!")
        st.write("Your responses have been recorded.")

        if st.button("Logout"):
            logout_user()
            st.rerun()
        return

    # Session cards
    st.subheader("Your Sessions")

    for session_key in ["session_1", "session_2"]:
        session_config = SESSIONS[session_key]
        session_id = session_config["id"]
        status = get_session_status(st.session_state.user_id, session_id)

        # Availability
        is_available = True
        if "requires_completion" in session_config:
            required = session_config["requires_completion"]
            required_status = get_session_status(
                st.session_state.user_id,
                SESSIONS["session_1"]["id"],
            )
            if required_status != "completed":
                is_available = False

        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"### {session_config['name']}")
                st.write(session_config["description"])
                st.caption(f"Difficulty: {session_config['difficulty']}")

            with col2:
                if status == "completed":
                    st.success("✅ Complete")
                elif status == "in_progress":
                    st.warning("⏸️ In Progress")
                elif not is_available:
                    st.info("🔒 Locked")
                else:
                    st.info("📝 Available")

            with col3:
                if status in ("completed",) or not is_available:
                    st.write("")
                else:
                    if st.button("Start", key=f"start_{session_id}", type="primary"):
                        start_session(session_id)
                        st.rerun()

            st.write("---")

    # Logout
    if st.button("Logout"):
        logout_user()
        st.rerun()


def render_character_selection():
    """Render character selection (Condition 1 only)."""
    st.title("Choose Your Tutor")

    topic = get_research_topic(st.session_state.current_session_id)
    st.write(f"Select a character to help you learn about {topic.name}")

    characters = get_all_character_names()
    cols = st.columns(3)

    for i, char_name in enumerate(characters[:6]):  # Show first 6
        character = get_character(char_name)

        with cols[i % 3]:
            st.subheader(char_name)
            st.write(f"*{character.personality}*")

            if st.button(f"Choose {char_name}", key=f"char_{char_name}"):
                st.session_state.selected_character = char_name
                st.session_state.phase = "learning"
                st.session_state.start_time = time.time()
                st.session_state.session_active = True
                generate_initial_message(topic, 1)
                st.rerun()


def start_session(session_id: str):
    """Initialize a learning session."""
    topic = get_research_topic(session_id)
    condition = st.session_state.condition

    # Initialize AI client
    st.session_state.ai_client = SimpleAIClient()
    st.session_state.current_session_id = session_id

    # Save session start to database (only if not admin test)
    if not st.session_state.get("is_admin_test", False):
        save_session_start(st.session_state.user_id, session_id, condition)

    # Initialize based on condition
    if condition in [1, 2]:  # Scaffolded
        st.session_state.flow = tutor_flow.flow_manager.TutorFlow(
            topic.name, "Tutor"
        )

        if condition == 1:
            st.session_state.phase = "character_selection"
        else:
            st.session_state.phase = "learning"
            st.session_state.start_time = time.time()
            st.session_state.session_active = True
            generate_initial_message(topic, condition)

    else:
        # Condition 3: direct chat
        st.session_state.phase = "learning"
        st.session_state.start_time = time.time()
        st.session_state.session_active = True
        st.session_state.messages = []

        welcome = (
            f"Hello! I'm here to answer your questions about {topic.name}. "
            "What would you like to know?"
        )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": welcome,
                "timestamp": time.time(),
            }
        )

        if not st.session_state.get("is_admin_test", False):
            save_message(
                st.session_state.user_id,
                session_id,
                "assistant",
                welcome,
            )