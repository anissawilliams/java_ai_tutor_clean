# views/admin.py

import streamlit as st
from firebase_admin import db

from utils.database import get_all_users
from utils.config import SESSIONS
from utils.auth import logout_user

from content.research_topics import get_research_topic
from content.static_quiz import get_quiz, score_quiz
from content.survey import render_survey, validate_survey_complete

from client.ai_client import SimpleAIClient
from tutor_flow.flow_manager import TutorFlow
from tutor_flow.step_guide import StepGuide
from characters import get_character


# ---------------------------------------------------------
# Admin configuration
# ---------------------------------------------------------

ADMIN_EMAILS = [
    "anissawilliamschs@gmail.com",
    "hashemi@cofc.edu",
    "rashidp@cofc.edu",
    "tiwaria@cofc.edu",
]


def is_admin(email: str) -> bool:
    """Check if an email is an admin."""
    return email.lower() in [e.lower() for e in ADMIN_EMAILS]


def get_or_create_admin_user(user_id: str, email: str) -> dict:
    """
    Create or get admin user with special privileges.
    Admins can manually select conditions.
    """
    try:
        ref = db.reference(f"admins/{user_id}")
        admin_data = ref.get()

        if not admin_data:
            admin_data = {
                "email": email,
                "is_admin": True,
                "created_at": None,
                "selected_condition": None,
                "sessions": {
                    "arraylist": {"status": "not_started"},
                    "recursion": {"status": "not_started"},
                },
            }
            ref.set(admin_data)

        return admin_data

    except Exception as e:
        st.error(f"Error managing admin user: {e}")
        return {}


def should_show_admin_dashboard(user_id: str, email: str) -> bool:
    """
    Determine if admin dashboard should be shown.
    """
    if not is_admin(email):
        return False

    get_or_create_admin_user(user_id, email)
    return True


# ---------------------------------------------------------
# Admin Dashboard UI
# ---------------------------------------------------------

def render_admin_dashboard():
    """Render special admin dashboard with condition selection."""
    st.title("🔧 Admin Dashboard")
    st.write(f"Welcome, **{st.session_state.email}** (Admin)")

    st.info("As an admin, you can test all three experimental conditions.")
    st.write("---")

    # -------------------------
    # Condition selection
    # -------------------------
    st.subheader("Select Test Condition")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Condition 1")
        st.write("**Character-Based Scaffolded**")
        st.caption("Character personalities + 5-step scaffolding + visuals")
        if st.button("Test Condition 1", key="admin_c1", type="primary"):
            st.session_state.admin_test_condition = 1
            st.session_state.condition = 1
            st.rerun()

    with col2:
        st.markdown("### Condition 2")
        st.write("**Non-Character Scaffolded**")
        st.caption("Generic tutor + 5-step scaffolding + visuals")
        if st.button("Test Condition 2", key="admin_c2", type="primary"):
            st.session_state.admin_test_condition = 2
            st.session_state.condition = 2
            st.rerun()

    with col3:
        st.markdown("### Condition 3")
        st.write("**Direct Chat (Control)**")
        st.caption("Plain Q&A, no scaffolding, no visuals")
        if st.button("Test Condition 3", key="admin_c3", type="primary"):
            st.session_state.admin_test_condition = 3
            st.session_state.condition = 3
            st.rerun()

    st.write("---")

    # -------------------------
    # Admin Tools
    # -------------------------
    with st.expander("🛠️ Admin Tools"):
        st.write("**Data Export**")
        st.write("Access the data export dashboard:")
        if st.button("Go to Data Export"):
            st.query_params.update({"admin": "true"})
            st.rerun()

        st.write("---")

        st.write("**User Management**")
        users = get_all_users()

        total_users = len([u for u in users.values() if not u.get("is_admin", False)])
        condition_counts = {1: 0, 2: 0, 3: 0}

        for user_data in users.values():
            if not user_data.get("is_admin", False):
                condition = user_data.get("condition", 0)
                if condition in condition_counts:
                    condition_counts[condition] += 1

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students", total_users)
        with col2:
            st.metric("Condition 1", condition_counts[1])
        with col3:
            st.metric("Condition 2", condition_counts[2])
        with col4:
            st.metric("Condition 3", condition_counts[3])

    # -------------------------
    # Session selection
    # -------------------------
    st.write("---")
    st.subheader("Test Sessions")

    if "admin_test_condition" not in st.session_state:
        st.info("👆 Please select a condition above to start testing.")
        return

    st.success(f"Testing as Condition {st.session_state.admin_test_condition}")

    for session_key in ["session_1", "session_2"]:
        session_config = SESSIONS[session_key]
        session_id = session_config["id"]

        admin_session_id = f"admin_{st.session_state.user_id}_{session_id}"

        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"### {session_config['name']}")
                st.write(session_config["description"])
                st.caption(f"Difficulty: {session_config['difficulty']}")

            with col2:
                if st.button("Start Test", key=f"admin_start_{session_id}", type="secondary"):
                    st.session_state.is_admin_test = True
                    from views.dashboard import start_session
                    start_session(session_id)
                    st.rerun()

            st.write("---")

    if st.button("Logout"):
        logout_user()
        st.rerun()


