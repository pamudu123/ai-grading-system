from typing import Any
from .graph import build_grader_graph
from .state import GraderState

def grade_short_answer(
    question: str, 
    student_answer: str, 
    correct_answer: str, 
    max_score: int = 10
) -> dict[str, Any]:
    """
    Grades a short answer question.
    
    Args:
        question: The question text.
        student_answer: The answer provided by the student.
        correct_answer: The model correct answer.
        max_score: Maximum possible score (default 10).
        
    Returns:
        Dictionary containing assigned_score, feedback, and confidence.
    """
    app = build_grader_graph()
    
    initial_state: GraderState = {
        "question": question,
        "student_answer": student_answer,
        "correct_answer": correct_answer,
        "max_score": max_score,
        "assigned_score": 0,
        "feedback": "",
        "confidence": 0.0
    }
    
    final_state = app.invoke(initial_state)
    
    return {
        "assigned_score": final_state.get("assigned_score"),
        "feedback": final_state.get("feedback"),
        "confidence": final_state.get("confidence")
    }
