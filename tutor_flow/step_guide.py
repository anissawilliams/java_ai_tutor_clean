from typing import List
from .steps import ScaffoldStep, ConversationMessage


class StepGuide:
    """
    System instructions for each scaffold step.
    OPTIMIZED FOR OPENAI - Clear, directive, structured.
    """

    @staticmethod
    def get_metaphor_prompt(role: str, topic_name: str, topic_concept: str) -> str:
        """Prompt for the initial metaphor generation."""
        return (
            f"Explain {topic_name} using a clear metaphor.\n"
            f"Concept: {topic_concept}\n\n"
            "Use an everyday analogy (suitcase, backpack, etc).\n"
            "Then ask: 'What does this remind you of from your experience?'\n"
            "Keep it under 120 words."
        )

    @staticmethod
    def get_response_prompt(
            role: str,
            topic_name: str,
            current_step: ScaffoldStep,
            user_input: str,
            context_messages: List[ConversationMessage]
    ) -> str:
        """Clear instructions for each step - OpenAI optimized."""

        # 1. INITIAL METAPHOR
        if current_step == ScaffoldStep.INITIAL_METAPHOR:
            return (
                "Give your metaphor for Dynamic ArrayList.\n"
                "Use everyday comparison (suitcase expanding, backpack growing, etc).\n"
                "End with: 'What does this remind you of?'\n"
                "120 words max."
            )

        # 2. STUDENT METAPHOR
        if current_step == ScaffoldStep.STUDENT_METAPHOR:
            return (
                f"Student said: '{user_input}'\n\n"
                "Respond with exactly this structure:\n\n"
                "1. Acknowledge: 'Perfect! [their metaphor] is a great way to think about it.'\n\n"
                "2. Show mini code example:\n"
                "ArrayList<String> items = new ArrayList<>();\n"
                "items.add(\"A\"); // starts small, grows automatically\n\n"
                "3. Ask: 'Ready to see how this works visually?'\n\n"
                "100 words total. No more, no less."
            )

        # 3. VISUAL DIAGRAM
        if current_step == ScaffoldStep.VISUAL_DIAGRAM:
            return (
                "Visual already shown. Student responded.\n\n"
                "Say ONLY: 'Great! Now let's see the actual code that does this.'\n\n"
                "One sentence. Nothing else."
            )

        # 4. CODE STRUCTURE
        if current_step == ScaffoldStep.CODE_STRUCTURE:
            return (
                "Show the resize() method:\n\n"
                "private void resize() {\n"
                "  Object[] newArray = new Object[capacity * 2];\n"
                "  for (int i = 0; i < size; i++) {\n"
                "    newArray[i] = internalArray[i]; // copies every element!\n"
                "  }\n"
                "  internalArray = newArray;\n"
                "}\n\n"
                "Point out the for-loop.\n"
                "Say: 'This loop copies every element. With 1000 elements, that's 1000 copies!'\n"
                "Ask: 'What happens if we have 1000 elements to copy?'\n\n"
                "120 words max."
            )

        # 5. CODE USAGE
        if current_step == ScaffoldStep.CODE_USAGE:
            return (
                f"Student answered: '{user_input}'\n\n"
                "Validate briefly: 'Right, it's expensive!'\n\n"
                "Show usage:\n"
                "ArrayList<String> items = new ArrayList<>();\n"
                "items.add(\"A\");\n"
                "items.add(\"B\");\n\n"
                "Then say: 'Let's practice! Here's a scenario...'\n\n"
                "80 words max."
            )

        # 6. PRACTICE
        if current_step == ScaffoldStep.PRACTICE:
            word_count = len(user_input.split())

            # Count assistant messages in context to determine state
            assistant_message_count = sum(1 for msg in context_messages if msg.role == "assistant")

            # Check if this is first time or after answer
            if assistant_message_count < 1:
                # First time - give problem
                return (
                    "Give this exact practice problem:\n\n"
                    "'Let's practice!\n"
                    "- Capacity: 8\n"
                    "- Current size: 7\n"
                    "- We add 2 elements\n\n"
                    "What happens?'\n\n"
                    "Just ask this. Nothing else."
                )
            elif word_count >= 3:
                # They answered - validate SIMPLY
                return (
                    f"Student answered: '{user_input}'\n\n"
                    "Say EXACTLY:\n"
                    "'Exactly! After adding element 8, the array is full. "
                    "Element 9 triggers a resize: doubles to 16, copies all 8 elements.\n\n"
                    "Ready to summarize what you learned?'\n\n"
                    "Do NOT add extra explanations. Just validate and ask if ready."
                )
            else:
                # They said "yes" - move to reflection
                return "Move to reflection step."
        # 7. REFLECTION
        if current_step == ScaffoldStep.REFLECTION:
            word_count = len(user_input.split())

            if word_count < 8:
                # They just said "yes"
                return (
                    "Ask: 'In your own words, what did you learn about "
                    "ArrayList's internal resizing?'"
                )
            else:
                # They gave summary
                return (
                    "Say:\n"
                    "'Perfect! ArrayList is convenient but resizing costs O(n). "
                    "Understanding this makes you a better programmer.\n\n"
                    "Ready for the quiz?'\n\n"
                    "60 words max."
                )

        return "Continue teaching clearly and concisely."