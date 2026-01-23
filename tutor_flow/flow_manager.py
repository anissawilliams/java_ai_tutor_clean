# tutor_flow/flow_manager.py
# STABLE VERSION FOR OPENAI - PRODUCTION READY

from __future__ import annotations
from typing import List
from .steps import ScaffoldStep, ConversationMessage, RoleType


class TutorFlow:
    """Manages the scaffolded tutoring flow - STABLE for OpenAI."""

    def __init__(self, topic_name: str, character_name: str) -> None:
        self.topic_name: str = topic_name
        self.character_name: str = character_name
        self.current_step: ScaffoldStep = ScaffoldStep.INITIAL_METAPHOR
        self.messages: List[ConversationMessage] = []
        self.step_message_count: int = 0
        self.completed: bool = False

    def add_message(self, role: RoleType, content: str) -> None:
        """Append a message tagged with the current scaffold step."""
        msg = ConversationMessage(
            role=role,
            content=content,
            step=self.current_step,
        )
        self.messages.append(msg)
        if role == "assistant":
            self.step_message_count += 1

    def get_recent_context(self, n: int = 5) -> List[ConversationMessage]:
        """Return the last n messages for prompt context."""
        if n <= 0:
            return []
        return self.messages[-n:]

    def should_advance_step(self, user_message: str) -> bool:
        """
        Decide whether to move to the next scaffold step.
        STABLE - tested with OpenAI.
        """
        user_lower = user_message.lower().strip()
        word_count = len(user_message.split())

        # 1. INITIAL_METAPHOR → STUDENT_METAPHOR
        # Student gives their metaphor (at least 10 chars)
        if self.current_step == ScaffoldStep.INITIAL_METAPHOR:
            return len(user_message.strip()) > 10

        # 2. STUDENT_METAPHOR → VISUAL DIAGRAM
        # After tutor responds, student says ready
        if self.current_step == ScaffoldStep.STUDENT_METAPHOR:
            if self.step_message_count < 1:
                return False
            affirmatives = ["yes", "yeah", "sure", "ok", "ready", "yep"]
            return any(term in user_lower for term in affirmatives)

        # 3. VISUAL DIAGRAM → CODE STRUCTURE
        # After visual shown, student acknowledges
        if self.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            if self.step_message_count < 1:
                return False
            affirmatives = ["yes", "ok", "got it", "cool", "nice", "sure"]
            return any(term in user_lower for term in affirmatives)

        # 4. CODE STRUCTURE → CODE USAGE
        # After code shown, student responds
        if self.current_step == ScaffoldStep.CODE_STRUCTURE:
            if self.step_message_count < 1:
                return False
            # Accept any response with 2+ words
            return word_count >= 2

        # 5. CODE USAGE → PRACTICE
        # After usage shown, student responds
        if self.current_step == ScaffoldStep.CODE_USAGE:
            if self.step_message_count < 1:
                return False
            return word_count >= 2

        # 6. PRACTICE → REFLECTION
        # Need 2 exchanges (question + validation)
        if self.current_step == ScaffoldStep.PRACTICE:
            if self.step_message_count < 2:
                return False
            affirmatives = ["yes", "ready", "ok", "sure"]
            return any(term in user_lower for term in affirmatives)

        # 7. REFLECTION → END
        if self.current_step == ScaffoldStep.REFLECTION:
            if self.step_message_count < 1:
                return False
            # Advance after summary OR after saying ready for quiz
            is_summary = word_count >= 8
            is_ready = any(term in user_lower for term in ["yes", "ready", "ok", "sure"])
            return is_summary or is_ready

        return False

    def advance_step(self) -> None:
        """Advance to the next scaffold step or mark flow as complete."""
        steps = list(ScaffoldStep)
        try:
            idx = steps.index(self.current_step)
        except ValueError:
            return

        if idx < len(steps) - 1:
            self.current_step = steps[idx + 1]
            self.step_message_count = 0
        else:
            self.completed = True