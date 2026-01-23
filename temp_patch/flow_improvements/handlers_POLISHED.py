import time
import streamlit as st
from utils.database import (
    save_message,
    save_scaffold_progress
)

def generate_initial_message(topic, condition):
    """Generate the initial learning message for scaffolded conditions."""
    from content.characters import get_character
    from tutor_flow.step_guide import StepGuide
    
    session_id = st.session_state.current_session_id

    # Build system prompt
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
            "CRITICAL RULES:\n"
            "- Give ONE focused explanation per response\n"
            "- Do NOT repeat information from previous messages\n"
            "- Move forward through the material, don't circle back\n"
            "- If you already explained something, reference it briefly and move on\n"
            "- Keep responses under 150 words\n"
            "- Be clear and encouraging"
        )

    # Build intro + metaphor prompt
    if condition == 1:
        character_name = st.session_state.selected_character
        intro_text = (
            f"Hello! I'm {character_name}, and I'm here to help you understand {topic.name}.\n\n"
            f"**What you'll learn:**\n"
            f"{topic.concept}\n\n"
            f"I'll guide you through this step-by-step. Let's start with a helpful way to think about this.\n\n"
        )
    else:
        intro_text = (
            f"Hello! Welcome to our session on {topic.name}.\n\n"
            f"**Learning objective:**\n"
            f"{topic.concept}\n\n"
            f"I'll guide you through this using clear explanations and examples. Let's begin!\n\n"
        )
    
    metaphor_prompt = StepGuide.get_metaphor_prompt(
        "Tutor", topic.name, topic.concept
    )
    
    full_prompt = intro_text + metaphor_prompt

    # Generate message
    try:
        initial_message = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt,
            user_message=full_prompt,
            temperature=0.9,
        )
    except Exception:
        initial_message = (
            f"Hello! Let's learn about {topic.name}.\n\n"
            f"**What we'll cover:** {topic.concept}\n\n"
            f"{topic.metaphor_prompt}\n\n"
            "What does this remind you of from your own experience?"
        )

    # Add to flow
    st.session_state.flow.add_message("assistant", initial_message)

    # Save to database
    save_message(
        st.session_state.user_id,
        session_id,
        "assistant",
        initial_message,
        step=st.session_state.flow.current_step.value,
    )


def handle_user_message_scaffolded(user_input: str):
    """Handle user message for scaffolded conditions (1 & 2)."""
    from content.characters import get_character
    from tutor_flow.step_guide import StepGuide
    from tutor_flow.steps import ScaffoldStep
    from content.research_topics import get_research_topic
    from content.visuals import get_topic_visual
    
    flow = st.session_state.flow
    topic = get_research_topic(st.session_state.current_session_id)
    condition = st.session_state.condition
    session_id = st.session_state.current_session_id

    # Add user message
    flow.add_message("user", user_input)
    save_message(st.session_state.user_id, session_id, "user", user_input)

    # Step advancement
    if flow.should_advance_step(user_input):
        flow.advance_step()
        save_scaffold_progress(
            st.session_state.user_id,
            session_id,
            flow.current_step.value
        )

        # ✅ CRITICAL FIX: Show visual WITH explanation
        if flow.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            visual = get_topic_visual(st.session_state.current_session_id)
            
            # Complete message with visual AND walkthrough
            if topic.key == 'arraylist':
                walkthrough = (
                    "Let me walk you through this:\n"
                    "- **Step 1**: The old array is full (4/4 elements)\n"
                    "- **Step 2**: Create a new, larger array (capacity 8)\n"
                    "- **Step 3**: Copy all elements to the new array\n"
                    "- **Step 4**: Add the new element (E)\n\n"
                    "Does this diagram help you see how the resizing works?"
                )
            else:  # recursion
                walkthrough = (
                    "Let me walk you through this:\n"
                    "- **Building up**: Each call adds to the stack\n"
                    "- **Base case**: Stops the recursion (n=1)\n"
                    "- **Unwinding**: Stack returns values back up\n\n"
                    "Can you see how the stack builds up and then unwinds?"
                )
            
            visual_message = (
                "Perfect! Here's a visual diagram showing exactly how this works.\n\n"
                f"📊 **Visual Diagram:**\n{visual}\n\n"
                f"{walkthrough}"
            )
            
            flow.add_message("assistant", visual_message)
            save_message(
                st.session_state.user_id,
                session_id,
                "assistant",
                visual_message,
                step=flow.current_step.value,
            )
            # Return immediately - visual message is complete
            return

        # Check for session completion
        start_time = st.session_state.get('start_time', time.time())
        elapsed_minutes = (time.time() - start_time) / 60

        if (flow.completed or elapsed_minutes >= 15) and not st.session_state.get('quiz_ready', False):
            st.session_state.quiz_ready = True
            st.rerun()

    # Build system prompt
    if condition == 1:
        character = get_character(st.session_state.selected_character)
        system_prompt = character.get_system_prompt(topic.name)
    else:
        system_prompt = f"You are a helpful CS tutor teaching {topic.name}."

    # Build response prompt
    response_prompt = StepGuide.get_response_prompt(
        "Tutor",
        topic.name,
        flow.current_step,
        user_input,
        flow.get_recent_context(5),
    )

    # Build conversation history
    recent_messages = flow.get_recent_context(5)
    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in recent_messages[:-1]
    ]

    # Generate response
    try:
        response = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt + "\n\n" + response_prompt,
            user_message=user_input,
            conversation_history=conversation_history,
        )
    except Exception:
        response = "I'm having trouble responding. Could you try rephrasing that?"

    # Add response
    flow.add_message("assistant", response)
    save_message(
        st.session_state.user_id,
        session_id,
        "assistant",
        response,
        step=flow.current_step.value,
    )


def handle_user_message_direct(user_input: str):
    """Handle user message for direct chat condition (3)."""
    from content.research_topics import get_research_topic
    
    topic = get_research_topic(st.session_state.current_session_id)
    session_id = st.session_state.current_session_id

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": time.time(),
    })
    save_message(st.session_state.user_id, session_id, "user", user_input)

    # Build conversation history
    conversation_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-10:]
    ]

    # Simple system prompt
    system_prompt = (
        f"You are a helpful assistant answering questions about {topic.name} in Java.\n\n"
        "Provide clear, accurate answers. Include code examples when helpful. Be concise."
    )

    # Generate response
    try:
        response = st.session_state.ai_client.generate_response(
            system_prompt=system_prompt,
            user_message=user_input,
            conversation_history=conversation_history[:-1],
        )
    except Exception:
        response = "I'm having trouble responding. Could you try rephrasing that?"

    # Add response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": time.time(),
    })
    save_message(st.session_state.user_id, session_id, "assistant", response)
