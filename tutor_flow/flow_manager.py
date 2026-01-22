# tutor_flow/flow_manager.py

from __future__ import annotations
from typing import List
from .steps import ScaffoldStep, ConversationMessage, RoleType


class TutorFlow:
    """
    Manages the scaffolded tutoring flow.
    POLISHED VERSION with smooth step progression.
    """

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
        POLISHED with expanded keywords for better flow.
        """
        user_lower = user_message.lower().strip()
        word_count = len(user_message.split())

        # 1. INITIAL METAPHOR → STUDENT METAPHOR
        if self.current_step == ScaffoldStep.INITIAL_METAPHOR:
            # Student gives metaphor (at least 2 words, 10+ chars)
            return len(user_message.strip()) > 10 and word_count >= 2

        # 2. STUDENT METAPHOR → VISUAL DIAGRAM
        if self.current_step == ScaffoldStep.STUDENT_METAPHOR:
            # Require at least 1 tutor response (asked "ready to see visual?")
            if self.step_message_count < 1:
                return False

            # Expanded affirmatives
            affirmatives = ["yes", "yeah", "yep", "yup", "sure", "ok", "okay", "ready",
                            "definitely", "totally", "absolutely", "cool", "great", "nice",
                            "sounds good", "let's", "go", "show", "next"]
            return any(term in user_lower for term in affirmatives)

        # 3. VISUAL DIAGRAM → CODE STRUCTURE
        if self.current_step == ScaffoldStep.VISUAL_DIAGRAM:
            # Require at least 1 tutor response (visual appeared with question)
            if self.step_message_count < 1:
                return False

            # Expanded affirmatives and understanding indicators
            affirmatives = ["yes", "yeah", "yep", "sure", "ok", "okay", "got it",
                            "makes sense", "i see", "helpful", "cool", "nice", "clear",
                            "definitely", "totally", "understand", "understood", "yup",
                            "show me", "next", "continue", "go ahead"]
            return any(term in user_lower for term in affirmatives)

        # 4. CODE STRUCTURE → CODE USAGE
        if self.current_step == ScaffoldStep.CODE_STRUCTURE:
            # Require at least 1 tutor response (showed code + asked question)
            if self.step_message_count < 1:
                return False

            # Accept reasonable answers or affirmatives
            affirmatives = ["yes", "sure", "ok", "okay", "got it", "makes sense",
                            "cool", "nice", "next", "continue"]
            answered = word_count >= 3  # "slow", "it's expensive", etc.
            return any(term in user_lower for term in affirmatives) or answered

        # 5. CODE USAGE → PRACTICE
        if self.current_step == ScaffoldStep.CODE_USAGE:
            # Require at least 1 tutor response (showed usage + asked question)
            if self.step_message_count < 1:
                return False

            # Accept answers or affirmatives
            affirmatives = ["yes", "sure", "ok", "okay", "ready", "let's", "go", "next"]
            answered = word_count >= 4  # They gave an answer
            return any(term in user_lower for term in affirmatives) or answered

        # 6. PRACTICE → REFLECTION
        if self.current_step == ScaffoldStep.PRACTICE:
            # First check: Did we give the practice problem?
            if self.step_message_count < 1:
                return False

            # After student answers problem (5+ words), advance to allow validation
            if self.step_message_count == 1:
                answered = word_count >= 5
                if answered:
                    return True

            # After validation (2+ messages) and they said ready, advance to reflection
            if self.step_message_count >= 2:
                affirmatives = ["yes", "ready", "sure", "ok", "okay", "let's", "go"]
                return any(term in user_lower for term in affirmatives)

            return False

        # 7. REFLECTION → END
        # flow_manager.py - REFLECTION advancement
        if self.current_step == ScaffoldStep.REFLECTION:
            if self.step_message_count < 1:
                return False

            # Advance after they give summary (8+ words) OR say they're done/good/ready
            is_summary = word_count >= 8
            is_done = any(term in user_lower for term in ["yes", "ready", "sure", "ok",
                                                          "okay", "let's", "done", "good",
                                                          "finished", "thanks", "thank you"])
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
            old_step = self.current_step
            self.current_step = steps[idx + 1]
            self.step_message_count = 0
            # Debug logging (optional - comment out in production)
            # print(f"[FLOW] Advanced: {old_step.value} → {self.current_step.value}")
        else:
            # Reached the end
            self.completed = True
