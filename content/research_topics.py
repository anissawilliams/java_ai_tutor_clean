"""
Research Topics
ArrayList and Recursion content for the study
Updated with Professor's "Stop Sign" and "Suitcase" methodologies
"""

from dataclasses import dataclass
from typing import List, Dict

@dataclass
# content/research_topics.py

class ResearchTopic:
    """
    Holds ALL topic-specific content AND step-specific instructional guidance.
    StepGuide becomes a generic engine that simply pulls from this.
    """

    def __init__(
        self,
        key: str,
        name: str,
        difficulty: str,
        concept: str,
        key_points: list[str],
        metaphor_prompt: str,
        agent_crisis: str,
        agent_solution: str,
        code_focus: str,
        instructions: dict[str, str],
    ):
        self.key = key
        self.name = name
        self.difficulty = difficulty
        self.concept = concept
        self.key_points = key_points
        self.metaphor_prompt = metaphor_prompt
        self.agent_crisis = agent_crisis
        self.agent_solution = agent_solution
        self.code_focus = code_focus
        self.instructions = instructions

    def instructions_for(self, step_name: str) -> str:
        """
        Return the instruction block for a given scaffold step.
        """
        return self.instructions.get(step_name, "")


# -------------------------------------------------------------------------
# TOPIC 1: ARRAYLIST (The Suitcase / Dynamic Resizing)
# -------------------------------------------------------------------------
ARRAYLIST_TOPIC = ResearchTopic(
    key="arraylist",
    name="Dynamic ArrayList",
    difficulty="easy",
    concept=(
        "An abstraction that allows an array to feel 'infinite' by secretly "
        "replacing a full underlying array with a larger one."
    ),
    key_points=[
        "Java arrays are fixed size; ArrayList feels 'infinite'.",
        "When full, it creates a new, larger array (Hidden Work).",
        "It copies all old items to the new array.",
        "Then it points the reference variable to the new array.",
        "The crisis: what happens when the suitcase (array) is full?"
    ],
    metaphor_prompt=(
        "Think about an ArrayList like a suitcase. If your suitcase is full, "
        "but you bought more clothes, what do you do? You have to buy a bigger "
        "suitcase and move ALL your clothes over to the new one before you can "
        "add the new items."
    ),
    agent_crisis=(
        "Java arrays are fixed size. If our array has 4 slots and they are all "
        "full, and we try to add a 5th element, the program crashes. How do we "
        "fix this without changing the nature of arrays?"
    ),
    agent_solution=(
        "We need to create a new, larger array, copy everything over, and then "
        "switch to using that new array (e.g., internalArray = newArray)."
    ),
    code_focus=(
        "The resizing logic: checking if full, creating newArray, copying items, "
        "and reassigning internalArray."
    ),
    instructions={
        "initial_metaphor": (
            "Start with this metaphor:\n"
            "\"{metaphor_prompt}\"\n"
            "Then ask the student what this reminds them of from their own life."
        ),
        "student_metaphor": (
            "1. Briefly acknowledge the student's metaphor or example.\n"
            "2. Pivot to the conflict: {agent_crisis}\n"
            "3. Ask: 'Ready to see how this works visually?'"
        ),
        "visual_diagram": (
            "The visual was already shown. Do NOT show it again.\n"
            "Ask ONE question: 'What part of this diagram is most helpful?'\n"
            "Listen to their answer, then move forward. Keep response under 50 words."
        ),
        "code_structure": (
            "Show the resize() method implementation ONCE.\n"
            "Highlight: (1) create new array, (2) copy loop, (3) reassign reference.\n"
            "Ask ONE focused question: 'What do you notice about this copy loop?'\n"
            "Do NOT walk through pseudocode. Do NOT re-explain resizing logic."
        ),
        "contrast": (
            "1. Ask: 'What do you think Java's ArrayList does behind the scenes "
            "when it runs out of space?'\n"
            "2. Explain that ArrayList performs a similar resize: it creates a "
            "bigger array, copies all elements, and switches to that array.\n"
            "3. Highlight that the heavy O(n) work still happens; it's just hidden "
            "from the programmer."
        ),
        "code_usage": (
            "Show ONE simple usage example: creating array, adding elements.\n"
            "Mention resize happens automatically when capacity exceeded.\n"
            "Ask: 'What happens performance-wise when we add 1000 items?'\n"
            "Do NOT re-explain resizing. Student already knows this."
        ),
        "practice": (
            "Ask ONE practice question about when resizing occurs.\n"
            "Example: 'If capacity is 8 and size is 7, what happens when we add 2 elements?'\n"
            "Give brief feedback. Move to reflection quickly."
        ),
        "reflection": (
            "Ask student to summarize what they learned in 1-2 sentences.\n"
            "Key point: ArrayList feels infinite but has O(n) resize cost.\n"
            "This is the final step - wrap up concisely."
        ),
    }
)
# -------------------------------------------------------------------------
# TOPIC 2: RECURSION (The Stop Sign / Base Case)
# -------------------------------------------------------------------------
RECURSION_TOPIC = ResearchTopic(
    key="recursion",
    name="Recursion: The Stop Sign (Base Case)",
    difficulty="medium",
    concept=(
        "A method that solves a problem by calling a smaller version of itself "
        "until it reaches a trivial solution (the base case)."
    ),
    key_points=[
        "Recursion solves a problem by calling a smaller version of itself.",
        "The base case is the 'Stop Sign' where recursion ends.",
        "The recursive case does work and calls the function again.",
        "The call stack fills up with pending recursive calls.",
    ],
    metaphor_prompt=(
        "Think of recursion like a process that keeps stepping down a staircase "
        "until it reaches the bottom step, where it can finally stop and turn around."
    ),
    agent_crisis=(
        "If we write a recursive function without an if-statement or base case, "
        "and we call it, it calls itself, which calls itself, and so on. When "
        "does it actually return a value?"
    ),
    agent_solution=(
        "We must define a base case—the 'Stop Sign'—that returns a simple, "
        "hard-coded value, and ensure each recursive call moves us closer to that base case."
    ),
    code_focus=(
        "Distinguishing the base case from the recursive case and ensuring that "
        "each call reduces n so we eventually hit the base case."
    ),
    instructions={
        "initial_metaphor": (
            "Start with a simple metaphor for recursion, such as walking down a "
            "staircase one step at a time until you reach the bottom.\n"
            "Use this to hint that there must be a final, simplest step where you stop."
        ),
        "student_metaphor": (
            "1. Acknowledge the student's metaphor or example.\n"
            "2. Pivot to the crisis: {agent_crisis}\n"
            "3. Ask: 'Ready to see how the call stack works visually?'"
        ),
        "visual_diagram": (
            "The student has seen a visual diagram showing the recursive call stack.\n"
            "1. Explain how each recursive call gets added to the stack, building up.\n"
            "2. Point out how the base case stops the recursion.\n"
            "3. Show how the stack unwinds, each call returning its value.\n"
            "4. Ask: 'Can you see how the stack builds up and then unwinds?'"
        ),
        "code_structure": (
            "1. Show a recursive factorial function and first present it WITHOUT "
            "a base case to create the 'crisis'.\n"
            "2. Ask: 'If I call this version, when does it stop calling itself?'\n"
            "3. Then introduce the proper structure:\n"
            "   FUNCTION factorial(n):\n"
            "       IF n == 1:\n"
            "           RETURN 1           // Base Case (Stop Sign)\n"
            "       ELSE:\n"
            "           RETURN n * factorial(n - 1)  // Recursive Case\n"
            "4. Emphasize the difference between the base case (stop sign) and "
            "the recursive case (doing work and calling again)."
        ),
        "code_usage": (
            "1. Ask: 'What happens if we remove or forget the base case?'\n"
            "2. Explain that the call stack fills up with recursive calls, leading "
            "to a stack overflow.\n"
            "3. Ask them to identify which line is the base case and which is the "
            "recursive case in the factorial example."
        ),
        "practice": (
            "1. Review the student's attempt at writing or modifying a recursive function.\n"
            "2. Help them clearly separate the base case from the recursive case.\n"
            "3. Ensure that the recursive call always moves n closer to the base case "
            "(for example, n - 1 in factorial)."
        ),
        "reflection": (
            "1. Ask: 'How does thinking in terms of a base case and recursive case "
            "help you design recursive functions?'\n"
            "2. Have them restate the role of the base case as the 'Stop Sign'.\n"
            "3. Ask them to explain, in their own words, how the call stack fills "
            "and then unwinds in the factorial example."
        ),
    }
)

RESEARCH_TOPICS = {
    'arraylist': ARRAYLIST_TOPIC,
    'recursion': RECURSION_TOPIC
}

def get_research_topic(topic_key: str) -> ResearchTopic:
    if topic_key not in RESEARCH_TOPICS:
        for topic in RESEARCH_TOPICS.values():
            if topic.name == topic_key:
                return topic
        raise ValueError(f"Topic '{topic_key}' not found")
    return RESEARCH_TOPICS[topic_key]