# tutor_flow/step_guide.py

from typing import Iterable
from .steps import ScaffoldStep, ConversationMessage
from content.research_topics import get_research_topic


class StepGuide:

    @staticmethod
    def get_metaphor_prompt(character_name: str, topic_name: str, concept: str) -> str:
        return (
            f"You are {character_name}, introducing the topic: {topic_name}.\n\n"
            f"Start with a simple metaphor:\n\"{concept}\"\n\n"
            "Then ask: \"What does this metaphor remind you of from your own experience?\"\n"
            "Keep your response under 80 words."
        )

    @staticmethod
    def format_context(messages: Iterable[ConversationMessage]) -> str:
        lines = []
        for m in messages:
            prefix = "Student" if m.role == "user" else "Tutor"
            lines.append(f"{prefix} ({m.step.value}): {m.content}")
        return "\n".join(lines) if lines else "No recent context."

    @staticmethod
    def get_response_prompt(
        character_name: str,
        topic_key: str,
        current_step: ScaffoldStep,
        user_message: str,
        recent_context: Iterable[ConversationMessage],
    ) -> str:

        topic = get_research_topic(topic_key)
        recent_text = StepGuide.format_context(recent_context)

        # Pull instructions from the topic
        instructions = topic.instructions_for(current_step.value)

        # Fill in placeholders
        instructions = instructions.format(
            metaphor_prompt=topic.metaphor_prompt,
            agent_crisis=topic.agent_crisis,
            agent_solution=topic.agent_solution,
            code_focus=topic.code_focus,
        )

        # Inject contrast if the topic defines one
        if current_step == ScaffoldStep.CODE_STRUCTURE:
            contrast = topic.instructions_for("contrast")
            if contrast:
                instructions += "\n\n" + contrast.format(
                    agent_crisis=topic.agent_crisis,
                    code_focus=topic.code_focus,
                )

        return (
            f"You are {character_name} teaching {topic.name}.\n"
            f"Current scaffold stage: {current_step.value}.\n\n"
            f"INSTRUCTIONS:\n{instructions}\n\n"
            "Recent conversation context:\n"
            f"{recent_text}\n\n"
            f"Student just said:\n\"{user_message}\"\n\n"
            "Now respond as the tutor. Keep your reply under 150 words, "
            "be clear and encouraging, and stay tightly focused on this stage."
        )