from typing import List
from .steps import ScaffoldStep, ConversationMessage


class StepGuide:
    """
    Generates system instructions for each scaffold step.
    Ensures the AI behaves correctly for the specific phase of learning.
    """

    @staticmethod
    def get_metaphor_prompt(role: str, topic_name: str, topic_concept: str) -> str:
        """Prompt for the initial metaphor generation."""
        return (
            f"Explain {topic_name} using a clear, non-technical metaphor.\n"
            f"Concept to cover: {topic_concept}\n"
            "Compare the technical concept to a real-world object or situation.\n"
            "End by asking the student what this reminds them of from their own experience."
        )

    @staticmethod
    def get_response_prompt(
            role: str,
            topic_name: str,
            current_step: ScaffoldStep,
            user_input: str,
            context_messages: List[ConversationMessage]
    ) -> str:
        """
        Returns the specific instruction for the current step.
        """

        # 1. INITIAL METAPHOR
        if current_step == ScaffoldStep.INITIAL_METAPHOR:
            return (
                "The user is responding to your metaphor.\n"
                "1. Acknowledge their response warmly.\n"
                "2. Briefly explain the 'Conflict' (why the old way/fixed array is bad).\n"
                "3. Explain the 'Resolution' (how the dynamic way fixes it).\n"
                "4. Ask: 'Ready to see how this works visually?'"
            )

        # 2. STUDENT METAPHOR
        if current_step == ScaffoldStep.STUDENT_METAPHOR:
            return (
                "The user has shared their own analogy or agreed to yours.\n"
                "1. Validate their analogy if they gave one.\n"
                "2. Transition to the next step.\n"
                "3. Ask: 'Ready to see a visual diagram of how this works?'"
            )

        # 3. VISUAL DIAGRAM
        if current_step == ScaffoldStep.VISUAL_DIAGRAM:
            # Note: The actual diagram is usually injected by the logic layer before this.
            return (
                "You have just shown (or are about to show) a visual diagram.\n"
                "1. Explain the steps in the diagram briefly (Step 1, 2, 3).\n"
                "2. Ask a checking question to ensure they understand the visual flow.\n"
                "   (e.g., 'Does that resizing logic make sense?')"
            )

        # 4. CODE STRUCTURE
        if current_step == ScaffoldStep.CODE_STRUCTURE:
            return (
                "Now explain the internal code structure.\n"
                "1. Show a brief code snippet (e.g., the resize method or internal array).\n"
                "2. Highlight a specific line (like the copy loop).\n"
                "3. Ask a specific observation question:\n"
                "   'What do you notice about...?' or 'Why do we need to...?'"
            )

        # 5. CODE USAGE
        if current_step == ScaffoldStep.CODE_USAGE:
            return (
                "Explain how to USE this data structure.\n"
                "1. Show 2-3 lines of code on how to instantiate and add items.\n"
                "2. IMPORTANT: Ask a critical thinking question about Performance/Cost.\n"
                "   (e.g., 'What happens to performance if we add 1000 items and it resizes often?')"
            )

        # 6. PRACTICE
        if current_step == ScaffoldStep.PRACTICE:
            # CHECK CONTEXT: Did the user just answer the usage question?
            # If the user's last message was long (> 5 words), they likely answered the previous question.
            user_answered_prev = len(user_input.split()) > 5

            validation_instruction = ""
            if user_answered_prev:
                validation_instruction = (
                    "CRITICAL: The user just answered your previous question about performance/usage. "
                    "Start by VALIDATING their answer (e.g., 'Exactly, copying is expensive...').\n"
                )

            return (
                f"{validation_instruction}"
                "Then, present a short conceptual practice problem or scenario.\n"
                "1. Give a scenario (e.g., 'Capacity is 8, size is 7, we add 2 items').\n"
                "2. Ask them what happens internally.\n"
                "Keep it focused on the mechanics we just learned."
            )

        # 7. REFLECTION
        if current_step == ScaffoldStep.REFLECTION:
            # Similar check: Did they answer the practice problem?
            return (
                "The user has answered the practice problem.\n"
                "1. Confirm if they were right or wrong.\n"
                "2. Ask them to summarize what they learned in 1-2 sentences.\n"
                "3. Focus on the trade-offs (convenience vs. performance)."
            )

        # Fallback
        return f"Continue teaching {topic_name}. Be helpful and encouraging."