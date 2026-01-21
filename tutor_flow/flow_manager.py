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

    # -------- Message management --------

    def add_message(self, role: RoleType, content: str) -> None:
        """Append a message tagged with the current scaffold step."""
        msg = ConversationMessage(
            role=role,
            content=content,
            step=self.current_step,
        )
        self.messages.append(msg)

    def get_recent_context(self, n: int = 5) -> List[ConversationMessage]:
        """Return the last n messages for prompt context."""
        if n <= 0:
            return []
        return self.messages[-n:]

    # -------- Step logic --------

    def should_advance_step(self, user_message: str) -> bool:
        """
        Decide whether to move to the next scaffold step based on the
        student's latest message.
        """
        user_lower = user_message.lower()

        if self.current_step == ScaffoldStep.INITIAL_METAPHOR:
            # Move on once they give a reasonably substantive metaphor/response
            return len(user_message.strip()) > 15

        if self.current_step == ScaffoldStep.STUDENT_METAPHOR:
            # Only advance when they explicitly signal readiness
            ready_terms = ["ready", "go", "show me", "yes", "ok", "okay",
                           "understand", "yep", "yeah"]
            return any(term in user_lower for term in ready_terms)

        if self.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            # Only advance when they explicitly signal readiness
            ready_terms = ["ready", "go", "show me", "yes", "ok", "okay",
                           "understand", "yep", "yeah", "helpful", "interesting"]
            return any(term in user_lower for term in ready_terms)

        if self.current_step == ScaffoldStep.CODE_STRUCTURE:
            # Advance after acknowledgment of manual logic / "hidden work"
            ack_terms = ["makes sense", "i see", "copy", "expensive",
                         "heavy", "got it", "understand", "ohhh"]
            return any(term in user_lower for term in ack_terms)

        if self.current_step == ScaffoldStep.CODE_USAGE:
            # Move to practice once they engage at least minimally
            return len(user_message.strip()) > 10

        if self.current_step == ScaffoldStep.PRACTICE:
            next_step = ScaffoldStep.REFLECTION

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