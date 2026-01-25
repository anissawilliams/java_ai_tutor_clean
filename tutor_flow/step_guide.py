# tutor_flow/step_guide.py
"""
Generates prompts for each scaffold step.
SIMPLIFIED: Give AI clear context and goals, trust it to execute well.
"""

from typing import List, Optional
from .steps import ScaffoldStep, ConversationMessage


class StepGuide:
    """
    Generates AI prompts for each scaffold step.
    Focus: Clear goals + context. Let AI handle the conversation naturally.
    """

    @staticmethod
    def get_metaphor_prompt(topic) -> str:
        """Generate the initial metaphor prompt."""
        return (
            f"You are starting a tutoring session on {topic.name}.\n\n"
            f"CONCEPT: {topic.concept}\n\n"
            f"METAPHOR TO USE:\n{topic.metaphor_prompt}\n\n"
            "YOUR TASK:\n"
            "1. Introduce yourself briefly\n"
            "2. Explain the concept using the metaphor above\n"
            "3. End by asking: 'What does this remind you of from your own experience?'\n\n"
            "Keep it warm and under 150 words."
        )

    @staticmethod
    def get_response_prompt(
            topic,
            current_step: ScaffoldStep,
            user_input: str,
            context_messages: List[ConversationMessage],
    ) -> str:
        """
        Generate a prompt based on current step and conversation context.

        The AI should:
        - Respond naturally to what the student said
        - Accomplish the goal for this step
        - Transition smoothly to the next topic when appropriate
        """

        # Get topic-specific guidance
        step_key = current_step.value
        topic_guidance = topic.instructions.get(step_key, "")
        if topic_guidance:
            topic_guidance = topic_guidance.replace("{metaphor_prompt}", topic.metaphor_prompt)
            topic_guidance = topic_guidance.replace("{agent_crisis}", topic.agent_crisis)
            topic_guidance = topic_guidance.replace("{agent_solution}", topic.agent_solution)
            topic_guidance = topic_guidance.replace("{topic_name}", topic.name)
            topic_guidance = topic_guidance.replace("{code_focus}", topic.code_focus)

        # Build context from recent messages
        recent_context = ""
        if context_messages:
            recent_context = "RECENT CONVERSATION:\n"
            for msg in context_messages[-3:]:
                role = "Student" if msg.role == "user" else "You"
                recent_context += f"{role}: {msg.content[:100]}...\n"

        # ============================================================
        # STEP-SPECIFIC PROMPTS
        # ============================================================

        if current_step == ScaffoldStep.INITIAL_METAPHOR:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "Respond to what they said and continue explaining the metaphor.\n"
                "End by asking what this reminds them of from their experience.\n"
                "Keep under 100 words."
            )

        if current_step == ScaffoldStep.STUDENT_METAPHOR:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"{recent_context}\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "WHAT TO DO:\n"
                "- If student shared a metaphor/example earlier and now says 'sure', 'yes', 'ready': "
                "They're ready for the visual! Say: 'Great! Let me show you a visual...'\n"
                "- If student just shared a new metaphor/example: Acknowledge it warmly, connect to the concept, "
                f"then introduce the crisis: \"{topic.agent_crisis}\" and ask 'Ready to see how this works visually?'\n\n"
                "Keep under 100 words."
            )

        if current_step == ScaffoldStep.VISUAL_DIAGRAM:
            return (
                f"TOPIC: {topic.name}\n\n"
                "A visual diagram was just shown to the student.\n"
                f"Student said: \"{user_input}\"\n\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "YOUR RESPONSE:\n"
                "- If they're confused: Explain the diagram more clearly\n"
                "- If they understand: Acknowledge and transition to code\n"
                "- Say: 'Now let's look at the actual code...'\n\n"
                "Keep under 75 words."
            )

        if current_step == ScaffoldStep.CODE_STRUCTURE:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"{recent_context}\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                f"CODE FOCUS: {topic.code_focus}\n\n"
                "YOUR TASK (based on conversation state):\n"
                "- If you haven't shown code yet: Show the INTERNAL implementation code, "
                "highlight the key parts, and ask a question about it.\n"
                "- If student answered your question: Validate their answer (RIGHT/WRONG), "
                "explain briefly, then ask 'Ready to see how to use this?'\n"
                "- If student is confused: Clarify without repeating everything.\n\n"
                "Keep under 150 words."
            )

        if current_step == ScaffoldStep.CODE_USAGE:
            return (
                f"TOPIC: {topic.name}\n\n"
                f"Student said: \"{user_input}\"\n\n"
                f"{recent_context}\n"
                f"TOPIC GUIDANCE:\n{topic_guidance}\n\n"
                "YOUR TASK (based on conversation state):\n"
                "- If you haven't shown usage code: Show simple USAGE examples, "
                "explain how it works from the user's perspective, ask a question.\n"
                "- If student answered your question: Validate their answer, "
                "then ask 'Ready to practice with a scenario?'\n"
                "- If student says ready: Confirm and prepare to move on.\n\n"
                "Keep under 120 words."
            )

        if current_step == ScaffoldStep.PRACTICE:
            # Check if student just said a short affirmative vs gave a real answer
            is_just_affirmative = len(user_input.split()) <= 2

            if is_just_affirmative:
                return (
                        f"TOPIC: {topic.name}\n\n"
                        "STUDENT JUST SAID: \"" + user_input + "\" (this is just an affirmative, NOT an answer)\n\n"
                                                               "YOU MUST NOW GIVE A PRACTICE PROBLEM.\n\n"
                                                               "Create a simple scenario like:\n"
                                                               "'Let's practice! If you call factorial(4), walk me through what happens step by step. "
                                                               "What does the call stack look like?'\n\n"
                                                               "DO NOT praise them for a summary they didn't give.\n"
                                                               "DO NOT say 'Great job!' - they haven't done anything yet.\n"
                                                               "JUST GIVE THE PRACTICE PROBLEM.\n"
                                                               "Keep under 75 words."
                )
            else:
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"Student answered your practice problem: \"{user_input}\"\n\n"
                    "VALIDATE THEIR ANSWER:\n"
                    "1. Say 'Correct!' or 'Not quite...'\n"
                    "2. Briefly explain (2 sentences max)\n"
                    "3. Say: 'Ready to summarize what you learned?'\n\n"
                    "Keep under 75 words."
                )

        if current_step == ScaffoldStep.REFLECTION:
            # Check if student just said a short affirmative vs gave a real summary
            word_count = len(user_input.split())
            is_just_affirmative = word_count <= 3

            if is_just_affirmative:
                return (
                        f"TOPIC: {topic.name}\n\n"
                        "STUDENT JUST SAID: \"" + user_input + "\" (this is just an affirmative, NOT a summary)\n\n"
                                                               "YOU MUST NOW ASK FOR THEIR SUMMARY.\n\n"
                                                               "Say exactly: 'In your own words, what did you learn about " + topic.name + " today? "
                                                                                                                                           "What is the base case and why is it important?'\n\n"
                                                                                                                                           "DO NOT say 'Great summary!' - they haven't given one yet.\n"
                                                                                                                                           "DO NOT move to quiz yet.\n"
                                                                                                                                           "JUST ASK THE QUESTION.\n"
                                                                                                                                           "Keep under 50 words."
                )
            else:
                return (
                    f"TOPIC: {topic.name}\n\n"
                    f"Student gave their summary: \"{user_input}\"\n\n"
                    "THIS IS THEIR SUMMARY. ACCEPT IT.\n\n"
                    "Say:\n"
                    "1. 'Excellent summary!' (or similar praise)\n"
                    "2. One specific thing they got right\n"
                    "3. 'You're ready for the quiz!'\n\n"
                    "DO NOT ask follow-up questions.\n"
                    "DO NOT ask them to expand.\n"
                    "THIS IS THE END OF THE LESSON.\n"
                    "Keep under 60 words."
                )

        # Fallback
        return (
            f"Continue teaching {topic.name}.\n"
            f"Student said: \"{user_input}\"\n\n"
            "Respond helpfully and keep the lesson moving forward."
        )