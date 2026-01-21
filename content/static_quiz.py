"""
Static Quiz Questions
Same questions for all participants to ensure valid comparison
"""

from dataclasses import dataclass
from typing import List


@dataclass
class QuizQuestion:
    """A quiz question with multiple choice answers"""
    question: str
    options: List[str]
    correct_index: int  # Index of correct answer (0-based)
    explanation: str


# TODO: Replace with actual quiz questions from professors

ARRAYLIST_QUIZ = [
    QuizQuestion(
        question="""Scenario: You want to store a list of student test scores (whole numbers) in an ArrayList. 
                You try to write: ArrayList<int> scores = new ArrayList<>();
                Why will this code cause a compiler error in Java?""",
        options=[
            "ArrayList can only store Objects (like Integer), not primitive data types (like int).",
            "ArrayList is only designed to hold text (String), not numbers.",
            "You forgot to specify the maximum number of scores in the parentheses.",
            "You must use a Double array if you want to store any kind of number."
        ],
        correct_index=0,
        explanation="Generics in Java do not support primitive types; you must use Wrapper classes like Integer."
    ),
    QuizQuestion(
        question="""Scenario: You have an array int[] nums = {1, 2, 3}; and an ArrayList<Integer> list. 
                Both have data inside them. Which of the following correctly shows how to get the 
                value at the second position (index 1) for both?""",
        options=[
            "Array: nums.get(1); ArrayList: list[1]",
            "Array: nums[1]; ArrayList: list[1]",
            "Array: nums[1]; ArrayList: list.get(1)",
            "Array: nums.get(1); ArrayList: list.get(1)"
        ],
        correct_index=2,
        explanation="Arrays use square brackets [] while ArrayLists use the .get() method."
    ),
    QuizQuestion(
        question="""Scenario: You have a list of tasks in an ArrayList. When a task is finished, 
                you use the .remove(0) method to delete the first item. What happens to the 
                remaining items in the ArrayList after you remove the item at index 0?""",
        options=[
            "The index 0 becomes null, and all other items stay at their original index.",
            "All remaining items automatically shift down one position (the item at index 1 moves to index 0).",
            "The ArrayList is deleted from memory, and you must create a new one.",
            "The program will throw an error because you are only allowed to remove items from the end."
        ],
        correct_index=1,
        explanation="ArrayLists are contiguous; removing an element causes all subsequent elements to shift left."
    )
]


RECURSION_QUIZ = [
    QuizQuestion(
        question="What is essential for every recursive method?",
        options=[
            "A loop",
            "A base case",
            "Multiple parameters",
            "A return type of int"
        ],
        correct_index=1,
        explanation="Every recursive method MUST have a base case to stop the recursion, otherwise it will run forever and cause a stack overflow."
    ),
    
    QuizQuestion(
        question="What happens if a recursive method has no base case?",
        options=[
            "It returns 0",
            "It runs forever until stack overflow",
            "It automatically stops after 100 calls",
            "The compiler prevents it"
        ],
        correct_index=1,
        explanation="Without a base case, the method keeps calling itself forever until the call stack runs out of memory (stack overflow)."
    ),
    
    QuizQuestion(
        question="In recursion, where are function calls stored?",
        options=[
            "The heap",
            "The cache",
            "The call stack",
            "The hard drive"
        ],
        correct_index=2,
        explanation="Each recursive call is pushed onto the call stack, which is why too many recursive calls can cause stack overflow."
    ),
    
    QuizQuestion(
        question="What does factorial(3) return if defined recursively?",
        options=[
            "3",
            "6",
            "9",
            "12"
        ],
        correct_index=1,
        explanation="factorial(3) = 3 * 2 * 1 = 6. The recursive calls compute 3 * factorial(2), where factorial(2) = 2 * 1."
    ),
    
    QuizQuestion(
        question="What is the base case in fibonacci(n)?",
        options=[
            "n == 0",
            "n == 0 or n == 1",
            "n < 0",
            "n == 10"
        ],
        correct_index=1,
        explanation="Fibonacci has two base cases: fib(0) = 0 and fib(1) = 1. These stop the recursion."
    ),
    
    QuizQuestion(
        question="Compared to iteration, recursion typically uses:",
        options=[
            "Less memory",
            "More memory due to call stack",
            "The same amount of memory",
            "No memory"
        ],
        correct_index=1,
        explanation="Each recursive call uses stack memory. Iteration uses less memory since it doesn't create multiple stack frames."
    ),
    
    QuizQuestion(
        question="Which problem is naturally suited for recursion?",
        options=[
            "Printing numbers 1 to 100",
            "Traversing a tree structure",
            "Finding the maximum in an array",
            "Swapping two variables"
        ],
        correct_index=1,
        explanation="Tree traversal is naturally recursive because trees have a recursive structure (each node has subtrees)."
    )
]


# Use 5 questions for each topic (can adjust based on professor feedback)
ARRAYLIST_QUIZ_FINAL = ARRAYLIST_QUIZ[:5]
RECURSION_QUIZ_FINAL = RECURSION_QUIZ[:5]


def get_quiz(topic_key: str) -> List[QuizQuestion]:
    """Get the quiz for a specific topic."""
    if topic_key == 'arraylist':
        return ARRAYLIST_QUIZ_FINAL
    elif topic_key == 'recursion':
        return RECURSION_QUIZ_FINAL
    else:
        return []


def score_quiz(topic_key: str, user_answers: dict) -> tuple:
    """
    Score a quiz.
    
    Args:
        topic_key: 'arraylist' or 'recursion'
        user_answers: dict mapping question index to selected answer text
    
    Returns:
        (score, total, results_list)
        results_list contains dicts with question, user_answer, correct_answer, is_correct
    """
    quiz = get_quiz(topic_key)
    results = []
    score = 0
    
    for i, question in enumerate(quiz):
        user_answer = user_answers.get(i)
        correct_answer = question.options[question.correct_index]
        is_correct = user_answer == correct_answer
        
        if is_correct:
            score += 1
        
        results.append({
            'question': question.question,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question.explanation
        })
    
    return score, len(quiz), results


