import time
import streamlit as st
# Lazy imports to avoid circular dependencies
# from content.characters import get_character
# from tutor_flow.step_guide import StepGuide
# from tutor_flow.steps import ScaffoldStep
# from content.research_topics import get_research_topic
# from content.visuals import get_topic_visual
from utils.database import (
    save_message,
    save_scaffold_progress
)


def generate_initial_message(topic, condition):
    """Generate the initial learning message for scaffolded conditions."""
    from characters import get_character
    from tutor_flow.step_guide import StepGuide

    session_id = st.session_state.current_session_id

    # 1. Define the base personality/goal
    if condition == 1:
        character = get_character(st.session_state.selected_character)
        base_system = character.get_system_prompt(topic.name)
    else:
        base_system = (
            f"You are a helpful CS tutor teaching {topic.name}.\n\n"
            "Your goal is to help the student understand the topic through:\n"
            "1) metaphors and analogies\n"
            "2) conceptual understanding\n"
            "3) code examples\n"
            "4) usage explanations\n\n"
            "Be clear, encouraging, and keep responses under 150 words."
        )

    # 2. Get the specific instructions for this step
    # We move this to the system side so the AI knows these are 'rules' to follow.
    metaphor_instructions = StepGuide.get_metaphor_prompt(
        "Tutor", topic.name, topic.concept
    )

    # Combine personality with current task instructions
    full_system_prompt = f"{base_system}\n\n### CURRENT TASK:\n{metaphor_instructions}"

    # 3. Create a 'Trigger' user message
    # Instead of sending the intro text AS the user, we tell the AI
    # to start the conversation using that specific intro.
    if condition == 1:
        character_name = st.session_state.selected_character
        trigger_message = (
            f"Start the session. Introduce yourself as {character_name}, "
            f"explain that the learning objective is: {topic.concept}, "
            f"and then provide the metaphor as instructed."
        )
    else:
        trigger_message = (
            f"Start the session. Welcome the student to {topic.name}, "
            f"state that the objective is {topic.concept}, "
            f"and then provide the metaphor as instructed."
        )

    # Generate message
    try:
        initial_message = st.session_state.ai_client.generate_response(
            system_prompt=full_system_prompt,
            user_message=trigger_message,
            temperature=0.9,
        )
    except Exception:
        # Fallback remains the same
        initial_message = (
            f"Hello! Let's learn about {topic.name}.\n\n"
            f"**What we'll cover:** {topic.concept}\n\n"
            "Imagine a suitcase that automatically grows bigger as you pack more clothes into it. "
            "What does this remind you of from your own experience?"
        )

    # Add to flow and save
    st.session_state.flow.add_message("assistant", initial_message)
    save_message(
        st.session_state.user_id,
        session_id,
        "assistant",
        initial_message,
        step=st.session_state.flow.current_step.value,
    )


def handle_user_message_scaffolded(user_input: str):
    """Handle user message for scaffolded conditions (1 & 2)."""
    from characters import get_character
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

        # Show visual at VISUAL_DIAGRAM step
        if flow.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            visual = get_topic_visual(st.session_state.current_session_id)
            
            visual_intro = (
                "Great! Now let me show you a visual diagram to help you see how this works.\n\n"
            )
            
            flow.add_message("assistant", f"{visual_intro}📊 **Visual Diagram:**\n{visual}")
            save_message(
                st.session_state.user_id,
                session_id,
                "assistant",
                f"{visual_intro}📊 **Visual Diagram:**\n{visual}",
                step=flow.current_step.value,
            )

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
