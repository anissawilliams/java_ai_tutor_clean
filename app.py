"""
Java Learning Research Study - Main Application
Implements 3 experimental conditions with Firebase integration
"""

import streamlit as st
import time

# Configuration and setup
from utils.config import (
    SESSION_DURATION, CONDITIONS, SESSIONS,
    STUDY_INFO
)

# Admin module
from client.admin_module import (
    should_show_admin_dashboard,
    render_admin_dashboard
)

# Authentication and data
from utils.auth import require_auth, render_login_page, get_user_data, logout_user
from utils.database import (
    save_session_start, save_message, save_scaffold_progress,
    save_quiz_responses, save_survey_responses, complete_session,
    get_session_status, get_next_session
)


# Content
from content.research_topics import get_research_topic
#from code_examples import get_code_example  # <--- Import from the correct file
from content.static_quiz import get_quiz, score_quiz

# AI and learning components
from client.ai_client import SimpleAIClient
from characters import get_all_character_names
from content.survey import render_survey, validate_survey_complete
import tutor_flow.flow_manager
from tutor_flow.steps import ScaffoldStep
from __delete_later.visuals import get_topic_visual

# Admin
from utils.data_export import render_admin_export


def initialize_session_state():
    """Initialize all session state variables."""
    # Auth state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    
    # Session state
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'condition' not in st.session_state:
        st.session_state.condition = None
    if 'phase' not in st.session_state:
        st.session_state.phase = 'dashboard'  # dashboard, learning, quiz, survey, complete
    
    # Learning state
    if 'session_active' not in st.session_state:
        st.session_state.session_active = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'ai_client' not in st.session_state:
        st.session_state.ai_client = None
    if 'flow' not in st.session_state:
        st.session_state.flow = None
    if 'selected_character' not in st.session_state:
        st.session_state.selected_character = None
    
    # Quiz state
    if 'quiz_answers' not in st.session_state:
        st.session_state.quiz_answers = {}
    
    # Survey state
    if 'survey_responses' not in st.session_state:
        st.session_state.survey_responses = {}


def render_dashboard():
    """Render the main dashboard showing session progress."""
    # Check if user is admin
    if should_show_admin_dashboard(st.session_state.user_id, st.session_state.email):
        render_admin_dashboard()
        return
    
    # Regular student dashboard
    st.title(f"Welcome, {st.session_state.email}!")
    
    # Get user data
    user_data = get_user_data(st.session_state.user_id)
    condition = user_data.get('condition', 1)
    condition_name = CONDITIONS.get(condition, 'Unknown')
    
    st.session_state.condition = condition
    
    # Show study info
    with st.expander("ℹ️ About This Study"):
        st.write(STUDY_INFO['description'])
        st.write(f"**Estimated time:** {STUDY_INFO['estimated_time']}")
        st.write(f"**Your condition:** {condition_name}")
    
    st.write("---")
    
    # Check which session is next
    next_session = get_next_session(st.session_state.user_id)
    
    if next_session is None:
        # Both sessions complete!
        st.success("🎉 You've completed both sessions!")
        st.balloons()
        st.write("Thank you for participating in our research study!")
        st.write("Your responses have been recorded.")
        
        if st.button("Logout"):
            logout_user()
            st.rerun()
        return
    
    # Show session cards
    st.subheader("Your Sessions")
    
    for session_key in ['session_1', 'session_2']:
        session_config = SESSIONS[session_key]
        session_id = session_config['id']
        status = get_session_status(st.session_state.user_id, session_id)
        
        # Determine if session is available
        is_available = True
        if 'requires_completion' in session_config:
            required = session_config['requires_completion']
            required_status = get_session_status(st.session_state.user_id, 
                                                SESSIONS['session_1']['id'])
            if required_status != 'completed':
                is_available = False
        
        # Render session card
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"### {session_config['name']}")
                st.write(session_config['description'])
                st.caption(f"Difficulty: {session_config['difficulty']}")
            
            with col2:
                if status == 'completed':
                    st.success("✅ Complete")
                elif status == 'in_progress':
                    st.warning("⏸️ In Progress")
                elif not is_available:
                    st.info("🔒 Locked")
                else:
                    st.info("📝 Available")
            
            with col3:
                if status == 'completed':
                    st.write("")  # Spacing
                elif not is_available:
                    st.write("")  # Can't start yet
                else:
                    if st.button("Start", key=f"start_{session_id}", type="primary"):
                        start_session(session_id)
                        st.rerun()
            
            st.write("---")
    
    # Logout button
    if st.button("Logout"):
        logout_user()
        st.rerun()


