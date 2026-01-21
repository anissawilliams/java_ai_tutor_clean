# tutor_flow/steps.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal
import time


class ScaffoldStep(Enum):
    """Stages of the pedagogical scaffold."""
    INITIAL_METAPHOR = "initial_metaphor"
    STUDENT_METAPHOR = "student_metaphor"
    VISUAL_DIAGRAM = "visual_diagram"
    CODE_STRUCTURE = "code_structure"
    CODE_USAGE = "code_usage"
    PRACTICE = "practice"
    REFLECTION = "reflection"


RoleType = Literal["user", "assistant", "system"]


@dataclass
class ConversationMessage:
    """Message exchanged during a scaffolded tutoring session."""
    role: RoleType
    content: str
    step: ScaffoldStep
    timestamp: float = field(default_factory=time.time)