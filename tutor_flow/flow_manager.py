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
        self.step_message_count: int = 0
        self.completed: bool = False  # NEW: Tracks if flow is finished

    # -------- Message management --------

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

    # -------- Step logic --------

    def should_advance_step(self, user_message: str) -> bool:
        """
        Decide whether to move to the next scaffold step.
        ENSURES proper flow through all 7 steps.
        """
        user_lower = user_message.lower().strip()
        word_count = len(user_message.split())

        # 1. INITIAL METAPHOR -> STUDENT METAPHOR
        if self.current_step == ScaffoldStep.INITIAL_METAPHOR:
            return len(user_message.strip()) > 10 and word_count >= 2

        # 2. STUDENT METAPHOR -> VISUAL DIAGRAM
        if self.current_step == ScaffoldStep.STUDENT_METAPHOR:
            if self.step_message_count < 1:
                return False
            affirmatives = ["yes", "yeah", "yep", "sure", "ok", "okay", "ready"]
            return any(term in user_lower for term in affirmatives)

        # 3. VISUAL DIAGRAM -> CODE STRUCTURE
        if self.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            if self.step_message_count < 1:
                return False
            affirmatives = ["yes", "yeah", "sure", "ok", "okay", "got it", "makes sense", "cool", "nice"]
            return any(term in user_lower for term in affirmatives)

        # 4. CODE STRUCTURE -> CODE USAGE
        if self.current_step == ScaffoldStep.CODE_STRUCTURE:
            if self.step_message_count < 1:
                return False
            affirmatives = ["yes", "sure", "ok", "okay", "got it", "makes sense"]
            return any(term in user_lower for term in affirmatives)

        # 5. CODE USAGE -> PRACTICE
        if self.current_step == ScaffoldStep.CODE_USAGE:
            if self.step_message_count < 1:
                return False
            affirmatives = ["yes", "sure", "ok", "okay", "got it"]
            answered = word_count >= 5
            return any(term in user_lower for term in affirmatives) or answered

        # 6. PRACTICE -> REFLECTION
        if self.current_step == ScaffoldStep.PRACTICE:
            if self.step_message_count < 1:
                return False
            affirmatives = ["yes", "sure", "ready", "ok", "done"]
            attempted = word_count >= 4
            return any(term in user_lower for term in affirmatives) or attempted

        # 7. REFLECTION -> END
        if self.current_step == ScaffoldStep.REFLECTION:
            is_summary = word_count >= 8
            is_done = any(term in user_lower for term in ["done", "finished"])
            return is_summary or is_done

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
            # We are at the last step and tried to advance
            self.completed = True