def start_session(session_id: str):
    """Initialize a learning session."""
    # Get topic
    topic = get_research_topic(session_id)
    condition = st.session_state.condition
    
    # Initialize AI client
    st.session_state.ai_client = SimpleAIClient()
    st.session_state.current_session_id = session_id

    
    # Save session start to database (only if not admin test)
    if not st.session_state.get('is_admin_test', False):
        save_session_start(st.session_state.user_id, session_id, condition)
    
    # Initialize based on condition
    if condition in [1, 2]:  # Scaffolded conditions
        # Initialize flow
        st.session_state.flow = tutor_flow.flow_manager.TutorFlow(topic.name, "Tutor")
        
        # For condition 1, let them select character
        if condition == 1:
            st.session_state.phase = 'character_selection'
        else:
            # Condition 2: Start directly with generic tutor
            st.session_state.phase = 'learning'
            st.session_state.start_time = time.time()
            st.session_state.session_active = True
            generate_initial_message(topic, condition)
    else:
        # Condition 3: Direct chat (no scaffolding)
        st.session_state.phase = 'learning'
        st.session_state.start_time = time.time()
        st.session_state.session_active = True
        st.session_state.messages = []
        
        # Simple welcome message
        welcome = f"Hello! I'm here to answer your questions about {topic.name}. What would you like to know?"
        st.session_state.messages.append({
            'role': 'assistant',
            'content': welcome,
            'timestamp': time.time()
        })
        
        # Only save if not admin test
        if not st.session_state.get('is_admin_test', False):
            save_message(st.session_state.user_id, session_id, 'assistant', welcome)


from characters import get_character
from tutor_flow.step_guide import StepGuide

def generate_initial_message(topic, condition):
    """Generate the initial learning message."""
    session_id = st.session_state.current_session_id

    if condition == 1:
        character = get_character(st.session_state.selected_character)
        system_prompt = character.get_system_prompt(topic.name)
    else:
        system_prompt = (
            f"You are a helpful CS tutor teaching {topic.name}.\n\n"
            "Your goal is to help the student understand the topic through:\n"
            "1) metaphors and analogies\n"
            "2) conceptual understanding\n"
            "3) code examples\n"
            "4) usage explanations\n\n"
            "Be clear, encouraging, and keep responses under 150 words."
        )

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

    # Add to flow
    st.session_state.flow.add_message("assistant", initial_message)

    if not st.session_state.get("is_admin_test", False):
        save_message(
            st.session_state.user_id,
            session_id,
            "assistant",
            initial_message,
            step=st.session_state.flow.current_step.value,
        )

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
                st.session_state.phase = 'learning'
                st.session_state.start_time = time.time()
                st.session_state.session_active = True
                generate_initial_message(topic, 1)
                st.rerun()


def handle_user_message_scaffolded(user_input: str):
    """Handle user message for scaffolded conditions (1 & 2)."""
    flow = st.session_state.flow
    topic = get_research_topic(st.session_state.current_session_id)
    condition = st.session_state.condition
    session_id = st.session_state.current_session_id
    
    # Add user message
    flow.add_message('user', user_input)
    
    # Only save if not admin test
    if not st.session_state.get('is_admin_test', False):
        save_message(st.session_state.user_id, session_id, 'user', user_input)
    
    # Check step advancement
    old_step = flow.current_step
    if flow.should_advance_step(user_input):
        flow.advance_step()
        
        # Only save if not admin test
        if not st.session_state.get('is_admin_test', False):
            save_scaffold_progress(st.session_state.user_id, session_id, flow.current_step.value)
        
        # Show visual if advancing to CODE_STRUCTURE
        if flow.current_step == ScaffoldStep.CODE_STRUCTURE:
            visual = get_topic_visual(st.session_state.current_session_id)
            flow.add_message('assistant', f"📊 **Visual Diagram:**\n{visual}")
            
            # Only save if not admin test
            if not st.session_state.get('is_admin_test', False):
                save_message(st.session_state.user_id, session_id, 'assistant', 
                            f"📊 **Visual Diagram:**\n{visual}", 
                            step=flow.current_step.value)
    
    # Generate response
    if condition == 1:
        character = get_character(st.session_state.selected_character)
        system_prompt = character.get_system_prompt(topic.name)
    else:
        system_prompt = f"You are a helpful CS tutor teaching {topic.name}."

    response_prompt = StepGuide.get_response_prompt(
        "Tutor",
        topic.name,
        flow.current_step,
        user_input,
        flow.get_recent_context(5),
    )
    
    # Build conversation history
    recent_messages = flow.get_recent_context(5)
    conversation_history = [{'role': m.role, 'content': m.content} for m in recent_messages[:-1]]
    
    try:
        response = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt + "\n\n" + response_prompt,
            user_message=user_input,
            conversation_history=conversation_history
        )
    except:
        response = "I'm having trouble responding. Could you try rephrasing that?"
    
    # Add response
    flow.add_message('assistant', response)
    
    # Only save if not admin test
    if not st.session_state.get('is_admin_test', False):
        save_message(st.session_state.user_id, session_id, 'assistant', response,
                    step=flow.current_step.value)


