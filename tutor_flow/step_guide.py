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
                "2. Briefly connect to the technical concept (1 sentence)\n"
                "3. End by asking: 'Ready to see how this works visually?'\n\n"
                "CRITICAL: You MUST end with that exact question.\n"
                "Keep response under 80 words.\n"
                "Do NOT explain further. Just acknowledge and ask."
            )

        # 2. STUDENT METAPHOR
        if current_step == ScaffoldStep.STUDENT_METAPHOR:
            return (
                "The student said they're ready (yes/sure/ok).\n\n"
                "Give ONLY this transition:\n"
                "'Perfect! Let me show you what happens inside the computer...'\n\n"
                "DO NOT ADD ANYTHING ELSE. Just that one sentence.\n"
                "The visual will appear automatically next."
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
                "Show the RESIZE method implementation (the internal 'hidden work').\n\n"
                "Example code to show:\n"
                "```java\n"
                "private void resize() {\n"
                "  Object[] newArray = new Object[capacity * 2]; // Create larger array\n"
                "  for (int i = 0; i < size; i++) { // Copy loop - THIS IS KEY!\n"
                "    newArray[i] = internalArray[i]; // Copying each element\n"
                "  }\n"
                "  internalArray = newArray; // Switch to new array\n"
                "}\n"
                "```\n\n"
                "CRITICAL - Point out the COPY LOOP:\n"
                "'Notice the for-loop on line 3? That copies EVERY element one by one.\n"
                "This is the hidden work - it happens automatically, but it takes time.'\n\n"
                "Then ask:\n"
                "'What do you think happens if we have 1000 elements to copy?'\n\n"
                "This step is about showing the INTERNAL MECHANISM, not usage.\n"
                "Do NOT show ArrayList usage code here - that's the next step.\n"
                "Keep explanation under 150 words."
            )

        # 5. CODE USAGE
        if current_step == ScaffoldStep.CODE_USAGE:
            # Check if they tried to answer the previous question
            user_lower = user_input.lower()
            has_answer_keywords = any(word in user_lower
                                      for word in ["slow", "expensive", "time", "copy",
                                                   "multiple", "several", "many"])
            is_substantive = len(user_input.split()) >= 4
            pure_affirmative = user_lower.strip() in ["yes", "yeah", "yep", "sure",
                                                      "ok", "okay", "ready"]

            if (has_answer_keywords or is_substantive) and not pure_affirmative:
                validation = (
                    "FIRST: Validate their answer!\n"
                    "- If they said 'slow/expensive': 'Exactly! Copying is O(n)...'\n"
                    "- If they gave specifics: 'Good thinking!'\n\n"
                )
            else:
                validation = ""

            return (
                f"{validation}"
                "Then show simple USAGE example (3-4 lines):\n"
                "ArrayList<String> items = new ArrayList<>();\n"
                "items.add(\"A\");\n"
                "items.add(\"B\"); // etc.\n\n"
                "Ask specific question:\n"
                "'If we start with capacity 4 and keep adding items up to 100, "
                "how many times will it resize?'\n\n"
                "Accept:\n"
                "- Specific numbers\n"
                "- 'Multiple times' / 'several'\n"
                "- Questions\n\n"
                "Validate briefly, then transition: 'Let's practice with a scenario...'"
            )

        # 6. PRACTICE
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
