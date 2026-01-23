from typing import List
from .steps import ScaffoldStep, ConversationMessage


class StepGuide:
    """
    Generates system instructions for each scaffold step.
    POLISHED VERSION with smooth transitions and validation.
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
        POLISHED with clear transitions and validation.
        """

        # 1. INITIAL METAPHOR
        if current_step == ScaffoldStep.INITIAL_METAPHOR:
            return (
                "The student shared their metaphor/analogy.\n\n"
                "Response structure:\n"
                "1. Acknowledge warmly: 'Great metaphor!' or 'Perfect analogy!'\n"
                "2. Introduce the CONFLICT (why fixed arrays are a problem)\n"
                "3. Tease the SOLUTION (we can solve this)\n"
                "4. Ask: 'Ready to see how this works visually?'\n\n"
                "Keep response under 100 words.\n"
                "Be encouraging and build excitement for what's next."
            )

        # 2. STUDENT METAPHOR
        if current_step == ScaffoldStep.STUDENT_METAPHOR:
            return (
                "The student said they're ready to see the visual.\n\n"
                "Give ONE transition sentence:\n"
                "'Perfect! Let me show you what happens inside the computer...'\n\n"
                "Then STOP. The visual diagram will appear automatically with explanation.\n"
                "Do NOT continue talking. Just that one sentence."
            )

        # 3. VISUAL DIAGRAM
        if current_step == ScaffoldStep.VISUAL_DIAGRAM:
            return (
                "The visual diagram already appeared WITH step-by-step walkthrough.\n"
                "The student is responding to: 'Does this diagram help you see how it works?'\n\n"
                "If they said yes/got it:\n"
                "'Excellent! Now let's look at the actual Java code that does this...'\n\n"
                "Do NOT:\n"
                "- Re-show the visual\n"
                "- Re-explain the steps\n"
                "- Repeat anything\n\n"
                "Just give ONE transition sentence to code. That's it."
            )

        # 4. CODE STRUCTURE
        if current_step == ScaffoldStep.CODE_STRUCTURE:
            return (
                "Show the code that implements this concept.\n\n"
                "Structure:\n"
                "1. Show the key method (resize, recursive function, etc.)\n"
                "2. Point to ONE specific line (the copy loop, the recursive call)\n"
                "3. Ask a LEADING question:\n"
                "   'What do you think happens if we have 1000 elements to copy?'\n\n"
                "Accept answers like:\n"
                "- 'slow' / 'expensive' / 'takes time'\n"
                "- 'it copies them all'\n"
                "- Any reasonable engagement\n\n"
                "Keep under 150 words.\n"
                "Do NOT re-explain concepts from previous steps."
            )

        # 5. CODE USAGE
        if current_step == ScaffoldStep.CODE_USAGE:
            user_answered = len(user_input.split()) > 5
            
            validation = ""
            if user_answered:
                validation = (
                    "FIRST: Validate their answer!\n"
                    "- If they said 'slow/expensive': 'Exactly! Copying is O(n)...'\n"
                    "- If they gave specifics: 'Good thinking!'\n\n"
                )
            
            return (
                f"{validation}"
                "Then show simple USAGE example (3-4 lines):\n"
                "ArrayList<String> items = new ArrayList<>();\n"
                "items.add(\"A\");\n"
                "items.add(\"B\");  // etc.\n\n"
                "Ask specific question:\n"
                "'If we start with capacity 4 and keep adding items up to 100, "
                "how many times will it resize?'\n\n"
                "Accept:\n"
                "- Specific numbers\n"
                "- 'Multiple times' / 'several'\n"
                "- Questions\n\n"
                "Validate briefly, then transition: 'Let's practice with a scenario...'"
            )

        # 6. PRACTICE (CRITICAL: ADD VALIDATION)
        if current_step == ScaffoldStep.PRACTICE:
            user_answered = len(user_input.split()) > 4
            
            if user_answered:
                # They answered the practice problem - VALIDATE IT
                return (
                    "The student just answered your practice scenario.\n\n"
                    "CRITICAL VALIDATION STEPS:\n"
                    "1. Tell them if they're RIGHT or WRONG\n"
                    "   - If RIGHT: 'Exactly correct!'\n"
                    "   - If WRONG: 'Not quite...'\n\n"
                    "2. Explain the correct answer:\n"
                    "   - Walk through what happens step-by-step\n"
                    "   - Keep it under 75 words\n\n"
                    "3. Ask: 'Ready to summarize what you learned today?'\n\n"
                    "Do NOT skip validation. Students need to know if they got it right."
                )
            else:
                # First time at this step - give the practice problem
                return (
                    "Give a concrete practice scenario.\n\n"
                    "Example:\n"
                    "'Let's practice! Imagine:\n"
                    " - Current capacity: 8\n"
                    " - Current size: 7\n"
                    " - We add 2 new elements\n"
                    " What happens internally?'\n\n"
                    "Keep scenario simple and focused on the core mechanism we learned."
                )

        # 7. REFLECTION
        if current_step == ScaffoldStep.REFLECTION:
            return (
                "The student gave their summary.\n\n"
                "Final response structure:\n"
                "1. Validate: 'Perfect!' or 'Exactly!'\n"
                "2. Add final insight:\n"
                "   'Understanding this hidden work makes you a better programmer - "
                "   you'll know when to use ArrayList and when not to.'\n"
                "3. Close with encouragement:\n"
                "   'Great work today! Now let's test your knowledge with a quick quiz.'\n\n"
                "Keep under 75 words total.\n"
                "This is the wrap-up - make it encouraging and conclusive."
            )

        # Fallback
        return f"Continue teaching {topic_name}. Be helpful and encouraging."