def handle_user_message_direct(user_input: str):
    """Handle user message for direct chat condition (3)."""
    topic = get_research_topic(st.session_state.current_session_id)
    session_id = st.session_state.current_session_id
    
    # Add user message
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input,
        'timestamp': time.time()
    })
    
    # Only save if not admin test
    if not st.session_state.get('is_admin_test', False):
        save_message(st.session_state.user_id, session_id, 'user', user_input)
    
    # Build conversation history
    conversation_history = [
        {'role': m['role'], 'content': m['content']} 
        for m in st.session_state.messages[-10:]  # Last 10 messages
    ]
    
    # Simple system prompt - no scaffolding
    system_prompt = f"""You are a helpful assistant answering questions about {topic.name} in Java.

Provide clear, accurate answers. Include code examples when helpful. Be concise."""
    
    try:
        response = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt,
            user_message=user_input,
            conversation_history=conversation_history[:-1]
        )
    except:
        response = "I'm having trouble responding. Could you try rephrasing that?"
    
    # Add response
    st.session_state.messages.append({
        'role': 'assistant',
        'content': response,
        'timestamp': time.time()
    })
    
    # Only save if not admin test
    if not st.session_state.get('is_admin_test', False):
        save_message(st.session_state.user_id, session_id, 'assistant', response)


def render_learning_session():
    """Render the learning session (all conditions)."""
    topic = get_research_topic(st.session_state.current_session_id)
    condition = st.session_state.condition
    
    # Admin testing indicator
    if st.session_state.get('is_admin_test', False):
        st.info(f"🔧 **Admin Test Mode** - Testing Condition {condition} - Data will not be saved")
    
    # Header
    st.title(f"Learning: {topic.name}")
    
    # Timer
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
    
    # Check if time is up
    if elapsed >= SESSION_DURATION:
        st.session_state.phase = 'quiz'
        st.rerun()
    
    # Display messages based on condition
    chat_container = st.container(height=500)
    
    with chat_container:
        if condition in [1, 2]:  # Scaffolded
            for msg in st.session_state.flow.messages:
                with st.chat_message(msg.role):
                    st.write(msg.content)
        else:  # Direct chat
            for msg in st.session_state.messages:
                with st.chat_message(msg['role']):
                    st.write(msg['content'])
    
    # Chat input
    user_input = st.chat_input("Type your response...")
    
    if user_input:
        if condition in [1, 2]:
            handle_user_message_scaffolded(user_input)
        else:
            handle_user_message_direct(user_input)
        st.rerun()


