from typing import TypedDict, Optional

class GraderState(TypedDict):
    """
    State for the Short Answer Grader Agent.
    """
    student_answer: str
    correct_answer: str
    question: str
    max_score: int
    
    # Outputs
    assigned_score: Optional[int]
    feedback: Optional[str]
    confidence: Optional[float]