# ---------------------------------------------------------
# Admin Test Session Helpers
# ---------------------------------------------------------

def start_admin_test_session(session_id: str):
    """Start a test session for admin."""
    from content.research_topics import get_research_topic
    import time

    topic = get_research_topic(session_id)
    condition = st.session_state.admin_test_condition

    st.session_state.ai_client = SimpleAIClient()
    st.session_state.current_session_id = session_id
    st.session_state.start_time = time.time()
    st.session_state.is_admin_test = True

    if condition in [1, 2]:
        st.session_state.flow = TutorFlow(topic.name, "Tutor")

        if condition == 1:
            st.session_state.phase = "character_selection"
        else:
            st.session_state.phase = "learning"
            st.session_state.session_active = True
            generate_admin_initial_message(topic, condition)

    else:
        st.session_state.phase = "learning"
        st.session_state.session_active = True
        st.session_state.messages = []

        welcome = (
            f"Hello! I'm here to answer your questions about {topic.name}. "
            "What would you like to know?"
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": welcome, "timestamp": time.time()}
        )


def generate_admin_initial_message(topic, condition):
    """Generate initial message for admin test."""
    if condition == 1:
        character = get_character(st.session_state.selected_character)
        system_prompt = character.get_system_prompt(topic.name)
    else:
        system_prompt = f"You are a helpful CS tutor teaching {topic.name}."

    metaphor_prompt = StepGuide.get_metaphor_prompt(
        "Tutor", topic.name, topic.concept
    )

    try:
        initial_message = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt,
            user_message=metaphor_prompt,
            temperature=0.9,
        )
    except Exception:
        initial_message = (
            f"Hello! Let's learn about {topic.name}.\n\n"
            f"{topic.metaphor_prompt}\n\n"
            "What does this remind you of from your own experience?"
        )

    st.session_state.flow.add_message("assistant", initial_message)


# ---------------------------------------------------------
# Wrappers to skip DB writes during admin tests
# ---------------------------------------------------------

def save_admin_message_wrapper(original_save_function):
    def wrapper(*args, **kwargs):
        if st.session_state.get("is_admin_test", False):
            return
        return original_save_function(*args, **kwargs)
    return wrapper


def save_admin_quiz_wrapper(original_save_function):
    def wrapper(*args, **kwargs):
        if st.session_state.get("is_admin_test", False):
            return
        return original_save_function(*args, **kwargs)
    return wrapper


def save_admin_survey_wrapper(original_save_function):
    def wrapper(*args, **kwargs):
        if st.session_state.get("is_admin_test", False):
            return
        return original_save_function(*args, **kwargs)
    return wrapper