def render_quiz():
    """Render the quiz."""
    topic = get_research_topic(st.session_state.current_session_id)
    session_id = st.session_state.current_session_id
    
    st.title(f"📝 Quiz: {topic.name}")
    st.write("Please answer these questions based on what you learned.")
    st.write("---")
    
    quiz_questions = get_quiz(session_id)
    
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    
    if not st.session_state.quiz_submitted:
        # Display questions
        for i, q in enumerate(quiz_questions):
            st.subheader(f"Question {i+1}")
            st.write(q.question)
            
            answer = st.radio(
                "Select your answer:",
                options=q.options,
                key=f"quiz_q_{i}",
                index=None
            )
            
            if answer:
                st.session_state.quiz_answers[i] = answer
            
            st.write("")
        
        # Submit button
        all_answered = len(st.session_state.quiz_answers) == len(quiz_questions)
        
        if st.button("Submit Quiz", type="primary", disabled=not all_answered):
            # Score quiz
            score, total, results = score_quiz(session_id, st.session_state.quiz_answers)
            
            # Only save if not admin test
            if not st.session_state.get('is_admin_test', False):
                save_quiz_responses(st.session_state.user_id, session_id, 
                                  st.session_state.quiz_answers, score, total)
            
            st.session_state.quiz_submitted = True
            st.session_state.quiz_score = score
            st.session_state.quiz_total = total
            st.session_state.quiz_results = results
            st.rerun()
        
        if not all_answered:
            st.info(f"Please answer all questions ({len(st.session_state.quiz_answers)}/{len(quiz_questions)} complete)")
    
    else:
        # Show results
        st.success("✅ Quiz Complete!")
        st.metric("Your Score", f"{st.session_state.quiz_score}/{st.session_state.quiz_total}")
        
        st.write("---")
        
        # Show each question with feedback
        for i, result in enumerate(st.session_state.quiz_results):
            with st.expander(f"Question {i+1} - {'✅ Correct' if result['is_correct'] else '❌ Incorrect'}"):
                st.write(f"**Q:** {result['question']}")
                st.write(f"**Your answer:** {result['user_answer']}")
                if not result['is_correct']:
                    st.write(f"**Correct answer:** {result['correct_answer']}")
                st.info(f"**Explanation:** {result['explanation']}")
        
        st.write("---")
        
        if st.button("Continue to Survey", type="primary"):
            st.session_state.phase = 'survey'
            st.rerun()


def render_survey_page():
    """Render the survey."""
    topic = get_research_topic(st.session_state.current_session_id)
    session_id = st.session_state.current_session_id
    condition = st.session_state.condition
    
    responses = render_survey(topic.name, condition)
    st.session_state.survey_responses = responses
    
    # Check if complete
    is_complete, missing = validate_survey_complete(responses)
    
    st.write("---")
    
    if st.button("Submit Survey", type="primary", disabled=not is_complete):
        # Only save if not admin test
        if not st.session_state.get('is_admin_test', False):
            # Save to database
            save_survey_responses(st.session_state.user_id, session_id, responses)
            
            # Mark session complete
            complete_session(st.session_state.user_id, session_id)
        
        st.session_state.phase = 'complete'
        st.rerun()
    
    if not is_complete:
        st.warning(f"Please answer all required questions ({missing} remaining)")


def render_complete():
    """Render completion page."""
    st.title("✅ Session Complete!")
    st.success("Thank you for completing this session!")
    
    # Check if there's another session
    next_session = get_next_session(st.session_state.user_id)
    
    if next_session:
        st.write("You have one more session to complete later in the semester.")
        st.write("We'll let you know when it's time!")
    else:
        st.balloons()
        st.write("You've completed both sessions!")
        st.write("Thank you for participating in our research!")
    
    if st.button("Back to Dashboard", type="primary"):
        # Reset session state
        st.session_state.current_session_id = None
        st.session_state.phase = 'dashboard'
        st.session_state.session_active = False
        st.session_state.flow = None
        st.session_state.messages = []
        st.session_state.quiz_answers = {}
        st.session_state.survey_responses = {}
        st.session_state.quiz_submitted = False
        st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Java Learning Study",
        page_icon="🎓",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Check authentication
    if not require_auth():
        render_login_page()
        return
    
    # Show admin export if URL parameter
    if st.query_params.get("admin") == "true":
        render_admin_export()
        return
    
    # Route based on phase
    if st.session_state.phase == 'dashboard':
        render_dashboard()
    elif st.session_state.phase == 'character_selection':
        render_character_selection()
    elif st.session_state.phase == 'learning':
        render_learning_session()
    elif st.session_state.phase == 'quiz':
        render_quiz()
    elif st.session_state.phase == 'survey':
        render_survey_page()
    elif st.session_state.phase == 'complete':
        render_complete()


if __name__ == "__main__":
    main()
