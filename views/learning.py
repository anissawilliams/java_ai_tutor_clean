# views/learning.py

import time
import streamlit as st

from utils.config import SESSION_DURATION
from content.research_topics import get_research_topic

from tutor_flow.handlers import (
    handle_user_message_scaffolded,
    handle_user_message_direct,
)


def render_learning_session():
    """Render the learning session (all conditions)."""

    topic = get_research_topic(st.session_state.current_session_id)
    condition = st.session_state.condition

    # -------------------------
    # Admin testing indicator
    # -------------------------
    if st.session_state.get("is_admin_test", False):
        st.info(
            f"🔧 **Admin Test Mode** — Testing Condition {condition}. "
            "Data will not be saved."
        )

    # -------------------------
    # Header + Timer
    # -------------------------
    st.title(f"Learning: {topic.name}")

    elapsed = time.time() - st.session_state.start_time
    remaining = max(0, SESSION_DURATION - elapsed)
    mins = int(remaining // 60)
    secs = int(remaining % 60)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**Topic:** {topic.name} ({topic.difficulty})")
    with col2:
        st.metric("Time Left", f"{mins}:{secs:02d}")

    st.write("---")

    # -------------------------
    # Time up → move to quiz
    # -------------------------
    if elapsed >= SESSION_DURATION:
        st.session_state.phase = "quiz"
        st.rerun()

    # -------------------------
    # Chat display
    # -------------------------
    top_content = st.container()
    with top_content:
        st.title(f"**Topic:** {topic.name}")
        st.write(f"Let's learn about {topic.name} together!")

        st.write("---")

    chat_history_container = st.container()

    # 3. Create a container for the Input (This "pins" it to the end of the history)
    input_container = st.container()

    with input_container:
        user_input = st.chat_input("Type your response...")

    # 4. Render History INTO the history container
    with chat_history_container:
        if condition in [1, 2]:
            for msg in st.session_state.flow.messages:
                with st.chat_message(msg.role):
                    st.write(msg.content)
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

    # 5. Logic Handling
    if user_input:
        if condition in [1, 2]:
            handle_user_message_scaffolded(user_input)
        else:
            handle_user_message_direct(user_input)
        st.rerun()