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

        # 1. INITIAL METAPHOR (AI gives their metaphor first)
        if current_step == ScaffoldStep.INITIAL_METAPHOR:
            return (
                f"Explain {topic_name} using a clear, non-technical metaphor.\n"
                "Compare the technical concept to a real-world object or situation.\n"
                "End by asking the student what this reminds them of from their own experience."
            )

        # 2. STUDENT METAPHOR (Student gave theirs, AI responds with code)
        if current_step == ScaffoldStep.STUDENT_METAPHOR:
            return (
                "The student shared their metaphor/analogy.\n\n"
                "You MUST do ALL FOUR of these:\n"
                "1. Acknowledge warmly: 'Perfect analogy!' or 'Great example!'\n"
                "2. Connect their metaphor to Dynamic ArrayLists (1-2 sentences):\n"
                "   'Just like your expandable suitcase, a Dynamic ArrayList...'\n"
                "3. Show a tiny code snippet (3-5 lines) that illustrates the concept:\n"
                "   ```java\n"
                "   ArrayList<String> items = new ArrayList<>();\n"
                "   items.add(\"item1\"); // starts small, auto-expands!\n"
                "   ```\n"
                "4. End with: 'Ready to see how this works visually?'\n\n"
                "CRITICAL: Include ALL steps. Keep total response under 120 words."
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
                "DO NOT ASK QUESTIONS. DO NOT RECAP.\n\n"
                "Show ONLY this code:\n\n"
                "```java\n"
                "private void resize() {\n"
                "  Object[] newArray = new Object[capacity * 2];\n"
                "  for (int i = 0; i < size; i++) { // ← KEY LINE\n"
                "    newArray[i] = internalArray[i];\n"
                "  }\n"
                "  internalArray = newArray;\n"
                "}\n"
                "```\n\n"
                "Say: 'Notice the for-loop? It copies EVERY element. "
                "What happens with 1000 elements?'\n\n"
                "That's it. 100 words max."
            )

        # 5. CODE USAGE
        if current_step == ScaffoldStep.CODE_USAGE:
            return (
                "Brief validation (1 sentence).\n\n"
                "Show usage:\n"
                "```java\n"
                "ArrayList<String> items = new ArrayList<>();\n"
                "items.add(\"A\");\n"
                "items.add(\"B\");\n"
                "```\n\n"
                "Say: 'Let's practice with a scenario...'\n\n"
                "Under 75 words. NO questions."
            )

        # 6. PRACTICE
        # step_guide.py - PRACTICE section
        if current_step == ScaffoldStep.PRACTICE:
            user_lower = user_input.lower()
            has_numbers = any(char.isdigit() for char in user_input)
            # Check word count - but make sure it's a substantial answer
            user_answered = len(user_input.split()) >= 2 or has_numbers

            # Check if they're indicating readiness to move on (after validation)
            readiness_keywords = ["ready", "sure", "ok", "okay", "yes", "let's", "go"]
            is_ready = any(keyword in user_lower for keyword in readiness_keywords)

            # If they answered with substance (not just "yes"), validate
            if user_answered and not is_ready:
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
                # First time at this step OR they said they're ready
                # Give the practice problem
                return (
                    "Give a simple word problem - NO CODE.\n\n"
                    "CRITICAL: Do NOT show any Java code. Just give numbers.\n\n"
                    "Example format:\n"
                    "'Let's practice! Imagine:\n"
                    "- Current capacity: 8\n"
                    "- Current size: 7\n"
                    "- We add 2 new elements\n\n"
                    "What happens internally?'\n\n"
                    "Use different numbers than the example.\n"
                    "Keep it to 3-4 lines maximum.\n"
                    "NO CODE. Just the scenario and question."
                )

        # 7. REFLECTION
        if current_step == ScaffoldStep.REFLECTION:
            user_word_count = len(user_input.split())

            # Check if they just said "yes/ready" vs actually gave a summary
            if user_word_count < 8:
                # They just said "yes" - ask for the actual summary
                return (
                    "The student said they're ready to summarize.\n\n"
                    "Now ask them to give their summary:\n"
                    "'Great! In your own words, what did you learn about "
                    "how ArrayLists work internally?'\n\n"
                    "Keep it brief and encouraging."
                )
            else:
                # They gave a real summary - validate and wrap up
                return (
                    "The student gave their summary.\n\n"
                    "Final response structure:\n"
                    "1. Validate: 'Perfect!' or 'Exactly!'\n"
                    "2. Add final insight:\n"
                    "   'Understanding this hidden work makes you a better programmer - "
                    "   you'll know when to use ArrayList and when not to.'\n"
                    "3. Ask: 'Ready for the quiz?'\n\n"
                    "Keep under 75 words total.\n"
                    "This is the wrap-up - make it encouraging and ask if ready for quiz."
                )

        # Fallback
        return f"Continue teaching {topic_name}. Be helpful and encouraging."
