# tutor_flow/flow_manager.py

from __future__ import annotations
from typing import List
from .steps import ScaffoldStep, ConversationMessage, RoleType


class TutorFlow:
    """
    Manages the scaffolded tutoring flow:
    - current step
    - message history
    - when to advance steps
    """

    def __init__(self, topic_name: str, character_name: str) -> None:
        self.topic_name: str = topic_name
        self.character_name: str = character_name
        self.current_step: ScaffoldStep = ScaffoldStep.INITIAL_METAPHOR
        self.messages: List[ConversationMessage] = []
        self.step_message_count: int = 0  # Track messages at current step

    # -------- Message management --------

    def add_message(self, role: RoleType, content: str) -> None:
        """Append a message tagged with the current scaffold step."""
        msg = ConversationMessage(
            role=role,
            content=content,
            step=self.current_step,
        )
        self.messages.append(msg)
        
        # Increment counter for assistant messages
        if role == "assistant":
            self.step_message_count += 1

    def get_recent_context(self, n: int = 5) -> List[ConversationMessage]:
        """Return the last n messages for prompt context."""
        if n <= 0:
            return []
        return self.messages[-n:]

    # -------- Step logic --------

    def should_advance_step(self, user_message: str) -> bool:
        """
        Decide whether to move to the next scaffold step.
        Balanced: accepts natural student responses but avoids premature advancement.
        Also considers context from previous tutor message.
        """
        user_lower = user_message.lower().strip()
        word_count = len(user_message.split())
        
        # Get last tutor message for context
        last_tutor_msg = ""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                last_tutor_msg = msg.content.lower()
                break

        if self.current_step == ScaffoldStep.INITIAL_METAPHOR:
            # Move on once they give substantive metaphor (15+ chars, 3+ words)
            return len(user_message.strip()) > 15 and word_count >= 3

        if self.current_step == ScaffoldStep.STUDENT_METAPHOR:
            # If tutor asked "ready to see", accept any affirmative
            tutor_asked_ready = any(phrase in last_tutor_msg for phrase in 
                                   ["ready to see", "want to see", "ready for", 
                                    "shall we", "let's look"])
            
            affirmatives = ["yes", "yeah", "yep", "sure", "ok", "okay", "ready",
                          "let's go", "show me", "i'm ready", "sounds good", 
                          "go ahead", "continue", "yup", "definitely", "absolutely"]
            
            # Advance if affirmative OR if tutor asked and student responded positively
            return any(term in user_lower for term in affirmatives) or (
                tutor_asked_ready and word_count <= 3 and len(user_lower) < 20
            )

        if self.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            # Accept affirmatives OR acknowledgment
            affirmatives = ["yes", "yeah", "yep", "sure", "ok", "okay", "got it",
                          "makes sense", "i see", "understand", "helpful", "clear",
                          "cool", "nice", "good", "right", "yup", "great"]
            return any(term in user_lower for term in affirmatives)

        if self.current_step == ScaffoldStep.CODE_STRUCTURE:
            # Accept general affirmatives OR questions about usage
            affirmatives = ["yes", "yeah", "sure", "ok", "okay", "got it",
                          "makes sense", "i see", "understand", "good", "right",
                          "cool", "nice", "great"]
            usage_questions = ["how do i", "how would i", "how to use", 
                             "what about", "can i"]
            return (any(term in user_lower for term in affirmatives) or
                   any(term in user_lower for term in usage_questions))

        if self.current_step == ScaffoldStep.CODE_USAGE:
            # Accept affirmatives to move to practice
            affirmatives = ["yes", "yeah", "sure", "ok", "okay", "got it",
                          "makes sense", "understand", "good", "ready",
                          "let's practice", "practice", "try", "cool"]
            return any(term in user_lower for term in affirmatives)

        if self.current_step == ScaffoldStep.PRACTICE:
            # Accept affirmatives to move to reflection
            affirmatives = ["yes", "yeah", "sure", "ok", "okay", "got it",
                          "done", "finished", "good", "understand", "ready",
                          "no more", "that's all", "yup", "yep"]
            return any(term in user_lower for term in affirmatives)

        # Default: do NOT advance
        return False

    def advance_step(self) -> None:
        """Advance to the next scaffold step if one exists."""
        steps = list(ScaffoldStep)
        try:
            idx = steps.index(self.current_step)
        except ValueError:
            return

        if idx < len(steps) - 1:
            self.current_step = steps[idx + 1]
            self.step_message_count = 0  # Reset counter for new step